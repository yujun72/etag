import os
import xml.etree.ElementTree as ET
import csv
import re

def parse_and_append_to_csv(base_path, output_file):
    ns = {"ns": "http://traffic.transportdata.tw/standard/traffic/schema/"}
    
    # 建立 CSV 並寫入表頭
    with open(output_file, "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=[
            "Date", "TimeGroup", "Start", "End", "VehicleType",
            "VehicleCount", "AvgTripTime", "AvgSpeed"
        ])
        writer.writeheader()

    # 逐筆讀取 XML 檔案，並寫入 CSV
    for folder in os.listdir(base_path):
        if folder.startswith("etag_2025"):
            folder_path = os.path.join(base_path, folder)
            date_str = folder.replace("etag_", "")

            for file in os.listdir(folder_path):
                if file.endswith(".xml"):
                    filepath = os.path.join(folder_path, file)
                    try:
                        tree = ET.parse(filepath)
                        root = tree.getroot()
                        match = re.search(r"(\d{4})", file)
                        time_str = match.group(1) if match else "0000"

                        rows = []
                        for live in root.findall(".//ns:ETagPairLive", ns):
                            pair_id_elem = live.find("ns:ETagPairId", ns)
                            pair_id = pair_id_elem.text if pair_id_elem is not None else ""
                            start, end = pair_id.split("-") if "-" in pair_id else ("", "")

                            for flow in live.findall(".//ns:Flow", ns):
                                vtype = flow.findtext("ns:VehicleType", default="", namespaces=ns)
                                ttime = flow.findtext("ns:TravelTime", default="0", namespaces=ns)
                                speed = flow.findtext("ns:SpaceMeanSpeed", default="0", namespaces=ns)
                                count = flow.findtext("ns:VehicleCount", default="0", namespaces=ns)

                                try:
                                    row = {
                                        "Date": date_str,
                                        "TimeGroup": time_str,
                                        "Start": start,
                                        "End": end,
                                        "VehicleType": vtype,
                                        "VehicleCount": int(count),
                                        "AvgTripTime": float(ttime),
                                        "AvgSpeed": float(speed)
                                    }
                                    rows.append(row)
                                except:
                                    continue
                        
                        # 每讀完一個檔案就寫一次
                        if rows:
                            with open(output_file, "a", newline='', encoding='utf-8') as f:
                                writer = csv.DictWriter(f, fieldnames=rows[0].keys())
                                writer.writerows(rows)
                            print(f"✅ 已寫入：{filepath}")

                    except Exception as e:
                        print(f"⚠️ 無法解析：{filepath}，原因：{e}")

    print("🎉 所有資料已寫入 CSV 完成")

# 📌 設定資料夾與輸出檔名
base_path = "./"  # 這是你存放 etag_2025xxxx 資料夾的地方
output_csv = "eTag_逐筆統計_不吃記憶體.csv"

# 執行程式
parse_and_append_to_csv(base_path, output_csv)
