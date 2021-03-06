from util import hook

@hook.command
def chattiness(bot_input, bot_output):
    if bot_input.input_string:
        new_setting = bot_input.input_string
        if type(new_setting) is not int:
            bot_output.say("Nice try, {user_nick}.")
            return

        new_chattiness = int(new_setting)
        if type(new_chattiness) is int and 0 <= new_chattiness <= 100:
            old_chattiness = int(bot_output.chattiness * 100)
            new_chattiness = new_chattiness
            bot_output.chattiness = float(new_chattiness) / 100
            if old_chattiness < new_chattiness:
                bot_output.say("Looks like I'll be chatting much more now.")
            elif old_chattiness > new_chattiness:
                bot_output.say("I guess I won't be saying as much now.")
            else:
                bot_output.say("Are you drunk?  I can't change my chattiness to be what it is already!!??")
        else:
            bot_output.say("Soo.... I can only chat between 1 and 100 times out every 100 chances I get.\
            So... enter a 1, or 100, or a number between those, m'kay?")
    else:
        bot_output.say("Current chattiness is {0} out of every 100 times.  Pass chattiness number in to update".format(int(bot_output.chattiness * 100)))
