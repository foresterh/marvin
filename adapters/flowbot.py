from external.flowdock import JSONStream, Chat
from core import marvin
from util import logger, web, dictionaryutils

class BotInput(object):
    def __getitem__(self, val):
        return self.__dict__[val]

    def __setitem__(self, key, value):
        self[key] = value


class BotOutput():

    def __init__(self, config):
        self.setup(config)

    def setup(self, config):
        self.flow_user_api_key = config["flow_user_api_key"]
        # chattiness on a scale of 0 to 1 (most is every time)
        self.chattiness = 0.5
        self.flow_token = config["flow_token"]
        self.channels = config["channels"]
        self.debug = bool(config["debug"])
        self.nick = config["nick"]
        self.username = config["username"]
        self.password = config["password"]
        self.master = config["master"]
        self.users = []
        self.responses = config["responses"]

        self.chat = Chat(self.flow_token)

    def say(self, msg):
        logger.log("sending message %s" % msg[:20])
        self.chat.post(msg, self.nick)

    def private_message(self, msg):
        logger.log("sending private message %s" % msg)
        self.chat.post(msg, self.nick)


    def get_users(self):
        endpoint = "users"
        url = "https://api.flowdock.com/v1/%s"

        user_endpoint = url % endpoint
        logger.log("hitting endpoint: %s" % user_endpoint)
        self.users = web.get_json(user_endpoint, self.username, self.password)
        return self.users


    def get_user_by_id(self, user_id):
        if not self.users:
            self.get_users()
        user = [u for u in self.users if str(u["id"]) == user_id]
        if user and len(user):
            return user[0]
        return "anonymous"


    def get_user_by_name(self, user_name):
        if not self.users:
            self.get_users()
        user = [u for u in self.users if str(u["nick"]) == user_name]
        if user and len(user):
            return user[0]
        return "anonymous"


    def run_markov(self, data):
        markov_input = dictionaryutils.DictToObject(**data)
        user_id = data['nick']
        markov_input.nick = self.get_user(user_id)
        markov.markov_master(self, markov_input)

    def run_imitate(self, data):
        markov_input = dictionaryutils.DictToObject(**data)
        user_id = data['nick']
        markov_input.nick = self.get_user(user_id)
        markov.markov_imitate(self, markov_input)

    def _parse_stream(self, bot):
        stream = JSONStream(self.flow_user_api_key)
        gen = stream.fetch(self.channels, active=True)
        for data in gen:
            #logger.log(data)
            process_message = type(data) == dict and (data['event'] == "message" or data['event'] == "comment")
            if process_message and ('external_user_name' not in data or data['external_user_name'].lower() != self.nick.lower()):
                bot_input = BotInput()
                if type(data['content']) is dict:
                    bot_input.message = data["content"]['text'].lower()
                elif "content" in data:
                    bot_input.message = data["content"].lower()
                else:
                    break
                if ("user" in data and int(data["user"]) > 0):
                    bot_input.nick = self.get_user_by_id(data["user"])["nick"]
                elif ("external_name" in data):
                    bot_input.nick = data["external_name"]
                else:
                    bot_input.nick = "anonymous"
                bot_input.bot = bot

                marvin.process(bot_input, self)


    def run(self, bot):
        self.user = str(self.get_user_by_name(self.nick)["id"])
        marvin.say_hi(self)
        self._parse_stream(bot)