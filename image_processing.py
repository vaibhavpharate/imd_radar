import os
import pandas as pd
from datetime import datetime, timedelta
from PIL import Image
import numpy as np
from scipy.ndimage import distance_transform_edt

# pwd
caz_border_box = (0,153,566,719)
ppi_border_box = (0,0,719,719)
sri_border_box = (0,0,719,719)

delhi_list_colors = ([58,0,160],
[0,25,176],
[0,58,200],
[0,71,255],
[0,121,255],
[26,163,255],
[83,209,255],
[135,241,255],
[135,241,255],
[252,252,122],
[255,230,0],    
[255,189,0],
[255,115,0],
[255,63,0],
[200,0,0],
[200,0,79])


import logging
home_path = '/home/ubuntu/vaib/imd_radar'
target = os.path.join(home_path,'target')
target_processed = os.path.join(home_path,'target_processed')

# Configure logging
logging.basicConfig(filename=os.path.join(home_path,"processed_images.log"), filemode="w",
                    format="%(asctime)s;%(message)s", level=logging.INFO)

## get list of all the available images
all_files = []
for x in os.listdir(target):
    for file_type in os.listdir(os.path.join(target,x)):
        for file_name in os.listdir(os.path.join(target,x,file_type)):
            if file_name not in all_files:
                all_files.append(file_name)

files_available = pd.DataFrame({'files':all_files})

def get_timestamp(x):
    return datetime.strptime(x,"%Y%m%dT%H%M")

files_available['variable'] = files_available['files'].str.split("_").str[0]
files_available['location'] = files_available['files'].str.split("_").str[1]
files_available['timestamp'] = files_available['files'].str.split("_").str[2]
files_available = files_available.loc[files_available['timestamp'].str.len()<=17,:]
files_available['timestamp'] = files_available['timestamp'].str[:-4]

files_available['timestamp'] = files_available['timestamp'].apply(get_timestamp)

unique_locations = list(files_available['location'].unique())
unique_variables = list(files_available['variable'].unique())

for x in unique_locations:
    if os.path.exists(os.path.join(target_processed,x)) == False:
        os.mkdir(os.path.join(target_processed,x))
    for y in unique_variables:
        if os.path.exists(os.path.join(target_processed,x,y)) == False:
            os.mkdir(os.path.join(target_processed,x,y))

# len("20240808T1400.gif")
def process_image(variable,location,timestamp,file_name):
    file_path = os.path.join(target,location,variable,file_name)
    destination_file_name = f"{file_name[:-4]}.png"
    destination_path = os.path.join(target_processed,location,variable,destination_file_name)

    if os.path.exists(destination_path):
        print("File Already processed")
    else:
        image_path = file_path
        image = Image.open(image_path)
        border_box = {'caz':caz_border_box,'ppi':ppi_border_box,'sri':sri_border_box}
        cropped_image = image.crop(border_box[variable])
        image = cropped_image.convert('RGB')
        image_array = np.array(image)
        black_threshold = 10
        black_mask = np.all(image_array <= black_threshold, axis=-1)
        distance, indices = distance_transform_edt(black_mask, return_indices=True)
        image_array[black_mask] = image_array[tuple(indices[:, black_mask])]
        output_image = Image.fromarray(image_array)

        output_image = output_image.convert('RGBA')
        pixels = output_image.load()
        for x in range(output_image.width):
            for y in range(output_image.height):
                r, g, b,a= pixels[x, y]  # Get the RGBA values
                # print([r,g,b])
                if [r, g, b] not in delhi_list_colors:
                    pixels[x, y] = (0, 0, 0, 0) 
        output_image.save(destination_path, format='PNG')
        logging.info(f"{destination_file_name};Done")

now_files = files_available.sort_values('timestamp',ascending=False)
now_files = now_files.loc[now_files['location']=='delhi',:]
for index,row in now_files.iterrows():
    # print("here")
    process_image(variable=row['variable'],
                  timestamp=row['timestamp'],
                  location=row['location'],
                  file_name=row['files']
                  )