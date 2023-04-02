import os
import time

from loguru import logger
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler

from db import DB
from utils import get_youtube_video_id
from ai import chat_gpt_request

load_dotenv()

db = DB()
db.login(os.getenv('DB_USERNAME'), os.getenv('DB_PASSWORD'))

async def handle_ping(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /ping is issued."""
    await update.message.reply_text("pong")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Echo the user message."""
    videoId = get_youtube_video_id(update.message.text)
    if not videoId:
        return
    m = await update.message.reply_text("Loading summary....", reply_to_message_id=update.message.message_id)
    logger.info(f'Getting transcript for {videoId}...')
    try:
        resp = db.get_transcript(videoId)
        transcript = resp['transcript']
        title = resp['title']
        summary = None
        try:
            summary = db.get_summary(videoId)
        except:
            pass
        if summary:
            logger.info(f'Got summary for {videoId} from DB')
            await m.edit_text(f'Summary for "{title}"\n\n{summary.summary}')
            return
        logger.info(f'Getting summary for {videoId}...')
        # get the summary
        start = time.time()
        summary = await chat_gpt_request(transcript)
        end = time.time()
        logger.info(f'Took {round(end-start, 2)}s to generate summary.')
        await m.edit_text(f'Summary for "{title}"\n\n{summary}')
        # post to db
        db.post_summary(videoId, summary)
        logger.info(f'Posted summary for {videoId} to DB')
    except Exception as e:
        logger.error(e)
        await m.edit_text('Error generating summary. If this is a valid video, please try again later.')

def main() -> None:
    """Start the bot."""
    # Create the Application and pass it your bot's token.
    application = Application.builder().token(os.getenv("TELEGRAM_BOT_TOKEN")).build()

    # Add the command handler to the application
    application.add_handler(CommandHandler("ping", handle_ping))
    application.add_handler(MessageHandler(None, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == "__main__":
    main()
