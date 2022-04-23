import re
from flask import Flask, request
import telegram

import os

global bot
global BOT_TOKEN
BOT_TOKEN = os.environ.get('BOT_TOKEN')
URL = os.environ.get('URL')
bot = telegram.Bot(token=BOT_TOKEN)

app = Flask(__name__)

@app.route(f'/{BOT_TOKEN}'.format(BOT_TOKEN), methods=['POST'])
def respond():
   # retrieve the message in JSON and then transform it to Telegram object
  update = telegram.Update.de_json(request.get_json(force=True), bot)

  chat_id = update.message.chat.id
  msg_id = update.message.message_id

   # Telegram understands UTF-8, so encode text for unicode compatibility
  text = update.message.text.encode('utf-8').decode()
   # for debugging purposes only
  print("got text message :", text)
   # the first time you chat with the bot AKA the welcoming message
  if text == "/start":
       # print the welcoming message
      bot_welcome = """
      Welcome to coolAvatar bot, the bot is using the service from http://avatars.adorable.io/ to generate cool looking avatars based on the name you enter so please enter a name and the bot will reply with an avatar for your name.
      """
       # send the welcoming message
      bot.sendMessage(chat_id=chat_id, text=bot_welcome, reply_to_message_id=msg_id)

  if text == "/predict":
    url = "https://avatars.githubusercontent.com/nathaliaop"
    bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
    pass
    '''else:
       try:
           # clear the message we got from any non alphabets
           text = re.sub(r"\W", "_", text)
           # create the api link for the avatar based on http://avatars.adorable.io/
           url = "https://api.adorable.io/avatars/285/{}.png".format(text.strip())
           # reply with a photo to the name the user sent,
           # note that you can send photos by url and telegram will fetch it for you
           bot.sendPhoto(chat_id=chat_id, photo=url, reply_to_message_id=msg_id)
       except Exception:
           # if things went wrong
           bot.sendMessage(chat_id=chat_id, text="There was a problem in the name you used, please enter different name", reply_to_message_id=msg_id)'''

  return 'ok'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
  bot_running = bot.setWebhook(f'https://api.telegram.org/bot{BOT_TOKEN}/setWebhook?url={URL}')
  if bot_running:
      return "Bot is running!"
  else:
      return "Something went wrong..."

@app.route('/')
def index():
    return '.'

if __name__ == '__main__':
  port = os.environ.get('PORT', 5000)
  app.run(host='0.0.0.0', port=port)
