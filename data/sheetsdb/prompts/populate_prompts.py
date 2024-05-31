import os
import pandas as pd
import csv

def populate_prompts():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(script_dir, 'prompts_sheets.csv')
    print("fetching sheet names from: ",file_path)
    prompts_sheets = pd.read_csv(file_path)
    print("worked till here")
    prompts_sheet_id = "1ygn55doSW6XVAGw1Tp5WEXBswQoqkRZBHUCT8LaXS2U"
    for index, row in prompts_sheets.iterrows():
        row_dict = row.to_dict()
        print("Processing sheet: ",row_dict["name"])
        sheet_link = "https://docs.google.com/spreadsheets/export?id={0}&gid={1}&exportFormat=csv".format(prompts_sheet_id,row_dict["gid"])
        df = pd.read_csv(sheet_link)
        sheet_path = file_path.replace("data\sheetsdb\prompts\prompts_sheets.csv","app\process\{0}\prompts.csv".format(row_dict["app_name"]))
        print("Writing to:",sheet_path)
        df.to_csv(sheet_path, quoting=csv.QUOTE_NONNUMERIC)
        
# populate_prompts()


