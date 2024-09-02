# [重要更新資訊](https://github.com/agentasteriski/DiffTrainer/blob/main/ANNOUNCEMENT-zh.md)
![DiffTrainer](https://github.com/agentasteriski/DiffTrainer/blob/main/assets/difftrainerlogo.png?raw=true)

*[English](./README.md)* **中文（正體）**

⚠中文版本的自述文件内容并不一定是最新的並且可能存在有翻譯的錯誤，如果中文版本與英文原版有什麽出入的話以英文原版爲準

# 用於處理和訓練 DiffSinger 模型的 CustomTkInter GUI
DiffTrainer 將 DiffSinger 最有用的工具整合到一個簡單的圖形包中。
- [nnsvs-db-converter](https://github.com/UtaUtaUtau/nnsvs-db-converter) 用於將 wav+lab 資料轉換為 wav/ds+csv
- [DiffSinger](https://github.com/openvpi/DiffSinger)的基礎訓練功能
- OpenUtau匯出腳本
## 安裝選項
### 如果你從未用過Python：
- 執行 conda_installer.bat
- 執行 setup.bat
- 使用 run_guiA.bat 進行預處理和訓練
- 使用 run_guiB.bat 匯出 onnx

### 如果你用過Python：
- DiffTrainer 預設使用 Miniconda 來管理衝突的套件要求。
- 要使用現有的 conda 安裝：
 - 執行setup.bat自動建立所需的環境
 - 或使用 /assets/ 中的需求文件建立兩個環境
 - 在一個中執行 torchdropA.py，在另一個中執行 torchdropB.py
 - run_guiA.bat 和 run_guiB.bat 分別在環境 DifftrainerA 和 DifftrainerB 中啟動 Difftrainer

## 語言支持
DiffTrainer 使用 [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) 來允許 GUI 語言選擇。 歡迎所有使用者將 [en_US](/strings/en_US.yaml) 中找到的文字翻譯為其他語言並提交拉取請求。

## 待辦事項
很快
- 更好的自述文件

最終
- 完全支持 .ds 訓練
- 高級匯出
- 更多翻譯
- 一個不 amogus 的圖標
