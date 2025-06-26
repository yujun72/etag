import os
import xml.etree.ElementTree as ET
import csv
import re
from collections import defaultdict
from tqdm import tqdm  # ✅ pip install tqdm（顯示進度條）

# ✅ 車種對應加權係數表
VEHICLE_WEIGHT = {
    "31": 1.0,  # 小型車
    "41": 1.5,  # 大型車
    "42": 1.5,
    "51": 1.5,  # 聯結車
    "52": 1.5
}

# ✅ 輸出 CSV 表頭
output_csv = "vdetag_0616_0622_加權統計結果.csv"
fieldnames = ["Date", "TimeGroup", "Start", "End", "WeightedVolume", "WeightedAvgTripTime", "WeightedAvgSpeed"]

with open(output_csv, "w", newline='', encoding='utf-8') as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

# ✅ 分析範圍（6/16～6/22）
base_path = "./"
date_range = ["20250616", "20250617", "20250618", "20250619", "20250620", "20250621", "20250622"]

# ✅ 處理每一天
for date_str in tqdm(date_range, desc="📅 日期處理中"):
    folder_path = os.path.join(base_path, f"etag_{date_str}")
    if not os.path.exists(folder_path):
        print(f"⚠️ 資料夾不存在：{folder_path}")
        continue

    # 暫存統計資料（用 dict groupby）
    stats = defaultdict(lambda: {"volume": 0, "speed_sum": 0, "ttime_sum": 0, "count": 0})

    files = sorted([f for f in os.listdir(folder_path) if f.endswith(".xml")])
    for file in tqdm(files, desc=f"  📂 {date_str} 中處理檔案", leave=False):
        filepath = os.path.join(folder_path, file)
        try:
            tree = ET.parse(filepath)
            root = tree.getroot()
            match = re.search(r"(\d{4})", file)
            time_str = match.group(1) if match else "0000"

            for live in root.findall(".//{*}ETagPairLive"):
                pair_id_elem = live.find(".//{*}ETagPairId")
                pair_id = pair_id_elem.text if pair_id_elem is not None else ""
                start, end = pair_id.split("-") if "-" in pair_id else ("", "")

                for flow in live.findall(".//{*}Flow"):
                    vtype = flow.findtext(".//{*}VehicleType", "")
                    ttime = float(flow.findtext(".//{*}TravelTime", "0"))
                    speed = float(flow.findtext(".//{*}SpaceMeanSpeed", "0"))
                    count = int(flow.findtext(".//{*}VehicleCount", "0"))

                    weight = VEHICLE_WEIGHT.get(vtype, 0)
                    weighted_volume = count * weight

                    key = (date_str, time_str, start, end)
                    stats[key]["volume"] += weighted_volume
                    stats[key]["ttime_sum"] += ttime * count
                    stats[key]["speed_sum"] += speed * count
                    stats[key]["count"] += count

        except Exception as e:
            print(f"⚠️ 無法解析：{filepath}，原因：{e}")

    # ✅ 每天處理完就寫入 CSV
    with open(output_csv, "a", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        for (date, time_str, start, end), val in stats.items():
            cnt = val["count"]
            writer.writerow({
                "Date": date,
                "TimeGroup": time_str,
                "Start": start,
                "End": end,
                "WeightedVolume": round(val["volume"], 1),
                "WeightedAvgTripTime": round(val["ttime_sum"] / cnt, 2) if cnt else 0,
                "WeightedAvgSpeed": round(val["speed_sum"] / cnt, 2) if cnt else 0,
            })

print("✅ 所有加權統計已完成，結果儲存在：", output_csv)
