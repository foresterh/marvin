#!/usr/bin/env python

import os
import random
from util import hook, web

l = list()


#def quote_me(phenny, input):
#    quote_to_say =random.sample(l, 1)[0]
#    return quote_to_say
#    #phenny.say(quote_to_say)

@hook.command
def quote(bot_input, bot_output):
    ".q/.quote [#chan] [nick] [#n]/.quote add <nick> <msg> -- gets " \
        "random or [#n]th quote by <nick> or from <#chan>/adds quote"
    quote_to_say =random.sample(l, 1)[0]
    bot_output.say(quote_to_say)


@hook.regex(r'quote (?P<name>[\w\d\s]*)')
def quote_person(bot_input, bot_output):
    url = "http://www.iheartquotes.com/api/v1/random?source=%s"
    #second_url = "http://en.wikiquote.org/w/api.php"
    if bot_input.groupdict():
        person_name = bot_input.groupdict()["name"]
        if person_name:
            quote_api = url % person_name.replace(' ','_')
            user_quote = web.get_text(quote_api)
            if user_quote:
                bot_output.say(user_quote)
            else:
                bot_output.say("Never heard of him.")


def load_quotes(quote_list, file):
    new_quote = ''
    f = open(file, 'r')
    for line in f:
        line = line.strip()
        if line == '%':
            quote_list.append(new_quote)
            new_quote = ''
        else:
            if new_quote != '':
                new_quote += ' '
            new_quote += line
    f.close()

#quote_me.commands = ['quote']
#quote_me.example = '.quote'

# Load all fortunes into memory.
files = os.listdir('quotes')
for file in files:
    load_quotes(l, 'quotes/' + file)
