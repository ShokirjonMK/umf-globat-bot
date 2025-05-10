import pandas as pd

def download_sheet_to_excel(csv_url: str, output_path: str = "trucks.xlsx"):
    """
    Google Sheets'dan CSV formatida yuklab olib, Excel faylga saqlaydi.

    :param csv_url: Google Sheets'dan export qilingan CSV havola
    :param output_path: Saqlanadigan Excel fayl nomi
    """
    try:
        print(f"📥 Ma'lumot yuklanmoqda: {csv_url}")
        df = pd.read_csv(csv_url)
        df.to_excel(output_path, index=False)
        print(f"✅ Excel fayl saqlandi: {output_path}")
    except Exception as e:
        print(f"❌ Xatolik yuz berdi: {e}")

# Misol uchun chaqirish:
if __name__ == "__main__":
    url = "https://docs.google.com/spreadsheets/d/1w1dvleB--83DaNHMoyp6dswHtwgWL2yqZKe6hzl9sOo/export?format=csv&gid=1603469063"
    download_sheet_to_excel(url, "trucks.xlsx")
