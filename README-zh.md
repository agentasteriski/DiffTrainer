![DiffTrainer](https://github.com/agentasteriski/DiffTrainer/blob/main/assets/difftrainerlogo.png?raw=true)

# 多辭典測試版
非常粗糙。已知問題：
- 甚至不確定我們做得對嗎
- langloader 編輯器通常隱藏在主視窗後面
- 老實說 langloader 又醜又糟糕
- 如果您載入一個資料集，然後改變主意並載入另一個資料集，則無法寫入配置


*[English](./README.md)* **中文（正體）**

⚠中文版本的自述文件内容并不一定是最新的並且可能存在有翻譯的錯誤，如果中文版本與英文原版有什麽出入的話以英文原版爲準

# 用於處理和訓練 DiffSinger 模型的 CustomTkInter GUI
DiffTrainer 將 DiffSinger 最有用的工具整合到一個簡單的圖形包中。
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) 用於將 wav+lab 資料轉換為 wav/ds+csv
- [SOME](https://github.com/openvpi/SOME) 用於估計音調
- [DiffSinger](https://github.com/openvpi/DiffSinger)的基礎訓練功能
- OpenUtau匯出腳本
## 安裝選項
### 如果您有 NVIDIA GPU：
- 確保安裝了相容版本的 [CUDA Toolkit](https://developer.nvidia.com/cuda-11-8-0-download-archive)
  - 目前相容版本：11.8、12.1、12.4、12.6
- 繼續下一個“如果”

### 如果你從未用過Python：
- 執行 conda_installer.bat
- 在 DiffTrainer 上運行一次“更新工具”
- 之後使用 run_gui.bat 啟動

### 如果你用過Python：
- DiffTrainer 預設使用 Miniconda 來管理衝突的套件要求。
- 要使用現有的 conda 安裝：
  - 將requirements.txt安裝到基礎環境（強烈建議 3.10，其他版本可能仍適用於基礎環境）
  - 執行setup_conda_envs.py來配置所需的環境
  - 選擇第一個選項卡上的“更新工具”以完成安裝
- 從 v0.2.1 開始，環境名稱是硬編碼要求。

已知問題：
- langloader 編輯器通常隱藏在主視窗後面
- ~~說實話，langloader 實在太醜太糟了~~ 已從 0.3.14（2025 年 1 月 16 日）開始改進
- 如果您在儲存間隔或批次大小方塊中輸入，終端機視窗中會出現錯誤
- 沒有實際影響，只需輸入您的數字並忽略它
- 如果您載入了一個資料集，然後改變主意並載入了另一個資料集，則無法寫入配置
- 不要將檢查點資料夾命名為“acoustic”或“variance”，這會與 onnx 匯出清理衝突
- （僅限 Linux）如果文字和按鈕出現鋸齒狀：
- 在基礎環境中，`conda install --channel=conda-forge tk[build=xft_*]`
- （僅限 Mac）依賴項 `libcs​​t` 的依賴項不再針對 x86 打包
- 在執行 setup_conda_envs.py 之前，將 `libcs​​` 添加到 environmentA/B.yml 的上半部（不確定這是否會繼續工作或舊版本有什麼其他影響）

## 語言支持
DiffTrainer 使用 [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) 來允許 GUI 語言選擇。 歡迎所有使用者將 [en_US](/strings/en_US.yaml) 中找到的文字翻譯為其他語言並提交拉取請求。

## 待辦事項
很快
- 更好的自述文件

最終
- ~~高級匯出~~
- 更多翻譯
- ~~一個不 amogus 的圖標~~
