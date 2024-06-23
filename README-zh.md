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
- 執行 python_installer.bat ，完成安裝程序
- 執行 setup.bat
- 之後使用 run_gui.bat 啟動

### 如果你用過Python：
- 特別需要Python 3.10： [直接下載安裝程式](https://www.python.org/ftp/python/3.10.11/python-3.10.11-amd64.exe)
- 如果您想要專門安裝在 DiffTrainer 資料夾中的副本，您可以使用 python_installer.bat
- 一旦安裝了Python 3.10，就可以執行 setup.bat 來下載需求組件，或執行通常的 `pip install -r requirements.txt`
- 建議多個Python版本的使用者使用 [Miniconda](https://docs.anaconda.com/free/miniconda/miniconda-other-installer-links/) 。

## 已知錯誤
- 在非羅馬字母的語言中字符是損壞的

## 語言支持
DiffTrainer 使用 [ez-localizr](https://github.com/spicytigermeat/ez-localizr/tree/main) 來允許 GUI 語言選擇。 歡迎所有使用者將 [en_US](/strings/en_US.yaml) 中找到的文字翻譯為其他語言並提交拉取請求。

## 待辦事項
很快
- 更好的自述文件
- SOME用於 MIDI 估算

最終
- 高級匯出
- 更多翻譯
- 一個不 amogus 的圖標
