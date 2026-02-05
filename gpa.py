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
def load_excel(path):
    df = pd.read_excel(path)
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

#主程式
'''
def main():
    df = load_excel("data/sample_grade.xlsx")
    gpa = calculate_gpa(df, "4.3")
    print(gpa)

if __name__ == "__main__":
    main()
'''