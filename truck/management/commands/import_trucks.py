import json
from django.core.management.base import BaseCommand
from datetime import datetime

from truck.models import Company, Truck, Driver

class Command(BaseCommand):
    help = "Import trucks and drivers from JSON file"

    def handle(self, *args, **kwargs):
        with open("Asadga.json", "r", encoding="utf-8") as f:
            data = json.load(f)

        company_title = "One Step Cargo Inc"
        company, _ = Company.objects.get_or_create(title=company_title)

        for entry in data:
            truck_number = entry.get(" ", "").strip()
            make = entry.get("Make")
            model = entry.get("Model")

            year_raw = entry.get("Year\n(OR)")
            year = int(float(year_raw)) if year_raw else None

            plate = entry.get("Plate")
            vin = entry.get("VIN\n(NM)")

            # Null safe status check
            status_raw = entry.get("Status")
            status = "active" if status_raw and status_raw.lower() == "enroute" else "inactive"

            truck, _ = Truck.objects.get_or_create(
                number=truck_number,
                defaults={
                    "make": make,
                    "model": model,
                    "year": year,
                    "plate_number": plate,
                    "vin_number": vin,
                    "status": status,
                }
            )

            full_name = entry.get("Driver")
            reg_date = entry.get("Registration")
            date_obj = None
            if reg_date:
                try:
                    date_obj = datetime.strptime(reg_date.split(" ")[0], "%Y-%m-%d").date()
                except:
                    pass

            if full_name:
                driver_type_raw = entry.get("Whose Truck\n(NY)")
                driver_type = "owner" if driver_type_raw and driver_type_raw.lower() == "owner" else "company"

                Driver.objects.get_or_create(
                    full_name=full_name.strip(),
                    truck=truck,
                    company=company,
                    defaults={
                        "mode": "offline",
                        "date": date_obj or datetime.now().date(),
                        "driver_type": driver_type
                    }
                )

        self.stdout.write(self.style.SUCCESS("✅ Truck va Driver ma'lumotlari JSON dan import qilindi."))
