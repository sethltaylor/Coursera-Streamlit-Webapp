import streamlit as st
import pandas as pd
import numpy as np

DATA_URL = (
"/home/rhyme/Desktop/Project/Motor_Vehicle_Collisions_-_Crashes.csv
)

st.title("Motor Vechile Collisions in NYC")
st.markdown("Streamlit dashboard to monitor vechile collisions in NYC")

@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': "date/time"}, inplace=True)
    return DATA_URL

data = load_data(10000)

st.subheader('Raw Data')
st.write(data)
