#主要邏輯與前端
import gpa
import streamlit as st
import pandas as pd

#模板下載
from io import BytesIO     
from openpyxl.comments import Comment

#網頁標題
st.title("GPA CALCULATOR")


#檔案上傳區
st.subheader("檔案上傳")
file = st.file_uploader(label = "請上傳Excel檔案，或下載模板")


#模板下載區
def build_template_xlsx() -> bytes:
    # === courses sheet（欄位順序完全照你給的）===
    df_courses = pd.DataFrame(columns=[
        "term",
        "course",
        "score",
        "credit",
        "count_gpa",
    ])

    # === ranks sheet（欄位順序完全照你給的）===
    df_ranks = pd.DataFrame(columns=[
        "term",
        "class_rank",
        "class_size",
        "dept_rank",
        "dept_size",
        "sem_grade",
    ])

    bio = BytesIO()
    with pd.ExcelWriter(bio, engine="openpyxl") as writer:
        df_courses.to_excel(writer, sheet_name="courses", index=False)
        df_ranks.to_excel(writer, sheet_name="ranks", index=False)

        wb = writer.book

        # --- courses 註解 ---
        ws = wb["courses"]
        ws["A1"].comment = Comment(
            "學年度-學期，例如 2024-1；1=上學期(Fall)，2=下學期(Spring)",
            "GPA Calculator"
        )
        ws["B1"].comment = Comment("課程名稱（文字）", "GPA Calculator")
        ws["C1"].comment = Comment("分數（數字，滿分 100.0）", "GPA Calculator")
        ws["D1"].comment = Comment("學分數（數字）", "GPA Calculator")
        ws["E1"].comment = Comment(
            "是否列入 GPA 計算（選填；1=列入；2=不列入）",
            "GPA Calculator"
        )
        ws.freeze_panes = "A2"

        # --- ranks 註解 ---
        ws2 = wb["ranks"]
        ws2["A1"].comment = Comment(
            "學年度-學期，需與 courses 的 term 對齊",
            "GPA Calculator"
        )
        ws2["B1"].comment = Comment("班排名（數字，1 表示第一名）", "GPA Calculator")
        ws2["C1"].comment = Comment("班級人數（數字）", "GPA Calculator")
        ws2["D1"].comment = Comment("系排名（選填）", "GPA Calculator")
        ws2["E1"].comment = Comment("系人數（選填）", "GPA Calculator")
        ws2["F1"].comment = Comment("學期成績（數字）", "GPA Calculator")
        ws2.freeze_panes = "A2"

    bio.seek(0)
    return bio.getvalue()

#判斷使用者是否正確上傳檔案
if file is not None:
    df_courses = gpa.load_excel(file, "courses")     #用來分析GPA
    df_ranks = gpa.load_excel(file, "ranks")     #用來分析排名
else:
    st.caption("請上傳Excel檔案，或下載模板填寫")
    #讓使用者下載模板
    #st.write("下載 Excel 模板")
    #st.caption("請依照格式與註解填寫")
    st.write("方法1 : 外校學生請下載模板")
    image1, image2= st.columns(2)
    image3, image4= st.columns(2)
    image1.image("image/下載模板.png",caption= "(1)點擊 \"下載GPA Excel模板\"")
    image2.image("image/填寫模板1.png", caption="(2)依照格式填寫sheet1 \"courses\" (一行一筆資料)")
    image3.image("image/填寫模板2.png", caption="(3)依照格式填寫sheet2 \"ranks\" (一行一筆資料)")
    image4.image("image/上傳資料.png", caption="(4)將填好的Excel下載 並且上傳至 \"GPA CALCULATOR\"")
    st.download_button(
    label="下載 GPA Excel 模板",
    data=build_template_xlsx(),
    file_name="gpa_template.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    st.write("")
    st.write("方法2 : 高師大學生請至\"單一登入平台\"的\"歷年成績查詢\"複製資料並且直接貼到空白Excel")
    st.stop()

#預覽與勾選課程區
st.subheader("課程預覽")
st.caption("請勾選要列入計算之課程")
df_courses["include"] = df_courses["count_gpa"].fillna(1).astype(int).eq(1)
#根據count_gpa這個欄位，產生內部用的欄位include
#fillna(1) : 如果使用者漏填的話自動補1
#astype(int) : 如果使用者選錯儲存格格式，則自斷轉換成int
#eq(1) : 把儲存格中的int轉成布林值，1=True；0=False  

df_courses_edit = st.data_editor(
    df_courses,
    column_config = {"include" : st.column_config.CheckboxColumn("列入GPA計算")},
    disabled = ["term", "course", "score", "credit"]
)
#根據使用者勾選的結果，產生新的資料 df_course_edit 
#st.data_editor : 允許使用者在前端編輯，並且產生出新的df
#column_config : 把某欄位顯示成想要的樣子
#disabled : 絕對不要被編輯到的欄位

df_courses_calc = df_courses_edit[df_courses_edit["include"]].copy()
#產生一張新的df(複製出來的，不要影響原資料)
st.write("")


#結果分析區
st.subheader("分析結果")
system = st.radio("請選擇GPA制度",("4.0", "4.3"))

#產生歷年gpa的df
terms = sorted(df_courses_calc["term"].unique())
gpas = [
    gpa.calculate_gpa(
        df_courses_calc[df_courses_calc["term"] == t],
        system
    )
    for t in terms
    ]
df_gpa = pd.DataFrame({
    "term" : terms,
    "gpa" : gpas
})

#排版用---------------------------------------------------------------------------------------------------
left_column1, right_column1 = st.columns(2)
left_column2, mid_column2, right_column2 = st.columns(3)
left_column3, right_column3 = st.columns(2)
#排版用---------------------------------------------------------------------------------------------------


#GPA相關資料''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#顯示歷年GPA
left_column1.write("歷年GPA結果")
left_column1.write(df_gpa)

#顯示GPA折線圖
right_column1.write("GPA折線圖")
right_column1.line_chart(df_gpa, x = "term", y = "gpa")


#排名相關資料''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#產生歷年排名的df
terms = sorted(df_ranks["term"].unique())

class_prs = [
    gpa.calculate_pr(
        df_ranks[df_ranks["term"] == t]["class_rank"].iloc[0],
        df_ranks[df_ranks["term"] == t]["class_size"].iloc[0]
    )
    for t in terms
]

dept_prs = []
for t in terms:
    row = df_ranks[df_ranks["term"] == t].iloc[0]
    if pd.notna(row.get("dept_rank")) and pd.notna(row.get("dept_size")):
        dept_prs.append(gpa.calculate_pr(row["dept_rank"], row["dept_size"]))
    else:
        dept_prs.append(None)

df_rank = pd.DataFrame({
    "term": terms,
    "class_rank": [df_ranks[df_ranks["term"] == t]["class_rank"].iloc[0] for t in terms],
    "class_pr": class_prs,
    "dept_rank": [df_ranks[df_ranks["term"] == t].get("dept_rank", pd.Series([None])).iloc[0] for t in terms],
    "dept_pr": dept_prs,
})

#顯示歷年排名
left_column2.write("歷年排名結果")
left_column2.write(df_rank)

#顯示排名折線圖
mid_column2.write("排名折線圖(Pr)")
mid_column2.line_chart(df_rank, x = "term", y = ["class_pr", "dept_pr"])

#顯示排名折線圖
import altair as alt     

right_column2.write("排名折線圖（數字越小代表表現越好）")

chart = alt.Chart(df_rank).mark_line(point=True).encode(
    x=alt.X("term:N", title="學期"),
    y=alt.Y(
        "class_rank:Q",
        title="班排名（越小越好）",
        scale=alt.Scale(reverse=True)   
    ),
    tooltip=["term", "class_rank"]
)

right_column2.altair_chart(chart, use_container_width=True)

#學期成績相關資料''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''''
#建立歷年學期成績df
df_sem_grade = pd.DataFrame({
    "term" : df_ranks["term"],
    "sem_grade" : df_ranks["sem_grade"]
})

#顯示歷年學期成績
left_column3.write("歷年學期成績")
left_column3.write(df_sem_grade)

#顯示學期成績折線圖
right_column3.write("學期成績折線圖")
right_column3.line_chart(df_sem_grade, x = "term", y = "sem_grade")

#回饋表單
with st.sidebar:
    st.markdown("### 📝 使用回饋")
    st.markdown("[👉 點我填寫回饋表單](https://forms.gle/2ZFEE3JVatDS5RYu9)")
    