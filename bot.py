from telegram.ext import Updater, CommandHandler
import requests, time, os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

main_message = '''Bem-vindo à Rossman! Para prever o faturamneto das próximas semanas, digite um número de 1 a 6 com um comando no seguinte formato /predict 1

1: Primeira semana de agosto
2: Segunda semana de agosto
3: Terceira seman de agosto
4: Quarta semana de agosto
5: Primeira semana de setembro
6: Segunda semana de setembro'''

error_message = 'Adicione um número de 1 a 6 ao comando! Exemplo: /predict 1'

def api_request(year, month, number, chat_id, context, update):
    # request to API
    url = 'https://rossman-drugstore-sales.herokuapp.com/predict'
    response = requests.post(
        url,
        json = {
        "Year": year,
        "Month": month
        }
    )

    # if request is sucessful
    if(response.status_code == 200):
        response = pd.DataFrame(response.json(), columns=response.json()[0].keys())
        new_dataset = response[['Prediction', 'Day']].groupby('Day').sum().reset_index()
        
        # clear the figure before getting a new one
        plt.clf()
        plt.switch_backend('agg')

        # plot new figure
        fig = sns.lineplot(data=new_dataset, x="Day", y="Prediction")
        fig.ticklabel_format(style='plain', axis='y')
        fig.ticklabel_format(style='plain', axis='x')
        fig.locator_params(integer=True)

        # show only the requested week
        if (number == 1):
            fig.set(xlim=(1, 8))
        if (number == 2):
            fig.set(xlim=(9,15))
        if (number == 3):
            fig.set(xlim=(16,22))
        if (number == 4):
            fig.set(xlim=(23,31))
        if (number == 5):
            fig.set(xlim=(1,5))
        if (number == 6):
            fig.set(xlim=(6,16))

        # save plot as png
        plt.savefig(f'assets/prediction_plot{number}.png')

        # send plot to user
        context.bot.sendPhoto(chat_id=chat_id, caption=f'Faturamento na semana {number}', photo=open(f'assets/prediction_plot{number}.png', 'rb'))

    # if request is unsucessful
    else:
        update.message.reply_text('Ocorreu um erro na requisição')

def start(update, context):
    update.message.reply_text(main_message)

def predict(update, context):
    text = update.message.text.split('/predict ')
    chat_id = update.message.chat_id

    if (len(text) != 2):
        update.message.reply_text(error_message)
        return
    if (text[1]).isdigit() == False:
        update.message.reply_text(error_message)
        return
    number = int(text[1])
    # if user message is not empty
    if (number >= 1) & (number <= 6):
        # get month and year
        year = 2015
        if number <= 4:
            month = 8
        if number > 4:
            month = 9

        context.dispatcher.run_async(api_request, year, month, number, chat_id, context, update)

    # if user message is empty
    else:
        update.message.reply_text(error_message)

def main():
   # start the bot.
    BOT_TOKEN =  os.environ.get('BOT_TOKEN')
    updater = Updater(BOT_TOKEN)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict, run_async=False))

    updater.start_polling()
    print("Bot is running!")

if __name__ == '__main__':
    main()
