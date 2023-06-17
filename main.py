import os
import time

from loguru import logger
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler

from db import DB
from utils import get_youtube_video_id

load_dotenv()

db = DB()
db.login(os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'))


async def handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /ping is issued."""
    await update.message.reply_text("pong")


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    if not update.message:
        return
    # temporary fix. Make sure to fix the regex later. This prevents non youtube links from being processed
    if not 'youtu.be' in update.message.text and not 'youtube.com' in update.message.text:
        return
    videoId = get_youtube_video_id(update.message.text)
    if not videoId:
        return
    m = await update.message.reply_text("Loading transcript...", reply_to_message_id=update.message.message_id)
    logger.info(f'Getting transcript for {videoId}...')
    resp = None
    try:
        resp = db.get_transcript(videoId)
        title = resp['title']
        logger.info(f'Got transcript for {videoId}')
        await m.edit_text(f'Generating summary for "{title}"...')
        logger.info(f'Generating summary for {videoId}...')
        summary = None
        try:
            summary = db.get_summary(videoId, str(update.message.chat_id))
        except:
            raise Exception('Error getting summary from DB')
        if summary:
            logger.info(f'Got summary for {videoId} from DB')
            logger.info(summary)
            if 'error' in summary:
                await m.edit_text(summary['error'])
                return
            await m.edit_text(f'Summary for "{title}"\n\n{summary.get("summary")}')
            return
        logger.info(f'Posted summary for {videoId} to DB')
    except Exception as e:
        logger.error(e)
        logger.error(resp)
        if "error" in resp:
            await m.edit_text(resp['error'])
        else:
            await m.edit_text('Error generating summary. If this is a valid video, please try again later.')


def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(
        os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add the command handler to the application
    application.add_handler(CommandHandler("ping", handle_ping))
    application.add_handler(MessageHandler(None, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()


if __name__ == "__main__":
    main()
