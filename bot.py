from telegram.ext import Updater, CommandHandler
import requests, time
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

main_message = 'Bem-vindo à Rossman! Para prever o faturamento, digite o comando com ano e o mês (a partir do mês de agosto de 2015) nesse formato: /predict 8-2015'

def start(update, context):
    update.message.reply_text(main_message)

def predict(update, context):
    text = update.message.text.split('/predict ')
    chat_id = update.message.chat_id

    # if user message is not empty
    if(len(text) == 2):
        # get month and year
        date = text[1].split('-')

        # if format is invalid
        if len(date) != 2:
            update.message.reply_text('Formato inválido!')
        else:
            month, year = date
            # request to API
            url = 'https://rossman-drugstore-sales.herokuapp.com/predict'
            response = requests.post(url, json={
            "Year": year,
            "Month": month
            })
            time.sleep(5)

            # if request is sucessful
            if(response.status_code == 200):
                response = pd.DataFrame(response.json(), columns=response.json()[0].keys())
                new_dataset = response[['Prediction', 'Day']].groupby('Day').sum().reset_index()
                fig = sns.lineplot(data=new_dataset, x="Day", y="Prediction")
                fig.ticklabel_format(style='plain', axis='y')

                # save plot as png
                plt.savefig('assets/prediction_plot.png')

                time.sleep(2)

                # send plot to user
                context.bot.sendPhoto(chat_id=chat_id, caption=f'Faturamento nos dias do mês {month} de {year}', photo=open('assets/prediction_plot.png', 'rb'))

            # if request is unsucessful
            else:
                update.message.reply_text('Dados não disponíveis ou ocorreu um erro na requisição')
    
    # if user message is empty
    else:
        update.message.reply_text('Adicione uma data ao comando!')

def main():

    os.environ['BOT_TOKEN'] = "5385864743:AAEiOs14z7a_ebSfsSXTkXogU516_j8X5q4"
    os.environ['URL'] = "https://rossman-drugstore-telegram-bot.herokuapp.com/"
   # start the bot.
    BOT_TOKEN =  os.environ.get('BOT_TOKEN')
    URL = os.environ.get('URL')
    updater = Updater(BOT_TOKEN, use_context=True)
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("predict", predict))

    updater.start_polling()
    print("Bot is running!")

if __name__ == '__main__':
    main()