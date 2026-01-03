__version__ = (1, 0, 0)
# meta banner: https://raw.githubusercontent.com/kchemniy/hikka-modules/main/banners/DeletedMessages.png
# meta developer: @kchemniy_modules
# scope: hikka_only
# scope: hikka_min 1.2.10

import html
import asyncio
from datetime import datetime
from typing import Optional, Dict, List

from telethon.tl.types import Message, User, Channel, Chat
from telethon.tl.functions.messages import GetMessagesViewsRequest
from telethon.tl.functions.channels import GetMessagesRequest as GetChannelMessagesRequest

from .. import loader, utils


@loader.tds
class DeletedMessagesMod(loader.Module):
    """Показывает удалённые сообщения в чате."""

    strings = {
        "name": "DeletedMessages",
        "no_args": "❌ <b>Укажите действие:</b>\n<code>.deleted on</code> - включить отслеживание\n<code>.deleted off</code> - выключить отслеживание\n<code>.deleted list</code> - показать список удаленных сообщений\n<code>.deleted clear</code> - очистить историю",
        "already_enabled": "✅ <b>Отслеживание удалённых сообщений уже включено</b>",
        "already_disabled": "✅ <b>Отслеживание удалённых сообщений уже выключено</b>",
        "enabled": "✅ <b>Отслеживание удалённых сообщений включено</b>\nТеперь я буду сохранять все сообщения и показывать их при удалении.",
        "disabled": "✅ <b>Отслеживание удалённых сообщений выключено</b>",
        "cleared": "✅ <b>История удалённых сообщений очищена</b>",
        "no_deleted": "📭 <b>В этом чате нет удалённых сообщений</b>",
        "deleted_header": "🗑 <b>Удалённые сообщения в этом чате:</b>\n\n",
        "loading": "⏳ <b>Загружаю удалённые сообщения...</b>",
        "deleted_msg": (
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Время отправки:</b> {time}\n"
            "🗑 <b>Удалено:</b> {deleted_time}\n"
            "📄 <b>Сообщение:</b>\n{content}\n"
            "{media_info}"
            "{replies_info}"
            "━━━━━━━━━━━━━━━━━━━━\n"
        ),
        "unknown_sender": "<i>Неизвестный отправитель</i>",
        "deleted_by": "🗑 <b>Удалил:</b> {deleter}\n",
        "media_file": "📁 <b>Файл:</b> <code>{filename}</code>\n",
        "media_photo": "🖼 <b>Фото</b>\n",
        "media_video": "🎬 <b>Видео</b>\n",
        "media_audio": "🎵 <b>Аудио</b>\n",
        "media_voice": "🎤 <b>Голосовое сообщение</b>\n",
        "media_sticker": "🩷 <b>Стикер</b>\n",
        "media_document": "📄 <b>Документ</b>\n",
        "media_contact": "👤 <b>Контакт</b>\n",
        "media_location": "📍 <b>Локация</b>\n",
        "media_poll": "📊 <b>Опрос:</b> {question}\n",
        "media_game": "🎮 <b>Игра:</b> {title}\n",
        "reply_to": "↩️ <b>Ответ на сообщение:</b> {reply_id}\n",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "reactions": "❤️ <b>Реакции:</b> {reactions}\n",
        "saved_by": "💾 <b>Сохранено в:</b> {saver}\n",
    }

    strings_ru = {
        "name": "DeletedMessages",
        "no_args": "❌ <b>Укажите действие:</b>\n<code>.deleted on</code> - включить отслеживание\n<code>.deleted off</code> - выключить отслеживание\n<code>.deleted list</code> - показать список удаленных сообщений\n<code>.deleted clear</code> - очистить историю",
        "already_enabled": "✅ <b>Отслеживание удалённых сообщений уже включено</b>",
        "already_disabled": "✅ <b>Отслеживание удалённых сообщений уже выключено</b>",
        "enabled": "✅ <b>Отслеживание удалённых сообщений включено</b>\nТеперь я буду сохранять все сообщения и показывать их при удалении.",
        "disabled": "✅ <b>Отслеживание удалённых сообщений выключено</b>",
        "cleared": "✅ <b>История удалённых сообщений очищена</b>",
        "no_deleted": "📭 <b>В этом чате нет удалённых сообщений</b>",
        "deleted_header": "🗑 <b>Удалённые сообщения в этом чате:</b>\n\n",
        "loading": "⏳ <b>Загружаю удалённые сообщения...</b>",
        "deleted_msg": (
            "👤 <b>Отправитель:</b> {sender}\n"
            "🕐 <b>Время отправки:</b> {time}\n"
            "🗑 <b>Удалено:</b> {deleted_time}\n"
            "📄 <b>Сообщение:</b>\n{content}\n"
            "{media_info}"
            "{replies_info}"
            "━━━━━━━━━━━━━━━━━━━━\n"
        ),
        "unknown_sender": "<i>Неизвестный отправитель</i>",
        "deleted_by": "🗑 <b>Удалил:</b> {deleter}\n",
        "media_file": "📁 <b>Файл:</b> <code>{filename}</code>\n",
        "media_photo": "🖼 <b>Фото</b>\n",
        "media_video": "🎬 <b>Видео</b>\n",
        "media_audio": "🎵 <b>Аудио</b>\n",
        "media_voice": "🎤 <b>Голосовое сообщение</b>\n",
        "media_sticker": "🩷 <b>Стикер</b>\n",
        "media_document": "📄 <b>Документ</b>\n",
        "media_contact": "👤 <b>Контакт</b>\n",
        "media_location": "📍 <b>Локация</b>\n",
        "media_poll": "📊 <b>Опрос:</b> {question}\n",
        "media_game": "🎮 <b>Игра:</b> {title}\n",
        "reply_to": "↩️ <b>Ответ на сообщение:</b> {reply_id}\n",
        "views": "👁 <b>Просмотры:</b> {views}\n",
        "forwards": "🔄 <b>Репосты:</b> {forwards}\n",
        "reactions": "❤️ <b>Реакции:</b> {reactions}\n",
        "saved_by": "💾 <b>Сохранено в:</b> {saver}\n",
        "_cls_doc": "Показывает удалённые сообщения в чате",
    }

    def __init__(self):
        self.config = loader.ModuleConfig(
            loader.ConfigValue(
                "auto_enable",
                False,
                lambda: "Автоматически включать отслеживание в новых чатах",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "save_media",
                True,
                lambda: "Сохранять информацию о медиа",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "show_deleter",
                True,
                lambda: "Показывать кто удалил сообщение",
                validator=loader.validators.Boolean()
            ),
            loader.ConfigValue(
                "max_history",
                100,
                lambda: "Максимальное количество сохраненных сообщений на чат",
                validator=loader.validators.Integer(minimum=10, maximum=1000)
            ),
            loader.ConfigValue(
                "notify_on_delete",
                True,
                lambda: "Уведомлять при удалении сообщения",
                validator=loader.validators.Boolean()
            ),
        )
        self.tracked_chats: Dict[int, bool] = {}
        self.deleted_messages: Dict[int, List[Dict]] = {}
        self.message_cache: Dict[int, Dict] = {}

    async def client_ready(self, client, db):
        self._client = client
        self._db = db
        
        # Загружаем сохраненные данные
        self.tracked_chats = self._db.get(__name__, "tracked_chats", {})
        self.deleted_messages = self._db.get(__name__, "deleted_messages", {})
        self.message_cache = self._db.get(__name__, "message_cache", {})

    def save_data(self):
        """Сохраняет данные в базу данных"""
        self._db.set(__name__, "tracked_chats", self.tracked_chats)
        self._db.set(__name__, "deleted_messages", self.deleted_messages)
        self._db.set(__name__, "message_cache", self.message_cache)

    def _format_time(self, timestamp: datetime) -> str:
        """Форматирует время"""
        return timestamp.strftime("%d.%m.%Y %H:%M:%S")

    def _get_sender_name(self, sender) -> str:
        """Получает имя отправителя"""
        if not sender:
            return self.strings("unknown_sender")
        
        if isinstance(sender, User):
            if sender.username:
                return f"@{sender.username} ({sender.first_name or ''} {sender.last_name or ''})".strip()
            return f"{sender.first_name or ''} {sender.last_name or ''}".strip() or f"User {sender.id}"
        elif isinstance(sender, (Channel, Chat)):
            return getattr(sender, "title", f"Chat {sender.id}")
        
        return str(sender)

    async def _save_message(self, message: Message):
        """Сохраняет сообщение в кэш"""
        if not message:
            return
        
        chat_id = utils.get_chat_id(message)
        if chat_id not in self.tracked_chats or not self.tracked_chats[chat_id]:
            return
        
        # Ограничиваем количество сохраненных сообщений
        if chat_id in self.message_cache:
            if len(self.message_cache[chat_id]) >= self.config["max_history"]:
                # Удаляем самые старые сообщения
                keys = list(self.message_cache[chat_id].keys())
                for key in keys[:len(keys) - self.config["max_history"] + 1]:
                    del self.message_cache[chat_id][key]
        
        message_data = {
            "id": message.id,
            "sender_id": message.sender_id,
            "date": message.date.timestamp(),
            "text": message.text or message.raw_text or "",
            "media": bool(message.media),
            "reply_to": message.reply_to.reply_to_msg_id if message.reply_to else None,
            "views": getattr(message, "views", None),
            "forwards": getattr(message, "forwards", None),
            "reactions": getattr(message, "reactions", None),
        }
        
        # Сохраняем информацию о медиа
        if message.media and self.config["save_media"]:
            message_data["media_info"] = self._get_media_info(message.media)
        
        if chat_id not in self.message_cache:
            self.message_cache[chat_id] = {}
        
        self.message_cache[chat_id][message.id] = message_data
        self.save_data()

    def _get_media_info(self, media) -> Dict:
        """Получает информацию о медиа"""
        media_info = {"type": "unknown"}
        
        try:
            if hasattr(media, "photo"):
                media_info["type"] = "photo"
            elif hasattr(media, "document"):
                doc = media.document
                if any(attr in doc.mime_type for attr in ["video", "mp4"]):
                    media_info["type"] = "video"
                elif "audio" in doc.mime_type or any(attr in doc.mime_type for attr in ["ogg", "mpeg"]):
                    media_info["type"] = "audio"
                elif doc.mime_type == "image/webp" and any(attr.name == "sticker" for attr in doc.attributes):
                    media_info["type"] = "sticker"
                else:
                    media_info.update({
                        "type": "document",
                        "filename": next((attr.file_name for attr in doc.attributes if hasattr(attr, "file_name")), "file")
                    })
            elif hasattr(media, "contact"):
                media_info["type"] = "contact"
            elif hasattr(media, "geo"):
                media_info["type"] = "location"
            elif hasattr(media, "poll"):
                media_info.update({
                    "type": "poll",
                    "question": media.poll.question
                })
            elif hasattr(media, "game"):
                media_info.update({
                    "type": "game",
                    "title": media.game.title
                })
        except:
            pass
        
        return media_info

    async def _on_message(self, message: Message):
        """Обрабатывает входящие сообщения"""
        await self._save_message(message)

    async def _on_message_deleted(self, event):
        """Обрабатывает удаленные сообщения"""
        chat_id = utils.get_chat_id(event)
        if chat_id not in self.tracked_chats or not self.tracked_chats[chat_id]:
            return
        
        deleted_time = datetime.now()
        
        for msg_id in event.deleted_ids:
            if chat_id in self.message_cache and msg_id in self.message_cache[chat_id]:
                # Получаем сохраненное сообщение
                msg_data = self.message_cache[chat_id][msg_id]
                
                # Добавляем информацию о том, кто удалил
                deleter_info = ""
                if self.config["show_deleter"] and hasattr(event, "deleter_id"):
                    try:
                        deleter = await self._client.get_entity(event.deleter_id)
                        deleter_info = self.strings("deleted_by").format(
                            deleter=self._get_sender_name(deleter)
                        )
                    except:
                        pass
                
                deleted_msg = {
                    **msg_data,
                    "deleted_time": deleted_time.timestamp(),
                    "deleter_info": deleter_info,
                    "original_chat_id": chat_id,
                }
                
                if chat_id not in self.deleted_messages:
                    self.deleted_messages[chat_id] = []
                
                self.deleted_messages[chat_id].append(deleted_msg)
                
                # Уведомляем об удалении
                if self.config["notify_on_delete"]:
                    try:
                        sender_name = "Неизвестный отправитель"
                        if msg_data.get("sender_id"):
                            try:
                                sender = await self._client.get_entity(msg_data["sender_id"])
                                sender_name = self._get_sender_name(sender)
                            except:
                                pass
                        
                        text = f"🗑 <b>Сообщение удалено</b>\n👤 <b>От:</b> {sender_name}\n🕐 <b>Было отправлено:</b> {self._format_time(datetime.fromtimestamp(msg_data['date']))}"
                        
                        if msg_data.get("text"):
                            text += f"\n📄 <b>Текст:</b> {utils.escape_html(msg_data['text'][:100])}{'...' if len(msg_data['text']) > 100 else ''}"
                        
                        await self._client.send_message(chat_id, text)
                    except:
                        pass
                
                # Удаляем из кэша
                del self.message_cache[chat_id][msg_id]
                self.save_data()

    async def watcher(self, message):
        """Наблюдатель за сообщениями"""
        if isinstance(message, Message) and message.text:
            await self._on_message(message)
        elif hasattr(message, "deleted_ids"):
            await self._on_message_deleted(message)

    @loader.command(ru_doc="Управление отслеживанием удаленных сообщений")
    async def deleted(self, message: Message):
        """Управление отслеживанием удаленных сообщений"""
        args = utils.get_args_raw(message)
        chat_id = utils.get_chat_id(message)
        
        if not args:
            await utils.answer(message, self.strings("no_args"))
            return
        
        if args.lower() == "on":
            if chat_id in self.tracked_chats and self.tracked_chats[chat_id]:
                await utils.answer(message, self.strings("already_enabled"))
                return
            
            self.tracked_chats[chat_id] = True
            self.save_data()
            await utils.answer(message, self.strings("enabled"))
            
        elif args.lower() == "off":
            if chat_id not in self.tracked_chats or not self.tracked_chats[chat_id]:
                await utils.answer(message, self.strings("already_disabled"))
                return
            
            self.tracked_chats[chat_id] = False
            self.save_data()
            await utils.answer(message, self.strings("disabled"))
            
        elif args.lower() == "clear":
            if chat_id in self.deleted_messages:
                self.deleted_messages[chat_id] = []
                self.save_data()
            await utils.answer(message, self.strings("cleared"))
            
        elif args.lower() == "list":
            await self._show_deleted_list(message)
            
        else:
            await utils.answer(message, self.strings("no_args"))

    async def _show_deleted_list(self, message: Message):
        """Показывает список удаленных сообщений"""
        chat_id = utils.get_chat_id(message)
        
        if chat_id not in self.deleted_messages or not self.deleted_messages[chat_id]:
            await utils.answer(message, self.strings("no_deleted"))
            return
        
        loading_msg = await utils.answer(message, self.strings("loading"))
        
        result = [self.strings("deleted_header")]
        
        for i, msg_data in enumerate(reversed(self.deleted_messages[chat_id][-50:]), 1):
            try:
                # Получаем информацию об отправителе
                sender_name = self.strings("unknown_sender")
                if msg_data.get("sender_id"):
                    try:
                        sender = await self._client.get_entity(msg_data["sender_id"])
                        sender_name = self._get_sender_name(sender)
                    except:
                        pass
                
                # Форматируем время
                send_time = self._format_time(datetime.fromtimestamp(msg_data["date"]))
                deleted_time = self._format_time(datetime.fromtimestamp(msg_data["deleted_time"]))
                
                # Форматируем текст
                content = utils.escape_html(msg_data.get("text", ""))
                if not content:
                    content = "<i>Нет текста</i>"
                
                # Информация о медиа
                media_info = ""
                if msg_data.get("media_info"):
                    media_type = msg_data["media_info"].get("type", "")
                    if media_type == "photo":
                        media_info = self.strings("media_photo")
                    elif media_type == "video":
                        media_info = self.strings("media_video")
                    elif media_type == "audio":
                        media_info = self.strings("media_audio")
                    elif media_type == "sticker":
                        media_info = self.strings("media_sticker")
                    elif media_type == "document":
                        filename = msg_data["media_info"].get("filename", "file")
                        media_info = self.strings("media_file").format(filename=filename)
                    elif media_type == "contact":
                        media_info = self.strings("media_contact")
                    elif media_type == "location":
                        media_info = self.strings("media_location")
                    elif media_type == "poll":
                        question = msg_data["media_info"].get("question", "")
                        media_info = self.strings("media_poll").format(question=question)
                    elif media_type == "game":
                        title = msg_data["media_info"].get("title", "")
                        media_info = self.strings("media_game").format(title=title)
                
                # Информация о ответах и статистике
                replies_info = ""
                if msg_data.get("deleter_info"):
                    replies_info += msg_data["deleter_info"]
                
                if msg_data.get("reply_to"):
                    replies_info += self.strings("reply_to").format(reply_id=msg_data["reply_to"])
                
                if msg_data.get("views") is not None:
                    replies_info += self.strings("views").format(views=msg_data["views"])
                
                if msg_data.get("forwards") is not None:
                    replies_info += self.strings("forwards").format(forwards=msg_data["forwards"])
                
                if msg_data.get("reactions") is not None:
                    reactions_count = len(msg_data["reactions"].results) if hasattr(msg_data["reactions"], "results") else 0
                    replies_info += self.strings("reactions").format(reactions=reactions_count)
                
                # Формируем сообщение
                msg_text = self.strings("deleted_msg").format(
                    sender=sender_name,
                    time=send_time,
                    deleted_time=deleted_time,
                    content=content,
                    media_info=media_info,
                    replies_info=replies_info
                )
                
                result.append(f"<b>#{i}</b>\n{msg_text}")
                
            except Exception as e:
                continue
        
        # Разбиваем на части если слишком длинное
        full_text = "".join(result)
        chunks = [full_text[i:i+4000] for i in range(0, len(full_text), 4000)]
        
        try:
            await loading_msg.delete()
        except:
            pass
        
        for chunk in chunks:
            await self._client.send_message(
                chat_id,
                chunk,
                reply_to=getattr(message, "reply_to_msg_id", None)
            )

    @loader.command(ru_doc="Включить отслеживание во всех чатах")
    async def deletedglobalon(self, message: Message):
        """Включить отслеживание во всех чатах"""
        self.tracked_chats = {utils.get_chat_id(message): True}
        self.save_data()
        await utils.answer(message, "✅ <b>Глобальное отслеживание включено</b>")

    @loader.command(ru_doc="Статистика отслеживания")
    async def deletedstats(self, message: Message):
        """Показать статистику отслеживания"""
        chat_id = utils.get_chat_id(message)
        
        tracked_chats_count = sum(1 for v in self.tracked_chats.values() if v)
        deleted_count = sum(len(msgs) for msgs in self.deleted_messages.values())
        cached_count = sum(len(msgs) for msgs in self.message_cache.values())
        
        current_tracked = "✅" if self.tracked_chats.get(chat_id) else "❌"
        current_deleted = len(self.deleted_messages.get(chat_id, []))
        
        text = (
            f"📊 <b>Статистика DeletedMessages:</b>\n\n"
            f"• Отслеживаемых чатов: <code>{tracked_chats_count}</code>\n"
            f"• Всего удаленных сообщений: <code>{deleted_count}</code>\n"
            f"• Сообщений в кэше: <code>{cached_count}</code>\n\n"
            f"<b>Текущий чат:</b>\n"
            f"• Отслеживание: {current_tracked}\n"
            f"• Удаленных сообщений: <code>{current_deleted}</code>"
        )
        
        await utils.answer(message, text)
