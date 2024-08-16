import pandas as pd
import numpy as np
import os
from math import pi, atan, sinh, cos, log, tan, radians, degrees
import numpy as np
from PIL import Image,ImageDraw
from datetime import datetime,timedelta
import math
import logging
from sqlalchemy import create_engine, text

home_path = os.getcwd()
processed_source = os.path.join(home_path,'target_processed')
image_widths = {'caz':566,'ppi':719,'sri':719}
zoom_levels = {'caz':8.47,'ppi':9.54,'sri':9.54}
map_size = {'caz':250,'ppi':150,'sri':150}

## Database connections
conn_dict = {'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'postgres',
        'USER': 'admin123',
        'PASSWORD': 'tensor123',
        'HOST': 'tensordb1.cn6gzof6sqbw.us-east-2.rds.amazonaws.com',
        'PORT': '5432',}
# Configure logging
logging.basicConfig(filename=os.path.join(home_path,"radar_processed.log"), filemode="w",
                    format="%(asctime)s;%(message)s", level=logging.INFO)

def get_connection(host,port,user,passord,database):
    connection_string = f"postgresql://{user}:{passord}@{host}/{database}"
    db_connect = create_engine(connection_string)
    try:
        with db_connect.connect() as conn:
            conn.execute(text("SELECT 1"))
            print("\n\n---------------------Connection Successful")
            return db_connect
    except Exception as e:
        print("\n\n---------------------Connection Failed")

db_connection = get_connection(host = conn_dict['HOST'],
                              port = conn_dict['PORT'],
                              user = conn_dict['USER'],
                              passord=conn_dict['PASSWORD'],
                              database=conn_dict['NAME'])


def get_timestamp(x):
    return datetime.strptime(x,'%Y%m%dT%H%M')



def get_all_files(processed_source):
    all_files = []
    for location in os.listdir(processed_source):
        if location == "delhi":
            for var in os.listdir(os.path.join(processed_source,location)):
                for file in os.listdir(os.path.join(processed_source,location,var)):
                    if file not in all_files:
                        all_files.append(file)
            df_imgs = pd.DataFrame({'files':all_files})
            df_imgs['var'] = df_imgs['files'].str.split("_").str[0]
            df_imgs['location'] = df_imgs['files'].str.split("_").str[1]
            df_imgs['timestamp'] = df_imgs['files'].str.split("_").str[2].str[:-4]
            df_imgs['timestamp'] = df_imgs['timestamp'].apply(get_timestamp)
            df_imgs.sort_values('timestamp',ascending=False,inplace=True)

            return df_imgs


## load Sites
sites = pd.read_csv(f"{home_path}/delhi_sites.csv")
sites = sites.loc[~sites['latitude'].isna(),:]

## get radar colors data
radar_colors = pd.read_csv(f'{home_path}/radar_colors_delhi.csv')
radar_colors['rgb'] = radar_colors.loc[:,['r','g','b']].values.tolist()

df_imgs = get_all_files(processed_source=processed_source)

## get sample dataframe
sample = df_imgs.loc[df_imgs['timestamp']=='2024-08-08 20:10:00',:]

# print(sample)
## process the image
for index,row in sample.iterrows():
    timestamp = row['timestamp']
    var = row['var']
    file_name = row['files']
    location = row['location']
    file_path = os.path.join(processed_source,location,var,file_name)
    data_df = None
    # print(os.path.exists(file_path))
    for st_index,st_row in sites.iterrows():
        lat = st_row['latitude']
        lon = st_row['longitude']
        locality_id = st_row['localityId']
        
        image = Image.open(file_path)
        key_x = f"{var}_x"
        key_y = f"{var}_y"
        x = st_row[key_x]
        y = st_row[key_y]

        # Get the pixel color value at (x, y)
        pixel_color = image.getpixel((x, y))
        rgb = [pixel_color[0],pixel_color[1],pixel_color[2]]
        a = pixel_color[3]
        color_data = radar_colors[radar_colors['rgb'].apply(lambda x: x == rgb)]
        if len(color_data)>0 and a==255:
            var_data = color_data[var].iloc[0]
            # print(var_data)
        else:
            # print(a)
            var_data = 0

        if type(data_df)==type(None):

            data_df = pd.DataFrame({'timestamp':[timestamp],var:[var_data],'localityId':[locality_id]})

        else:
            new_df = pd.DataFrame({'timestamp':[timestamp],var:[var_data],'localityId':[locality_id]})
            data_df = pd.concat([data_df,new_df],ignore_index=True)
        try:
            data_df.to_sql(name=var,schema='imd',index=False,con=db_connection,if_exists='append')
            logging.info(f"{file_name};{timestamp};Done")
        except Exception as e:
            print(e)
            logging.info(f"{file_name};{timestamp};{e}")