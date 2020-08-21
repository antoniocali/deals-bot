from telethon import TelegramClient
from telethon.hints import EntityLike
from telethon.tl.types import PeerUser

# Use your own values from my.telegram.org
api_id = 1733178
api_hash = "cdb7ddc714337bc3124a5d3be496305d"
bot_token = "1359800920:AAEdWoszwb3MVlmag9400flUG1DTItXhyHw"

# We have to manually call "start" if we want an explicit bot token

bot = TelegramClient("bot", api_id, api_hash)
from telethon.tl.functions.messages import AddChatUserRequest
# Starting as a bot account


# But then we can use the client instance as usual
async def main():
    username = await bot.get_input_entity('t.me/provalolasd')
    print(username)
    # await bot(AddChatUserRequest())
    message = await bot.send_message(username, message="Hello")

    # message = bot.send_message(username, message='Some <b>bold</b> and <i>italic</i> text')
    # print(message)


with bot.start(bot_token=bot_token):
    bot.loop.run_until_complete(main())

