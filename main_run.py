import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import logging
import os

# 5-55/10 * * * * /home/tensor/vaib/imd_radar/env/bin/python3.11  /home/tensor/vaib/imd_radar/main_run.py
# 5,15,25,35,45,55 * * * * /home/tensor/vaib/imd_radar/env/bin/python3.11  /home/tensor/vaib/imd_radar/main_run.py

import requests

home_path = '/home/tensor/vaib/imd_radar'
target = os.path.join(home_path,'target')


# Configure logging
logging.basicConfig(filename="caz_lgs.log", filemode="w",
                    format="%(asctime)s;%(message)s", level=logging.INFO)
# Log messages


types_frames = ['caz','sri','ppi']
locations = ['delhi','patna','mumbai']
locations_dict = {'delhi':'delhi','patna':'ptn','mumbai':'vrv'}
# logging.info("This is a debug message")


for x in locations:
    if os.path.exists(os.path.join(target,x)) == False:
        os.mkdir(os.path.join(target,x))
    for y in types_frames:
        if os.path.exists(os.path.join(target,x,y)) == False:
            os.mkdir(os.path.join(target,x,y))


# pd.read_csv('caz_lgs.log',delimiter=";",header=None)
import shutil
now_timestamp = datetime.now()
minus_tmstp = now_timestamp - timedelta(minutes=25)
format_timestamp = minus_tmstp.strftime("%Y%m%dT%H%M")
for x in locations:
    for y in types_frames:
        link = f"https://mausam.imd.gov.in/Radar/{y}_{locations_dict[x]}.gif"
        resp = requests.get(link, stream=True)
        if resp.status_code == 200:
            file_name = f'{y}_{x}_{format_timestamp}.gif'
            with open(os.path.join(target,x,y,file_name),'wb') as f:
                print("This")
                resp.raw.decode_content = True
                shutil.copyfileobj(resp.raw, f)
                logging.info(f"{y};{x};{now_timestamp};{file_name}")
        else:
            print(link)
            print("Cannot Retreat Frame")


