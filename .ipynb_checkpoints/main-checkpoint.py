from unicodedata import name
import pandas as pd
import numpy as np
import dash
import plotly.express as px

df = pd.read_csv('bird-window-collision-death.csv')

print(df.head())

fig = px.pie(data_frame=df, names='Genre', values='Japan Sales')

app = dash.Dash()