import time
import pandas as pd
import translators as ts

from tqdm import tqdm

TRANSLATOR_COLS = ['google', 'alibaba', 'baidu',
                   'bing', 'youdao', 'iflyrec', 'caiyun']
DB = 'zh-translations-competitions1.xls'
SHEET_NAME = 'zh-cn.teams'
PREACCELERATE = True
SOURCE_LANGUAGE = 'en'
TARGET_LANGUAGE = 'zh-cn'
SOURCE_COL = 'TEAMS'
REFERENCE_COL = 'ZH-CN TEAMS'

df = pd.read_excel(DB, sheet_name=SHEET_NAME)
df = df[:1000]
total_rows = len(df.index)
# add columns for each translator
for t in TRANSLATOR_COLS:
    df[t] = ''

if PREACCELERATE:
    _ = ts.preaccelerate_and_speedtest()

# create timer and error dicts
timer_dict = {}
error_dict = {}

# add 0 errors for each translator
for t in TRANSLATOR_COLS:
    error_dict[t] = 0

# translate
pbar = tqdm(total=total_rows)
for t in TRANSLATOR_COLS:
    pbar.set_description(f'Translating with {t}')
    tic = time.perf_counter()
    for i, row in df.iterrows():
        try:
            df.at[i, t] = str(ts.translate_text(
                row[SOURCE_COL], translator=t, from_language=SOURCE_LANGUAGE, to_language=TARGET_LANGUAGE))
        except:
            pass
        if df.at[i, t] != df.at[i, REFERENCE_COL]:
            error_dict[t] += 1
        pbar.update(1)
    toc = time.perf_counter()
    timer_dict[t] = toc - tic
    pbar.reset()

# create timer and error dataframes
timer_df = pd.DataFrame.from_dict(timer_dict, orient='index', columns=['time'])
error_df = pd.DataFrame.from_dict(
    error_dict, orient='index', columns=['errors'])
for t in TRANSLATOR_COLS:
    err_rate = error_df.loc[t, 'errors'] / total_rows
    error_df.loc[t, 'error_rate'] = err_rate

# save to xlsx (xls is not supported)
with pd.ExcelWriter('zh-translations-competitions1-translated.xlsx') as writer:
    df.to_excel(writer, sheet_name=SHEET_NAME)
    timer_df.to_excel(writer, sheet_name='translation_time_(s)')
    error_df.to_excel(writer, sheet_name='translation_errors')
