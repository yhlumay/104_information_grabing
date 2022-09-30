import requests
import re
from bs4 import BeautifulSoup as soup
import pandas as pd
import matplotlib.pyplot as plt
from pylab import mpl

mpl.rcParams['font.sans-serif'] = ['DFKai-SB']
mpl.rcParams['axes.unicode_minus'] = False
# 可輸入不同的關鍵字、所需頁數和地區來進行搜尋
keyword = 'python'
page = 5
loc = ['台北市', '新北市', '桃園市']
locationlist = {'台北市': '6001001000%2C', '新北市': '6001002000%2C', '宜蘭縣': '6001003000%2C', '基隆市': '6001004000%2C', '桃園市': '6001005000%2C', '新竹縣市': '6001006000%2C', '苗栗縣': '6001007000%2C', '台中市': '6001008000%2C', '彰化縣': '6001010000%2C', '南投縣': '6001011000%2C',
                '雲林縣': '6001012000%2C', '嘉義縣市': '6001013000%2C', '台南市': '6001014000%2C', '高雄市': '6001016000%2C', '屏東縣': '6001018000%2C', '台東縣': '6001019000%2C', '花蓮縣': '6001020000%2C', '澎湖縣': '6001021000%2C', '金門縣': '6001022000%2C', '連江縣': '6001023000%2C'}

values = []
for p in range(1, page+1):
    location = ''
    for i in loc:
        location = location + str(locationlist.get(str(i)))
    # 依照關鍵字組合成搜尋所需網址
    url = 'https://www.104.com.tw/jobs/search/?ro=0&kwop=7&keyword='+keyword+'&expansionType=area%2Cspec%2Ccom%2Cjob%2Cwf%2Cwktm&area='+location+'&order=14&asc=0&page=' + \
        str(p)+'&mode=l&langFlag=0&langStatus=0&recommendJob=1&hotJob=1'

    HEADERS = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
        "Referer": "https://www.104.com.tw/jobs/search/"
    }
    web = requests.get(url, headers=HEADERS)
    search = soup(web.text, 'html.parser')
    result = search.find_all(
        'article', {'class': 'job-mode js-job-item'})
    # 從'搜尋的頁面'進行靜態爬蟲抓取資料
    for res in result:
        job_name = res.find('ul').a.text
        company = res.find('li', {'class': 'job-mode__company'}).a.text.strip()
        pattern = '公司住址：(.*?)$'
        addr = res.find('li', {'class': 'job-mode__company'}).a['title']
        address = re.findall(pattern, str(addr))[0]
        location = res.find('li', {'class': 'job-mode__area'}).text
        companylink = res.find('li', {'class': 'job-mode__company'}).a['href']
        exp = res.find('li', {'class': 'job-mode__exp'}).text
        edu = res.find('li', {'class': 'job-mode__edu'}).text
        # 爬蟲找出職缺頁的連結及職缺編號，以進行職缺頁面資料的抓取
        joblink = res.find('li', {'class': 'job-mode__jobname'}).a['href']
        pattern = 'www.104.com.tw/job/(.*?)?jobsource'
        jobno = re.findall(pattern, str(joblink))[0].rstrip('?')
        # 進行動態爬蟲
        job_url = 'https://www.104.com.tw/job/ajax/content/' + str(jobno)
        HEADERS = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/104.0.0.0 Safari/537.36',
            'Referer': 'https://www.104.com.tw/job/{jobno}'
        }
        job_web = requests.get(job_url, headers=HEADERS)
        job_data = job_web.json()
        job_content = job_data['data']
        industry = job_content['industry']
        other_welfare = job_content['welfare']['welfare']
        salary_min = job_content['jobDetail']['salaryMin']
        if salary_min == 0:
            salary_min = 40000
        salary_max = job_content['jobDetail']['salaryMax']
        if salary_max == 0:
            salary_max = 40000
        exp = job_content['condition']['workExp']
        edu = job_content['condition']['edu']
        description = job_content['jobDetail']['jobDescription']
        other_description = job_content['condition']['other']
        salary_type = job_content['jobDetail']['salaryType']

        value = [job_name, joblink, company, industry, location, address, companylink,
                 exp, edu, description, other_description, other_welfare, salary_min, salary_max, salary_type]
        columns = ['職缺名稱', '職缺連結', '公司名稱', '公司產業別', '公司區域', '公司地址',
                   '公司連結', '經歷要求', '學歷要求', '職缺內容', '其他描述', '其他福利', '薪資下限', '薪資上限', '薪資型態']
        values.append(value)
# 將抓取出來的資料彙整，匯出CSV檔案
df = pd.DataFrame()
df = pd.DataFrame(values, columns=columns)
df.to_csv('104jobinformation.csv', encoding='utf_8_sig')
