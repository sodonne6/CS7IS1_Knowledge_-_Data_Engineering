
import pandas as pd

cols = ["Airport ID","Name","City","Country","IATA","ICAO",
        "Latitude","Longitude","Altitude","Timezone","DST",
        "Tz database time zone","Type","Source"]

df = pd.read_csv("airports.dat", header=None, names=cols)
df = df.replace(r"\\N","", regex=True)  # keep quotes, just clear \N
df.to_csv("airports.csv", index=False)
