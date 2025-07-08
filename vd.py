import os, requests, gzip, shutil
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from bs4 import BeautifulSoup

# 🔧 設定日期（YYYYMMDD）
target_date = "20250616"
base_url = f"https://tisvcloud.freeway.gov.tw/history/motc20/VD/{target_date}/"
folder = f"vd_{target_date}"
os.makedirs(folder, exist_ok=True)

# 🚗 車型加權設定
VEHICLE_WEIGHT = {"S": 1.0, "L": 1.5, "T": 1.5}

# 🔍 抓出網頁上可下載的 .gz 檔案
try:
    r = requests.get(base_url, timeout=20)
    r.raise_for_status()
except Exception as e:
    print(f"❌ 無法連線網站：{e}")
    exit()

soup = BeautifulSoup(r.text, "html.parser")
gz_files = [a["href"] for a in soup.find_all("a") if a["href"].endswith(".xml.gz")]
print(f"📂 找到 {len(gz_files)} 筆檔案")

# ⬇ 下載所有 .gz
for name in tqdm(gz_files, desc="下載檔案"):
    url = base_url + name
    path = os.path.join(folder, name)
    if not os.path.exists(path):
        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(path, "wb") as f:
                    f.write(r.content)
        except:
            continue

# 📂 解壓所有 .gz → .xml
for file in os.listdir(folder):
    if file.endswith(".gz"):
        gz_path = os.path.join(folder, file)
        xml_path = gz_path[:-3]
        if not os.path.exists(xml_path):
            try:
                with gzip.open(gz_path, "rb") as f_in, open(xml_path, "wb") as f_out:
                    shutil.copyfileobj(f_in, f_out)
            except:
                pass

# 🔍 命名空間
#ns = {"vd": "http://traffic.device/VDLive.xsd"}
#records = []
