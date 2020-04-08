import logging
import os

from telegram.ext import Updater, CommandHandler
from mcrcon import MCRcon

TG_BOT_TOKEN = os.environ["TG_BOT_TOKEN"]
MCRCON_HOST = os.environ["MCRCON_HOST"]
MCRCON_PASS = os.environ["MCRCON_PASS"]

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)


def start(update, context):
    update.message.reply_text('Available commands: \n'
                              '/list : Lists all currently connected players. \n'
                              '/say <message> : Broadcasts a message to all players as the server. \n'
                              '/give <player> <name> : Gives player blocks/items with the item name name. ')


def execute(command):
    logger.info(command)
    with MCRcon(MCRCON_HOST, MCRCON_PASS) as mcr:
        response = mcr.command(command)
        logger.info(response)
        return response


def list(update, context):
    update.message.reply_text(execute("/list"))


def say(update, context):
    split = update.message.text.split(" ", 1)
    if len(split) == 2:
        message = split[1]
        execute("/say " + message)
        update.message.reply_text(message)


def give(update, context):
    argument = " ".join(update.message.text.split(" ", 2)[1:])
    update.message.reply_text(execute("/give " + argument))


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def main():
    logger.info("TG_BOT_TOKEN=%s", TG_BOT_TOKEN)
    logger.info("MCRCON_HOST=%s", MCRCON_HOST)
    logger.info("MCRCON_PASS=%s", MCRCON_PASS)

    updater = Updater(TG_BOT_TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", start))
    dp.add_handler(CommandHandler("list", list))
    dp.add_handler(CommandHandler("say", say))
    dp.add_handler(CommandHandler("give", give))

    dp.add_error_handler(error)

    updater.start_polling()

    updater.idle()


if __name__ == '__main__':
    main()
