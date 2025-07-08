import os
import xml.etree.ElementTree as ET
import pandas as pd
from tqdm import tqdm

# ✅ 權重設定
VEHICLE_WEIGHT = {"S": 1.0, "L": 1.5, "T": 1.5}

# ✅ 目標日期清單（依照你的資料夾命名）
dates = ["20250616", "20250617", "20250618", "20250619", "20250620", "20250621", "20250622"]
base_folder = "."  # ← 資料夾就在目前目錄下

# ✅ 命名空間
ns = {"ns": "http://traffic.transportdata.tw/standard/traffic/schema/"}

# ✅ 收集所有紀錄
records = []

# ✅ 開始處理每一天
for target_date in dates:
    folder = os.path.join(base_folder, f"vd_{target_date}")
    time_points = [f"{h:02d}{m:02d}" for h in range(24) for m in range(0, 60, 5)]
    file_list = [f"VDLive_{t}.xml" for t in time_points]

    print(f"\n📅 處理日期：{target_date}")
    for file in tqdm(file_list, desc=f"📂 讀取 {target_date}"):
        path = os.path.join(folder, file)
        if not os.path.exists(path):
            continue

        try:
            tree = ET.parse(path)
            root = tree.getroot()

            # ⏰ 解析時間來自檔名
            collect_time = f"{target_date[:4]}-{target_date[4:6]}-{target_date[6:]} {file[7:9]}:{file[9:11]}:00"

            for live in root.findall(".//ns:VDLive", ns):
                vdid = live.findtext("ns:VDID", "", ns)
                status = live.findtext("ns:status", "", ns)

                for flow in live.findall(".//ns:LinkFlow", ns):
                    linkid = flow.findtext("ns:LinkID", "", ns)
                    for lane in flow.findall(".//ns:Lane", ns):
                        laneid = lane.findtext("ns:LaneID", "", ns)
                        lanetype = lane.findtext("ns:LaneType", "", ns)
                        try:
                            speed2 = float(lane.findtext("ns:Speed", "0", ns))
                            occupancy = float(lane.findtext("ns:Occupancy", "0", ns))
                        except:
                            continue  # 跳過有問題資料

                        for vehicle in lane.findall(".//ns:Vehicle", ns):
                            vtype = vehicle.findtext("ns:VehicleType", "", ns)
                            try:
                                volume = int(vehicle.findtext("ns:Volume", "0", ns))
                                speed = float(vehicle.findtext("ns:Speed", "0", ns))
                            except:
                                continue
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
            print(f"⚠️ 解析錯誤於 {file}：{e}")
            continue

# ✅ 建立 DataFrame
df = pd.DataFrame(records)
print("\n📋 欄位：", df.columns.tolist())
print("🧮 總筆數：", len(df))

# ✅ 輸出原始檔
df.to_csv("VD_原始_整週.csv", index=False, encoding="utf-8-sig")

# ✅ 彙總統計（每 5 分鐘）
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

summary.to_csv("VD_彙總_整週.csv", index=False, encoding="utf-8-sig")

print("\n✅ 完成！已輸出：VD_原始_整週.csv 與 VD_彙總_整週.csv")
