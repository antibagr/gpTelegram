import asyncio
import typing

import openai
import openai.types.chat
import telethon
import telethon.tl.custom
import telethon.tl.functions
import telethon.tl.types
import uvloop
from loguru import logger

from app.settings import settings

client = telethon.TelegramClient(
    session=settings.TELEGRAM_SESSION_NAME,
    api_id=settings.TELEGRAM_API_ID.get_secret_value(),
    api_hash=settings.TELEGRAM_APP_API_HASH.get_secret_value(),
)
openai_client = openai.AsyncOpenAI(api_key=settings.OPENAI_API_KEY.get_secret_value())


async def get_transcribed_audio(event: telethon.tl.custom.Message) -> str:
    logger.info(f"Received audio message: {event.audio}")
    while True:
        transcription: telethon.tl.types.messages.TranscribedAudio = await client(
            telethon.tl.functions.messages.TranscribeAudioRequest(
                peer=event.peer_id,
                msg_id=event.id,
            )
        )
        logger.debug(f"Transcription: {transcription.stringify()}")
        if transcription.pending or not transcription.text:
            await asyncio.sleep(10)
        else:
            logger.debug(f"Transcription: {transcription.text}")
            return typing.cast(str, transcription.text)


def _filter_message(message: telethon.tl.custom.Message) -> bool:
    return bool(
        message.is_private
        # and not message.out
        and not message.is_group
        and not message.is_channel
        and ((message.text and not message.text.startswith("/")) or message.voice or message.audio)
    )


async def get_chatgpt_answer_suggestions(prompt: str) -> list[str]:
    response = await openai_client.chat.completions.create(
        model="gpt-4",
        messages=[
            {
                "role": "system",
                "content": """Imagine receiving a message on Telegram from
a friend asking you the prompt below. Pretend to be a normal regular dude, not a bot!!!
Considering the casual and brief nature of social messenger conversations,
use internet slang and abbrs, make syntax mistakes periodically. Generate a short, and realistic response that could be sent as a reply.
Ensure each response is similar to how people talk in social messengers.
""",
            },
            {
                "role": "user",
                "content": prompt,
            },
        ],
        n=3,
    )
    return [choice.message.content for choice in response.choices]


async def get_selected_suggestion(message: str, suggestions: list[str]) -> str | None:
    suggestions.insert(0, "Skip")
    logger.info(f"Message: {message}")
    for _i, _suggestion in enumerate(suggestions, start=0):
        logger.info(f"{_i + 1}. {_suggestion}")

    while True:
        user_input = input("Select a suggestion: ")
        if user_input in {"", "q", "quit", "exit"}:
            return None
        try:
            selected_suggestion = suggestions[int(user_input) - 1]
            break
        except ValueError:
            while True:
                logger.info("You replied with custom text. Do you want to send this as a reply? (y/n)")
                if (confirm := input()) in {"y", "yes", ""}:
                    return user_input
                if confirm in {"n", "no"}:
                    break

    if selected_suggestion != suggestions[0]:
        return selected_suggestion
    return None


@client.on(telethon.events.NewMessage(func=_filter_message))
async def message(event: telethon.tl.custom.Message) -> None:
    if event.audio or event.voice:
        text = await get_transcribed_audio(event)
    else:
        text = str(event.text)
    suggestions = await get_chatgpt_answer_suggestions(text)
    reply = await get_selected_suggestion(text, suggestions)
    if reply:
        await event.reply(reply)


async def main() -> None:
    logger.info("Starting the bot")
    await client.start()
    await client.run_until_disconnected()
    logger.info("Stopping the bot")


uvloop.run(main())
