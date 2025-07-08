import os, requests, gzip, shutil
from tqdm import tqdm
from bs4 import BeautifulSoup

# ✅ 欲抓取的一週日期（自行指定）
dates = ["20250621"]

# ✅ 每 5 分鐘一筆的時間點（共 288 筆）
valid_times = [f"{h:02d}{m:02d}" for h in range(24) for m in range(0, 60, 5)]

for date in dates:
    base_url = f"https://tisvcloud.freeway.gov.tw/history/motc20/VD/{date}/"
    folder = f"vd_{date}"
    os.makedirs(folder, exist_ok=True)

    print(f"\n📅 處理日期：{date}")

    # 🔍 抓出當天所有 .gz 檔案連結
    try:
        r = requests.get(base_url, timeout=20)
        r.raise_for_status()
    except Exception as e:
        print(f"❌ 無法連線：{base_url}，錯誤：{e}")
        continue

    soup = BeautifulSoup(r.text, "html.parser")
    all_files = [a["href"] for a in soup.find_all("a") if a["href"].endswith(".xml.gz")]
    gz_files = [f for f in all_files if f[7:11] in valid_times]

    print(f"🔍 找到 {len(gz_files)} 筆每 5 分鐘檔案")

    # ⬇ 下載 .gz
    for name in tqdm(gz_files, desc=f"⬇ 下載 {date}"):
        url = base_url + name
        path = os.path.join(folder, name)
        if not os.path.exists(path):
            try:
                r = requests.get(url, timeout=10)
                if r.status_code == 200:
                    with open(path, "wb") as f:
                        f.write(r.content)
            except Exception as e:
                print(f"⚠️ 下載失敗 {name}: {e}")

    # 🗜 解壓 .gz → .xml
    for file in os.listdir(folder):
        if file.endswith(".gz"):
            gz_path = os.path.join(folder, file)
            xml_path = gz_path[:-3]
            if not os.path.exists(xml_path):
                try:
                    with gzip.open(gz_path, "rb") as f_in, open(xml_path, "wb") as f_out:
                        shutil.copyfileobj(f_in, f_out)
                except Exception as e:
                    print(f"⚠️ 解壓失敗 {file}: {e}")

print("\n✅ 所有日期資料下載與解壓完成！")
