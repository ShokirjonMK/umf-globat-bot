import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") 
django.setup()

from telebot import types
from types import SimpleNamespace
from truck.models import AllowedGroup, Truck, TruckOrientation, OrientationType, TelegramUser, Driver, TruckStatus

ADMIN_IDS = [1784374540, 644442895]
user_last_message = {}

def main_handlers(bot):

    def delete_last(chat_id):
        if chat_id in user_last_message:
            try:
                for msg_id in user_last_message[chat_id]:
                    bot.delete_message(chat_id, msg_id)
            except:
                pass
        user_last_message[chat_id] = []

    @bot.message_handler(commands=["start"])
    def handle_start(message):
        tg_user = message.from_user

        TelegramUser.objects.update_or_create(
            telegram_id=tg_user.id,
            defaults={
                'first_name': tg_user.first_name,
                'last_name': tg_user.last_name,
                'username': tg_user.username,
                'language_code': tg_user.language_code,
                'is_bot': tg_user.is_bot
            }
        )

        delete_last(message.chat.id)
        m = bot.send_message(message.chat.id, "🔍 Truck raqamini kiriting (masalan: /truck 245):")
        user_last_message[message.chat.id] = [message.message_id, m.message_id]

    @bot.message_handler(commands=["getid"])
    def get_chat_id(message):
        bot.send_message(
            message.chat.id,
            f"🆔 Chat ID: `{message.chat.id}`\n👥 Type: {message.chat.type}",
            parse_mode="Markdown"
        )

    @bot.message_handler(commands=["truck"])
    def handle_truck_command(message):
        chat = message.chat
        chat_id = chat.id
        chat_id_str = str(chat_id)

        if chat.type in ["group", "supergroup"]:
            allowed_ids = list(AllowedGroup.objects.values_list("group_id", flat=True))
            chat_username = chat.username
            chat_invite_link = getattr(chat, "invite_link", None)

            if not (
                chat_id_str in allowed_ids or
                (chat_username and chat_username in allowed_ids) or
                (chat_invite_link and chat_invite_link in allowed_ids)
            ):
                bot.send_message(
                    chat_id,
                    "⛔ *Ushbu guruhda bot ishlashi taqiqlangan.*\nIltimos, botdan foydalanish uchun *admin bilan bog‘laning.*",
                    parse_mode="Markdown"
                )
                return

        try:
            truck_number = message.text.split(" ", 1)[1].strip()
        except IndexError:
            m = bot.send_message(
                chat_id,
                "❗ Truck raqamini `/truck TRK-245` tarzida kiriting.",
                parse_mode="Markdown"
            )
            user_last_message[chat_id] = [message.message_id, m.message_id]
            return

        TelegramUser.objects.update_or_create(
            telegram_id=message.from_user.id,
            defaults={
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'language_code': message.from_user.language_code,
                'is_bot': message.from_user.is_bot
            }
        )

        process_truck_number(message, truck_number)

    def process_truck_number(message, truck_number):
        chat_id = message.chat.id
        user_id = message.from_user.id

        delete_last(chat_id)

        trucks = Truck.objects.select_related('status', 'company').filter(number=truck_number).order_by('-created_at')

        if not trucks.exists():
            m = bot.send_message(chat_id, "❌ Bunday truck topilmadi.")
            user_last_message[chat_id] = [message.message_id, m.message_id]
            return

        truck = trucks.first()

        driver = Driver.objects.filter(truck=truck).order_by('-created_at').first()
        company_name = driver.company.title if driver and driver.company else "—"
        driver_info = (
            f"👤 Driver: {driver.full_name}\n"
            f"🗓 Sana: {driver.date}\n"
            f"🚦 Mode: `{driver.mode}`\n"
            f"🔁 Type: `{driver.driver_type}`\n"
            f"✅ Confirmation: {driver.confirmation or '—'}\n"
            f"✍️ Sign: {driver.sign or '—'}\n"
            f"📄 DocuSign: {driver.docusign or '—'}\n"
        ) if driver else "👤 Driver: —\n"

        truck_info = (
            f"🚛 *Truck:* `{truck.number}`\n"
            f"🏢 *Company:* {company_name}\n"
            f"🔧 *Make/Model:* {truck.make or '—'} / {truck.model or '—'}\n"
            f"🎨 *Color:* {truck.color or '—'}\n"
            f"🔑 *VIN:* `{truck.vin_number or '—'}`\n"
            f"🔹 *Plate:* `{truck.plate_number or '—'}`\n"
            f"🗕 *Year:* {truck.year or '—'}\n"
            f"🌐 *State:* {truck.st or '—'}\n"
            f"👥 *Whose Truck:* {truck.whose_truck or '—'}\n"
            f"👨🏻‍✈️ *Owner:* {truck.owner_name or '—'}\n"
            f"📍 *Driver:* {truck.driver_name or '—'}\n"
            f"📄 *Notes:* {truck.notes or '—'}\n"
            f"🚲 *Status:* {truck.status.title if truck.status else '—'}\n\n"
        )

        orientations = TruckOrientation.objects.filter(truck=truck).select_related('orientation_type')
        existing_type_ids = orientations.values_list('orientation_type_id', flat=True)
        missing_types = OrientationType.objects.exclude(id__in=existing_type_ids)

        for otype in missing_types:
            TruckOrientation.objects.create(
                truck=truck,
                orientation_type=otype,
                status=TruckOrientation.Status.NOT_DONE
            )

        orientations = TruckOrientation.objects.filter(truck=truck).select_related('orientation_type')

        orientation_text = "🧾 *Orientation statuslari:*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)

        if user_id in ADMIN_IDS:
            markup.add(
                types.InlineKeyboardButton("✏️ Orientation holatini o‘zgartirish", callback_data=f"edit:type:{truck.id}"),
                types.InlineKeyboardButton("🚜 Truck statusni o‘zgartirish", callback_data=f"edit:status:{truck.id}")
            )

        for orientation in orientations:
            status_icon = "✅" if orientation.status == "done" else "❌"
            updated = orientation.updated_at.strftime("%Y-%m-%d %H:%M")
            orientation_text += f"{orientation.orientation_type.name}: {status_icon} `{orientation.status}`\n_🕒 {updated}_\n"

        if user_id in ADMIN_IDS:
            for orientation in orientations:
                markup.add(types.InlineKeyboardButton(
                    text=f"{orientation.orientation_type.name} - EDIT",
                    callback_data=f"edit:{orientation.id}"
                ))

        text = truck_info + driver_info + orientation_text
        m = bot.send_message(chat_id, text, parse_mode="Markdown", reply_markup=markup if markup.keyboard else None)
        user_last_message[chat_id].append(m.message_id)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit"))
    def handle_edit_callbacks(call):
        user_id = int(call.from_user.id)
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Faqat admin o‘zgartira oladi.", show_alert=True)
            return

        data = call.data.split(":")

        if len(data) == 2:
            orientation_id = data[1]
            try:
                orientation = TruckOrientation.objects.get(id=orientation_id)
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("✏️ Orientation holatini o‘zgartirish", callback_data=f"edit:type:{orientation.truck.id}"),
                    types.InlineKeyboardButton("🚜 Truck statusni o‘zgartirish", callback_data=f"edit:status:{orientation.truck.id}")
                )
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            except TruckOrientation.DoesNotExist:
                bot.answer_callback_query(call.id, "❌ Orientation topilmadi.")
        elif data[1] == "type" and len(data) == 3:
            truck_id = data[2]
            try:
                truck = Truck.objects.get(id=truck_id)
                markup = types.InlineKeyboardMarkup(row_width=2)
                for otype in OrientationType.objects.all():
                    markup.add(types.InlineKeyboardButton(
                        text=otype.name,
                        callback_data=f"set:type:{truck_id}:{otype.id}"
                    ))
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="✏️ Qaysi *orientation* turini o‘zgartirasiz?",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            except Truck.DoesNotExist:
                bot.answer_callback_query(call.id, "❌ Truck topilmadi.")
        elif data[1] == "status" and len(data) == 3:
            truck_id = data[2]
            try:
                truck = Truck.objects.get(id=truck_id)
                markup = types.InlineKeyboardMarkup()
                for s in TruckStatus.objects.all():
                    markup.add(types.InlineKeyboardButton(s.title, callback_data=f"set:status:{truck_id}:{s.id}"))
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text="🚜 Truck statusni tanlang:",
                    reply_markup=markup
                )
            except Truck.DoesNotExist:
                bot.answer_callback_query(call.id, "❌ Truck topilmadi.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set:status"))
    def set_truck_status(call):
        user_id = int(call.from_user.id)
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Ruxsat yo‘q.", show_alert=True)
            return

        _, _, truck_id, status_id = call.data.split(":")
        try:
            truck = Truck.objects.get(id=truck_id)
            new_status = TruckStatus.objects.get(id=status_id)
            truck.status = new_status
            truck.save()
            bot.answer_callback_query(call.id, f"✅ Truck status yangilandi: {new_status.title}")
            delete_last(call.message.chat.id)
            fake_message = SimpleNamespace(chat=call.message.chat, from_user=call.from_user, message_id=call.message.message_id)
            process_truck_number(fake_message, truck.number)
        except Exception:
            bot.answer_callback_query(call.id, "❌ Xatolik yuz berdi.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set:type"))
    def set_orientation_status(call):
        user_id = int(call.from_user.id)
        if user_id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Ruxsat yo‘q.", show_alert=True)
            return

        try:
            _, _, truck_id, orientation_type_id = call.data.split(":")
            truck = Truck.objects.get(id=truck_id)
            otype = OrientationType.objects.get(id=orientation_type_id)

            orientation, _ = TruckOrientation.objects.get_or_create(
                truck=truck,
                orientation_type=otype,
                defaults={"status": TruckOrientation.Status.NOT_DONE}
            )

            orientation.status = (
                TruckOrientation.Status.NOT_DONE if orientation.status == "done"
                else TruckOrientation.Status.DONE
            )
            orientation.save()

            bot.send_message(
                call.message.chat.id,
                f"✅ *{otype.name}* statusi: `{orientation.status}` ga o‘zgartirildi.",
                parse_mode="Markdown"
            )

            delete_last(call.message.chat.id)
            fake_message = SimpleNamespace(chat=call.message.chat, from_user=call.from_user, message_id=call.message.message_id)
            process_truck_number(fake_message, truck.number)

        except Exception:
            bot.answer_callback_query(call.id, "❌ O‘zgartirishda xatolik yuz berdi.")

    @bot.message_handler(commands=["status"])
    def handle_status_command(message):
        markup = types.InlineKeyboardMarkup(row_width=2)
        for status in TruckStatus.objects.all():
            markup.add(types.InlineKeyboardButton(
                text=status.title,
                callback_data=f"view:status:{status.id}"
            ))
        bot.send_message(message.chat.id, "🚦 Qaysi truck statusni ko‘rmoqchisiz?", reply_markup=markup)

    @bot.callback_query_handler(func=lambda call: call.data.startswith("view:status:") or call.data.startswith("page:"))
    def view_trucks_by_status(call):
        try:
            if call.data.startswith("view:status:"):
                _, _, status_id = call.data.split(":")
                page = 0
            else:
                _, status_id, page = call.data.split(":")
                page = int(page)

            status = TruckStatus.objects.get(id=status_id)
            trucks = Truck.objects.filter(status=status)
            truck_numbers = list(trucks.values_list('number', flat=True))

            batch_size = 10
            total_pages = (len(truck_numbers) + batch_size - 1) // batch_size
            total_count = len(truck_numbers)

            start = page * batch_size
            end = start + batch_size
            chunk = truck_numbers[start:end]

            text = f"*{status.title}* statusidagi trucklar (sahifa {page + 1}/{total_pages}) - jami: {total_count} ta\n\n"
            text += "\n".join(f"`{num}`" for num in chunk)

            markup = types.InlineKeyboardMarkup()
            buttons = []
            if page > 0:
                buttons.append(types.InlineKeyboardButton("⬅️ Oldingi", callback_data=f"page:{status.id}:{page - 1}"))
            if page < total_pages - 1:
                buttons.append(types.InlineKeyboardButton("Keyingi ➡️", callback_data=f"page:{status.id}:{page + 1}"))
            if buttons:
                markup.add(*buttons)

            if call.data.startswith("view:status:"):
                bot.send_message(call.message.chat.id, text, parse_mode="Markdown", reply_markup=markup)
            else:
                bot.edit_message_text(
                    chat_id=call.message.chat.id,
                    message_id=call.message.message_id,
                    text=text,
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}", show_alert=True)

    @bot.message_handler(commands=["truck"])
    def handle_truck_command(message):
        chat = message.chat
        chat_id = chat.id
        chat_id_str = str(chat_id)

        if chat.type in ["group", "supergroup"]:
            allowed_ids = list(AllowedGroup.objects.values_list("group_id", flat=True))
            chat_username = chat.username
            chat_invite_link = getattr(chat, "invite_link", None)

            if not (
                chat_id_str in allowed_ids or
                (chat_username and chat_username in allowed_ids) or
                (chat_invite_link and chat_invite_link in allowed_ids)
            ):
                bot.send_message(
                    chat_id,
                    "⛔ *Ushbu guruhda bot ishlashi taqiqlangan.*\nIltimos, botdan foydalanish uchun *admin bilan bog‘laning.*",
                    parse_mode="Markdown"
                )
                return

        try:
            truck_number = message.text.split(" ", 1)[1].strip()
        except IndexError:
            m = bot.send_message(
                chat_id,
                "❗ Truck raqamini `/truck TRK-245` tarzida kiriting.",
                parse_mode="Markdown"
            )
            user_last_message[chat_id] = [message.message_id, m.message_id]
            return

        TelegramUser.objects.update_or_create(
            telegram_id=message.from_user.id,
            defaults={
                'first_name': message.from_user.first_name,
                'last_name': message.from_user.last_name,
                'username': message.from_user.username,
                'language_code': message.from_user.language_code,
                'is_bot': message.from_user.is_bot
            }
        )

        process_truck_number(message, truck_number)