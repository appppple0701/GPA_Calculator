import pandas as pd

#分數(score)轉換成等第(grade)的邏輯
#4.0制度
def score_to_point4(score):
    if pd.isna(score):     #如果掃到的分數是空的就噴None
        return None
    if score >= 80:
        return 4
    elif 80 > score >= 70:
        return 3
    elif 70 > score >= 60:
        return 2
    elif 60 > score >= 50:
        return 1
    else:
        return 0

#4.3制度
def score_to_point43(score):
    if pd.isna(score):     #如果掃到的分數是空的 就噴None
        return None
    if 90 <= score:
        return 4.3
    elif 90 > score >= 85:
        return 4.0
    elif 85 > score >= 80:
        return 3.7
    elif 80 > score >= 77:
        return 3.3
    elif 77 > score >= 73:
        return 3.0
    elif 73 > score >= 70:
        return 2.7
    elif 70 > score >= 67:
        return 2.3
    elif 67 > score >= 63:
        return 2.0
    elif 63 > score >= 60:
        return 1.7
    else:
        return 0

#讀取檔案 : excel
def load_excel(path, sheet_name):
    df = pd.read_excel(path, sheet_name=sheet_name)
    return df


#GPA計算 兩制度共用 : sigma(point * credit) / sigma(credit)
def calculate_gpa(df, system = "4.3", term = None):     #預設計算4.3制 並且範圍為所有資料

    mask = (df["count_gpa"] == 1) & (~df["score"].isna())
    if term is not None:
        mask &= (df["term"] == term)
    df = df.loc[mask].copy()      #為了避免panda不清楚要操作view或df本體 所以乾脆直接複製一份出來
    #loc : 直接用標籤來定位欄與列 (可以搭配mask 上面是在定位mask那幾列並複製)

    #判斷要轉換的制度
    if system == "4.3":
        funct = score_to_point43
    elif system == "4.0":
        funct = score_to_point4
    else:
        raise ValueError("system must be '4.0' or '4.3' !!")

    df["point"] = df["score"].apply(funct)     #把成績轉換成點數

    point_sum = (df["point"] * df["credit"]).sum()     #point * credict

    credits_sum = df["credit"].sum()
    if credits_sum == 0:
        return None

    gpa = round(point_sum / (credits_sum),2)     #計算GPA

    return gpa 
#-----------------------------------------------------------------------------------------

#rank排名計算邏輯
def calculate_pr(rank, size):
    if pd.isna(rank) or pd.isna(size):
        return None
    try:
        rank = int(rank)
        size = int(size)
    except:
        return None
    if rank <= 0 or size <= 0:
        return None
    
    pr = ( 1 - ( rank - 1 ) / size ) * 100
    return round(pr, 1)


# ===== NKNU (高師大) 歷年成績查詢：貼上到 Excel 的格式解析 =====
import re
from datetime import datetime

def _parse_nknu_paste_excel(excel_file) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    讀取「從高師大歷年成績查詢頁面複製→貼到空白Excel」的格式：
    - 通常只有一張工作表（例如 工作表1）
    - A欄會出現：113 學年度 第 1 學期
    - 表格欄位：科目名稱、學分、歸類、必選修、分數
    - 下面會有學期平均、名次/班級人數等摘要
    """
    raw = pd.read_excel(excel_file, sheet_name=0, header=None, dtype=object)

    courses = []
    ranks = []

    current_term = None
    sem_grade = None
    class_rank = None
    class_size = None

    # 113 學年度 第 1 學期
    term_re = re.compile(r"(\d{3})\s*學年度.*第\s*([12])\s*學期")

    def flush_rank():
        nonlocal sem_grade, class_rank, class_size, current_term
        if current_term is None:
            return
        ranks.append({
            "term": current_term,
            "class_rank": class_rank,
            "class_size": class_size,
            "dept_rank": None,
            "dept_size": None,
            "sem_grade": sem_grade
        })

    for _, row in raw.iterrows():
        a = row.get(0)

        # --- 1) 新學期區塊開始 ---
        if isinstance(a, str):
            m = term_re.search(a.replace("\u3000", " ").replace("\t", " "))
            if m:
                # 前一學期摘要入表
                flush_rank()

                roc = int(m.group(1))      # 民國年
                sem = int(m.group(2))      # 1 / 2
                year = roc + 1911          # 民國轉西元：113 -> 2024
                current_term = f"{year}-{sem}"

                # reset
                sem_grade = None
                class_rank = None
                class_size = None
                continue

        if current_term is None:
            continue

        # --- 2) 摘要：學期平均/操行成績 ---
        if isinstance(a, str) and "學期平均" in a:
            v = row.get(4)
            if isinstance(v, (int, float)) and not pd.isna(v):
                sem_grade = float(v)
            elif isinstance(v, str):
                s = v.replace("／", "/").replace(" ", "")
                parts = s.split("/")
                try:
                    sem_grade = float(parts[0])
                except:
                    sem_grade = None
            continue

        # --- 3) 摘要：學期名次/全班人數（注意：9/23 可能被 Excel 認成日期） ---
        if isinstance(a, str) and "學期名次" in a:
            v = row.get(4)
            if isinstance(v, datetime):
                s = f"{v.month}/{v.day}"
            else:
                s = "" if v is None else str(v)

            s = s.replace("／", "/").replace(" ", "")
            parts = s.split("/")
            if len(parts) >= 2:
                try:
                    class_rank = int(float(parts[0]))
                except:
                    class_rank = None
                try:
                    class_size = int(float(parts[1]))
                except:
                    class_size = None
            continue

        # --- 4) 表頭列跳過 ---
        if a == "科目名稱":
            continue

        # --- 5) 課程列 ---
        course = a
        credit = row.get(1)
        score = row.get(4)

        if course is None or (isinstance(course, float) and pd.isna(course)):
            continue

        # 避免漏抓其他摘要列
        if isinstance(course, str) and ("修習學分" in course or "學期平均" in course or "學期名次" in course):
            continue

        # credit
        try:
            credit_val = float(credit)
        except:
            credit_val = None

        # score：可能是 未送 / 空白 / NaN
        if isinstance(score, str):
            score_str = score.strip()
            if score_str in ("未送", ""):
                score_val = None
            else:
                try:
                    score_val = float(score_str)
                except:
                    score_val = None
        else:
            if score is None or (isinstance(score, float) and pd.isna(score)):
                score_val = None
            else:
                try:
                    score_val = float(score)
                except:
                    score_val = None

        courses.append({
            "term": current_term,
            "course": str(course).strip(),
            "score": score_val,
            "credit": credit_val,
            "count_gpa": 1,   # 預設全算，讓使用者前端勾選排除
        })

    # 最後一學期摘要入表
    flush_rank()

    df_courses = pd.DataFrame(courses, columns=["term", "course", "score", "credit", "count_gpa"])
    df_ranks = pd.DataFrame(ranks, columns=["term", "class_rank", "class_size", "dept_rank", "dept_size", "sem_grade"])
    return df_courses, df_ranks


def load_grade_file_auto(excel_file) -> tuple[pd.DataFrame, pd.DataFrame]:
    """
    自動辨識：
    - 有 courses/ranks sheet -> 你的模板
    - 沒有 -> 嘗試 NKNU 貼上格式
    """
    try:
        xl = pd.ExcelFile(excel_file)
        sheets = set(xl.sheet_names)

        if {"courses", "ranks"}.issubset(sheets):
            df_courses = pd.read_excel(excel_file, sheet_name="courses")
            df_ranks = pd.read_excel(excel_file, sheet_name="ranks")
            return df_courses, df_ranks

        # fallback：高師大貼上格式
        return _parse_nknu_paste_excel(excel_file)

    except Exception as e:
        raise RuntimeError(f"無法讀取檔案，請確認檔案格式是否正確。原始錯誤：{e}")
