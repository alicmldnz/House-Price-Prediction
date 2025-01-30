import pandas as pd

csv_files = ["1.2-.csv","375-474.csv","600-799.csv","800-1.199.csv"]

dataframes = []

for file in csv_files:
    df = pd.read_csv(file)
    dataframes.append(df)

merged_df = pd.concat(dataframes, ignore_index=True)

merged_df.to_csv("alldata.csv", index=False)