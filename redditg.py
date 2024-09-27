import praw
from telegram.ext import ApplicationBuilder
import asyncio
from os import environ
import redis

r = redis.Redis(host='localhost', port=6379, db=0)

telegram_channel_id = environ.get('TELEGRAM_CHANNEL_ID')

reddit = praw.Reddit(
    client_id=environ.get('REDDIT_CLIENT_ID'),
    client_secret=environ.get('REDDIT_CLIENT_SECRET'),
    user_agent='python:reddit-bot:v1.0',
)

app = ApplicationBuilder().token(environ.get('TELEGRAM_BOT_TOKEN')).build()

def is_image(url):
    return url.endswith(('.jpg', '.jpeg', '.png', '.gif'))

async def fetch_and_send_posts():
    subreddit = reddit.subreddit('wallpaper')
    for submission in subreddit.top(limit=20, time_filter="day"):
        if submission.over_18 or r.exists(submission.id):
            continue
        try:
            if is_image(submission.url):
                await app.bot.send_photo(chat_id=telegram_channel_id, photo=submission.url, caption=submission.title)
                await app.bot.send_document(chat_id=telegram_channel_id, document=submission.url)
                r.set(submission.id, 0, ex=604800)
        except:
            continue

        
if __name__ == "__main__":
    asyncio.run(fetch_and_send_posts())
