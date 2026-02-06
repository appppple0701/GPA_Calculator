import gpa
import streamlit as st
import pandas as pd

#標題
st.header("GPA CALCULATOR")

#上傳檔案
st.subheader("檔案上傳")
file = st.file_uploader(
    label = "請上傳excel檔案"
)

if file is not None:
    df = gpa.load_excel(file)
    st.write("檔案預覽")
    st.write(df)

    #修改列入計算的課程
    if "count_gpa" not in df.columns:
        df["count_gpa"] = 1
        #使用者可能忘記要照格式加入這列
    # --------------------------------------------------
    # 1. 確保資料中有 count_gpa 這一欄
    #    若使用者上傳的 Excel 沒有這欄，
    #    預設視為「所有課程都列入 GPA 計算」
    # --------------------------------------------------

    df["include"] = df["count_gpa"].fillna(1).astype(int).eq(1)
    # --------------------------------------------------
    # 2. 產生內部使用的 include 欄位（Boolean）
    #    這一欄是給 Streamlit data_editor 用的
    #
    #    規則：
    #    - count_gpa == 1 → include = True
    #    - count_gpa == 0 → include = False
    #
    #    說明：
    #    - fillna(1)     : 避免有 NaN，預設當作列入計算
    #    - astype(int)   : 避免 Excel 用文字或其他型別存 0/1
    #    - eq(1)         : 等價於 (count_gpa == 1)
    # --------------------------------------------------

    st.subheader("勾選列入計算的課程")
    #st.write("請在此勾選")
    edited_df = st.data_editor(
        df,
        column_config={
            "include" : st.column_config.CheckboxColumn("列入GPA")
        },
        disabled=["term", "course", "score", "credit", "count_gpa"]
    )
    # --------------------------------------------------
    # 3. 讓使用者在前端勾選「是否列入 GPA 計算」
    #    - include 欄位會顯示成 checkbox
    #    - 其他欄位鎖定，避免誤改原始資料
    # --------------------------------------------------


    df_for_calc = edited_df[edited_df["include"]].copy()
    # --------------------------------------------------
    # 4. 產生實際用來計算 GPA 的 DataFrame
    #    df_for_calc = 只包含「include == True」的課程
    #
    #    重點：
    #    - 這是一個「篩選後的新 DataFrame」
    #    - 不會影響原本的 df
    #    - 後續所有 GPA 計算都應該用這個 df
    # --------------------------------------------------
    #st.write("以下為調整")
    #st.write(df_for_calc)

    st.subheader("GPA制度")
    system = st.radio("請選擇GPA制度",("4.0","4.3"))

    st.subheader("您的GPA")
    #outcome = gpa.calculate_gpa(df_for_calc, "4.3", )
    #st.write(outcome)

    terms = sorted(df_for_calc["term"].unique())

    gpas = [
    gpa.calculate_gpa(
        df_for_calc[df_for_calc["term"] == t],
        system
    )
    for t in terms
    ]

    df_gpa = pd.DataFrame({
        "term" : terms,
        "gpa" : gpas
    })
    st.write(df_gpa)

    st.subheader(f"您的總平均GPA : {gpa.calculate_gpa(df_for_calc,system)}")
else:
    st.write("請上傳excel檔案")

