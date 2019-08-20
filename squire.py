#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils.helpers import escape_markdown

from config import TOKEN, WHITELIST
from paths import PATHS


logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO,
                    filename='squire.log')
logger = logging.getLogger(__name__)


def whitelist_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(f"@{user.username} ({user.id}) is trying to access a priviledged command")
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
    update.message.reply_text("Hey! I can fetch you some files if you're whitelisted\n/help to learn more")


def show_help(update, context):
    """Send a message when the command /help is issued."""
    howto = (
        f"▪️Download this [repo](https://github.com/mtalimanchuk/file-squire-bot) to your remote machine\n"
        f"\n"
        f"▪️Open `config.py`, set your TOKEN (string) and WHITELIST (list of user IDs)\n"
        f"\n"
        f"▪️Open `paths.py`, add aliases and paths to {escape_markdown('PATH_MAP')}:\n"
        f"\n"
        f"`PATH_MAP = {{\n\t\"me:\" \"squire.log\", \n\t\"flask\": \"myflaskapp/logs/errors.log\"\n}}`\n"
        f"\n"
        f"▪️Start the bot. You are ready to fetch files from any device, e.g.\n"
        f"\t`/fetch me` to get _squire.log_"
    )
    update.message.reply_text(howto, parse_mode=ParseMode.MARKDOWN)


@whitelist_only
def fetch_file(update, context):
    try:
        path_alias = context.args[0]
        path = PATHS[path_alias]
        f = path.open('rb')
        logger.info(f"Sending {path} to {update.effective_user.username}")
        update.message.reply_document(f,
                                      caption=f"Your `{path}`, sir!",
                                      parse_mode=ParseMode.MARKDOWN)
    except IndexError:
        update.message.reply_text("⚠️\nPlease provide a configured path, e.g.\n`/fetch log_alias`\nYou can add them to `paths.py`",
                                  parse_mode=ParseMode.MARKDOWN)
    except KeyError:
        update.message.reply_text(f"❌\nCouldn't find alias *{path_alias}*. Make sure you've added it to `paths.py`",
                                  parse_mode=ParseMode.MARKDOWN)
    except FileNotFoundError:
        update.message.reply_text(f"❌\n*{path}* does not exist. Make sure `{path_alias}` is pointing to the correct file in `paths.py`",
                                  parse_mode=ParseMode.MARKDOWN)
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
