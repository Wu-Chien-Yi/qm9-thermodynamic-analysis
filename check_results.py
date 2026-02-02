import pandas as pd
import bz2
import json

# 1. 載入全量數據
with bz2.open("qm9_results.json.bz2", "rb") as f:
    data = json.loads(f.read().decode('utf-8'))

df = pd.DataFrame(data) #轉換成 Pandas 表格

# 2. 顯示基本統計資訊 (數量、平均、標準差、最小、最大)
print("--- 13 萬筆分子數據統計 ---")
print(df.describe())

# 3. 找出最穩定與最不穩定的分子
print("\n--- 熱力學極端分子 ---")
print("🔥 生成熱最高 (最不穩定):")
print(df.nlargest(1, 'Hf'))

print("\n❄️ 生成熱最低 (最穩定):")
print(df.nsmallest(1, 'Hf'))