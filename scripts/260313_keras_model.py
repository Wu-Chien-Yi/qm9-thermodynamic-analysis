# https://keras.io/guides/functional_api/

import numpy as np
import keras
from keras import layers
import os
from keras.callbacks import ModelCheckpoint
from tensorflow.keras.callbacks import EarlyStopping

# 取得這支腳本 (keras_model.py) 的絕對路徑
current_dir = os.path.dirname(os.path.abspath(__file__))

# 定義資料夾路徑 (往上一層再進到 data)
data_path = os.path.join(current_dir, "..", "data")
print(f"📂 正在搜尋資料夾: {os.path.abspath(data_path)}")

# 讀取檔案
X_train = np.load(os.path.join(data_path, 'train_X.npy'))
X_test = np.load(os.path.join(data_path, 'test_X.npy'))
y_train = np.load(os.path.join(data_path, 'train_y.npy'))
y_test = np.load(os.path.join(data_path, 'test_y.npy'))

print("✅ 資料讀取成功！")

# 2. 定義模型架構
inputs = keras.Input(shape=(512,)) #input層
# 隱藏層
x = layers.Dense(50, activation='tanh')(inputs)
# 輸出層：必須是一個神經元，用來預測 Heat of Formation 數值
outputs = layers.Dense(1)(x) 

model = keras.Model(inputs=inputs, outputs=outputs, name="qm9_model") # 建立好model了

# 3. 編譯模型 (Compile)
# loss: 損失函數，預測數值（迴歸）常用 'mse' (均方誤差) 或 'mae' (平均絕對誤差)
model.compile(
    loss='mse',
    metrics=['mae'] # 平均絕對誤差
)

model.summary()

# 4. 開始訓練 (Fit)
print("\n開始訓練模型...")

checkpoint = ModelCheckpoint("../lab_ex1/data/qm9_model.keras", 
                              monitor="val_loss",
                              verbose=0, 
                              save_best_only=True, 
                              save_weights_only=False, 
                              mode='auto', 
                              save_freq='epoch')

early = keras.callbacks.EarlyStopping(
    monitor="val_loss", # 要監控的評估指標
    min_delta=0, #最小變化值，當評估指標的變化小於此值表示沒有改善
    patience=5, #耐心值，設定模型經過多少週期沒有改善就停止訓練
    verbose=1, #輸出模式，設定 `1` 會顯示 `Early Stopping` 相關訊息
    mode="auto", # 監控評估指標變化方向，預設為 `auto` （自動判斷），依據是損失值（通常看最小值）或是準確度（通常看最大值）來選擇 `min` 或 `max`
    baseline=None, # 基準線，可以設定一個數值，會依據 `monitor` 設定的評估指標，若沒有達到設定數值會停止訓練
    restore_best_weights=False, #若設定為 `True`，在訓練結束時會回復到訓練過程中表現最佳的權重
    start_from_epoch=0, #設定第幾個週期開始使用 `EarlyStopping`
)

history = model.fit(
    X_train, y_train,
    batch_size=32,      # 每次看 32 筆資料就更新一次參數，測試集筆數大約是 13,400 筆(10%)，13400/32 = 418.75，所以測試集是419筆；training 集約 120,496 筆，20%做成validation set
    epochs=50,          # 所有的資料輪完 50 遍
    validation_split=0.2, # 從訓練集中抽 20% 出來當作 validation
    callbacks=[checkpoint, early]
)

# 5. 在測試集上評估 (Evaluate)
print("\n正在測試集上評估效能...")
test_results = model.evaluate(X_test, y_test)
print(f"測試集 MAE: {test_results[1]}")


'''
畫 epoch-loss 圖

import matplotlib.pyplot as plt

# 1. 提取 history 物件中的數據
# history.history 是一個字典，存有 'loss', 'mae', 'val_loss', 'val_mae'
train_mae = history.history['mae']
val_mae = history.history['val_mae']
epochs = range(1, len(train_mae) + 1)

# 2. 開始繪圖
plt.figure(figsize=(10, 6))

# 繪製訓練集 MAE
plt.plot(epochs, train_mae, 'bo-', label='Training MAE')
# 繪製驗證集 MAE
plt.plot(epochs, val_mae, 'ro-', label='Validation MAE')

# 3. 設定圖表細節
plt.title('Training and Validation MAE')
plt.xlabel('Epochs')
plt.ylabel('Mean Absolute Error (MAE)')
plt.legend()
plt.grid(True)

# 4. 顯示圖片 (如果你在遠端伺服器執行，請改用 plt.savefig('loss_plot.png'))
plt.show()

'''

# 將模型儲存為 Keras 標準格式
model.save('../lab_ex1/data/qm9_model.keras')
print("💾 模型已成功存檔於 data 資料夾！")