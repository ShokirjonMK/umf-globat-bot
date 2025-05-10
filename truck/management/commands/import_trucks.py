import json
from datetime import datetime
from django.core.management.base import BaseCommand
from truck.models import (
    Truck, TruckStatus, Company, TruckInsurance,
    TruckInspection, Driver
)


class Command(BaseCommand):
    help = "Import trucks and drivers from fleet.json (truck number only once)"

    def handle(self, *args, **options):
        with open('fleet.json', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        seen_numbers = set()

        for item in data:
            try:
                vin = self.safe_strip(item.get("VIN"))
                number = self.safe_strip(item.get(" ", ""))
                if not vin or not number or number in seen_numbers:
                    continue  # ✅ number oldin yaratilgan bo‘lsa o‘tkazib yuboramiz

                seen_numbers.add(number)

                status_obj, _ = TruckStatus.objects.get_or_create(
                    title=self.safe_strip(item.get("Status"))
                )
                company_obj, _ = Company.objects.get_or_create(
                    title=self.safe_strip(item.get("Company"))
                )

                truck, _ = Truck.objects.update_or_create(
                    vin_number=vin,
                    defaults={
                        "number": number,
                        "plate_number": self.safe_strip(item.get("Plate")),
                        "make": self.safe_strip(item.get("Make")),
                        "model": self.safe_strip(item.get("Model")),
                        "tm_or_b": self.safe_strip(item.get("TM/B")),
                        "color": self.safe_strip(item.get("Color")),
                        "year": self.safe_int(item.get("Year")),
                        "status": status_obj,
                        "notes": item.get("Notes"),
                        "st": self.safe_strip(item.get("ST")),
                        "whose_truck": self.safe_strip(item.get("Whose Truck")),
                        "owner_name": self.safe_strip(item.get("   Owner")),
                        "company": company_obj,
                        "driver_name": self.safe_strip(item.get("Driver")),
                    },
                )

                TruckInsurance.objects.update_or_create(
                    truck=truck,
                    defaults={
                        "proof_of_ownership": self.safe_bool(item.get("PROOF OF OWNERSHIP")),
                        "safety_carrier": self.safe_bool(item.get("SAFETY CARRIER")),
                        "liability_and_cargo": self.safe_bool(item.get("Liability and Cargo Insurance")),
                        "physical_damage": self.safe_bool(item.get("Physical Damage Ins")),
                        "physical_exp": self.parse_date(item.get("Physical Exp")),
                        "link": self.safe_link(item.get("Link")),
                    },
                )

                TruckInspection.objects.update_or_create(
                    truck=truck,
                    defaults={
                        "registration": self.safe_strip(item.get("Registration.1")),
                        "annual_inspection": self.safe_strip(item.get("Annual inspection")),
                        "rental_agreement": self.safe_strip(item.get("Rental Agreement")),
                        "outbound_inspection": self.safe_strip(item.get("Outbound inspection")),
                    },
                )

                driver_name = self.safe_strip(item.get("Driver"))
                if driver_name:
                    Driver.objects.update_or_create(
                        full_name=driver_name,
                        truck=truck,
                        defaults={
                            "company": company_obj,
                            "date": datetime.today().date(),
                            "mode": "offline",
                            "driver_type": "company" if "owner" not in self.safe_strip(item.get("Whose Truck")).lower() else "owner",
                        }
                    )

                count += 1

            except Exception as e:
                self.stderr.write(f"❌ Error with VIN {item.get('VIN')}: {e}")

        self.stdout.write(f"✅ {count} trucks and drivers imported (unique numbers only).")

    def parse_date(self, value):
        try:
            if not value or "risk" in str(value).lower() or "continuous" in str(value).lower():
                return None
            return datetime.fromisoformat(value)
        except Exception:
            try:
                return datetime.strptime(value, "%m/%d/%Y")
            except Exception:
                return None

    def safe_strip(self, val):
        return str(val).strip() if val else ""

    def safe_int(self, val):
        try:
            return int(val)
        except (ValueError, TypeError):
            return None

    def safe_bool(self, val):
        return str(val).strip().upper() == "YES" if val else False

    def safe_link(self, val):
        if not val or str(val).strip().lower() == "risk":
            return None
        return str(val).strip()
