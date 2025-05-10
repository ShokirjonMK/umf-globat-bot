import pandas as pd
from django.core.management.base import BaseCommand
from datetime import datetime
from truck.models import Company, Truck, Driver, TruckStatus, TruckInsurance, TruckInspection


class Command(BaseCommand):
    help = "Import trucks and related info from local Excel file"

    def handle(self, *args, **kwargs):
        file_path = "trucks.xlsx"  # 📁 Local fayl nomi

        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"❌ Excel faylni o‘qishda xatolik: {e}"))
            return

        def safe_date(val):
            try:
                return pd.to_datetime(val).date() if pd.notna(val) and val else None
            except Exception:
                return None

        for _, row in df.iterrows():
            truck_number = str(row.get("#")).strip()
            make = row.get("Make")
            model = row.get("Model")
            tm_or_b = row.get("TM/B")
            color = row.get("Color")
            status_title = row.get("Status")
            notes = row.get("Notes")
            vin = row.get("VIN")
            year = int(row.get("Year")) if pd.notna(row.get("Year")) else None
            plate = row.get("Plate")
            st = row.get("ST")
            whose = row.get("Whose Truck")
            owner = row.get("Owner")
            company_title = row.get("Company")
            driver_name = row.get("Driver")
            phone = row.get("Phone #")

            # 🔄 TruckStatus
            status = None
            if status_title:
                status, _ = TruckStatus.objects.get_or_create(title=status_title.strip())

            # 🔄 Company
            company, _ = Company.objects.get_or_create(title=company_title or "Unknown")

            # 🔄 Truck
            truck, _ = Truck.objects.update_or_create(
                number=truck_number,
                defaults={
                    "make": make,
                    "model": model,
                    "tm_or_b": tm_or_b,
                    "color": color,
                    "status": status,
                    "notes": notes,
                    "vin_number": vin,
                    "year": year,
                    "plate_number": plate,
                    "st": st,
                    "whose_truck": whose,
                    "owner_name": owner,
                    "company": company,
                    "driver_name": driver_name
                }
            )

            # 🔄 Driver
            reg_date = row.get("Registration")
            date_obj = safe_date(reg_date) or datetime.now().date()
            driver_type = "owner" if str(whose).lower() == "owner" else "company"

            if driver_name:
                Driver.objects.get_or_create(
                    full_name=driver_name,
                    truck=truck,
                    company=company,
                    defaults={
                        "mode": "offline",
                        "date": date_obj,
                        "driver_type": driver_type
                    }
                )

            # 🔄 TruckInsurance
            physical_exp = safe_date(row.get("Physical Exp"))
            TruckInsurance.objects.update_or_create(
                truck=truck,
                defaults={
                    "proof_of_ownership": str(row.get("PROOF OF OWNERSHIP")).strip().upper() == "YES",
                    "safety_carrier": str(row.get("SAFETY CARRIER")).strip().upper() == "YES",
                    "liability_and_cargo": str(row.get("Liability and Cargo Insurance")).strip().upper() == "YES",
                    "physical_damage": str(row.get("Physical Damage Ins")).strip().upper() == "YES",
                    "physical_exp": physical_exp,
                    "link": row.get("Link")
                }
            )

            # 🔄 TruckInspection
            TruckInspection.objects.update_or_create(
                truck=truck,
                defaults={
                    "registration": row.get("Registration"),
                    "annual_inspection": row.get("Annual inspection"),
                    "rental_agreement": row.get("Rental Agreement"),
                    "outbound_inspection": row.get("Outbound inspection")
                }
            )

        self.stdout.write(self.style.SUCCESS("✅ Excel'dan Truck va bog‘liq ma'lumotlar import qilindi."))
