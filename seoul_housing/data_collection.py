# -*- coding:utf-8 -*-
import requests
import pandas as pd
from dotenv import load_dotenv

import os

load_dotenv()

SERVICE_KEY = os.getenv('SEOUL_API_KEY')
if not SERVICE_KEY:
    raise ValueError("환경 변수 'SEOUL_API_KEY'가 설정되지 않았습니다. .env 파일을 확인하세요.")


def main():
    data = None
    for j in range(1,12):
        url = f'http://openapi.seoul.go.kr:8088/{SERVICE_KEY}/json/tbLnOpendataRtmsV/{1+((j-1)*1000)}/{j*1000}'
        print(url)
        req = requests.get(url)
        
        content = req.json()
        con = content['tbLnOpendataRtmsV']['row']
        result = pd.DataFrame(con)
        data = pd.concat([data, result])
    data = data.reset_index(drop=True)
    data['CTRT_DAY']  = pd.to_datetime(data['CTRT_DAY'], format=("%Y%m%d"))
    # data.to_csv('./data/seoul_real_estate.csv', index=False)
    os.makedirs("./data", exist_ok=True)  
    data.to_csv('./data/sample.csv', index=False)

if __name__=="__main__":
    main()

