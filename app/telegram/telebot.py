from telethon import TelegramClient
import yaml

# Use a config file for moment
with open('./app/telegram/config.yaml', 'r') as stream: 
    config = yaml.safe_load(stream)
    api_id = config['api_id']
    api_hash = config['api_hash']
    bot_token = config['bot_token']


bot = TelegramClient("bot", api_id, api_hash)
# Starting as a bot account


# But then we can use the client instance as usual
async def main():
    channel = await bot.get_input_entity('t.me/provalolasd')
    print(channel)
    message = await bot.send_message(channel, message="Hello")
    print(message)


with bot.start(bot_token=bot_token):
    bot.loop.run_until_complete(main())

