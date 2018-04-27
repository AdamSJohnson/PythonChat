import Chat
import Chat2

def choice_getter():
    try:
        choice = int(input('1 to Host\n2 to connect: '))
        if choice == 1 or choice == 2:
            return choice
        else:
            return 0
    except ValueError:
        return 0
#get a choice value of 1 or 2 to initalize either the host chat 
# or the connecting chat
choice = choice_getter()
while not choice:
    choice = choice_getter()


if choice == 1:
    Chat.chat_server()
else:
    Chat2.chat_server()