import os
import gzip
import shutil

# 設定你的資料夾路徑（這邊以 etag_20250616 ~ etag_20250622 為例）
base_path = "./"  # 或換成你實際的路徑

for folder in os.listdir(base_path):
    if folder.startswith("etag_202505"):
        folder_path = os.path.join(base_path, folder)
        print(f"📂 解壓中：{folder}")
        for file in os.listdir(folder_path):
            if file.endswith(".xml.gz"):
                gz_path = os.path.join(folder_path, file)
                xml_path = os.path.join(folder_path, file.replace(".gz", ""))
                with gzip.open(gz_path, 'rb') as f_in:
                    with open(xml_path, 'wb') as f_out:
                        shutil.copyfileobj(f_in, f_out)
                print(f"✅ 解壓完成：{file}")
