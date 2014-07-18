from core import marvin

class BotInput(object):
    def __getitem__(self, val):
        return self.__dict__[val]

    def __setitem__(self, key, value):
        self[key] = value

class BotOutput():
    def __init__(self, config):
        print("Hello")
        self.spoken = False
        self.responses = config["responses"]
        self.chattiness = 0.01
        self.nick = config["nick"]
        self.master = config["master"]


    def say(self, msg):
        print(msg)
        self.spoken = True

    def private_message(self, user, msg):
        print("Private message to %s: %s" % (user, msg))


    def get_user_by_name(self, user_name):
        return {"nick": user_name, "id": 0}


    def run(self, bot):
        self.nick = "bob"#input("What shall I call you? ")
        print("Well hello there {0}.  What can I do for you?".format(self.nick))
        while True:
            self.spoken = False
            message = input("> ")
            if "exit" in message:
                print("Well that's rude.  Goodbye")
                exit()
            bot_input = BotInput()
            bot_input.message = message
            bot_input.bot = bot
            bot_input.nick = self.nick
            marvin.process(bot_input, self)
