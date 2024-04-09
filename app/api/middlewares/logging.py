import typing

import aiogram
from loguru import logger

from app.dto.types import Handler, Json


def _format_message(message: aiogram.types.Message) -> Json:
    print_attrs: Json = {"chat_type": message.chat.type}

    if message.from_user:
        print_attrs["user_id"] = message.from_user.id
    if message.text:
        print_attrs["text"] = message.text
    if message.video:
        print_attrs["caption"] = message.caption
        print_attrs["caption_entities"] = message.caption_entities
        print_attrs["video_id"] = message.video.file_id
        print_attrs["video_unique_id"] = message.video.file_unique_id
    if message.audio:
        print_attrs["duration"] = message.audio.duration
        print_attrs["file_size"] = message.audio.file_size
    if message.photo:
        print_attrs["caption"] = message.caption
        print_attrs["caption_entities"] = message.caption_entities
        print_attrs["photo_id"] = message.photo[-1].file_id
        print_attrs["photo_unique_id"] = message.photo[-1].file_unique_id

    return print_attrs


def _format_callback_query(callback_query: aiogram.types.CallbackQuery) -> Json:
    print_attrs: Json = {
        "query_id": callback_query.id,
        "data": callback_query.data,
        "user_id": callback_query.from_user.id,
        "inline_message_id": callback_query.inline_message_id,
    }

    if callback_query.message:
        print_attrs["message_id"] = callback_query.message.message_id
        print_attrs["chat_type"] = callback_query.message.chat.type
        print_attrs["chat_id"] = callback_query.message.chat.id

    return print_attrs


def _format_inline_query(inline_query: aiogram.types.InlineQuery) -> Json:
    return {
        "query_id": inline_query.id,
        "user_id": inline_query.from_user.id,
        "query": inline_query.query,
        "offset": inline_query.offset,
        "chat_type": inline_query.chat_type,
        "location": inline_query.location,
    }


def _format_pre_checkout_query(pre_checkout_query: aiogram.types.PreCheckoutQuery) -> Json:
    return {
        "query_id": pre_checkout_query.id,
        "user_id": pre_checkout_query.from_user.id,
        "currency": pre_checkout_query.currency,
        "amount": pre_checkout_query.total_amount,
        "payload": pre_checkout_query.invoice_payload,
        "option": pre_checkout_query.shipping_option_id,
    }


def _format_my_chat_member(my_chat_member: aiogram.types.ChatMemberUpdated) -> Json:
    return {
        "user_id": my_chat_member.from_user.id,
        "chat_id": my_chat_member.chat.id,
    }


def _format_chat_member(chat_member: aiogram.types.ChatMemberUpdated) -> Json:
    return {
        "user_id": chat_member.from_user.id,
        "chat_id": chat_member.chat.id,
        "old_state": chat_member.old_chat_member,
        "new_state": chat_member.new_chat_member,
    }


class LoggingMiddleware(aiogram.BaseMiddleware):
    def __init__(self) -> None:
        super().__init__()

    async def __call__(
        self,
        handler: Handler,
        event: aiogram.types.TelegramObject,
        data: Json,
    ) -> typing.Any:
        print_attrs = {}

        if not isinstance(event, aiogram.types.Update):
            raise NotImplementedError("LoggingMiddleware can handle only aiogram.types.Update")

        if event.message:
            message: aiogram.types.Message = event.message

            print_attrs = _format_message(message)

            logger_msg = (
                "received message | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)
        elif event.callback_query:
            callback_query: aiogram.types.CallbackQuery = event.callback_query

            print_attrs = _format_callback_query(callback_query)

            logger_msg = (
                "received callback query | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)
        elif event.inline_query:
            inline_query: aiogram.types.InlineQuery = event.inline_query

            print_attrs = _format_inline_query(inline_query)

            logger_msg = (
                "received inline query | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)
        elif event.pre_checkout_query:
            pre_checkout_query: aiogram.types.PreCheckoutQuery = event.pre_checkout_query

            print_attrs = _format_pre_checkout_query(pre_checkout_query)

            logger_msg = (
                "received pre-checkout query | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)
        elif event.my_chat_member:
            upd: aiogram.types.ChatMemberUpdated = event.my_chat_member

            print_attrs = _format_my_chat_member(upd)

            logger_msg = (
                "received my chat member update | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)
        elif event.chat_member:
            upd: aiogram.types.ChatMemberUpdated = event.chat_member  # type: ignore[no-redef]

            print_attrs = _format_chat_member(upd)

            logger_msg = (
                "received chat member update | "
                + " | ".join(f"{key}: {value}" for key, value in print_attrs.items() if value is not None),
            )
            logger.info(*logger_msg)

        return await handler(event, data)
