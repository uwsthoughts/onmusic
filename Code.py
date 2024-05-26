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
    return pd.read_csv(BytesIO(data))

# Load data, ensuring 'year' is numeric and converting danceability/energy to numeric
data_files = {
    'dance': 'agg_dance_sbg_avg.csv',
    'label': 'agg_label_eng_dan_avg.csv',
    'energy': 'agg_sbg_eng_avg.csv'
}
data = {name: (df.astype({'year': int})
                .assign(**{col: pd.to_numeric(df[col], errors='coerce') for col in ['danceability', 'energy'] if col in df}))
        for name, df in (read_gcs_csv('love-uwsthoughts', file) for file in data_files.values())}

# Pivot data for plotting
dance_subgenres = data['label'].pivot(index='year', columns='label_name', values='danceability')
energy_subgenres = data['energy'].pivot(index='year', columns='subgenre_name', values='energy')
dance_labels = data['label'].pivot(index='year', columns='label_name', values='danceability')
energy_labels = data['label'].pivot(index='year', columns='label_name', values='energy')

# Filter selections based on available data
default_options = {
    'dance_subgenres': ['Melodic Techno', 'Tropical House', 'Organic House'],
    'energy_subgenres': ['Melodic Techno', 'Tropical House', 'Organic House'],
    'labels': ['Afterlife Records', 'Anjunadeep', 'All Day I Dream']
}
available_options = {
    'dance_subgenres': list(dance_subgenres.columns),
    'energy_subgenres': list(energy_subgenres.columns),
    'labels': list(dance_labels.columns)
}
selected_options = {key: [x for x in defaults if x in available] for key, (defaults, available) in default_options.items()}

# Sidebar filter widgets
selected_dance_subgenres = st.sidebar.multiselect(
    'Select Subgenres for Danceability',
    options=available_options['dance_subgenres'],
    default=selected_options['dance_subgenres']
)
selected_energy_subgenres = st.sidebar.multiselect(
    'Select Subgenres for Energy',
    options=available_options['energy_subgenres'],
    default=selected_options['energy_subgenres']
)
selected_labels = st.sidebar.multiselect(
    'Select Labels for Danceability and Energy',
    options=available_options['labels'],
    default=selected_options['labels']
)

# Radar chart for recent data
radar_data = data['label'][data['label']['year'] == data['label']['year'].max()][['label_name', 'danceability', 'energy']].melt(id_vars='label_name', var_name='metric', value_name='value')
fig = px.line_polar(radar_data, r='value', theta='metric', color='label_name', line_close=True, title="Danceability vs. Energy")
st.plotly_chart(fig)

# Plot data with filters applied
def plot_data(data_pivot, selected, title):
    if selected:
        st.line_chart(data_pivot[selected])
    else:
        st.warning(f"No selections for {title}")

st.write("Average Danceability by Subgenre")
plot_data(dance_subgenres, selected_dance_subgenres, "Danceability")

st.write("Average Energy by Subgenre")
plot_data(energy_subgenres, selected_energy_subgenres, "Energy")

st.write("Average Danceability by Record Label")
plot_data(labels, selected_labels, "Danceability")

