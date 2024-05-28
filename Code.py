import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
import plotly.express as px
from google.cloud import storage
from google.oauth2 import service_account
from io import BytesIO


import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title=" Electronic Music Data Discovery", page_icon="🎧")

st.title("My First Python Project: Understanding Electronic Music Characteristics")

# Main text content
st.write("""
This is my first Python project, which is focused on the discovery phase of working with a new dataset. This shows some initial ideas I had about the data and includes commentary on why it does or doesn't work. The goal is for a bit of radical 
transparency around how I think through a new data project and what does and doesn't matter to me. As I learn more Python and start getting into machine learning and neural network components, my approach will evolve.

Questions or comments about what I'm doing here? You can email me at hello@uwsthoughts.com

### Why Beatport and Spotify music data? Don’t you work in advertising?
""")

with st.expander("Technical Details"):
    st.write("""
    **Short Term Infrastructure:**
    Short Term Infrastructure:
    Initial deployment uses GCP cloud storage with authentication via a service account that has secret keys stored in Streamlit's secret key feature. I'm avoiding options like BigQuery or MySQL databases because I'm on a budget. 
    
    I did a lot of the initial heavy lifting around joining, organizing, and cleaning the data using free compute credits I had with Google Colab. I took what was initially 11GB of data and shaped it into what is now a 3GB Beatport fact table. 
    
    I'm purposefully working with a large baseline dataset so I can figure out how to effectively move it around and use it. 
    
    **Long Term Infrastructure:**
    I am working on my preferred AWS long term infrastructure. After a lot of research and even more trial and error, I settled on a one year paid-upfront reserved M5DN Large as the core of my long term needs: Instance memory: 8GB; Compute Units: 0; VCPUs: 2; storage: 76GB SSD; performance: 25GB.
    
    As a frame of reference, the P3 High Performance GPU Double Extra Large, which is on the cheaper end for full year reserved machine learning instances, will cost you $17,000 for one year up front. Instance memory: 32GB; compute units: 31; VCPUs: 8; GPUs: 1; Storage: EBS only; performance: up to 10GB.
    
    For those who either don't like numbers or are new to the show: $17,000 is more than $500
    """)

st.write("""
A few reasons for this:
- I love house and techno music. Actually, I’m obsessed with it. The subscription I’ve had the longest is YouTube Premium so I can watch DJ music sets without commercials. 
- Of the 170 accounts I follow on Instagram, 125 are house and techno artists, labels, promoters, or venues. NGL - I think I’ve muted everyone else #savage 
- I was talking to someone recently and they were telling me about a project they did around working with students to convey how they feel through music playlists. That inspired me to make this playlist, which is designed as three distinct playlists representing different styles of house and techno I love that all roll up into "3am with me:"
    - [ 
    - [3am at the rave](https://open.spotify.com/playlist/1AuETx4UiJIrlbCFLNfCtX)
    - [3am at Mayan Warrior](https://open.spotify.com/playlist/1AuETx4UiJIrlbCFLNfCtX)
    - [3am at a beach party](https://open.spotify.com/playlist/1AuETx4UiJIrlbCFLNfCtX)
      [3am with me](https://open.spotify.com/playlist/1AuETx4UiJIrlbCFLNfCtX)
      ]

      [
      	[At the rave]
        [At Mayan Warrior]
	[At a beach party]
      with me]
""") 

# Spotify embed
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

with st.expander("Documentation and Next Steps"):
    st.write("""
    **Overview:**
    This first release is presenting ideas "as-is" to bring transparency to the flow of experimenting with ideas that turn out to be good or bad. All charts are discovery first-drafts so minimal effort has been focused on things like making label_name be Label Name instead. That's really a last mile change for when your product is going into the wild as a final product. 
    
    This early on, I'm focused on what the data looks like and shaping future ideas to test out. Danceability by subgenre? Maybe not as interesting as I thought it could be. By label? Worth getting into more. Things like that.

    All charts have a Commentary dropdown where you can read my thoughts and potential ideas.

    **Data Sources:**
    I used this dataset from Kaggle:
    - [10M Beatport tracks & Spotify audio features](https://www.kaggle.com/datasets/mcfurland/10-m-beatport-tracks-spotify-audio-features)

    That data has this license:
    - [Open Data Commons Open Database License (ODbL) v1.0](http://opendatacommons.org/licenses/odbl/1.0/)

    **Metrics:**
    Metrics definitions come from Spotify. Documentation can be found here:
    - [Spotify Web API Reference](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)

    A one-sheet with definitions can be found here:
    - [What do the audio features mean?](https://help.spotontrack.com/article/what-do-the-audio-features-mean)

    **Next steps:**
    - This Streamlit site will have a short life as I'm standing up a custom website that better reflects how I want to do things. That's coming in the next few weeks so this site here is more or less out of the box.
    """)


#gcp setup and read data
credentials = service_account.Credentials.from_service_account_info(st.secrets["gcp_service_account"])
client = storage.Client(credentials=credentials)

@st.cache_data(ttl=None)
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

# Filter selections
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

with st.expander("Commentary"):
    st.write("""

OK, well, this is not very helpful, is it? It has a lot of noise because there’s no filter on it. Maybe that would make it a bit better. What do you do when the Hindenberg crashes into a Superfund site?
But what would this heat map even tell me that’s valuable? I saw it as an option in the documentation and thought “oh that could be cool” and, well, I was wrong. 

This brings me to the original sin of a ton of data visualizations I see: too much effort into making it look nice and minimal thought 
into effectively and efficiently conveying the data. If your chart requires an explanation beyond what the underlying data is then you’ve done it wrong. Assuming the reader generally knows the data, they should be able to understand the chart without you in the room. If they can’t: you’ve done it wrong. Often times, data can be effectively conveyed in two written sentences. 

Which brings me to another sin: PowerPoint presentations for data (or in general). They create a dynamic where someone is 
just talking at you for a while and creates no space for a conversation. The chart they don’t want you to see? In the appendix, 
if there at all. The question you should ask yourself when someone is giving a PowerPoint presentation is: what are they not telling 
me and what are their motives for not telling me? 
	

"""
)

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

with st.expander("Commentary"):
    st.write("""

This one is visually pretty but still not telling a whole lot. The Y-axis should have another decimal place for sure. These 
subgenres aren't changing as much as I expected over time. Is it the way the metric is calculated or have these subgenres really not changed? 

This brings me to another place where people go wrong with data: accepting the premise of the data in front of you. 
One of my first questions when I see a metric like danceability (as defined by Spotify) is: how exactly is this being defined? 
If all songs from a certain label or certain artists are automatically assigned a certain value then you can have data that looks like this.

You should question how the numbers in front of you came together before questioning what they show. This exercise will help you separate 
the BS metrics from the valuable ones and let you assigned your own weight to them. Just because someone says a metric is valuable doesn't mean 
it actually is.

"""
)

st.write("Average Energy by Subgenre")
plot_scatter(energy_subgenres, selected_energy_subgenres, "Average Energy by Subgenre", "Energy")

with st.expander("Commentary"):
    st.write("""

This suffers from the same underlying issues as the bar charts above, except also less interesting to look at. The data isn't 
changing much and this could be summarized in one written sentence with a support data table for reference.

"""
)

st.write("Average Danceability by Record Label")
plot_bar(dance_labels, selected_labels, "Average Danceability by Record Label", "Danceability")

with st.expander("Commentary"):
    st.write("""

Now this is pretty interesting. There's more variatation across the years for different labels, which speaks to trends within 
the music they're putting out. I would be interested to see data like this alongside how many people are listening to their music 
over time to see if there's a relatonship between popularity and degrading danceability. I'm going to see if there's a way to bring in 
Beatport or Spotify listening metrics. 

Still, conveying drops as just raw points instead of creating a contextual reference of some sort ("this is a drop of 10%") makes 
it difficult to assess true value. Is it statistically significant? Worthy of digging into more. Also worth seeing the trends by artists 
within these labels to see if there's something going on there. Not sure what I'm after on that front. Maybe the arrival or departure of a 
popular aritst changes things?

"""
)

st.write("Average Energy by Record Label")
plot_scatter(energy_labels, selected_labels, "Average Energy by Record Label", "Energy")

with st.expander("Commentary"):
    st.write("""

This is supposed to be a scatterplot, which isn't working that great with a filter on it. Scatterplots are less about specific data points and more 
about the trend of ostensibly similar datapoints. This is where I would like to see song-level trends for labels to see if that hunch is true or not. 
If there was a shift in a specific time frame, I can focus in on what happened in that window to drive it.

This leads me to my final point: data projects will always have periods of expanding and narrowing scope. You have a hunch, you chase it for a bit, it 
either works out or you go in a different direction. Moving linearally from A to Z without repeating some letters means you probably missed something. 
You should be in pursuit of truth, regardless of whether it confirms or dislodges your previously held beliefs. 

If you live in a massive vortex of delusion where you are right and everyone else just doesn't get it, the quality of your work will ienvtiably decline. 
It's hard to think of an effective search for truth and understanding that didn't involve being wrong a few times along the way. 

If you're afraid to have your ideas or assumptions challenged on the merits, my question is: why? 

"""
)
