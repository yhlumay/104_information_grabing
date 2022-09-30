import requests
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pylab import mpl
mpl.rcParams['font.sans-serif'] = ['DFKai-SB']
mpl.rcParams['axes.unicode_minus'] = False


def set_autopct(pct):
    return ('%1.2f%%' % pct) if pct > 5 else ''


# 匯入之前建立的CSV檔案
df = pd.DataFrame()
df = pd.read_csv('104jobinformation.csv')

#############################################################################
# 抓取'經歷要求'和'最低薪資'的欄位，建立圓餅圖-經歷要求與平均薪資分析
fig1 = plt.figure(num=1, figsize=(40, 40),
                  facecolor='#bdffe6', constrained_layout=True)
df_exp = df.loc[:, ['經歷要求']]
exp_columns = []
for year in range(1, 11):
    exp_columns.append(str(year) + '年以上')
exp_columns.append('不拘')
numbers = []
for nu in range(0, len(exp_columns)):
    a = df_exp[df_exp == exp_columns[nu]].dropna().size
    numbers.append(a)

salarymin = df.loc[:, ['公司產業別', '經歷要求', '薪資下限', '薪資型態']]
salarymin.loc[salarymin['薪資型態'] == 30, '薪資下限'] = 0
salarymin.loc[salarymin['薪資型態'] == 60, '薪資下限'] = round(salarymin['薪資下限']/12)
salarymin = salarymin.drop(salarymin.loc[salarymin['薪資下限'] == 0].index)

salary_meanlist = []
for e in range(0, len(exp_columns)):
    b = salarymin.loc[salarymin['經歷要求'] == exp_columns[e]]['薪資下限'].mean()
    salary_meanlist.append(('薪資:' + str(round(b, 1)) + '元'))

df_exp1 = pd.DataFrame(
    {'exp': exp_columns, 'num': numbers, 'samean': salary_meanlist})
df_exp1['expsamean'] = df_exp1['exp'] + '\n' + df_exp1['samean']
df_exp1 = df_exp1.drop(df_exp1[df_exp1['num'] == 0].index)

colors = ['#1c85d6', 'pink', '#73ede6', 'orange', '#dce208', 'green', '#fc4f78',
          '#ca00df', 'purple', '#7df4b2', 'lightgreen', '#d7727f', '#fda229', '#6ade91', '#ed4f47', '#b1007f', '#e63d20', '#c7f798', '#01e8cc', '#75dc8e', '#7f13f6', '#0dbbf7', '#fce5cc', '#54d0e5', '#c308ac', '#bffba6']

plt.pie(df_exp1['num'], labels=df_exp1['expsamean'], autopct=set_autopct,
        colors=colors, pctdistance=0.8, labeldistance=1.1, wedgeprops={'linewidth': 1, 'edgecolor': 'w'})
plt.title('經歷要求與平均薪資分析', fontsize=20)
plt.legend(df_exp1['exp'], loc=3)
plt.axis('equal')

#############################################################################
# 進行產業別分析，抓取公司的產業小類別建立雙環圖的第一個環，再對照到大類別，用大類別建立第二個環，形成'公司產業別分析'的雙環圖
fig2, small = plt.subplots(num=2, figsize=(
    40, 40), facecolor='#bdffe6', constrained_layout=True)
df_indu = df.loc[:, ['公司產業別']]

df_indu_index = df_indu.drop_duplicates()
df_indu_index.index = [a for a in range(0, len(df_indu_index))]
df_indu_indexlist = df_indu_index['公司產業別'].values.tolist()

ind_url = 'https://static.104.com.tw/category-tool/json/Indust.json'
req = requests.get(ind_url)
ind_ndf = []
for x in req.json():
    for y in x['n']:
        z = pd.DataFrame(y['n'])
        z['middle'] = y['des']
        z['big'] = x['des']
        ind_ndf.append(z)

ind_ndf = pd.concat(ind_ndf, ignore_index=True)
ind_ndf = ind_ndf.loc[:, ['big', 'middle', 'des', 'no']]
ind_ndf = ind_ndf.sort_values('no')

bigclass = ind_ndf['big'].values.tolist()
items = ind_ndf['des'].values.tolist()
dict1 = {}
for xyz in range(0, len(items)):
    dict1[items[xyz]] = bigclass[xyz]

industries = []
for idst in range(0, len(df_indu_indexlist)):
    i = df_indu[df_indu == df_indu_indexlist[idst]].dropna().size
    industries.append(i)

bigclass_list = []
for d in df_indu_indexlist:
    bc = dict1.get(d)
    bigclass_list.append(bc)

df_indus = pd.DataFrame({'big_class': bigclass_list,
                        'industry': df_indu_indexlist, 'count': industries})
df_indus = df_indus.drop(df_indus[df_indus['count'] == 0].index)

bc_ctg = df_indus['big_class'].drop_duplicates()
bc_ctg.index = [a for a in range(0, len(bc_ctg))]
bc_ctg_list = bc_ctg.values.tolist()

bc_count = []
for co in range(0, len(bc_ctg)):
    coo = df_indus[df_indus['big_class'] == bc_ctg[co]]['count'].sum()
    bc_count.append(coo)

bc_nums = pd.DataFrame({'bc_ctgs': bc_ctg_list, 'bc_num': bc_count})
bc_nums.sort_values(by='bc_num', ascending=True)

size = 0.4

plt.pie(bc_nums['bc_num'], labels=bc_nums['bc_ctgs'], autopct=set_autopct, colors=colors,
        pctdistance=0.85, labeldistance=1.1, radius=1, wedgeprops=dict(width=size, edgecolor='w'))
plt.pie(df_indus['count'],
        pctdistance=0.3, radius=1-size, wedgeprops=dict(width=size, edgecolor='w'))
plt.legend(bc_nums['bc_ctgs'], loc=3)

plt.title('公司產業別分析', fontsize=20)
plt.axis('equal')

#############################################################################
# 從上述雙環圖中可發現，電子資訊/軟體/半導體相關業的占比是最大的，於是進一步將此產業中的中產業別加入長條圖中顯示
fig3 = plt.figure(num=3, figsize=(40, 40),
                  facecolor='#bdffe6', constrained_layout=True)

fig31 = plt.subplot(211)

fig31.set_facecolor('#bdffe6')
plt.barh(bc_nums['bc_ctgs'], bc_nums['bc_num'], label='產業分析')
plt.xticks(np.arange(0, bc_nums['bc_num'].sum(), 10))
plt.title('公司產業別分析二', fontsize=20)
plt.legend()

fig32 = plt.subplot(212)

df_fig32_index = df_indus[['big_class']][df_indus[[
    'big_class']] == '電子資訊／軟體／半導體相關業'].dropna()
df_fig32_index_list = df_fig32_index.index.tolist()
df_fig32 = df_indus.loc[df_fig32_index_list]
fig32.set_facecolor('#bdffe6')
plt.barh(df_fig32['industry'], df_fig32['count'],
         label='電子資訊/軟體/半導體相關業之細項分析', color='#fcb28f',)

plt.xticks(np.arange(0, df_fig32['count'].sum(), 10))
plt.legend()

plt.show()
