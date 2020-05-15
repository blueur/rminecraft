import logging
import os

from mcrcon import MCRcon
from telegram import Update
from telegram.ext import CallbackContext, CommandHandler, Updater

TG_BOT_TOKEN = os.getenv('TG_BOT_TOKEN')
MCRCON_HOST = os.getenv('MCRCON_HOST')
MCRCON_PASS = os.getenv('MCRCON_PASS')
UPDATE_INTERVAL = int(os.getenv('UPDATE_INTERVAL', '8'))

JOB_KEY = 'notification'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


class ContextData:
    def __init__(self, chat_id: int, last_list: str):
        self.chat_id = chat_id
        self.last_list = last_list


def help(update: Update, context: CallbackContext):
    update.message.reply_text('Available commands: \n'
                              '/give <target> <item> [<count>] : Gives an item to a player. \n'
                              '/list : Lists players on the server. \n'
                              '/say <message> : Displays a message to multiple players. \n'
                              '/tell <targets> <message> : Displays a private message to other players. \n'
                              '/subscribe : Subscribe to notifications. \n'
                              '/unsubscribe : Unsubscribe to notifications. \n'
                              )


def execute(command: str):
    logger.debug(command)
    with MCRcon(MCRCON_HOST, MCRCON_PASS) as mcr:
        response = mcr.command(command)
        logger.debug(response)
        return response


def execute_and_reply(update: Update, context: CallbackContext):
    update.message.reply_text(execute(update.message.text))


def execute_silent(update: Update, context: CallbackContext):
    execute(update.message.text)


def list():
    return execute('/list')


def check_notification(context: CallbackContext):
    new_list = list()
    context_data: ContextData = context.job.context
    if new_list != context_data.last_list:
        context.bot.send_message(chat_id=context_data.chat_id, text=new_list)
        context.job.context = ContextData(context_data.chat_id, new_list)


def subscribe(update: Update, context: CallbackContext):
    unsubscribe(update, context)
    context_data = ContextData(update.message.chat_id, list())
    context.chat_data[JOB_KEY] = context.job_queue.run_repeating(check_notification, UPDATE_INTERVAL,
                                                                 context=context_data)


def unsubscribe(update: Update, context: CallbackContext):
    if JOB_KEY in context.chat_data:
        context.chat_data[JOB_KEY].schedule_removal()
        del context.chat_data[JOB_KEY]


def error(update: Update, context: CallbackContext):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logger.info('TG_BOT_TOKEN=%s', TG_BOT_TOKEN)
    logger.info('MCRCON_HOST=%s', MCRCON_HOST)
    logger.info('MCRCON_PASS=%s', MCRCON_PASS)

    updater = Updater(TG_BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', help))
    dp.add_handler(CommandHandler('help', help))
    dp.add_handler(CommandHandler('give', execute_and_reply))
    dp.add_handler(CommandHandler('list', execute_and_reply))
    dp.add_handler(CommandHandler('say', execute_silent))
    dp.add_handler(CommandHandler('tell', execute_and_reply))
    dp.add_handler(CommandHandler('subscribe', subscribe))
    dp.add_handler(CommandHandler('unsubscribe', unsubscribe))

    dp.add_error_handler(error)

    updater.start_polling(poll_interval=UPDATE_INTERVAL)

    updater.idle()


if __name__ == '__main__':
    main()
