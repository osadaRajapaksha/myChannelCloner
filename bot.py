# ChannelAutoPost – Modified for 10→10 Mirroring
# Based on ChannelAutoForwarder by @xditya
# Edited for 1-to-1 channel mirroring (fresh repost, not forward)

import logging
from telethon import TelegramClient, events, Button
from decouple import config

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format="[%(levelname)s] %(asctime)s - %(message)s"
)
log = logging.getLogger("ChannelAutoPost")

log.info("Starting Channel AutoPost Bot (1→1 mirror mode)...")

# Telegram credentials from .env
try:
    apiid = config("APP_ID", cast=int)
    apihash = config("API_HASH")
    bottoken = config("BOT_TOKEN")
    datgbot = TelegramClient(None, apiid, apihash).start(bot_token=bottoken)
except Exception as exc:
    log.error("Environment vars missing or invalid!")
    log.error(exc)
    exit()

# -------------- YOUR 10→10 CHANNEL MAPPING HERE -----------------
# Example format:
CHANNEL_PAIRS = {
    -1002867578605: -1002815938247,
    
    
}
# ---------------------------------------------------------------

# /start command
@datgbot.on(events.NewMessage(pattern="/start"))
async def start(event):
    await event.reply(
        f"Hi `{event.sender.first_name}`!\n\n"
        f"I’m a channel auto-post bot running in 1→1 mirror mode.\n"
        f"Messages from 10 source channels will be sent freshly to 10 targets.\n\n"
        f"Use /help for more info.",
        buttons=[
            Button.url("Repo", url="https://github.com/xditya/ChannelAutoForwarder"),
            Button.url("Developer", url="https://xditya.me"),
        ],
        link_preview=False,
    )

# /help command
@datgbot.on(events.NewMessage(pattern="/help"))
async def help_cmd(event):
    await event.reply(
        "**Help — 1→1 Channel Mirroring Bot**\n\n"
        "This bot listens to multiple source channels and sends their posts freshly to corresponding target channels.\n\n"
        "Example mapping:\n"
        "`src1 → dest1`, `src2 → dest2`, etc.\n\n"
        "No 'forwarded from' tag — posts look original.\n\n"
        "Make sure the bot is an **admin in both source and target channels.**"
    )

# Main handler for new messages
@datgbot.on(events.NewMessage(incoming=True, chats=list(CHANNEL_PAIRS.keys())))
async def mirror_message(event):
    src = event.chat_id
    dest = CHANNEL_PAIRS.get(src)
    if not dest:
        return

    try:
        # Skip unsupported content
        if event.poll:
            log.info(f"Skipping poll message in {src}")
            return

        # Handle different message types
        if event.photo:
            await datgbot.send_file(dest, event.media.photo, caption=event.text or "", link_preview=False)
        elif event.media:
            await datgbot.send_file(dest, event.media, caption=event.text or "")
        elif event.text:
            await datgbot.send_message(dest, event.text)
        else:
            log.info(f"Unhandled message type from {src}")

        log.info(f"✅ Mirrored message from {src} → {dest}")

    except Exception as e:
        log.error(f"❌ Failed to mirror message from {src} → {dest}: {e}")

log.info("Bot is now running. Listening for new messages...")
datgbot.run_until_disconnected()

