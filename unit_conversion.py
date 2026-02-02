#建立字典儲存298.15K下的H_atom

H_atom_Hartree = {
    "H": -0.497912,
    "C": -37.844411,
    "N": -54.581501,
    "O": -75.062219,
    "F": -99.716370
}

# 定義轉換因子
Hartree_to_kcal_mol = 627.5095

# 建立新字典儲存單位轉換後的H_atom_kcal_mol
# 這裡使用字典推導式，遍歷舊字典的 key (k) 和 value (v)
H_atom_kcal_mol = {k: v * Hartree_to_kcal_mol for k, v in H_atom_Hartree.items()}

# 打印結果
print("--- 轉換結果 (kcal/mol) ---")
for atom, energy in H_atom_kcal_mol.items(): #atom,energy 分別命名dict的key,value
    print(f"{atom}: {energy:.4f} kcal/mol")