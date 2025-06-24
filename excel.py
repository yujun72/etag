import os
import xml.etree.ElementTree as ET
import pandas as pd
import re

def parse_etag_folder(folder_path):
    ns = {"ns": "http://traffic.transportdata.tw/standard/traffic/schema/"}
    records = []

    for file in os.listdir(folder_path):
        if file.endswith(".xml"):
            filepath = os.path.join(folder_path, file)
            tree = ET.parse(filepath)
            root = tree.getroot()

            # 時間從檔名推斷
            match = re.search(r"(\d{4})", file)
            time_str = match.group(1) if match else "0000"

            for live in root.findall(".//ns:ETagPairLive", ns):
                pair_id = live.find("ns:ETagPairId", ns).text
                start, end = pair_id.split("-") if "-" in pair_id else ("", "")

                for flow in live.findall(".//ns:Flow", ns):
                    vtype = flow.findtext("ns:VehicleType", "", namespaces=ns)
                    ttime = float(flow.findtext("ns:TravelTime", "0", namespaces=ns))
                    speed = float(flow.findtext("ns:SpaceMeanSpeed", "0", namespaces=ns))
                    count = int(flow.findtext("ns:VehicleCount", "0", namespaces=ns))

                    records.append({
                        "TimeGroup": time_str,
                        "Start": start,
                        "End": end,
                        "VehicleType": vtype,
                        "VehicleCount": count,
                        "AvgTripTime": ttime,
                        "AvgSpeed": speed,
                    })
    return pd.DataFrame(records)

# 修改成你的資料夾路徑
df = parse_etag_folder("etag_20250616")

# 每 5 分鐘統計：依 Start+End+TimeGroup，加總車數、計算加權平均行駛時間與速度
summary = df.groupby(["TimeGroup", "Start", "End"]).apply(
    lambda g: pd.Series({
        "TotalVehicleCount": g["VehicleCount"].sum(),
        "WeightedAvgTripTime": (g["AvgTripTime"] * g["VehicleCount"]).sum() / g["VehicleCount"].sum() if g["VehicleCount"].sum() > 0 else 0,
        "WeightedAvgSpeed": (g["AvgSpeed"] * g["VehicleCount"]).sum() / g["VehicleCount"].sum() if g["VehicleCount"].sum() > 0 else 0
    })
).reset_index()

# 儲存成 Excel
summary.to_excel("etag統計結果.xlsx", index=False)
print("✅ 匯出完成：etag統計結果.xlsx")
