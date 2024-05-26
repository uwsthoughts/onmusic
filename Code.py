import pandas as pd
import streamlit as st
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO

# Streamlit title
st.title('Data Visualization from Google Cloud Storage')

# Use Streamlit secrets to access Google Cloud Storage
gcp_credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = storage.Client(credentials=gcp_credentials)

# Function to read CSV from Google Cloud Storage
def read_gcs_csv(bucket_name, file_name):
    bucket = client.get_bucket(bucket_name)
    blob = bucket.blob(file_name)
    data = blob.download_as_bytes()
    return pd.read_csv(BytesIO(data))

# Specify your Google Cloud Storage bucket and file names
bucket_name = 'love-uwsthoughts'
file_names = {
    'agg_dance_sbg_avg': 'agg_dance_sbg_avg.csv',
    'agg_label_eng_dan_avg': 'agg_label_eng_dan_avg.csv',
    'agg_sbg_eng_avg': 'agg_sbg_eng_avg.csv'
}

# Load files into dataframes
agg_dance_sbg_avg = read_gcs_csv(bucket_name, file_names['agg_dance_sbg_avg'])
agg_label_eng_dan_avg = read_gcs_csv(bucket_name, file_names['agg_label_eng_dan_avg'])
agg_sbg_eng_avg = read_gcs_csv(bucket_name, file_names['agg_sbg_eng_avg'])

# Ensure 'year' column is treated as an integer
for df in [agg_dance_sbg_avg, agg_label_eng_dan_avg, agg_sbg_eng_avg]:
    df['year'] = df['year'].astype(int)

# Ensure relevant columns are numeric
def ensure_numeric(df, columns):
    for col in columns:
        df[col] = pd.to_numeric(df[col], errors='coerce')
    return df

agg_dance_sbg_avg = ensure_numeric(agg_dance_sbg_avg, ['danceability'])
agg_label_eng_dan_avg = ensure_numeric(agg_label_eng_dan_avg, ['danceability', 'energy'])
agg_sbg_eng_avg = ensure_numeric(agg_sbg_eng_avg, ['energy'])

# Pivot data for plotting
danceability_by_subgenre = agg_dance_sbg_avg.pivot(index='year', columns='subgenre_name', values='danceability')
energy_by_subgenre = agg_sbg_eng_avg.pivot(index='year', columns='subgenre_name', values='energy')
danceability_by_label = agg_label_eng_dan_avg.pivot(index='year', columns='label_name', values='danceability')
energy_by_label = agg_label_eng_dan_avg.pivot(index='year', columns='label_name', values='energy')

# Set default selections for the filters
default_dance_subgenres = ['Melodic Techno', 'Tropical House', 'Organic House']
default_energy_subgenres = ['Melodic Techno', 'Tropical House', 'Organic House']
default_labels_dance_energy = ['Afterlife Records', 'Anjunadeep', 'All Day I Dream']

# Filter default selections to ensure they exist in the options
available_dance_subgenres = danceability_by_subgenre.columns
available_energy_subgenres = energy_by_subgenre.columns
available_labels = danceability_by_label.columns

default_dance_subgenres = [x for x in default_dance_subgenres if x in available_dance_subgenres]
default_energy_subgenres = [x for x in default_energy_subgenres if x in available_energy_subgenres]
default_labels_dance_energy = [x for x in default_labels_dance_energy if x in available_labels]

# Filter widgets
selected_dance_subgenres = st.sidebar.multiselect(
    'Select Subgenres for Danceability',
    options=available_dance_subgenres,
    default=default_dance_subgenres
)

selected_energy_subgenres = st.sidebar.multiselect(
    'Select Subgenres for Energy',
    options=available_energy_subgenres,
    default=default_energy_subgenres
)

selected_labels_dance_energy = st.sidebar.multiselect(
    'Select Labels for Danceability and Energy',
    options=available_labels,
    default=default_labels_dance_energy
)

# Plot the data with filters applied
st.write("Average Danceability by Subgenre")
if selected_dance_subgenres:
    st.line_chart(danceability_by_subgenre[selected_dance_subgenres])
else:
    st.warning("No subgenres selected for Danceability")

st.write("Average Energy by Subgenre")
if selected_energy_subgenres:
    st.line_chart(energy_by_subgenre[selected_energy_subgenres])
else:
    st.warning("No subgenres selected for Energy")

st.write("Average Danceability by Label")
if selected_labels_dance_energy:
    st.line_chart(danceability_by_label[selected_labels_dance_energy])
else:
    st.warning("No labels selected for Danceability")

st.write("Average Energy by Label")
if selected_labels_dance_energy:
    st.line_chart(energy_by_label[selected_labels_dance_energy])
else:
    st.warning("No labels selected for Energy")