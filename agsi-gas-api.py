# Download and visualize data from https://agis.gie.eu
# based on article of CT

import requests
import altair as alt
import pandas as pd
import os
from dotenv import load_dotenv

load_dotenv()

url = 'https://agsi.gie.eu/api'

params = {"country": "de", "from": "2022-01-01", "size": 300}

head = {"x-key": os.environ.get("API_KEY")}

# Download data
resp = requests.get(url=url, params=params, headers=head)
data = resp.json()

if not data['data']:
    exit("Error reading data from api. Check API key.")

# Create pandas dataframe

df = pd.json_normalize(data['data'])
df['full'] = df['full'].astype(float)
df['injection'] = df['injection'].astype(float)
df['withdrawal'] = -df['withdrawal'].astype(float)
df['gasDayStart'] = pd.to_datetime(df['gasDayStart'], errors='coerce')

# craete altair diagram

base = alt.Chart(df).mark_line().encode(x=alt.X('gasDayStart', axis=alt.Axis(title="Datum", format=("%b %Y"))))

line = base.mark_line(color='red').encode(
    y=alt.Y('full', axis=alt.Axis(title="Füllstand [%]"), scale=alt.Scale(padding=0, domain=[-100, 100])))

bar_i = base.mark_bar(color='green').encode(y=alt.Y('injection', axis=alt.Axis(title=" Einspeisung [GWh/d]"), scale=alt.Scale(padding=0, domain=[0, 2500])))
bar_w = base.mark_bar(color='red').encode(y=alt.Y('withdrawal', axis=alt.Axis(title="Entnahme [GWh/d]"),  scale=alt.Scale(padding=0, domain=[-2500, 0])))

bars = bar_i + bar_w
diagram = (line + bars).resolve_scale(y='independent')


diagram.properties(height=600, width=1200, title="Gasspeicher in Deutschland").save('data.html')
