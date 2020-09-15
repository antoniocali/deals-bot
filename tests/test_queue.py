from app.messages.message_system import MessageQueue
from time import sleep

c = MessageQueue.get_instance()

while 1:
    if c.isLock():
        sleep(1)
    else:
        print(c.nextElem().deal.category)
        sleep(1)
