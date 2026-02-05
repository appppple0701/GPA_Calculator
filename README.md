# GPA_Calculator

# A simple calculator for college student. 

# feature : 
-Supports 4.0 and 4.3 GPA scales.
-Import grades from excel. 


# How to use?
-本工具從固定格式的excel檔案讀取成績資料
-請將excel檔案存成.xlsx檔
-excel檔案必須包含以下欄位:
Column name/     Description/     Ex
course/     course name/     '計算機組織'
credit/     course credit/     3
score/     final score(0~100)/     93
term/     academic term('year-first/second')/     '2024-1'
count_gpa/ whether to include in GPA(1 == yes, 0 == no)/     1

-範例檔案詳見 : data/sample_grade.xlxs

## demos/ 資料夾說明
`demos/` 資料夾用來存放我在開發 GPA Calculator 前，
用來學習與測試 Streamlit 各種元件與功能的範例程式。

這些檔案主要用途為：
- 練習 Streamlit 元件（selectbox、slider、file uploader、progress 等）
- 驗證 UI 與資料流程是否可行
- 作為正式前端（Streamlit App）開發前的 prototype 與實驗環境

`demos/` 中的程式**不是最終產品的一部分**，
正式的 GPA 計算邏輯與前端實作將會在其他模組中完成。


# 記得要照格式使用喔 啾咪