#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from functools import wraps
import logging

from telegram import ParseMode
from telegram.ext import Updater, CommandHandler
from telegram.utils.helpers import escape_markdown

from config import TOKEN, WHITELIST
from paths import PATHS


logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    filename="squire.log",
)
logger = logging.getLogger(__name__)


def whitelist_only(func):
    @wraps(func)
    def wrapped(update, context, *args, **kwargs):
        user = update.effective_user
        logger.info(
            f"@{user.username} ({user.id}) is trying to access a privileged command"
        )
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
        "Hi!"
        "I can /fetch you some files if you are whitelisted\n"
        "/help to learn more"
    )
    update.message.reply_text(text)


def show_help(update, context):
    """Send a message when the command /help is issued."""
    howto = (
        f"▪️Download this [repo](https://github.com/mtalimanchuk/file-squire-bot) to your remote machine\n"
        f"\n"
        f"▪️Open `config.py`, set your `TOKEN` (string) and `WHITELIST` (list of user IDs)\n"
        f"\n"
        f"▪️Open `paths.py`, add aliases and paths to `{escape_markdown('PATH_MAP')}`:\n"
        f"\n"
        f"`PATH_MAP = {{\n"
        f'\t"me": "squire.log", \n'
        f'\t"flask": "myflaskapp/logs/errors.log"\n}}`\n'
        f"\n"
        f"▪️Start the bot. Fetch files using aliases in `paths.py`\n"
        f"\t`/fetch me` to get _squire.log_"
    )
    update.message.reply_text(howto, parse_mode=ParseMode.MARKDOWN)


@whitelist_only
def fetch_file(update, context):
    """Send a message or a file when the command /fetch [alias] is issued."""
    if context.args:
        for arg in context.args:
            try:
                path_alias = arg
                path = PATHS[path_alias]
                f = path.open("rb")
                logger.info(f"Sending {path} to {update.effective_user.username}")
                update.message.reply_document(
                    f, caption=f"Your `{path}`, sir!", parse_mode=ParseMode.MARKDOWN
                )
            except KeyError:
                text = (
                    f"❌\nCouldn't find alias *{path_alias}*.\n"
                    f"Make sure you've added it to `paths.py`"
                )
                update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            except FileNotFoundError:
                text = (
                    f"❌\n*{path}* does not exist.\n"
                    f"Make sure  alias `{path_alias}` is pointing to an existing file"
                )
                update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)
            except AttributeError:
                # sometimes editing a previously sent chat message
                # triggers the handler with an empty update
                pass

    else:
        text = (
            "⚠️\nPlease provide a configured path:\n"
            "`/fetch log_alias`\n"
            "You can add them to `paths.py`"
        )
        update.message.reply_text(text, parse_mode=ParseMode.MARKDOWN)


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


if __name__ == "__main__":
    main()
