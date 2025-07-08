import os
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

# ✅ 權重設定（S:小車=1.0, L:大車=1.5, T:聯結車=1.5）
VEHICLE_WEIGHT = {"S": 1.0, "L": 1.5, "T": 1.5}

# ✅ 設定檔案資料夾 & 日期（檔名會用到）
folder = "vd_20250616"
target_date = "20250616"

# ✅ 自動產生全天每 5 分鐘的時間點（共 288 筆）
time_points = [f"{h:02d}{m:02d}" for h in range(24) for m in range(0, 60, 5)]
file_list = [f"VDLive_{t}.xml" for t in time_points]

# ✅ 命名空間
ns = {"ns": "http://traffic.transportdata.tw/standard/traffic/schema/"}
records = []

# ✅ 開始分析
for file in tqdm(file_list, desc="📂 分析全天每 5 分鐘資料"):
    path = os.path.join(folder, file)
    if not os.path.exists(path):
        print(f"⚠️ 檔案不存在：{file}")
        continue

    try:
        tree = ET.parse(path)
        root = tree.getroot()

        # ✅ 解析時間來自檔名（每 5 分鐘一筆）
        collect_time = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:]} {file[7:9]}:{file[9:11]}:00"

        for live in root.findall(".//ns:VDLive", ns):
            vdid = live.find("ns:VDID", ns).text
            status = live.find("ns:status", ns).text

            for flow in live.findall(".//ns:LinkFlow", ns):
                linkid = flow.find("ns:LinkID", ns).text
                for lane in flow.findall(".//ns:Lane", ns):
                    laneid = lane.find("ns:LaneID", ns).text
                    lanetype = lane.find("ns:LaneType", ns).text
                    speed2 = float(lane.find("ns:Speed", ns).text)
                    occupancy = float(lane.find("ns:Occupancy", ns).text)

                    for vehicle in lane.findall(".//ns:Vehicle", ns):
                        vtype = vehicle.find("ns:VehicleType", ns).text
                        volume = int(vehicle.find("ns:Volume", ns).text)
                        speed = float(vehicle.find("ns:Speed", ns).text)

                        weight = VEHICLE_WEIGHT.get(vtype, 0)
                        weighted = volume * weight

                        records.append({
                            "DataCollectTime": collect_time,
                            "VDID": vdid,
                            "LinkID": linkid,
                            "LaneID": laneid,
                            "LaneType": lanetype,
                            "VehicleType": vtype,
                            "Volume": volume,
                            "Speed": speed,
                            "Speed2": speed2,
                            "Occupancy": occupancy,
                            "Status": status,
                            "WeightedVolume": weighted
                        })
    except Exception as e:
        print(f"❌ 錯誤於 {file}: {e}")
        continue

# ✅ 轉成 DataFrame
df = pd.DataFrame(records)
df.to_csv(f"VD_原始_{target_date}.csv", index=False, encoding="utf-8-sig")

# ✅ 彙總：每 5 分鐘的加權平均
summary = df.groupby("DataCollectTime").agg({
    "WeightedVolume": "sum",
    "Speed": lambda x: (x * df.loc[x.index, "WeightedVolume"]).sum() / df.loc[x.index, "WeightedVolume"].sum(),
    "Speed2": lambda x: (x * df.loc[x.index, "WeightedVolume"]).sum() / df.loc[x.index, "WeightedVolume"].sum()
}).reset_index()

summary.rename(columns={
    "WeightedVolume": "TotalWeightedVolume",
    "Speed": "WeightedAvgSpeed",
    "Speed2": "WeightedAvgSpeed2"
}, inplace=True)

summary.to_csv(f"VD_彙總_{target_date}.csv", index=False, encoding="utf-8-sig")

print(f"✅ 匯出完成：VD_原始_{target_date}.csv")
print(f"✅ 匯出完成：VD_彙總_{target_date}.csv")
