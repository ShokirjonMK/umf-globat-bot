import pandas as pd
import json
import warnings
from datetime import datetime, time

def convert_trucks_sheet_to_json(excel_path: str, json_path: str):
    """
    Excel fayldan faqat 'Trucks' varaqni o'qib, JSON formatga o'giradi.
    Sana, vaqt va NaN qiymatlarni stringga yoki nullga o'giradi.
    """
    try:
        warnings.simplefilter("ignore", UserWarning)
        df = pd.read_excel(excel_path, sheet_name='Trucks', dtype=object)
        df.columns = df.columns.map(str)

        # Sana, vaqt va NaN qiymatlarni stringga aylantirish
        for col in df.columns:
            df[col] = df[col].apply(lambda x:
                x.isoformat() if isinstance(x, (datetime, time)) else
                None if pd.isna(x) else x
            )

        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(df.to_dict(orient='records'), f, indent=4, ensure_ascii=False)

        print(f"✅ 'Trucks' sahifa JSON ga saqlandi: {json_path}")

    except Exception as e:
        print(f"❌ Xatolik: {e}")



convert_trucks_sheet_to_json("Fleet Management.xlsx", "fleet.json")
