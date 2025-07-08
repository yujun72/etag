import os

# 設定根資料夾（包含 etag_2025xxxx 資料夾的路徑）
base_path = "./"

# 逐一搜尋所有 etag_2025 開頭的資料夾
for folder in os.listdir(base_path):
    if folder.startswith("vd_202506"):
        folder_path = os.path.join(base_path, folder)
        for file in os.listdir(folder_path):
            if file.endswith(".xml.gz"):
                file_path = os.path.join(folder_path, file)
                try:
                    os.remove(file_path)
                    print(f"🗑 已刪除：{file_path}")
                except Exception as e:
                    print(f"⚠️ 刪除失敗：{file_path}，錯誤原因：{e}")

print("✅ 所有 .xml.gz 壓縮檔已清除完畢")
