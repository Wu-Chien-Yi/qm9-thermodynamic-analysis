import bz2
import json

# --- 另存成.txt檔 ---

# A. 讀取壓縮檔
print("正在解壓縮並轉換格式...")
with bz2.open("qm9_results.json.bz2", "rb") as source:
    data = json.loads(source.read().decode('utf-8'))

# B. 存成 .txt 檔
with open("qm9_results_list.txt", "w", encoding="utf-8") as target:
    # 寫入標題
    target.write(f"{'SMILES':<30} {'Hf (kcal/mol)':>15}\n")
    target.write("-" * 60 + "\n")
    
    # 逐行寫入分子數據
    for item in data:
        line = f"{item['smiles']:<30} {item['Hf']:15.4f}\n"
        target.write(line)

print("✅ 轉換完成！你可以打開 qm9_results_list.txt 檔案了。")