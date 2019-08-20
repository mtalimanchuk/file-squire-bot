#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
import logging
from pathlib import Path

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler

from config import TOKEN, WHITELIST


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='squire.log')
logger = logging.getLogger(__name__)


def whitelist_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(f"@{user.username} ({user.id}) is trying to access a privileged command")
        if user.id not in WHITELIST:
            logger.warning(f"Unauthorized access denied for {user.username}.")
            text = (
                "🚫 *ACCESS DENIED*\n"
                "Sorry, you are *not authorized* to use this command"
            )
            update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            return
        return func(update, context, *args, **kwargs)
    return wrapped


def start(update, context):
    """Send a message when the command /start is issued."""
    text = (
            "Hey! I can fetch some files if you're whitelisted"
            "\n/help to learn more"
    )
    update.message.reply_text(text)


def show_help(update, context):
    """Send a message when the command /help is issued."""
    howto = (
        f"▪️Download this [repo](https://github.com/mtalimanchuk/file-squire-bot) "
        f"to your remote machine\n"
        f"\n"
        f"▪️Open `config.py`, set your TOKEN (string) and WHITELIST (list of user IDs)\n"
        f"\n"
        f"▪️Start the bot. You are ready to fetch files from any device, e.g.\n"
        f"\t`/fetch logs/squire.log`"
    )
    update.message.reply_text(howto, parse_mode=ParseMode.MARKDOWN)


@whitelist_only
def fetch_file(update, context):
    try:
        path = Path(context.args[0])
        f = path.open('rb')
        logger.info(f"Sending {path} to {update.effective_user.username}")
        update.message.reply_document(f,
                                      caption=f"Your `{path}`, sir!",
                                      parse_mode=ParseMode.MARKDOWN)
    except IndexError:
        text = (
            f"⚠️\nPlease provide a configured path, e.g.\n"
            f"`/fetch log_alias`\n"
            f"You can add them to `paths.py`"
        )
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except FileNotFoundError:
        text = f"❌\n*{path}* does not exist."
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
    except AttributeError:
        pass


def error(update, context):
    """Log Errors caused by Updates."""
    logger.warning(f"Update {update} caused error {context.error}")


def main():
    # Create the Updater and pass it your bot's token.
    # Make sure to set use_context=True to use the new context based callbacks
    # Post version 12 this will no longer be necessary
    updater = Updater(TOKEN, use_context=True)

    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", show_help))
    dp.add_handler(CommandHandler("fetch", fetch_file))
    dp.add_error_handler(error)

    updater.start_polling()
    logger.info("BOT DEPLOYED. Ctrl+C to terminate")

    updater.idle()


if __name__ == '__main__':
    main()
