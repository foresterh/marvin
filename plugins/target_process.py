from util import hook, web
import json
import textwrap
import datetime


class Target_Process():
    user = ''
    password = ''
    tp_uri = ''

    def __init__(self, tp_name, username, password):
        self.data = []
        self.username = username
        self.password = password
        self.tp_uri = tp_name

    def get_object(self, api_suffix):
        # auth = base64.encodestring("%s:%s" % (self.user, self.password)).strip()
        # request = urllib.request.Request(self.tp_uri + api_suffix + "&format=json")
        # request.add_header("Authorization", "Basic %s" % auth)
        # response = urllib.request.urlopen(request)
        response = web.get_json(self.tp_uri + api_suffix, auth=(self.username, self.password))
        return response.read()

def json_date_as_datetime(jd):
    sign = jd[-7]
    if sign not in '-+' or len(jd) == 13:
        ms = int(jd[6:-2])
    else:
        ms = int(jd[6:-7])
        hh = int(jd[-7:-4])
        mm = int(jd[-4:-2])
        if sign == '-': mm = -mm
        ms += (hh * 60 + mm) * 60000
    return datetime.datetime(1970, 1, 1) \
        + datetime.timedelta(microseconds=ms * 1000)

@hook.regex(r'\bt(?:arget)?\ {0,2}p(?:rocess)?\ {1,2}recent\ {1,2}(?:(?P<days>\d{1,2})\ {0,2}da?y?s?|(?P<hours>\d{1,2})\ {0,2}ho?u?r?s?)\s*$', run_always=True)
def target_process(bot_input, bot_output):
    tp = Target_Process(bot_input.credentials["url"], bot_input.credentials["login"], bot_input.credentials["password"])

    days = bot_input.groupdict()["days"]
    hours = bot_input.groupdict()["hours"]

    if days is not None:
        comparison_date =  datetime.datetime.now() + datetime.timedelta(-1*int(days))
        output_string = "Stories modified in the last " + days + " days: \n"
        bug_string = "Bugs modified in the last " + days + " days: \n"
    else:
        comparison_date =  datetime.datetime.now() + datetime.timedelta(0, 0, 0, 0, 0, -1*int(hours))
        output_string = "Stories modified in the last " + hours + " hours: \n"
        bug_string = "Bugs modified in the last " + hours + " hours: \n"

    for user_story in json.loads(tp.get_object("UserStories?include=[Name,EntityState,ModifyDate,Effort]&where=(ModifyDate%20gte%20" + comparison_date.strftime("'%Y-%m-%d'") + ")%20and%20(Team.Name%20eq%20'" + bot_input.credentials["team_name"] + "')"))["Items"]:

        story_id = str(user_story["Id"])
        padding = " " * len(story_id + " - ")

        if json_date_as_datetime(user_story["ModifyDate"]) < comparison_date:
            continue

        output_string += "\n\t" + ("\n\t" + padding).join(textwrap.wrap(story_id  + " - " + user_story["Name"] + " [" + str(user_story["Effort"]) + "pt, " + user_story["EntityState"]["Name"] + "]", 80)) + "\n"

        lastEffort = None
        lastState = None

        for user_story_history in json.loads(tp.get_object("UserStoryHistories/?include=[Effort,EntityState,Modifier,Date]&where=UserStory.Id%20eq%20" + story_id))["Items"]:

            modifiedDate = json_date_as_datetime(user_story_history["Date"])
            modifiedDateStr = modifiedDate.strftime("%m/%d/%y %I:%M%p").replace(" 0", " ")

            state = user_story_history["EntityState"]["Name"]
            effort = str(user_story_history["Effort"]) + "pt"

            if json_date_as_datetime(user_story_history["Date"]) < comparison_date:
                lastState = state
                lastEffort = effort
                continue

            user = user_story_history["Modifier"]["FirstName"] + " " + user_story_history["Modifier"]["LastName"]

            if lastState:
                if lastState != state:
                    output_string += padding + " => " + user + " modified the state from " + lastState + " -> " + state + " on " + modifiedDateStr + "\n"
                if lastEffort != effort:
                    output_string += padding + " => " + user + " changed the effort from " + lastEffort + " -> " + effort + " on " + modifiedDateStr + "\n"
            else:
                output_string += padding + " => " + user + " added this " + effort + " story on " + modifiedDateStr + "\n"

            lastEffort = effort
            lastState = state

    bot_output.say(output_string.encode('UTF-8'))
    output_string = bug_string

    for bug in json.loads(tp.get_object("Bugs?include=[Name,UserStory,EntityState,ModifyDate]&where=(ModifyDate%20gte%20" + comparison_date.strftime("'%Y-%m-%d'") + ")%20and%20(Team.Name%20eq%20'" + bot_input.credentials["team_name"] + "')"))["Items"]:

        bug_id = str(bug["Id"])
        story_id = str(bug["UserStory"]["Id"])
        padding = " " * len(bug_id + " - ")

        if json_date_as_datetime(bug["ModifyDate"]) < comparison_date:
            continue

        output_string += "\n\t" + ("\n\t" + padding).join(textwrap.wrap(bug_id + " - " + bug["Name"] + " [" + bug["EntityState"]["Name"] + ", Story " + story_id + "]", 80)) + "\n"

        lastState = None

        for bug_history in json.loads(tp.get_object("BugHistories/?include=[EntityState,Modifier,Date]&where=Bug.Id%20eq%20" + bug_id))["Items"]:

            modifiedDate = json_date_as_datetime(bug_history["Date"])
            modifiedDateStr = modifiedDate.strftime("%m/%d/%y %I:%M%p").replace(" 0", " ")

            state = bug_history["EntityState"]["Name"]

            if json_date_as_datetime(bug_history["Date"]) < comparison_date:
                lastState = state
                continue

            user = bug_history["Modifier"]["FirstName"] + " " + bug_history["Modifier"]["LastName"]

            if lastState:
                if lastState != state:
                    output_string += padding + " => " + user + " modified the state from " + lastState + " -> " + state + " on " + modifiedDateStr + "\n"
            else:
                output_string += padding + " => " + user + " created this bug on " + modifiedDateStr + "\n"

            lastState = state

    bot_output.say(output_string.encode('UTF-8'))