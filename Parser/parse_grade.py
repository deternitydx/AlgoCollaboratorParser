from zipfile import ZipFile
import pandas as pd
from functools import reduce
import os
import sys
from CollaboratorsParser.py import CollaboratorsParser

cp = CollaboratorsParser()

def unzip_and_return_csv(abs_path_zip_folder):
    list_csv_locations=[]
    for root, dirs, files in os.walk(abs_path_zip_folder):
        for file in files:
            if cp._is_filetype(".zip", file):
                abs_file_path = os.path.join(root, file)
                cp._extract(abs_file_path, root)

    for root, dirs, files in os.walk(abs_path_zip_folder):
        for each_dir in dirs:
            inner_path = os.path.join(abs_path_zip_folder, each_dir)
            for r, d, f in os.walk(inner_path):
                for file in f:
                    if cp._is_filetype(".csv", file):
                        list_csv_location.append(os.path.join(inner_path, file))

    return list_csv_location

def parse_grade(list_of_csv_locations):
    list_df=[]
    for file in list_of_csv_locations:
        df = pd.read_csv(file, sep=',',engine='python',skiprows = [0,1])
         #extract the computing id and grade columns
        list_df.append(df.iloc[:,[0,4]])
    # merge all panda frames into one by the computing id
    df_f = reduce(lambda x, y: pd.merge(x, y, on = 'Display ID'), list_df)
    df_f.to_csv("grades_all.csv")


parse_grade(unzip_and_return_csv(_))