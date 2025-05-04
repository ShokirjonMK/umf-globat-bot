import os
import sys
import django

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings") 
django.setup()

from telebot import  types
from types import SimpleNamespace
from truck.models import Truck, TruckOrientation, OrientationType, TelegramUser, Driver

ADMIN_IDS = [1784374540]
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
        m = bot.send_message(message.chat.id, "🔍 Truck raqamini kiriting (masalan: TRK-245):")
        user_last_message[message.chat.id] = [message.message_id, m.message_id]
        bot.register_next_step_handler(message, process_truck_number)


    def process_truck_number(message):
        truck_number = message.text.strip()
        chat_id = message.chat.id
        user_id = message.from_user.id

        delete_last(chat_id)

        try:
            truck = Truck.objects.get(number=truck_number)
        except Truck.DoesNotExist:
            m = bot.send_message(chat_id, "❌ Bunday truck topilmadi.")
            user_last_message[chat_id] = [message.message_id, m.message_id]
            return

        driver = Driver.objects.filter(truck=truck).order_by('-created_at').first()
        company_name = driver.company.title if driver and driver.company else "—"
        driver_info = (
            f"*👤 Driver:* {driver.full_name}\n"
            f"*🗓 Sana:* {driver.date}\n"
            f"*🚦 Mode:* `{driver.mode}`\n"
            f"*🔁 Type:* `{driver.driver_type}`\n"
            f"*✅ Confirmation:* {driver.confirmation or '—'}\n"
            f"*✍️ Sign:* {driver.sign or '—'}\n"
            f"*📄 DocuSign:* {driver.docusign or '—'}\n"
        ) if driver else "*👤 Driver:* —\n"

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

        text = (
            f"🚛 *Truck:* `{truck.number}`\n"
            f"🏢 *Company:* {company_name}\n\n"
            f"{driver_info}"
            f"🧾 *Orientation statuslari:*\n\n"
        )
        markup = types.InlineKeyboardMarkup()

        for orientation in orientations:
            status_icon = "✅" if orientation.status == "done" else "❌"
            updated = orientation.updated_at.strftime("%Y-%m-%d %H:%M")
            text += f"*{orientation.orientation_type.name}*: {status_icon} `{orientation.status}`\n_🕒 {updated}_\n"

            if user_id in ADMIN_IDS:
                markup.add(types.InlineKeyboardButton(
                    text=f"{orientation.orientation_type.name} - EDIT",
                    callback_data=f"edit:{orientation.id}"
                ))

        m = bot.send_message(chat_id, text, reply_markup=markup if markup.keyboard else None)
        user_last_message[chat_id] = [message.message_id, m.message_id]


    @bot.callback_query_handler(func=lambda call: call.data.startswith("edit:"))
    def handle_edit_orientation(call):
        orientation_id = call.data.split(":")[1]

        if call.from_user.id not in ADMIN_IDS:
            bot.answer_callback_query(call.id, "⛔ Faqat admin o‘zgartira oladi.", show_alert=True)
            return

        try:
            orientation = TruckOrientation.objects.get(id=orientation_id)
            orientation.status = (
                TruckOrientation.Status.NOT_DONE if orientation.status == "done" else TruckOrientation.Status.DONE
            )
            orientation.save()
            bot.answer_callback_query(call.id, f"✅ Status o‘zgartirildi: {orientation.status.upper()}")

            delete_last(call.message.chat.id)

            truck = orientation.truck
            fake_message = SimpleNamespace(
                chat=call.message.chat,
                from_user=call.from_user,
                text=truck.number,
                message_id=call.message.message_id
            )
            process_truck_number(fake_message)

        except TruckOrientation.DoesNotExist:
            bot.answer_callback_query(call.id, "❌ Ma'lumot topilmadi.")
