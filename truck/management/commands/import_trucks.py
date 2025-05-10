import json
from datetime import datetime
from django.core.management.base import BaseCommand
from truck.models import (
    Truck, TruckStatus, Company, TruckInsurance,
    TruckInspection, Driver
)


class Command(BaseCommand):
    help = "Import trucks and drivers from fleet.json"

    def handle(self, *args, **options):
        with open('fleet.json', encoding='utf-8') as f:
            data = json.load(f)

        count = 0
        for item in data:
            try:
                vin = item.get("VIN")
                if not vin:
                    continue

                status_obj, _ = TruckStatus.objects.get_or_create(title=item.get("Status", "").strip())
                company_obj, _ = Company.objects.get_or_create(title=item.get("Company", "").strip())

                truck, _ = Truck.objects.update_or_create(
                    vin_number=vin,
                    defaults={
                        "number": str(item.get(" ", "")).strip(),
                        "plate_number": item.get("Plate"),
                        "make": item.get("Make"),
                        "model": item.get("Model"),
                        "tm_or_b": item.get("TM/B"),
                        "color": item.get("Color"),
                        "year": int(item["Year"]) if item.get("Year") else None,
                        "status": status_obj,
                        "notes": item.get("Notes"),
                        "st": item.get("ST"),
                        "whose_truck": item.get("Whose Truck"),
                        "owner_name": item.get("   Owner"),
                        "company": company_obj,
                        "driver_name": item.get("Driver"),
                    },
                )

                TruckInsurance.objects.update_or_create(
                    truck=truck,
                    defaults={
                        "proof_of_ownership": item.get("PROOF OF OWNERSHIP", "").strip().upper() == "YES",
                        "safety_carrier": item.get("SAFETY CARRIER", "").strip().upper() == "YES",
                        "liability_and_cargo": item.get("Liability and Cargo Insurance", "").strip().upper() == "YES",
                        "physical_damage": item.get("Physical Damage Ins", "").strip().upper() == "YES",
                        "physical_exp": self.parse_date(item.get("Physical Exp")),
                        "link": item.get("Link") if item.get("Link") != "RISK" else None,
                    },
                )

                TruckInspection.objects.update_or_create(
                    truck=truck,
                    defaults={
                        "registration": item.get("Registration.1", ""),
                        "annual_inspection": item.get("Annual inspection", ""),
                        "rental_agreement": item.get("Rental Agreement", ""),
                        "outbound_inspection": item.get("Outbound inspection", ""),
                    },
                )

                driver_name = item.get("Driver")
                if driver_name:
                    Driver.objects.update_or_create(
                        full_name=driver_name.strip(),
                        truck=truck,
                        defaults={
                            "company": company_obj,
                            "date": datetime.today().date(),
                            "mode": "offline",
                            "driver_type": "company" if "owner" not in (item.get("Whose Truck") or "").lower() else "owner",
                        }
                    )

                count += 1

            except Exception as e:
                self.stderr.write(f"❌ Error with VIN {item.get('VIN')}: {e}")

        self.stdout.write(f"✅ {count} trucks and drivers imported.")

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
