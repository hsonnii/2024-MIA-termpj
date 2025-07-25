import pandas as pd
import numpy as np

# 데이터 불러오기
df1 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/학교/2024-2/경정분 디벨롭/2019 배달데이터 분석/데이터/del_19.csv', header=None)
df2 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/학교/2024-2/경정분 디벨롭/2019 배달데이터 분석/데이터/del_20_0107.csv', header=None)

# 데이터 합치기
df = pd.concat([df1, df2], ignore_index=True)

# 중복 행 제거
df = df.drop_duplicates()

# 필요없는 컬럼 삭제 : 야식 컬럼 제거
df = df.drop(columns=[23])  # V24 컬럼 제거 (0부터 시작하는 인덱스)

# 컬럼명 변경
df.columns = [
    "address1", "address2", "date", "hour_time", "rain_type", "humid_val", "rain_val", "temp_val", "wind_val",
    "wind_type", "wind_ew_type", "wind_value", "wind_ctg", "kr_cnt", "snack_cnt", "cafe_dessert_cnt", "pork_jp_cnt",
    "fish_cnt", "chicken_cnt", "pizza_cnt", "asian_western_cnt", "cn_cnt", "jokb_bos_cnt", "steam_soup_cnt",
    "dosirak_cnt", "fast_cnt"
]


# 서울특별시 & 특정 구 필터링
df = df[(df['address1'] == '서울특별시') & df['address2'].isin(['강남구', '강서구', '송파구'])]

# 초미세먼지 데이터 불러오기
mj1 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/학교/2024-2/경정분 디벨롭/2019 배달데이터 분석/데이터/2019초미세먼지.csv')
mj2 = pd.read_csv('/content/drive/MyDrive/Colab Notebooks/학교/2024-2/경정분 디벨롭/2019 배달데이터 분석/데이터/2020초미세먼지.csv')

# 데이터 합치기
mj = pd.concat([mj1, mj2], ignore_index=True)

mj

# 날짜 변환 및 필터링
mj['일시'] = pd.to_datetime(mj['일시']).dt.strftime('%Y-%m-%d')
mj = mj[mj['구분'].isin(['강남구', '강서구', '송파구'])]

# 구별 일평균 초미세먼지 계산
mean_mj = mj.groupby(['일시', '구분'], as_index=False)['초미세먼지(PM25)'].mean()
mean_mj.rename(columns={'초미세먼지(PM25)': 'day_cmj_mean'}, inplace=True)

# 데이터 병합
df = df.merge(mean_mj, left_on=['address2', 'date'], right_on=['구분', '일시'], how='left')
df.drop(columns=['구분', '일시'], inplace=True)

# 결측값 처리 (월 평균 대체)
df['month'] = pd.to_datetime(df['date']).dt.month
for col in ['humid_val', 'wind_val', 'wind_value']:
    df[col] = df[col].replace(-1, np.nan)
    df[col] = df.groupby('month')[col].transform(lambda x: x.fillna(x.mean()))

# 초미세먼지 결측치 처리 (같은 날짜 나머지 구 평균)
df['day_cmj_mean'] = df.groupby('date')['day_cmj_mean'].transform(lambda x: x.fillna(x[x.notna()].mean()))

# 남은 결측치는 지역별 월 평균으로 대체
df['day_cmj_mean'] = df.groupby(['address2', 'month'])['day_cmj_mean'].transform(lambda x: x.fillna(x.mean()))

# 요일 컬럼 추가
df['weekday'] = pd.to_datetime(df['date']).dt.weekday + 1  # (1: 월요일, 7: 일요일)

# 불쾌지수 계산
df['DI'] = (9/5) * df['temp_val'] - 0.55 * (1 - (df['humid_val']/100)) * ((9/5) * df['temp_val'] - 26) + 32

# 최종 데이터 저장
df.to_csv("pj_finaldata.csv", index=False)

