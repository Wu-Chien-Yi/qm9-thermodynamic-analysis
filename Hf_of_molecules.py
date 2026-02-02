import os
import glob
import bz2
import json
import time
from tqdm import tqdm

#開始時間記錄點
start_time = time.time() 

# --- 0.定義轉換因子 ---
Hartree_to_kcal_mol = 627.5095
kJ_to_kcal = 1/4.184

#建立 H_atom_Hartree 字典，儲存298.15K下的H_atom
H_atom_Hartree = {
    "H": -0.497912,
    "C": -37.844411,
    "N": -54.581501,
    "O": -75.062219,
    "F": -99.716370
}

# 建立新字典儲存單位轉換後的 H_atom_kcal_mol
# H_atom_kcal_mol = {k: v * Hartree_to_kcal_mol for k, v in H_atom_Hartree.items()}

# --- 1.讀取壓縮檔、解壓縮，尋找並條列檔案 ---
folder_path = "dsgdb9nsd.xyz"

# glob.glob 會去資料夾裡把所有結尾是 .xyz 的檔案路徑都抓出來，存成一個清單 (List)
# os.path.join 則是確保路徑在 Linux/Windows 下都能正確拼接
file_list = sorted(glob.glob(os.path.join(folder_path, "*.xyz")))

if not file_list:
    print(f"找不到資料夾：{folder_path} 或資料夾內無 .xyz 檔案")
    print("請檢查資料夾名稱是否正確，或使用 'ls' 指令確認。")
else:
    print(f"找到 {len(file_list)} 個分子檔案。")
    # print(f"{'SMILES':<40} | {'Hf (kcal/mol)':>15}")
    # print("-" * 60)


# --- 2.用for迴圈重複讀取每個分子檔案（.txt檔），把裡面每一行都存成一個list，命名為line ---
results = [] #開result陣列

for file_path in tqdm(file_list, desc="計算中", unit="mol"): # 所有檔案都下去跑
    try:  
        with open(file_path, 'r') as f:
            lines = f.readlines() # read那個檔案，每一行存成list
            
        # 解析數據
        na = int(lines[0].strip()) # 檔案的第 1 行，strip把換行符號和多餘的空白刪掉，int轉成整數，這樣才可以給 for 迴圈計數
        properties = lines[1].split() # 檔案的第 2 行，所有的properties，用空格分隔
        H_molecule_Hartree = float(properties[14]) # property 的第十五個
        
        # 統計分子內的原子數量
        number_of_atom = {"H": 0, "C": 0, "N": 0, "O": 0, "F": 0}
        for i in range(2, na + 2):
            atom_symbol = lines[i].split()[0] # 取第i行用空格隔開後的第[0]個字串作為 atom_symbol
            if atom_symbol in number_of_atom: # 如果在 number_of_atom 這個字典裏面有這個 atom_symbol
                number_of_atom[atom_symbol] += 1 # 就在字典裡面+1
                
        # 抓取 SMILES (第 na+4 行，索引為 na+3)
        smiles = lines[na + 3].split()[0] # 有些檔案 SMILES 後面會有別的字，用 split()[0] 最保險

# --- 3.計算生成熱 ---

# A. 所有原子的 H 總和 in kcal/mol
        sum_H_atom_Hartree = sum(number_of_atom[a] * H_atom_Hartree[a] for a in number_of_atom)
    
# B. 298.15K 下元素從標準狀態生成此分子的生成熱 \Delta H (in Hartree)
        delta_H_Hartree = H_molecule_Hartree - sum_H_atom_Hartree
        delta_H_kcal_mol = delta_H_Hartree * Hartree_to_kcal_mol # 轉換成kcal/mol

# C. 建立氣態原子H字典
#原子化熱（Heat of Atomization）是指在標準狀態下，將 1 莫耳物質（如固態金屬、分子晶體）完全拆解為孤立氣態原子所需吸收的熱量
        H_gas_atom_kJ_mol = { "H":218.00 , "C":716.68, "N":472.68 , "O":249.18 , "F":79.38  } #Ref.NIST
        H_gas_atom_kcal_mol = {k: v * kJ_to_kcal for k, v in H_gas_atom_kJ_mol.items()} #kJ -> kcal轉換

#氣態原子H總和 = H_corr_kcal_mol
        H_corr_kcal_mol = sum(number_of_atom[a] * H_gas_atom_kcal_mol[a] for a in number_of_atom)
      
# D.生成熱Hf = delta_H_kcal_mol + H_corr_kcal_mol
        Hf = delta_H_kcal_mol + H_corr_kcal_mol

# E.把SMILES跟Hf存起來不print
        results.append({"smiles": smiles, "Hf": Hf})

    except Exception as e:
        # 如果某個檔案壞掉，記錄下來但不中斷程式
        continue
    
    
# --- 4. 將結果存成壓縮檔 (bz2) ---
print(f"\n 正在寫入壓縮檔 qm9_all_results.json.bz2 ...")
with bz2.open("qm9_results.json.bz2", "wb") as f:
    f.write(json.dumps(results).encode('utf-8'))
print(f"\n 處理完成，所有結果已存入 qm9_results.json.bz2")

# --- 5. 看一下時間總長 ---
print(f" 全部完成總耗時: {time.time() - start_time:.2f} 秒")


