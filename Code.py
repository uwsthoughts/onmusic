import pandas as pd
import streamlit as st
import plotly.express as px
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO

# Streamlit title and Google Cloud setup
st.title('My First Python Deployment: A Review of Beatport Music Data')
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = storage.Client(credentials=credentials)

# Function to read CSV from Google Cloud Storage
def read_gcs_csv(bucket_name, file_name):
    data = client.bucket(bucket_name).blob(file_name).download_as_bytes()
    df = pd.read_csv(BytesIO(data))
    if 'year' in df.columns:
        df['year'] = df['year'].astype(int)
    if 'danceability' in df.columns:
        df['danceability'] = pd.to_numeric(df['danceability'], errors='coerce')
    if 'energy' in df.columns:
        df['energy'] = pd.to_numeric(df['energy'], errors='coerce')
    return df

# Load data
data_files = {'dance': 'agg_dance_sbg_avg.csv', 'label': 'agg_label_eng_dan_avg.csv', 'energy': 'agg_sbg_eng_avg.csv'}
data = {name: read_gcs_csv('love-uwsthoughts', file) for name, file in data_files.items()}

# Pivot data for plotting
dance_subgenres = data['dance'].pivot(index='year', columns='subgenre_name', values='danceability')
energy_subgenres = data['energy'].pivot(index='year', columns='subgenre_name', values='energy')
dance_labels = data['label'].pivot(index='year', columns='label_name', values='danceability')
energy_labels = data['label'].pivot(index='year', columns='label_name', values='energy')

# Filter selections based on available data
default_options = {'dance_subgenres': ['Melodic Techno', 'Tropical House', 'Organic House'], 'energy_subgenres': ['Melodic Techno', 'Tropical House', 'Organic House'], 'labels': ['Afterlife Records', 'Anjunadeep', 'All Day I Dream']}
available_options = {key: list(data.columns) for key, data in zip(default_options, [dance_subgenres, energy_subgenres, dance_labels])}
selected_options = {key: [x for x in default_options[key] if x in available_options[key]] for key in default_options}

# Sidebar filter widgets
selected_dance_subgenres = st.sidebar.multiselect('Select Subgenres for Danceability', options=available_options['dance_subgenres'], default=selected_options['dance_subgenres'])
selected_energy_subgenres = st.sidebar.multiselect('Select Subgenres for Energy', options=available_options['energy_subgenres'], default=selected_options['energy_subgenres'])
selected_labels = st.sidebar.multiselect('Select Labels for Danceability and Energy', options=available_options['labels'], default=selected_options['labels'])

# Heatmap for recent data
recent_data = data['label'][data['label']['year'] == data['label']['year'].max()][['label_name', 'danceability', 'energy']]
heatmap_data = recent_data.melt(id_vars='label_name', var_name='metric', value_name='value')
heatmap = heatmap_data.pivot('label_name', 'metric', 'value')
st.plotly_chart(px.imshow(heatmap, aspect='auto', title="Heatmap of Danceability and Energy for Most Recent Year"))

# Plot data with filters applied
def plot_bar(data_pivot, selected, title, y_axis):
    if selected:
        df = data_pivot[selected].reset_index().melt(id_vars='year', var_name='category', value_name=y_axis)
        st.plotly_chart(px.bar(df, x='year', y=y_axis, color='category', barmode='group', title=title))
    else:
        st.warning(f"No selections for {title}")

def plot_scatter(data_pivot, selected, title, y_axis):
    if selected:
        df = data_pivot[selected].reset_index().melt(id_vars='year', var_name='category', value_name=y_axis)
        st.plotly_chart(px.scatter(df, x='year', y=y_axis, color='category', title=title))
    else:
        st.warning(f"No selections for {title}")

st.write("Average Danceability by Subgenre")
plot_bar(dance_subgenres, selected_dance_subgenres, "Average Danceability by Subgenre", "Danceability")

st.write("Average Energy by Subgenre")
plot_scatter(energy_subgenres, selected_energy_subgenres, "Average Energy by Subgenre", "Energy")

st.write("Average Danceability by Record Label")
plot_bar(dance_labels, selected_labels, "Average Danceability by Record Label", "Danceability")

st.write("Average Energy by Record Label")
plot_scatter(energy_labels, selected_labels, "Average Energy by Record Label", "Energy")
