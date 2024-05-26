import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO


st.title("My First Python Project: Understanding Beatport Music Trends")

# Main text content
st.write("""
This is my first Python project, which is focused on the the discovery phase of working with a new dataset. This shows some initial ideas I had about the data and includes commentary on why it does or doesn't work. The goal is for a bit a radical 
transparency around how I think through a new data project and what does and doesn't matter to me. As I learn more Python and start getting into machine learning and neural network components, my approach will evolve.

Questions or comments about what I'm doing here? You can email me at kevin@uwsthoughts.com

### Why Beatport and Spotify music data? Don’t you work in advertising?
A few reasons for this:
- I love house and techno music. Actually, I’m obsessed with it. The subscription I’ve had the longest is YouTube premium so I can watch DJ music sets without commercials. 
   - Of the 170 accounts I follow on Instagram, 125 are house and techno artists, labels, promoters, or venues. NGL - I think I’ve muted everyone else #savage 
- I was talking to someone recently and they were telling me about a project they did around working with students to convey how they feel through music playlists. That inspired me to make this playlist, which is designed as three distinct playlists representing different styles of house and techno I love that all roll up into "3am with me:"
   - [3am with me:
   - [3am at the rave]
   - [3am at Mayan Warrior]
   - [3am at a beach party]]
""")

# Embed the Spotify playlist iframe
components.html(
    """
    <iframe src="https://open.spotify.com/embed/playlist/1AuETx4UiJIrlbCFLNfCtX" width="300" height="380" frameborder="0" allowtransparency="true" allow="encrypted-media"></iframe>
    """,
    height=400
)

st.write("""
- I work for the Walt Disney Company so I wanted a dataset and project that would keep me clear of the actual existence or appearance of a conflict of interest. Disney is a big company but it doesn’t compete with Beatport or Spotify. 
   - That said: the opinions expressed here are my own.
""")

# Create an expander for additional content
with st.expander("Reference links"):
    st.write("""
    **Sources:**
    I used this dataset from Kaggle:
    - [10M Beatport tracks & Spotify audio features](https://www.kaggle.com/datasets/mcfurland/10-m-beatport-tracks-spotify-audio-features)

    That data has this license:
    - [Open Data Commons Open Database License (ODbL) v1.0](http://opendatacommons.org/licenses/odbl/1.0/)

    **Metrics:**
    Metrics definitions come from Spotify. Documentation can be found here:
    - [Spotify Web API Reference](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

    A one-sheet with definitions can be found here:
    - [What do the audio features mean?](https://help.spotontrack.com/article/what-do-the-audio-features-mean)
    """)

#gcp setup
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
heatmap = heatmap_data.pivot(index='label_name', columns='metric', values='value')
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
