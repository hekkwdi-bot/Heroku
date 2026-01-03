__version__ = (2, 0, 0)
# meta banner: https://i.imgur.com/deleted_messages_banner.png
# meta developer: @kilovsk
# meta designer: @kilovsk
# scope: hikka_only
# scope: hikka_min 1.3.0

import html
import asyncio
import time
from datetime import datetime
from typing import Optional, Dict, List, Tuple, Any

from telethon.tl.types import (
    Message, User, Channel, Chat,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaContact, MessageMediaGeo,
    MessageMediaPoll, MessageMediaGame,
    MessageMediaWebPage
)
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon import events

from .. import loader, utils
from ..inline.types import InlineCall, InlineQuery

# Иконки для разных типов сообщений
ICONS = {
    "text": "📝",
    "photo": "🖼",
    "video": "🎬",
    "audio": "🎵",
    "voice": "🎤",
    "sticker": "🩷",
    "document": "📄",
    "contact": "👤",
    "location": "📍",
    "poll": "📊",
    "game": "🎮",
    "webpage": "🌐",
    "gif": "🎞",
    "unknown": "❓"
}

@loader.tds
class DeletedMessagesMod(loader.Module):
    """✨ Красивый модуль для отслеживания удаленных сообщений с инлайн-интерфейсом"""

    strings = {
        "name": "DeletedMessages",
        "loading": "<b>🔄 Загружаю...</b>",
        "no_deleted": "🌸 <b>В этом чате еще не удаляли сообщения</b>",
        "enabled": "✅ <b>Отслеживание включено!</b>\nТеперь я буду сохранять все сообщения в этом чате.",
        "disabled": "✅ <b>Отслеживание выключено</b>",
        "already_enabled": "⚠️ <b>Отслеживание уже включено</b>",
        "already_disabled": "⚠️ <b>Отслеживание уже выключено</b>",
        "cleared": "🧹 <b>История очищена</b>",
        "stats": (
            "📊 <b>Статистика DeletedMessages</b>\n\n"
            "🌸 <b>Отслеживание:</b> {status}\n"
            "📁 <b>Сообщений в кэше:</b> {cached}\n"
            "🗑 <b>Удалено сообщений:</b> {deleted}\n"
            "💾 <b>Размер кэша:</b> {cache_size} сообщений\n"
            "👁 <b>Авто-уведомления:</b> {notify}"
        ),
        "deleted_notify": (
            "🚨 <b>Сообщение удалено!</b>\n\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Отправлено:</b> {time}\n"
            "{media_info}"
            "<b>Текст:</b>\n{preview}"
        ),
        "inline_title": "🗑 Удаленные сообщения",
        "inline_description": "Просмотр удаленных сообщений в этом чате",
        "inline_list": "📋 Список сообщений",
        "inline_stats": "📊 Статистика",
        "inline_settings": "⚙️ Настройки",
        "inline_clear": "🧹 Очистить",
        "inline_toggle": "{icon} Отслеживание",
        "back_btn": "🔙 Назад",
        "close_btn": "❌ Закрыть",
        "prev_btn": "⬅️ Назад",
        "next_btn": "➡️ Далее",
        "page_info": "📄 Страница {current}/{total}",
        "msg_info": (
            "🌸 <b>Информация о сообщении</b>\n\n"
            "{icon} <b>Тип:</b> {type}\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🆔 <b>ID:</b> <code>{msg_id}</code>\n"
            "🕐 <b>Отправлено:</b> {send_time}\n"
            "🗑 <b>Удалено:</b> {delete_time}\n"
            "{deleter_info}"
            "{media_details}"
            "{reply_info}"
            "{stats_info}"
            "\n<b>Содержимое:</b>\n{content}"
        ),
        "deleter_info": "👤 <b>Удалил:</b> {deleter}\n",
        "unknown_deleter": "<i>Неизвестно</i>",
        "reply_to": "↩️ <b>Ответ на:</b> <code>{msg_id}</code>\n",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "reactions": "❤️ <b>Реакции:</b> {reactions}\n",
        "auto_notify_on": "🔔 Авто-уведомления",
        "auto_notify_off": "🔕 Авто-уведомления",
        "save_media_on": "🖼 Сохранять медиа",
        "save_media_off": "🚫 Не сохранять медиа",
        "show_preview": "👁 Показывать превью",
        "compact_mode": "📱 Компактный вид",
        "theme_light": "☀️ Светлая тема",
        "theme_dark": "🌙 Темная тема",
        "delete_confirm": (
            "⚠️ <b>Подтверждение</b>\n\n"
            "Вы уверены, что хотите удалить историю удаленных сообщений?\n"
            "Это действие нельзя отменить."
        ),
        "yes_btn": "✅ Да",
        "no_btn": "❌ Нет",
        "deleted_success": "✅ <b>История удалена</b>",
        "cancelled": "❌ <b>Действие отменено</b>",
        "settings_saved": "✅ <b>Настройки сохранены</b>",
        "inline_msg_preview": "{icon} {sender}: {preview}",
        "unknown_sender": "Неизвестный",
        "no_text": "<i>Нет текста</i>",
        "media_photo": "Фото",
        "media_video": "Видео",
        "media_audio": "Аудио",
        "media_voice": "Голосовое",
        "media_sticker": "Стикер",
        "media_document": "Документ",
        "media_gif": "GIF",
        "inline_help": "ℹ️ Помощь",
        "help_text": (
            "🌸 <b>Помощь по DeletedMessages</b>\n\n"
            "<b>Основные команды:</b>\n"
            "• <code>.del on</code> - включить отслеживание\n"
            "• <code>.del off</code> - выключить отслеживание\n"
            "• <code>.del list</code> - показать список\n"
            "• <code>.del stats</code> - статистика\n"
            "• <code>.del clear</code> - очистить историю\n\n"
            "<b>Инлайн-режим:</b>\n"
            "• Напишите <code>@ваш_бот del</code> в любом чате\n"
            "• Используйте кнопки для навигации\n\n"
            "<b>Настройки:</b>\n"
            "• Авто-уведомления при удалении\n"
            "• Сохранение медиа\n"
            "• Компактный режим\n"
            "• Выбор темы"
        )
    }

    strings_ru = {
        "name": "DeletedMessages",
        "loading": "<b>🔄 Загружаю...</b>",
        "no_deleted": "🌸 <b>В этом чате еще не удаляли сообщения</b>",
        "enabled": "✅ <b>Отслеживание включено!</b>\nТеперь я буду сохранять все сообщения в этом чате.",
        "disabled": "✅ <b>Отслеживание выключено</b>",
        "already_enabled": "⚠️ <b>Отслеживание уже включено</b>",
        "already_disabled": "⚠️ <b>Отслеживание уже выключено</b>",
        "cleared": "🧹 <b>История очищена</b>",
        "stats": (
            "📊 <b>Статистика DeletedMessages</b>\n\n"
            "🌸 <b>Отслеживание:</b> {status}\n"
            "📁 <b>Сообщений в кэше:</b> {cached}\n"
            "🗑 <b>Удалено сообщений:</b> {deleted}\n"
            "💾 <b>Размер кэша:</b> {cache_size} сообщений\n"
            "👁 <b>Авто-уведомления:</b> {notify}"
        ),
        "deleted_notify": (
            "🚨 <b>Сообщение удалено!</b>\n\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Отправлено:</b> {time}\n"
            "{media_info}"
            "<b>Текст:</b>\n{preview}"
        ),
        "inline_title": "🗑 Удаленные сообщения",
        "inline_description": "Просмотр удаленных сообщений в этом чате",
        "inline_list": "📋 Список сообщений",
        "inline_stats": "📊 Статистика",
        "inline_settings": "⚙️ Настройки",
        "inline_clear": "🧹 Очистить",
        "inline_toggle": "{icon} Отслеживание",
        "back_btn": "🔙 Назад",
        "close_btn": "❌ Закрыть",
        "prev_btn": "⬅️ Назад",
        "next_btn": "➡️ Далее",
        "page_info": "📄 Страница {current}/{total}",
        "msg_info": (
            "🌸 <b>Информация о сообщении</b>\n\n"
            "{icon} <b>Тип:</b> {type}\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🆔 <b>ID:</b> <code>{msg_id}</code>\n"
            "🕐 <b>Отправлено:</b> {send_time}\n"
            "🗑 <b>Удалено:</b> {delete_time}\n"
            "{deleter_info}"
            "{media_details}"
            "{reply_info}"
            "{stats_info}"
            "\n<b>Содержимое:</b>\n{content}"
        ),
        "deleter_info": "👤 <b>Удалил:</b> {deleter}\n",
        "unknown_deleter": "<i>Неизвестно</i>",
        "reply_to": "↩️ <b>Ответ на:</b> <code>{msg_id}</code>\n",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "reactions": "❤️ <b>Реакции:</b> {reactions}\n",
        "auto_notify_on": "🔔 Авто-уведомления",
        "auto_notify_off": "🔕 Авто-уведомления",
        "save_media_on": "🖼 Сохранять медиа",
        "save_media_off": "🚫 Не сохранять медиа",
        "show_preview": "👁 Показывать превью",
        "compact_mode": "📱 Компактный вид",
        "theme_light": "☀️ Светлая тема",
        "theme_dark": "🌙 Темная тема",
        "delete_confirm": (
            "⚠️ <b>Подтверждение</b>\n\n"
            "Вы уверены, что хотите удалить историю удаленных сообщений?\n"
            "Это действие нельзя отменить."
        ),
        "yes_btn": "✅ Да",
        "no_btn": "❌ Нет",
        "deleted_success": "✅ <b>История удалена</b>",
        "cancelled": "❌ <b>Действие отменено</b>",
        "settings_saved": "✅ <b>Настройки сохранены</b>",
        "inline_msg_preview": "{icon} {sender}: {preview}",
        "unknown_sender": "Неизвестный",
        "no_text": "<i>Нет текста</i>",
        "media_photo": "Фото",
        "media_video": "Видео",
        "media_audio": "Аудио",
        "media_voice": "Голосовое",
        "media_sticker": "Стикер",
        "media_document": "Документ",
        "media_gif": "GIF",
        "inline_help": "ℹ️ Помощь",
        "help_text": (
            "🌸 <b>Помощь по DeletedMessages</b>\n\n"
            "<b>Основные команды:</b>\n"
            "• <code>.del on</code> - включить отслеживание\n"
            "• <code>.del off</code> - выключить отслеживание\n"
            "• <code>.del list</code> - показать список\n"
            "• <code>.del stats</code> - статистика\n"
            "• <code>.del clear</code> - очистить историю\n\n"
            "<b>Инлайн-режим:</b>\n"
            "• Напишите <code>@ваш_бот del</code> в любом чате\n"
            "• Используйте кнопки для навигации\n\n"
            "<b>Настройки:</b>\n"
            "• Авто-уведомления при удалении\n"
            "• Сохранение медиа\n"
            "• Компактный режим\n"
            "• Выбор темы"
        ),
        "_cls_doc": "✨ Красивый модуль для отслеживания удаленных сообщений с инлайн-интерфейсом"
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_notify",
                True,
                lambda: "Автоматически уведомлять о удаленных сообщениях",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "save_media_info",
                True,
                lambda: "Сохранять информацию о медиа-файлах",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "compact_view",
                False,
                lambda: "Компактный режим отображения",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "theme",
                "dark",
                lambda: "Тема интерфейса (dark/light)",
                validator=loader.validators.Choice(["dark", "light"])
            ),
            loader.ConfigValue(
                "max_cache_size",
                200,
                lambda: "Максимальное количество сообщений в кэше",
                validator=loader.validators.Integer(minimum=50, maximum=1000)
            ),
            loader.ConfigValue(
                "show_preview",
                True,
                lambda: "Показывать превью в списке",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "notify_sound",
                False,
                lambda: "Звук при уведомлении",
                validator=loader.validators.Boolean()
            ),
        )
        
        # Кэшированные данные
        self.tracked_chats: Dict[int, bool] = {}
        self.message_cache: Dict[int, Dict[int, Dict]] = {}
        self.deleted_messages: Dict[int, List[Dict]] = {}
        
        # Временное хранилище для инлайн режима
        self.inline_sessions: Dict[int, Dict] = {}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        
        # Загружаем сохраненные данные
        self._load_data()
        
        # Регистрируем хендлеры
        client.add_event_handler(self._on_message, events.NewMessage)
        client.add_event_handler(self._on_message_deleted, events.MessageDeleted)

    def _load_data(self):
        """Загружает данные из базы"""
        self.tracked_chats = self._db.get(__name__, "tracked_chats", {})
        self.message_cache = self._db.get(__name__, "message_cache", {})
        self.deleted_messages = self._db.get(__name__, "deleted_messages", {})

    def _save_data(self):
        """Сохраняет данные в базу"""
        self._db.set(__name__, "tracked_chats", self.tracked_chats)
        self._db.set(__name__, "message_cache", self.message_cache)
        self._db.set(__name__, "deleted_messages", self.deleted_messages)

    def _format_time(self, timestamp: datetime) -> str:
        """Форматирует время в красивый вид"""
        now = datetime.now()
        diff = now - timestamp
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "только что"
            elif diff.seconds < 3600:
                minutes = diff.seconds // 60
                return f"{minutes} мин. назад"
            else:
                hours = diff.seconds // 3600
                return f"{hours} ч. назад"
        elif diff.days == 1:
            return "вчера"
        elif diff.days < 7:
            return f"{diff.days} дн. назад"
        else:
            return timestamp.strftime("%d.%m.%Y %H:%M")

    def _get_sender_name(self, sender_id: int) -> str:
        """Получает имя отправителя"""
        try:
            entity = self._client._entity_cache.get(sender_id)
            if entity:
                if hasattr(entity, 'first_name'):
                    name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                    if entity.username:
                        return f"{name} (@{entity.username})"
                    return name
                elif hasattr(entity, 'title'):
                    return entity.title
        except:
            pass
        return self.strings("unknown_sender")

    def _get_message_icon(self, msg_data: Dict) -> str:
        """Определяет иконку для типа сообщения"""
        if msg_data.get("media_type"):
            return ICONS.get(msg_data["media_type"], ICONS["unknown"])
        return ICONS["text"]

    def _get_message_type(self, msg_data: Dict) -> str:
        """Определяет тип сообщения"""
        if msg_data.get("media_type"):
            media_type = msg_data["media_type"]
            if media_type == "photo":
                return self.strings("media_photo")
            elif media_type == "video":
                return self.strings("media_video")
            elif media_type in ["audio", "voice"]:
                return self.strings("media_audio") if media_type == "audio" else self.strings("media_voice")
            elif media_type == "sticker":
                return self.strings("media_sticker")
            elif media_type == "gif":
                return self.strings("media_gif")
            elif media_type == "document":
                return self.strings("media_document")
            else:
                return media_type.capitalize()
        return "Текст"

    async def _on_message(self, event: events.NewMessage.Event):
        """Сохраняет новые сообщения"""
        if not event.message:
            return
            
        chat_id = utils.get_chat_id(event.message)
        if chat_id not in self.tracked_chats or not self.tracked_chats[chat_id]:
            return
        
        msg = event.message
        msg_data = {
            "id": msg.id,
            "sender_id": msg.sender_id,
            "date": msg.date.timestamp(),
            "text": msg.raw_text or "",
            "reply_to": msg.reply_to.reply_to_msg_id if msg.reply_to else None,
        }
        
        # Сохраняем статистику
        if hasattr(msg, 'views'):
            msg_data["views"] = msg.views
        if hasattr(msg, 'forwards'):
            msg_data["forwards"] = msg.forwards
        if hasattr(msg, 'reactions'):
            msg_data["reactions"] = msg.reactions
        
        # Сохраняем информацию о медиа
        if msg.media and self.config["save_media_info"]:
            msg_data.update(self._parse_media(msg.media))
        
        # Сохраняем в кэш
        if chat_id not in self.message_cache:
            self.message_cache[chat_id] = {}
        
        self.message_cache[chat_id][msg.id] = msg_data
        
        # Ограничиваем размер кэша
        if len(self.message_cache[chat_id]) > self.config["max_cache_size"]:
            oldest_key = min(self.message_cache[chat_id].keys())
            del self.message_cache[chat_id][oldest_key]
        
        self._save_data()

    def _parse_media(self, media) -> Dict:
        """Парсит информацию о медиа"""
        result = {}
        
        if isinstance(media, MessageMediaPhoto):
            result["media_type"] = "photo"
        elif isinstance(media, MessageMediaDocument):
            doc = media.document
            mime_type = doc.mime_type.lower()
            
            if "video" in mime_type:
                result["media_type"] = "video"
            elif "audio" in mime_type:
                result["media_type"] = "audio"
            elif "image/webp" in mime_type:
                result["media_type"] = "sticker"
            elif "gif" in mime_type:
                result["media_type"] = "gif"
            else:
                result["media_type"] = "document"
                
            # Сохраняем информацию о файле
            if hasattr(doc, 'attributes'):
                for attr in doc.attributes:
                    if hasattr(attr, 'file_name'):
                        result["file_name"] = attr.file_name
                        break
        elif isinstance(media, MessageMediaContact):
            result["media_type"] = "contact"
        elif isinstance(media, MessageMediaGeo):
            result["media_type"] = "location"
        elif isinstance(media, MessageMediaPoll):
            result["media_type"] = "poll"
            result["poll_question"] = media.poll.question
        elif isinstance(media, MessageMediaGame):
            result["media_type"] = "game"
            result["game_title"] = media.game.title
        elif isinstance(media, MessageMediaWebPage):
            result["media_type"] = "webpage"
            result["webpage_title"] = media.webpage.title if media.webpage.title else "Веб-страница"
        
        return result

    async def _on_message_deleted(self, event: events.MessageDeleted.Event):
        """Обрабатывает удаленные сообщения"""
        chat_id = utils.get_chat_id(event)
        if chat_id not in self.tracked_chats or not self.tracked_chats[chat_id]:
            return
        
        deleted_time = datetime.now().timestamp()
        
        for msg_id in event.deleted_ids:
            if chat_id in self.message_cache and msg_id in self.message_cache[chat_id]:
                msg_data = self.message_cache[chat_id][msg_id].copy()
                msg_data["deleted_time"] = deleted_time
                msg_data["deleter_id"] = getattr(event, 'deleter_id', None)
                
                # Сохраняем в историю удаленных
                if chat_id not in self.deleted_messages:
                    self.deleted_messages[chat_id] = []
                
                self.deleted_messages[chat_id].append(msg_data)
                
                # Удаляем из кэша
                del self.message_cache[chat_id][msg_id]
                
                # Отправляем уведомление
                if self.config["auto_notify"]:
                    await self._send_deleted_notification(chat_id, msg_data)
                
                self._save_data()

    async def _send_deleted_notification(self, chat_id: int, msg_data: Dict):
        """Отправляет уведомление об удалении"""
        sender_name = self._get_sender_name(msg_data["sender_id"])
        send_time = self._format_time(datetime.fromtimestamp(msg_data["date"]))
        
        # Формируем превью текста
        text_preview = msg_data.get("text", "")[:100]
        if len(msg_data.get("text", "")) > 100:
            text_preview += "..."
        
        if not text_preview:
            text_preview = self.strings("no_text")
        
        # Информация о медиа
        media_info = ""
        if msg_data.get("media_type"):
            media_type = self._get_message_type(msg_data)
            media_info = f"📎 <b>Тип:</b> {media_type}\n"
        
        text = self.strings("deleted_notify").format(
            sender=sender_name,
            time=send_time,
            media_info=media_info,
            preview=utils.escape_html(text_preview)
        )
        
        try:
            await self._client.send_message(
                chat_id,
                text,
                silent=not self.config["notify_sound"]
            )
        except:
            pass

    @loader.command(ru_doc="Управление отслеживанием удаленных сообщений")
    async def delcmd(self, message: Message):
        """Главная команда модуля"""
        args = utils.get_args_raw(message).lower()
        chat_id = utils.get_chat_id(message)
        
        if not args:
            await self._show_main_menu(message)
            return
        
        if args == "on":
            await self._toggle_tracking(message, chat_id, True)
        elif args == "off":
            await self._toggle_tracking(message, chat_id, False)
        elif args == "list":
            await self._show_deleted_list(message)
        elif args == "stats":
            await self._show_stats(message)
        elif args == "clear":
            await self._clear_history(message)
        elif args == "help":
            await utils.answer(message, self.strings("help_text"))
        else:
            await self._show_main_menu(message)

    async def _show_main_menu(self, message: Message):
        """Показывает главное меню"""
        chat_id = utils.get_chat_id(message)
        is_tracking = self.tracked_chats.get(chat_id, False)
        
        text = (
            f"🌸 <b>DeletedMessages v{'.'.join(map(str, __version__))}</b>\n\n"
            f"📱 <b>Статус отслеживания:</b> {'✅ Включено' if is_tracking else '❌ Выключено'}\n"
            f"🗑 <b>Удалено сообщений:</b> {len(self.deleted_messages.get(chat_id, []))}\n\n"
            f"<b>Используйте команды:</b>\n"
            f"• <code>.del on/off</code> - вкл/выкл отслеживание\n"
            f"• <code>.del list</code> - список сообщений\n"
            f"• <code>.del stats</code> - статистика\n"
            f"• <code>.del clear</code> - очистить историю\n"
            f"• <code>.del help</code> - помощь"
        )
        
        await utils.answer(message, text)

    async def _toggle_tracking(self, message: Message, chat_id: int, enable: bool):
        """Включает/выключает отслеживание"""
        current = self.tracked_chats.get(chat_id, False)
        
        if enable == current:
            text = self.strings("already_enabled" if enable else "already_disabled")
        else:
            self.tracked_chats[chat_id] = enable
            self._save_data()
            text = self.strings("enabled" if enable else "disabled")
        
        await utils.answer(message, text)

    async def _show_deleted_list(self, message: Message):
        """Показывает список удаленных сообщений"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self.deleted_messages or not self.deleted_messages[chat_id]:
            await utils.answer(message, self.strings("no_deleted"))
            return
        
        deleted_list = self.deleted_messages[chat_id][-20:]  # Последние 20 сообщений
        text = "🗑 <b>Последние удаленные сообщения:</b>\n\n"
        
        for i, msg in enumerate(reversed(deleted_list), 1):
            sender_name = self._get_sender_name(msg["sender_id"])
            send_time = self._format_time(datetime.fromtimestamp(msg["date"]))
            icon = self._get_message_icon(msg)
            
            # Превью текста
            preview = msg.get("text", "")[:50]
            if len(msg.get("text", "")) > 50:
                preview += "..."
            if not preview:
                preview = f"[{self._get_message_type(msg)}]"
            
            text += f"{i}. {icon} <b>{sender_name}</b> ({send_time})\n"
            text += f"   <code>{utils.escape_html(preview)}</code>\n\n"
        
        await utils.answer(message, text)

    async def _show_stats(self, message: Message):
        """Показывает статистику"""
        chat_id = utils.get_chat_id(message)
        
        status = "✅ Включено" if self.tracked_chats.get(chat_id, False) else "❌ Выключено"
        cached = len(self.message_cache.get(chat_id, {}))
        deleted = len(self.deleted_messages.get(chat_id, []))
        cache_size = self.config["max_cache_size"]
        notify = "✅ Включены" if self.config["auto_notify"] else "❌ Выключены"
        
        text = self.strings("stats").format(
            status=status,
            cached=cached,
            deleted=deleted,
            cache_size=cache_size,
            notify=notify
        )
        
        await utils.answer(message, text)

    async def _clear_history(self, message: Message):
        """Очищает историю удаленных сообщений"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id in self.deleted_messages:
            self.deleted_messages[chat_id] = []
            self._save_data()
        
        await utils.answer(message, self.strings("cleared"))

    # Инлайн-режим
    @loader.inline_handler(thumb_url="https://img.icons8.com/color/96/000000/delete-message.png")
    async def deleted_inline(self, query: InlineQuery):
        """Инлайн-обработчик"""
        chat_id = query.chat_id
        
        # Главное меню
        buttons = [
            [
                {
                    "text": self.strings("inline_list"),
                    "callback": self.inline__show_list,
                    "args": (chat_id, 0)
                },
                {
                    "text": self.strings("inline_stats"),
                    "callback": self.inline__show_stats,
                    "args": (chat_id,)
                }
            ],
            [
                {
                    "text": self.strings("inline_settings"),
                    "callback": self.inline__show_settings,
                    "args": (chat_id,)
                },
                {
                    "text": self.strings("inline_clear"),
                    "callback": self.inline__confirm_clear,
                    "args": (chat_id,)
                }
            ],
            [
                {
                    "text": self.strings("inline_toggle").format(
                        icon="✅" if self.tracked_chats.get(chat_id, False) else "❌"
                    ),
                    "callback": self.inline__toggle_tracking,
                    "args": (chat_id,)
                }
            ]
        ]
        
        await query.answer(
            [
                {
                    "title": self.strings("inline_title"),
                    "description": self.strings("inline_description"),
                    "thumb_url": "https://img.icons8.com/color/96/000000/delete-message.png",
                    "message": self.strings("loading"),
                    "reply_markup": buttons
                }
            ],
            cache_time=0
        )

    async def inline__show_list(self, call: InlineCall, chat_id: int, page: int = 0):
        """Показывает список сообщений"""
        if chat_id not in self.deleted_messages or not self.deleted_messages[chat_id]:
            await call.edit(self.strings("no_deleted"), reply_markup=[
                [{"text": self.strings("back_btn"), "callback": self.inline__main_menu, "args": (chat_id,)}],
                [{"text": self.strings("close_btn"), "action": "close"}]
            ])
            return
        
        deleted_list = self.deleted_messages[chat_id]
        items_per_page = 5
        total_pages = (len(deleted_list) + items_per_page - 1) // items_per_page
        page = max(0, min(page, total_pages - 1))
        
        start_idx = page * items_per_page
        end_idx = min(start_idx + items_per_page, len(deleted_list))
        page_items = list(reversed(deleted_list))[start_idx:end_idx]
        
        text = f"🗑 <b>Удаленные сообщения</b>\n"
        text += f"{self.strings('page_info').format(current=page+1, total=total_pages)}\n\n"
        
        buttons = []
        
        for i, msg in enumerate(page_items, start_idx + 1):
            sender_name = self._get_sender_name(msg["sender_id"])
            send_time = self._format_time(datetime.fromtimestamp(msg["date"]))
            icon = self._get_message_icon(msg)
            
            # Превью
            preview = msg.get("text", "")[:30]
            if len(msg.get("text", "")) > 30:
                preview += "..."
            if not preview:
                preview = f"[{self._get_message_type(msg)}]"
            
            btn_text = f"{icon} {i}. {sender_name}"
            buttons.append([
                {
                    "text": btn_text,
                    "callback": self.inline__show_message,
                    "args": (chat_id, msg["id"], page)
                }
            ])
        
        # Навигация
        nav_buttons = []
        if page > 0:
            nav_buttons.append({
                "text": self.strings("prev_btn"),
                "callback": self.inline__show_list,
                "args": (chat_id, page - 1)
            })
        
        nav_buttons.append({
            "text": self.strings("back_btn"),
            "callback": self.inline__main_menu,
            "args": (chat_id,)
        })
        
        if page < total_pages - 1:
            nav_buttons.append({
                "text": self.strings("next_btn"),
                "callback": self.inline__show_list,
                "args": (chat_id, page + 1)
            })
        
        if nav_buttons:
            buttons.append(nav_buttons)
        
        buttons.append([{"text": self.strings("close_btn"), "action": "close"}])
        
        await call.edit(text, reply_markup=buttons)

    async def inline__show_message(self, call: InlineCall, chat_id: int, msg_id: int, page: int):
        """Показывает информацию о сообщении"""
        if chat_id not in self.deleted_messages:
            await call.answer("Сообщение не найдено")
            return
        
        msg = None
        for m in self.deleted_messages[chat_id]:
            if m.get("id") == msg_id:
                msg = m
                break
        
        if not msg:
            await call.answer("Сообщение не найдено")
            return
        
        # Формируем текст
        sender_name = self._get_sender_name(msg["sender_id"])
        send_time = self._format_time(datetime.fromtimestamp(msg["date"]))
        delete_time = self._format_time(datetime.fromtimestamp(msg["deleted_time"]))
        icon = self._get_message_icon(msg)
        msg_type = self._get_message_type(msg)
        
        # Информация о том, кто удалил
        deleter_info = ""
        if msg.get("deleter_id"):
            deleter_name = self._get_sender_name(msg["deleter_id"])
            deleter_info = self.strings("deleter_info").format(deleter=deleter_name)
        
        # Информация о медиа
        media_details = ""
        if msg.get("media_type"):
            media_details = f"📎 <b>Медиа:</b> {msg_type}\n"
            if msg.get("file_name"):
                media_details += f"📁 <b>Файл:</b> <code>{msg['file_name']}</code>\n"
        
        # Информация о ответе
        reply_info = ""
        if msg.get("reply_to"):
            reply_info = self.strings("reply_to").format(msg_id=msg["reply_to"])
        
        # Статистика
        stats_info = ""
        if msg.get("views") is not None:
            stats_info += self.strings("views").format(views=msg["views"])
        if msg.get("forwards") is not None:
            stats_info += self.strings("forwards").format(forwards=msg["forwards"])
        if msg.get("reactions") is not None:
            reactions_count = len(msg["reactions"]) if isinstance(msg["reactions"], list) else 0
            stats_info += self.strings("reactions").format(reactions=reactions_count)
        
        # Содержимое
        content = msg.get("text", "")
        if not content:
            content = self.strings("no_text")
        else:
            content = utils.escape_html(content)
        
        text = self.strings("msg_info").format(
            icon=icon,
            type=msg_type,
            sender=sender_name,
            msg_id=msg_id,
            send_time=send_time,
            delete_time=delete_time,
            deleter_info=deleter_info,
            media_details=media_details,
            reply_info=reply_info,
            stats_info=stats_info,
            content=content
        )
        
        buttons = [
            [
                {
                    "text": self.strings("back_btn"),
                    "callback": self.inline__show_list,
                    "args": (chat_id, page)
                },
                {"text": self.strings("close_btn"), "action": "close"}
            ]
        ]
        
        await call.edit(text, reply_markup=buttons)

    async def inline__show_stats(self, call: InlineCall, chat_id: int):
        """Показывает статистику в инлайне"""
        status = "✅ Включено" if self.tracked_chats.get(chat_id, False) else "❌ Выключено"
        cached = len(self.message_cache.get(chat_id, {}))
        deleted = len(self.deleted_messages.get(chat_id, []))
        cache_size = self.config["max_cache_size"]
        notify = "✅ Включены" if self.config["auto_notify"] else "❌ Выключены"
        
        text = self.strings("stats").format(
            status=status,
            cached=cached,
            deleted=deleted,
            cache_size=cache_size,
            notify=notify
        )
        
        buttons = [
            [{"text": self.strings("back_btn"), "callback": self.inline__main_menu, "args": (chat_id,)}],
            [{"text": self.strings("close_btn"), "action": "close"}]
        ]
        
        await call.edit(text, reply_markup=buttons)

    async def inline__show_settings(self, call: InlineCall, chat_id: int):
        """Показывает настройки"""
        text = "⚙️ <b>Настройки DeletedMessages</b>\n\n"
        
        buttons = [
            [
                {
                    "text": self.strings("auto_notify_on" if self.config["auto_notify"] else "auto_notify_off"),
                    "callback": self.inline__toggle_setting,
                    "args": (chat_id, "auto_notify")
                },
                {
                    "text": self.strings("save_media_on" if self.config["save_media_info"] else "save_media_off"),
                    "callback": self.inline__toggle_setting,
                    "args": (chat_id, "save_media_info")
                }
            ],
            [
                {
                    "text": self.strings("show_preview"),
                    "callback": self.inline__toggle_setting,
                    "args": (chat_id, "show_preview")
                },
                {
                    "text": self.strings("compact_mode"),
                    "callback": self.inline__toggle_setting,
                    "args": (chat_id, "compact_view")
                }
            ],
            [
                {
                    "text": self.strings("theme_light" if self.config["theme"] == "light" else "theme_dark"),
                    "callback": self.inline__toggle_setting,
                    "args": (chat_id, "theme")
                }
            ],
            [
                {"text": self.strings("back_btn"), "callback": self.inline__main_menu, "args": (chat_id,)},
                {"text": self.strings("close_btn"), "action": "close"}
            ]
        ]
        
        await call.edit(text, reply_markup=buttons)

    async def inline__toggle_setting(self, call: InlineCall, chat_id: int, setting: str):
        """Переключает настройку"""
        current = self.config[setting]
        
        if setting == "theme":
            new_value = "light" if current == "dark" else "dark"
        else:
            new_value = not current
        
        self.config[setting] = new_value
        
        await call.answer(self.strings("settings_saved"))
        await self.inline__show_settings(call, chat_id)

    async def inline__confirm_clear(self, call: InlineCall, chat_id: int):
        """Подтверждает очистку истории"""
        text = self.strings("delete_confirm")
        
        buttons = [
            [
                {
                    "text": self.strings("yes_btn"),
                    "callback": self.inline__clear_history,
                    "args": (chat_id,)
                },
                {
                    "text": self.strings("no_btn"),
                    "callback": self.inline__main_menu,
                    "args": (chat_id,)
                }
            ]
        ]
        
        await call.edit(text, reply_markup=buttons)

    async def inline__clear_history(self, call: InlineCall, chat_id: int):
        """Очищает историю"""
        if chat_id in self.deleted_messages:
            self.deleted_messages[chat_id] = []
            self._save_data()
        
        await call.edit(self.strings("deleted_success"), reply_markup=[
            [{"text": self.strings("back_btn"), "callback": self.inline__main_menu, "args": (chat_id,)}],
            [{"text": self.strings("close_btn"), "action": "close"}]
        ])

    async def inline__toggle_tracking(self, call: InlineCall, chat_id: int):
        """Переключает отслеживание"""
        current = self.tracked_chats.get(chat_id, False)
        self.tracked_chats[chat_id] = not current
        self._save_data()
        
        await call.answer(
            self.strings("enabled" if not current else "disabled")
        )
        await self.inline__main_menu(call, chat_id)

    async def inline__main_menu(self, call: InlineCall, chat_id: int):
        """Главное меню инлайна"""
        is_tracking = self.tracked_chats.get(chat_id, False)
        
        text = (
            f"🌸 <b>DeletedMessages v{'.'.join(map(str, __version__))}</b>\n\n"
            f"📱 <b>Статус отслеживания:</b> {'✅ Включено' if is_tracking else '❌ Выключено'}\n"
            f"🗑 <b>Удалено сообщений:</b> {len(self.deleted_messages.get(chat_id, []))}\n\n"
            f"Выберите действие:"
        )
        
        buttons = [
            [
                {
                    "text": self.strings("inline_list"),
                    "callback": self.inline__show_list,
                    "args": (chat_id, 0)
                },
                {
                    "text": self.strings("inline_stats"),
                    "callback": self.inline__show_stats,
                    "args": (chat_id,)
                }
            ],
            [
                {
                    "text": self.strings("inline_settings"),
                    "callback": self.inline__show_settings,
                    "args": (chat_id,)
                },
                {
                    "text": self.strings("inline_clear"),
                    "callback": self.inline__confirm_clear,
                    "args": (chat_id,)
                }
            ],
            [
                {
                    "text": self.strings("inline_toggle").format(
                        icon="✅" if is_tracking else "❌"
                    ),
                    "callback": self.inline__toggle_tracking,
                    "args": (chat_id,)
                }
            ],
            [
                {"text": self.strings("close_btn"), "action": "close"}
            ]
        ]
        
        await call.edit(text, reply_markup=buttons)

    async def watcher(self, message):
        """Общий ватчер для обработки событий"""
        pass

    @loader.command(ru_doc="Показать помощь по модулю")
    async def delhelp(self, message: Message):
        """Показывает помощь"""
        await utils.answer(message, self.strings("help_text"))
