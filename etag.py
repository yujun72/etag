import os
import requests

# ✅ 正確格式：ETag + 檔名中包含 Live
date_str = "20250622"
output_folder = f"etag_{date_str}"
os.makedirs(output_folder, exist_ok=True)

for hour in range(24):
    for minute in range(0, 60, 5):
        time_str = f"{hour:02d}{minute:02d}"
        filename = f"ETagPairLive_{time_str}.xml.gz"
        url = f"https://tisvcloud.freeway.gov.tw/history/motc20/ETag/{date_str}/{filename}"

        save_path = os.path.join(output_folder, filename)

        try:
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(save_path, 'wb') as f:
                    f.write(r.content)
                print(f"✅ 已下載：{filename}")
            else:
                print(f"⚠️ 檔案不存在：{filename}（HTTP {r.status_code}）")
        except Exception as e:
            print(f"❌ 錯誤：{filename}，錯誤原因：{e}")

print("🎉 單日下載完成")
