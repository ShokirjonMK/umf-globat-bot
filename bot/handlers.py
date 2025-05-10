import os
import sys
import django

from telebot import types
from types import SimpleNamespace

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") 
django.setup()

from truck.models import AllowedGroup, Truck, TruckOrientation, OrientationType, TelegramUser, Driver, TruckStatus

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
        m = bot.send_message(message.chat.id, "\ud83d\udd0d Truck raqamini kiriting (masalan: /truck 245):")
        user_last_message[message.chat.id] = [message.message_id, m.message_id]

    @bot.message_handler(commands=["getid"])
    def get_chat_id(message):
        bot.send_message(
            message.chat.id,
            f"\ud83c\udd94 Chat ID: `{message.chat.id}`\n\ud83d\udc65 Type: {message.chat.type}",
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
                    "\u26d4 *Ushbu guruhda bot ishlashi taqiqlangan.*\nIltimos, botdan foydalanish uchun *admin bilan bog\u2018laning.*",
                    parse_mode="Markdown"
                )
                return

        try:
            truck_number = message.text.split(" ", 1)[1].strip()
        except IndexError:
            m = bot.send_message(
                chat_id,
                "\u2757 Truck raqamini `/truck TRK-245` tarzida kiriting.",
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

        delete_last(chat_id)

        trucks = Truck.objects.select_related('status', 'company').filter(number=truck_number).order_by('-created_at')

        if not trucks.exists():
            m = bot.send_message(chat_id, "\u274c Bunday truck topilmadi.")
            user_last_message[chat_id] = [message.message_id, m.message_id]
            return

        truck = trucks.first()

        driver = Driver.objects.filter(truck=truck).order_by('-created_at').first()
        company_name = driver.company.title if driver and driver.company else "\u2014"
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

        orientation_text = "\ud83d\udcdf *Orientation statuslari:*\n\n"
        markup = types.InlineKeyboardMarkup(row_width=1)

        markup.add(
            types.InlineKeyboardButton("\u270f\ufe0f Orientation holatini o\u2018zgartirish", callback_data=f"edit:type:{truck.id}"),
            types.InlineKeyboardButton("\ud83d\ude9c Truck statusni o\u2018zgartirish", callback_data=f"edit:status:{truck.id}")
        )

        for orientation in orientations:
            status_icon = "\u2705" if orientation.status == "done" else "\u274c"
            updated = orientation.updated_at.strftime("%Y-%m-%d %H:%M")
            orientation_text += f"{orientation.orientation_type.name}: {status_icon} `{orientation.status}`\n_\ud83d\udd52 {updated}_\n"

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
        data = call.data.split(":")

        if len(data) == 2:
            orientation_id = data[1]
            try:
                orientation = TruckOrientation.objects.get(id=orientation_id)
                markup = types.InlineKeyboardMarkup()
                markup.add(
                    types.InlineKeyboardButton("\u270f\ufe0f Orientation holatini o\u2018zgartirish", callback_data=f"edit:type:{orientation.truck.id}"),
                    types.InlineKeyboardButton("\ud83d\ude9c Truck statusni o\u2018zgartirish", callback_data=f"edit:status:{orientation.truck.id}")
                )
                bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id, reply_markup=markup)
            except TruckOrientation.DoesNotExist:
                bot.answer_callback_query(call.id, "\u274c Orientation topilmadi.")
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
                    text="\u270f\ufe0f Qaysi *orientation* turini o\u2018zgartirasiz?",
                    reply_markup=markup,
                    parse_mode="Markdown"
                )
            except Truck.DoesNotExist:
                bot.answer_callback_query(call.id, "\u274c Truck topilmadi.")
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
                    text="\ud83d\ude9c Truck statusni tanlang:",
                    reply_markup=markup
                )
            except Truck.DoesNotExist:
                bot.answer_callback_query(call.id, "\u274c Truck topilmadi.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set:status"))
    def set_truck_status(call):
        _, _, truck_id, status_id = call.data.split(":")
        try:
            truck = Truck.objects.get(id=truck_id)
            new_status = TruckStatus.objects.get(id=status_id)
            truck.status = new_status
            truck.save()
            bot.answer_callback_query(call.id, f"\u2705 Truck status yangilandi: {new_status.title}")
            delete_last(call.message.chat.id)
            fake_message = SimpleNamespace(chat=call.message.chat, from_user=call.from_user, message_id=call.message.message_id)
            process_truck_number(fake_message, truck.number)
        except Exception:
            bot.answer_callback_query(call.id, "\u274c Xatolik yuz berdi.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith("set:type"))
    def set_orientation_status(call):
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
                f"\u2705 *{otype.name}* statusi: `{orientation.status}` ga o\u2018zgartirildi.",
                parse_mode="Markdown"
            )

            delete_last(call.message.chat.id)
            fake_message = SimpleNamespace(chat=call.message.chat, from_user=call.from_user, message_id=call.message.message_id)
            process_truck_number(fake_message, truck.number)

        except Exception:
            bot.answer_callback_query(call.id, "\u274c O\u2018zgartirishda xatolik yuz berdi.")
