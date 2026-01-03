__version__ = (4, 0, 0)
# meta banner: https://img.icons8.com/fluency/240/000000/deleted-message.png
# meta developer: @kilovsk
# scope: hikka_only
# scope: hikka_min 1.3.0

import html
import asyncio
import time
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Tuple, Any, Union
import re

from telethon.tl.types import (
    Message, User, Channel, Chat,
    MessageMediaPhoto, MessageMediaDocument,
    MessageMediaContact, MessageMediaGeo,
    MessageMediaPoll, MessageMediaGame,
    MessageMediaWebPage, PeerUser, PeerChat, PeerChannel
)
from telethon import events

from .. import loader, utils
from ..inline.types import InlineCall

# Эмодзи для разных типов контента
ICONS = {
    "text": "📝",
    "photo": "🖼️",
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
    "gif": "🎞️",
    "unknown": "❓",
    "forward": "🔄",
    "reply": "↩️",
    "edited": "✏️"
}

@loader.tds
class DeletedMessages(loader.Module):
    """Модуль для отслеживания удаленных сообщений"""

    strings = {
        "name": "DeletedMessages",
        "loading": "🔄 <b>Загружаю...</b>",
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
            "💾 <b>Размер кэша:</b> {cache_size}\n"
            "👁 <b>Авто-уведомления:</b> {notify}"
        ),
        "deleted_notify": (
            "🚨 <b>Сообщение удалено!</b>\n\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Отправлено:</b> {time}\n"
            "{media_info}"
            "<b>Текст:</b>\n{preview}"
        ),
        "msg_info": (
            "🌸 <b>Информация о сообщении</b>\n\n"
            "{icon} <b>Тип:</b> {type}\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🆔 <b>ID:</b> <code>{msg_id}</code>\n"
            "🕐 <b>Отправлено:</b> {send_time}\n"
            "🗑 <b>Удалено:</b> {delete_time}\n"
            "{deleter_info}"
            "{media_details}"
            "\n<b>Содержимое:</b>\n{content}"
        ),
        "deleter_info": "👤 <b>Удалил:</b> {deleter}\n",
        "unknown_deleter": "<i>Неизвестно</i>",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "unknown_sender": "Неизвестный",
        "no_text": "<i>Нет текста</i>",
        "media_photo": "Фото",
        "media_video": "Видео",
        "media_audio": "Аудио",
        "media_voice": "Голосовое",
        "media_sticker": "Стикер",
        "media_document": "Документ",
        "media_gif": "GIF",
        "help_text": (
            "🌸 <b>Помощь по DeletedMessages</b>\n\n"
            "<b>Основные команды:</b>\n"
            "• <code>.del on</code> - включить отслеживание\n"
            "• <code>.del off</code> - выключить отслеживание\n"
            "• <code>.del list</code> - показать список\n"
            "• <code>.del stats</code> - статистика\n"
            "• <code>.del clear</code> - очистить историю\n"
            "• <code>.del help</code> - эта справка"
        ),
        "no_args": "❌ <b>Используйте:</b> .del [on/off/list/stats/clear/help]",
        "global_toggle_on": "✅ <b>Глобальное отслеживание включено</b>",
        "global_toggle_off": "✅ <b>Глобальное отслеживание выключено</b>",
        "export_complete": "✅ <b>Экспорт завершен</b>",
        "search_results": "🔍 <b>Результаты поиска:</b>\n",
        "no_results": "<i>Ничего не найдено</i>",
    }

    strings_ru = {
        "name": "DeletedMessages",
        "loading": "🔄 <b>Загружаю...</b>",
        "no_deleted": "🌸 <b>В этом чате еще не удаляли сообщений</b>",
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
            "💾 <b>Размер кэша:</b> {cache_size}\n"
            "👁 <b>Авто-уведомления:</b> {notify}"
        ),
        "deleted_notify": (
            "🚨 <b>Сообщение удалено!</b>\n\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Отправлено:</b> {time}\n"
            "{media_info}"
            "<b>Текст:</b>\n{preview}"
        ),
        "msg_info": (
            "🌸 <b>Информация о сообщении</b>\n\n"
            "{icon} <b>Тип:</b> {type}\n"
            "👤 <b>Отправитель:</b> {sender}\n"
            "🆔 <b>ID:</b> <code>{msg_id}</code>\n"
            "🕐 <b>Отправлено:</b> {send_time}\n"
            "🗑 <b>Удалено:</b> {delete_time}\n"
            "{deleter_info}"
            "{media_details}"
            "\n<b>Содержимое:</b>\n{content}"
        ),
        "deleter_info": "👤 <b>Удалил:</b> {deleter}\n",
        "unknown_deleter": "<i>Неизвестно</i>",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "unknown_sender": "Неизвестный",
        "no_text": "<i>Нет текста</i>",
        "media_photo": "Фото",
        "media_video": "Видео",
        "media_audio": "Аудио",
        "media_voice": "Голосовое",
        "media_sticker": "Стикер",
        "media_document": "Документ",
        "media_gif": "GIF",
        "help_text": (
            "🌸 <b>Помощь по DeletedMessages</b>\n\n"
            "<b>Основные команды:</b>\n"
            "• <code>.del on</code> - включить отслеживание\n"
            "• <code>.del off</code> - выключить отслеживание\n"
            "• <code>.del list</code> - показать список\n"
            "• <code>.del stats</code> - статистика\n"
            "• <code>.del clear</code> - очистить историю\n"
            "• <code>.del help</code> - эта справка"
        ),
        "no_args": "❌ <b>Используйте:</b> .del [on/off/list/stats/clear/help]",
        "global_toggle_on": "✅ <b>Глобальное отслеживание включено</b>",
        "global_toggle_off": "✅ <b>Глобальное отслеживание выключено</b>",
        "export_complete": "✅ <b>Экспорт завершен</b>",
        "search_results": "🔍 <b>Результаты поиска:</b>\n",
        "no_results": "<i>Ничего не найдено</i>",
        "_cls_doc": "Модуль для отслеживания удаленных сообщений"
    }

    def __init__(self):
        # Используем правильные валидаторы из документации
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_notify",
                True,
                "Автоматически уведомлять о удаленных сообщениях",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "save_media_info",
                True,
                "Сохранять информацию о медиа-файлах",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "max_cache_size",
                500,
                "Максимальное количество сообщений в кэше",
                validator=loader.validators.Integer(minimum=1)
            ),
            loader.ConfigValue(
                "notify_sound",
                False,
                "Звук при уведомлении",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "global_track",
                False,
                "Глобальное отслеживание во всех чатах",
                validator=loader.validators.Boolean()
            ),
        )
        
        # Инициализируем локальную базу данных для всех пользователей
        self.tracked_chats = {}
        self.message_cache = {}
        self.deleted_messages = {}
        self.user_notifications = {}  # user_id -> список чатов для уведомлений

    async def client_ready(self, client, db):
        """Загружаем данные при старте"""
        self._client = client
        self._db = db
        
        # Загружаем из общей базы данных
        self._load_data()
        
        # Регистрируем обработчики событий
        client.add_event_handler(
            self._handle_message,
            events.NewMessage(outgoing=True)
        )
        client.add_event_handler(
            self._handle_deleted,
            events.MessageDeleted()
        )

    def _load_data(self):
        """Загружаем данные из базы"""
        # Используем self._db для работы с базой данных
        self.tracked_chats = self._db.get(__name__, "tracked_chats", {})
        self.message_cache = self._db.get(__name__, "message_cache", {})
        self.deleted_messages = self._db.get(__name__, "deleted_messages", {})
        self.user_notifications = self._db.get(__name__, "user_notifications", {})

    def _save_data(self):
        """Сохраняем данные в базу"""
        self._db.set(__name__, "tracked_chats", self.tracked_chats)
        self._db.set(__name__, "message_cache", self.message_cache)
        self._db.set(__name__, "deleted_messages", self.deleted_messages)
        self._db.set(__name__, "user_notifications", self.user_notifications)

    async def _handle_message(self, event):
        """Обрабатываем новое сообщение"""
        if not isinstance(event.message, Message):
            return
            
        chat_id = utils.get_chat_id(event.message)
        
        # Проверяем, отслеживается ли чат
        if not self.config["global_track"] and chat_id not in self.tracked_chats:
            return
            
        # Сохраняем сообщение в кэш
        await self._save_message(event.message)

    async def _save_message(self, message: Message):
        """Сохраняем сообщение в кэш"""
        chat_id = utils.get_chat_id(message)
        
        # Создаем запись о сообщении
        msg_data = {
            "id": message.id,
            "chat_id": chat_id,
            "sender_id": message.sender_id,
            "date": message.date.timestamp(),
            "text": message.raw_text or "",
            "media": bool(message.media),
            "reply_to": message.reply_to.reply_to_msg_id if message.reply_to else None,
        }
        
        # Сохраняем информацию о медиа, если нужно
        if message.media and self.config["save_media_info"]:
            msg_data["media_info"] = self._parse_media(message.media)
        
        # Инициализируем кэш для чата, если нужно
        if chat_id not in self.message_cache:
            self.message_cache[chat_id] = {}
        
        # Сохраняем сообщение
        self.message_cache[chat_id][message.id] = msg_data
        
        # Ограничиваем размер кэша
        cache = self.message_cache[chat_id]
        if len(cache) > self.config["max_cache_size"]:
            # Удаляем самое старое сообщение
            oldest_id = min(cache.keys())
            del cache[oldest_id]
        
        self._save_data()

    def _parse_media(self, media) -> Dict:
        """Парсим информацию о медиа"""
        result = {"type": "unknown"}
        
        try:
            if isinstance(media, MessageMediaPhoto):
                result["type"] = "photo"
            elif isinstance(media, MessageMediaDocument):
                doc = media.document
                mime = getattr(doc, "mime_type", "").lower()
                
                if "video" in mime:
                    result["type"] = "video"
                elif "audio" in mime:
                    result["type"] = "audio"
                elif "image/webp" in mime:
                    result["type"] = "sticker"
                elif "gif" in mime:
                    result["type"] = "gif"
                else:
                    result["type"] = "document"
            elif isinstance(media, MessageMediaContact):
                result["type"] = "contact"
            elif isinstance(media, MessageMediaGeo):
                result["type"] = "location"
            elif isinstance(media, MessageMediaPoll):
                result["type"] = "poll"
            elif isinstance(media, MessageMediaGame):
                result["type"] = "game"
            elif isinstance(media, MessageMediaWebPage):
                result["type"] = "webpage"
        except:
            pass
        
        return result

    async def _handle_deleted(self, event):
        """Обрабатываем удаленное сообщение"""
        chat_id = utils.get_chat_id(event)
        
        # Проверяем, отслеживается ли чат
        if not self.config["global_track"] and chat_id not in self.tracked_chats:
            return
            
        deleted_time = time.time()
        
        for msg_id in event.deleted_ids:
            # Ищем сообщение в кэше
            msg_data = await self._get_message_from_cache(chat_id, msg_id)
            if msg_data:
                # Добавляем информацию об удалении
                msg_data["deleted_time"] = deleted_time
                msg_data["deleter_id"] = getattr(event, "deleter_id", None)
                
                # Сохраняем в историю удаленных
                if chat_id not in self.deleted_messages:
                    self.deleted_messages[chat_id] = []
                
                self.deleted_messages[chat_id].append(msg_data)
                
                # Ограничиваем историю
                if len(self.deleted_messages[chat_id]) > 100:
                    self.deleted_messages[chat_id].pop(0)
                
                # Удаляем из кэша
                await self._remove_from_cache(chat_id, msg_id)
                
                # Отправляем уведомление пользователю, если он подписан
                if self.config["auto_notify"]:
                    user_id = event.deleter_id if hasattr(event, "deleter_id") else None
                    if user_id:
                        await self._send_user_notification(user_id, chat_id, msg_data)
                
                self._save_data()

    async def _get_message_from_cache(self, chat_id: int, msg_id: int) -> Optional[Dict]:
        """Получаем сообщение из кэша"""
        if chat_id in self.message_cache and msg_id in self.message_cache[chat_id]:
            return self.message_cache[chat_id][msg_id].copy()
        return None

    async def _remove_from_cache(self, chat_id: int, msg_id: int):
        """Удаляем сообщение из кэша"""
        if chat_id in self.message_cache and msg_id in self.message_cache[chat_id]:
            del self.message_cache[chat_id][msg_id]
            if not self.message_cache[chat_id]:
                del self.message_cache[chat_id]

    async def _send_user_notification(self, user_id: int, chat_id: int, msg_data: Dict):
        """Отправляем уведомление конкретному пользователю"""
        try:
            # Получаем информацию об отправителе
            sender_name = await self._get_sender_name(msg_data["sender_id"])
            send_time = self._format_time(datetime.fromtimestamp(msg_data["date"]))
            
            # Формируем превью текста
            preview = msg_data.get("text", "")[:200]
            if len(msg_data.get("text", "")) > 200:
                preview += "..."
            if not preview:
                preview = self.strings("no_text")
            
            # Информация о медиа
            media_info = ""
            if msg_data.get("media"):
                media_type = msg_data.get("media_info", {}).get("type", "unknown")
                media_name = self.strings.get(f"media_{media_type}", media_type)
                media_info = f"📎 <b>Тип:</b> {media_name}\n"
            
            text = self.strings("deleted_notify").format(
                sender=sender_name,
                time=send_time,
                media_info=media_info,
                preview=utils.escape_html(preview)
            )
            
            # Отправляем сообщение пользователю в ЛС
            await self._client.send_message(
                user_id,
                text,
                silent=not self.config["notify_sound"]
            )
        except Exception as e:
            # Если не удалось отправить, игнорируем
            pass

    def _format_time(self, dt: datetime) -> str:
        """Форматируем время для отображения"""
        now = datetime.now()
        diff = now - dt
        
        if diff.days == 0:
            if diff.seconds < 60:
                return "только что"
            elif diff.seconds < 3600:
                return f"{diff.seconds // 60} мин. назад"
            else:
                return f"{diff.seconds // 3600} ч. назад"
        elif diff.days == 1:
            return "вчера"
        elif diff.days < 7:
            return f"{diff.days} дн. назад"
        else:
            return dt.strftime("%d.%m.%Y %H:%M")

    async def _get_sender_name(self, sender_id: int) -> str:
        """Получаем имя отправителя"""
        try:
            entity = await self._client.get_entity(sender_id)
            
            if isinstance(entity, User):
                name = f"{entity.first_name or ''} {entity.last_name or ''}".strip()
                if entity.username:
                    return f"@{entity.username} ({name})"
                return name
            elif isinstance(entity, (Channel, Chat)):
                return getattr(entity, "title", f"Chat {sender_id}")
        except:
            pass
        
        return self.strings("unknown_sender")

    @loader.command(
        ru_doc="Управление отслеживанием удаленных сообщений",
        alias="del"
    )
    async def delcmd(self, message: Message):
        """Главная команда модуля - работает только для вызвавшего"""
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        user_id = message.sender_id
        
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        
        if args.lower() == "on":
            await self._toggle_tracking(message, chat_id, user_id, True)
        elif args.lower() == "off":
            await self._toggle_tracking(message, chat_id, user_id, False)
        elif args.lower() == "list":
            await self._show_deleted_list(message, chat_id)
        elif args.lower() == "stats":
            await self._show_stats(message, chat_id)
        elif args.lower() == "clear":
            await self._clear_history(message, chat_id)
        elif args.lower() == "help":
            await utils.answer(message, self.strings("help_text"))
        elif args.lower() == "global":
            await self._toggle_global(message)
        elif args.lower().startswith("search"):
            query = args[6:].strip()
            if query:
                await self._search_messages(message, chat_id, query)
            else:
                await utils.answer(message, "Укажите поисковый запрос")
        elif args.lower() == "export":
            await self._export_messages(message, chat_id)
        else:
            await utils.answer(message, self.strings("no_args"))

    async def _toggle_tracking(self, message: Message, chat_id: int, user_id: int, enable: bool):
        """Включаем/выключаем отслеживание для пользователя в чате"""
        # Инициализируем структуру для пользователя
        if user_id not in self.user_notifications:
            self.user_notifications[user_id] = []
        
        current_chats = self.user_notifications[user_id]
        
        if enable:
            if chat_id in current_chats:
                await utils.answer(message, self.strings("already_enabled"))
            else:
                current_chats.append(chat_id)
                self._save_data()
                await utils.answer(message, self.strings("enabled"))
        else:
            if chat_id not in current_chats:
                await utils.answer(message, self.strings("already_disabled"))
            else:
                current_chats.remove(chat_id)
                self._save_data()
                await utils.answer(message, self.strings("disabled"))
        
        # Также обновляем tracked_chats для чата
        # Собираем всех пользователей, которые отслеживают этот чат
        chat_users = []
        for uid, chats in self.user_notifications.items():
            if chat_id in chats:
                chat_users.append(uid)
        
        if chat_users:
            self.tracked_chats[chat_id] = True
        else:
            self.tracked_chats[chat_id] = False
        
        self._save_data()

    async def _show_deleted_list(self, message: Message, chat_id: int):
        """Показываем список удаленных сообщений только вызывавшему"""
        user_id = message.sender_id
        
        if chat_id not in self.deleted_messages or not self.deleted_messages[chat_id]:
            await utils.answer(message, self.strings("no_deleted"))
            return
        
        # Получаем последние 15 сообщений
        deleted_list = self.deleted_messages[chat_id][-15:]
        text = "🗑 <b>Последние удаленные сообщения:</b>\n\n"
        
        for i, msg in enumerate(reversed(deleted_list), 1):
            sender_name = await self._get_sender_name(msg["sender_id"])
            send_time = self._format_time(datetime.fromtimestamp(msg["date"]))
            
            # Определяем иконку
            icon = ICONS["text"]
            if msg.get("media"):
                media_type = msg.get("media_info", {}).get("type", "unknown")
                icon = ICONS.get(media_type, ICONS["unknown"])
            
            # Формируем превью
            preview = msg.get("text", "")[:50]
            if len(msg.get("text", "")) > 50:
                preview += "..."
            if not preview:
                media_type = msg.get("media_info", {}).get("type", "медиа")
                preview = f"[{media_type}]"
            
            text += f"{i}. {icon} <b>{sender_name}</b>\n"
            text += f"   <code>{utils.escape_html(preview)}</code>\n"
            text += f"   <i>{send_time}</i>\n\n"
        
        # Отправляем ответ только вызывавшему
        await utils.answer(message, text)

    async def _show_stats(self, message: Message, chat_id: int):
        """Показываем статистику только вызывавшему"""
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

    async def _clear_history(self, message: Message, chat_id: int):
        """Очищаем историю только для этого чата"""
        if chat_id in self.deleted_messages:
            self.deleted_messages[chat_id] = []
            self._save_data()
        
        await utils.answer(message, self.strings("cleared"))

    async def _toggle_global(self, message: Message):
        """Переключаем глобальное отслеживание"""
        self.config["global_track"] = not self.config["global_track"]
        status = self.strings("global_toggle_on" if self.config["global_track"] else "global_toggle_off")
        await utils.answer(message, status)

    async def _search_messages(self, message: Message, chat_id: int, query: str):
        """Ищем сообщения по тексту"""
        if chat_id not in self.deleted_messages:
            await utils.answer(message, self.strings("no_deleted"))
            return
        
        results = []
        query_lower = query.lower()
        
        for msg in self.deleted_messages[chat_id]:
            if query_lower in msg.get("text", "").lower():
                results.append(msg)
        
        if not results:
            await utils.answer(message, self.strings("no_results"))
            return
        
        text = f"🔍 <b>Найдено {len(results)} сообщений:</b>\n\n"
        
        for i, msg in enumerate(results[:10], 1):
            sender_name = await self._get_sender_name(msg["sender_id"])
            send_time = self._format_time(datetime.fromtimestamp(msg["date"]))
            
            # Выделяем найденный текст
            preview = msg.get("text", "")
            if len(preview) > 100:
                # Находим позицию запроса
                pos = preview.lower().find(query_lower)
                if pos > 20:
                    preview = "..." + preview[pos-20:]
                preview = preview[:100] + "..."
            
            text += f"{i}. <b>{sender_name}</b> ({send_time})\n"
            text += f"   <code>{utils.escape_html(preview)}</code>\n\n"
        
        await utils.answer(message, text)

    async def _export_messages(self, message: Message, chat_id: int):
        """Экспортируем сообщения в файл"""
        if chat_id not in self.deleted_messages:
            await utils.answer(message, self.strings("no_deleted"))
            return
        
        await utils.answer(message, "📤 <b>Экспортирую...</b>")
        
        # Формируем текст для экспорта
        export_text = f"Экспорт удаленных сообщений\nЧат: {chat_id}\nДата: {datetime.now().strftime('%d.%m.%Y %H:%M')}\n\n"
        
        for msg in self.deleted_messages[chat_id]:
            sender_name = await self._get_sender_name(msg["sender_id"])
            send_time = datetime.fromtimestamp(msg["date"]).strftime("%d.%m.%Y %H:%M")
            delete_time = datetime.fromtimestamp(msg.get("deleted_time", 0)).strftime("%d.%m.%Y %H:%M")
            
            export_text += f"Отправитель: {sender_name}\n"
            export_text += f"Отправлено: {send_time}\n"
            export_text += f"Удалено: {delete_time}\n"
            export_text += f"Текст: {msg.get('text', '')}\n"
            export_text += "-" * 40 + "\n"
        
        # Отправляем файл пользователю
        await self._client.send_file(
            message.sender_id,  # Отправляем только вызывавшему
            export_text.encode(),
            caption=self.strings("export_complete"),
            file_name=f"deleted_messages_{chat_id}.txt"
        )

    async def watcher(self, message):
        """Общий ватчер для событий"""
        # Используем отдельные обработчики, зарегистрированные в client_ready
        pass 
