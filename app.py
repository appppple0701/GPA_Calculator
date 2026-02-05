import gpa
import streamlit as st

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
else:
    st.write("請上傳excel檔案")

#修改列入計算的課程
if "count_gpa" not in df.columns:
    df["count_gpa"] = 1
    #使用者可能忘記要照格式加入這列

df["include"] = df["count_gpa"].fillna(1).astype(int).eq(1)
#內部產生一列新資料，對應count_gpa那列 (streamlit會把布林值的列輸出成勾選框)
#fillna(1) : 遇到nan的話自動填上1
#astype(int) : 避免excel用其他型別儲存1、0
#eq(1) : 等價於如果那格是1，對應的include那格紀錄True

st.subheader("勾選列入計算的課程")
#st.write("請在此勾選")
edited_df = st.data_editor(
    df,
    column_config={
        "include" : st.column_config.CheckboxColumn("列入GPA")
    },
    disabled=["term", "course", "score", "credit", "count_gpa"]
)

df_for_calc = edited_df[edited_df["include"]].copy()
#st.write("以下為調整")
#st.write(df_for_calc)