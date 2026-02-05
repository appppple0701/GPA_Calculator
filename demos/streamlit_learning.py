import streamlit as st
import pandas as pd

df = pd.read_excel("sample_grade.xlsx")

#1. st.write() : 印出東西
st.write("1. st.write()")
st.write(df)

#2. st.line_chart() : 把東西轉成折線圖
st.write("\n2. st.line_chart()")
st.line_chart(df)

#3. st.map() : 輸入經緯度就能輸出地圖
st.write("\n3. st.map()")
st.map({
        'lat' : [24.181048],
        'lon' : [120.71514]
       })

#4. st.slider()
st.write("\n4. st.slider()")
x = st.slider("x")
st.write(x, "squared is", x*x)

#5. st.text_input() : 
st.write("\n5. st.text_input()")
st.text_input("隨便輸入東西", key = 'thing')
st.session_state.thing

#6. st.checkbox() : 多選欄
st.write("\n6. st.checkbox()")
if st.checkbox('Show dataframe'):
    st.write(df)
elif st.checkbox('show bug'):
    st.write("bug")

#7. st.selectbox() : 下拉選項
st.write("\n7. st.selectbox()")
drink = st.selectbox("你今天想喝什麼?", ["預設","咖啡","紅茶","奶茶"])
st.write(drink)

#8. st.siderbar : 側邊欄
st.write("\n8. st.sidebar")

payment = st.sidebar.selectbox("選擇支付方式",['現金', '刷卡', 'linepay'])
st.write(payment)

tip = st.sidebar.slider("小費金額", 0.0, 50000.0)
st.write("小費:", tip)

#9. st.radio() : 單選
st.write("\n9. st.radio()")

left_column, right_column = st.columns(2)

payingTip = left_column.button("press me")
if payingTip:
    st.write("請選擇服務生")

with right_column:     #語法尚無法直接寫right_column 然後縮排
    waiter = st.radio("您今天的服務生是 : ", ("陳聖翰", "李有騰", "姚誠言"))
    st.write("您的服務生是", waiter)

#10. st.progress() : 進度條
import time

st.write("10. st.progress()")
if st.button("刷新"):
    bar = st.progress(0)
    bar.empty()
    for i in range(101):
        time.sleep(0.01)
        bar.progress(i)
    st.write("運行結束")

#11. stfile_uploader() : 上傳文件
st.write("11. st.file_uploader()")
upload_file = st.file_uploader(
    label = "請上傳文件"
)

if upload_file is not None:
    df = pd.read_csv(upload_file)
    st.write("文件上傳成功")
    st.write(df)
else:
    st.write("請上傳CSV文件")