# 新公告 2/17/25：自動更新錯誤 ( *[English](./ANNOUNCEMENT.md)* )
0.2.2 到 0.2.9 版本將不再正確觸發自動更新。若要還原此功能，請在您選擇的文字編輯器中編輯 difftrainer.py，並將版本：0.2.x 變更為版本：0.2.0。

# 舊公告：主要待定更改 ( *[English](./ANNOUNCEMENT.md)* )

### 版本 0.1.18 將是支援現有安裝程式和啟動程式方法的最後一個版本。由於直接衝突的軟體包需求（某些/訓練需要 Torch > 2.0，ONNX 匯出需要 Torch < 2.0），需要 Conda 或環境自我管理。考慮到這一點，安裝和啟動 .bat 檔案將替換為以下步驟：
- **（如果需要）** 運行 *conda_installer.bat*（以前稱為 *python_installer.bat*）以快速安裝 Miniconda3 的副本。產生的程式並非 DiffTrainer 獨有，還可用於管理其他 Python 3.x 專案的需求。現有的 Anaconda/Miniconda 安裝將透過以下設定進行檢測。
- 執行 *setup.bat* 自動建立和配置兩個環境：DifftrainerA 和 DifftrainerB。在此過程中，*torchdrop* 腳本會自動偵測任何已安裝的 CUDA 版本，並為 CPU 或 GPU 選擇適當的 Torch 版本。
  - 若要手動設定環境，要求檔案位於 /assets/ 中。在各自的環境中執行兩個 *torchdrop* 腳本以偵測所需的 Torch 版本並完成相依性安裝。
- 使用 DiffTrainer 主選項卡上的 *更新工具* 下載
- 對於預處理、二值化和訓練，請使用 *run_guiA.bat* 啟動。匯出 ONNX 檔案時使用 *run_guiB.bat*。

### 由於進行了大量更改，建議在配置 DiffTrainer 0.2.0 之前刪除所有舊版本的 DiffTrainer 和隨附檔案。如果使用 *python_installer.bat* 安裝 Python 的專用副本，請使用 /python 資料夾中的解除安裝程式。

### 鼓勵使用者在主分支發布之前透過下載 [SOME 分支](https://github.com/agentasteriski/DiffTrainer/tree/SOME) 手動升級到版本 0.2.0。
