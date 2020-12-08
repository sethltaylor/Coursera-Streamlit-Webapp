import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk
import plotly.express as px

DATA_URL = (
"C:/Users/setht/OneDrive/Desktop/Coursera-Streamlit-Webapp/data/Motor_Vehicle_Collisions_-_Crashes.csv"
)

# Title and markdown for web app
st.title("Motor Vechile Collisions in NYC")
st.markdown("Streamlit dashboard to monitor vechile collisions in NYC")

# Write function to load data and clean up columns/data
# Caching data so it doesn't reload every time
@st.cache(persist=True)
def load_data(nrows):
    data = pd.read_csv(DATA_URL, nrows = nrows, parse_dates = [['CRASH_DATE', 'CRASH_TIME']])
    data.dropna(subset = ['LATITUDE', 'LONGITUDE'], inplace=True)
    lowercase = lambda x: str(x).lower()
    data.rename(lowercase, axis = 'columns', inplace=True)
    data.rename(columns={'crash_date_crash_time': "date/time"}, inplace=True)
    return data

# Load first 100000 rows
data = load_data(100000)
original_data = data

st.header("Where are the most people injured in NYC?")
injured = data['injured_persons']
max_injured = int(injured.max())
injured_people = st.slider("Number of Persons Injured in Vehicle Collisions",0, max_injured)
st.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how="any"))

# slider to filter raw data by time
st.header("How many collisions occur at a given time?")
hour = st.slider("Hour to View", 0,23)
data = data[data['date/time'].dt.hour == hour]
# dynamically changing markdown based on slider
st.markdown("Vehicle Collisions Between %i:00 and %i:00" % (hour, (hour + 1) %24))

#midopint of spatial values for initializing view state
midpoint = (np.average(data['latitude']), np.average(data['longitude']))
#DeckGL 3d map
st.write(pdk.Deck(
    map_style="mapbox://styles/mapbox/light-v9",
    initial_view_state={
    "latitude": midpoint[0],
    "longitude": midpoint[1],
    "zoom": 11,
    "pitch": 50,
    },
    layers=[
    pdk.Layer(
    "HexagonLayer",
    data = data[['date/time', 'latitude', 'longitude']],
    get_position=['longitude', 'latitude'],
    radius=100,
    extruded=True,
    pickable=True,
    elevation_scale=4,
    elevation_range=[0,1000],
    ),
    ],
))

#Histogram breaking down collisions by minute within an hour
st.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour+1) %24))
filtered = data[
    (data['date/time'].dt.hour>= hour) & (data['date/time'].dt.hour < (hour + 1))
]
hist = np.histogram(filtered['date/time'].dt.minute, bins = 60, range=(0,60))[0]
chart_data = pd.DataFrame({'minute': range(60), 'crashes':hist})
fig = px.bar(chart_data, x='minute', y='crashes', hover_data=['minute', 'crashes'], height=400)
st.write(fig)

#Table of top 5 most dangerous streets by inured person type
st.header("Top 5 Most Dangerous Streets by Involved Person Type")
select = st.selectbox('Involved Person Type', ['Pedestrians', 'Cyclists', 'Motorists'])

if select == 'Pedestrians':
    st.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by=['injured_pedestrians'], ascending=False).dropna(how="any")[:5])
elif select == 'Cyclists':
    st.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by=['injured_cyclists'], ascending=False).dropna(how="any")[:5])
else:
    st.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by=['injured_motorists'], ascending=False).dropna(how="any")[:5])

#Give option to display raw data on webapp
if st.checkbox("Show Raw Data?", False):
    st.subheader('Raw Data')
    st.write(data)
