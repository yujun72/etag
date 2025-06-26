import os
import requests
from datetime import datetime, timedelta

# 設定起始與結束日期（你要的年份）
start_date = datetime.strptime("20250501", "%Y%m%d")
end_date = datetime.strptime("20250512", "%Y%m%d")

# 主迴圈：一天一資料夾
current_date = start_date
while current_date <= end_date:
    date_str = current_date.strftime("%Y%m%d")
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
                    print(f"✅ {date_str} 已下載：{filename}")
                else:
                    print(f"⚠️ {date_str} 檔案不存在：{filename}（HTTP {r.status_code}）")
            except Exception as e:
                print(f"❌ 錯誤：{date_str} {filename}，錯誤原因：{e}")
    
    current_date += timedelta(days=1)

print("🎉 全年份下載完成")
