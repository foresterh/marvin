from util import hook, storage


@hook.regex(r'(add )(?P<item>[\w\d\s]*)( to )(the |my )?(?P<list>[\w\d]*)( list)', run_always=True)
def add_to_list(bot_input, bot_output):
    """add [item] to [list name] -- adds something to a list that can be viewed or randomly selected from"""
    if bot_input.groupdict():
        item = bot_input.groupdict()["item"]
        list_name = bot_input.groupdict()["list"]
        storage.add_to_list(list_name, item)
        bot_output.say("Added %s to %s choices" % (item, list_name))


@hook.regex(r'(what\'s|when\'s|when is|get|view|search for|show) (on |my |me |the )*?(?P<request>[\w\d]*)( list)',
            run_always=True)
def search_list(bot_input, bot_output):
    if bot_input.groupdict():
        list_name = bot_input.groupdict()["request"]
        list_items =  storage.get_list(list_name)
        if list_items:
            bot_output.say(", ".join(list_items))
        else:
            bot_output.say("There's as many items on that list as there are friends in your phone.")


@hook.regex(r'(pick|decide|where) (something )?(random|from|on|my|me|the| )*(?P<request>[\w\d]*)( list)',
            run_always=True)
def show_random_list_item(bot_input, bot_output):
    if bot_input.groupdict():
        list_name = bot_input.groupdict()["request"]
        if list_name in storage:
            result = storage.get_random_value(list_name)
            bot_output.say("I pick %s" % result)
        else:
            bot_output.say("There's as many items on that list as there are friends in your phone.")