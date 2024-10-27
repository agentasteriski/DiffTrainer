![DiffTrainer](https://github.com/agentasteriski/DiffTrainer/blob/main/assets/difftrainerlogo.png?raw=true)

# 多辭典測試版
非常粗糙。已知問題：
- 甚至不確定我們做得對嗎
- langloader 編輯器通常隱藏在主視窗後面


*[English](./README.md)* **中文（正體）**

⚠中文版本的自述文件内容并不一定是最新的並且可能存在有翻譯的錯誤，如果中文版本與英文原版有什麽出入的話以英文原版爲準

# 用於處理和訓練 DiffSinger 模型的 CustomTkInter GUI
DiffTrainer 將 DiffSinger 最有用的工具整合到一個簡單的圖形包中。
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) 用於將 wav+lab 資料轉換為 wav/ds+csv
- [SOME](https://github.com/openvpi/SOME) 用於估計音調
- [DiffSinger](https://github.com/openvpi/DiffSinger)的基礎訓練功能
- OpenUtau匯出腳本
## 安裝選項
### 如果你從未用過Python：
- 執行 conda_installer.bat
- 之後使用 run_gui.bat 啟動

### 如果你用過Python：
- DiffTrainer 預設使用 Miniconda 來管理衝突的套件要求。
- 要使用現有的 conda 安裝：
  - 將requirements.txt安裝到基礎環境
  - 執行setup_conda_envs.py來配置所需的環境
- 從 v0.2.1 開始，環境名稱是硬編碼要求。

## 語言支持
DiffTrainer 使用 [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) 來允許 GUI 語言選擇。 歡迎所有使用者將 [en_US](/strings/en_US.yaml) 中找到的文字翻譯為其他語言並提交拉取請求。

## 待辦事項
很快
- 更好的自述文件

最終
- 高級匯出
- 更多翻譯
- 一個不 amogus 的圖標
