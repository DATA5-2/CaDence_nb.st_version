import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import matplotlib.pyplot as plt
import wordcloud
from wordcloud import WordCloud
import numpy as np


#######################  Page Config
st.set_page_config(
    page_title="CaDence",
    page_icon= "🎶",
    layout="wide",
    initial_sidebar_state="expanded")

alt.themes.enable("dark")

#######################
# CSS styling
st.markdown("""
<style>

[data-testid="block-container"] {
    padding-left: 2rem;
    padding-right: 2rem;
    padding-top: 1rem;
    padding-bottom: 0rem;
    margin-bottom: -7rem;
}

[data-testid="stVerticalBlock"] {
    padding-left: 0rem;
    padding-right: 0rem;
}

[data-testid="stMetric"] {
    background-color: #393939;
    text-align: center;
    padding: 15px 0;
}

[data-testid="stMetricLabel"] {
    display: flex;
    justify-content: center;
    align-items: center;
}

[data-testid="stMetricDeltaIcon-Up"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

[data-testid="stMetricDeltaIcon-Down"] {
    position: relative;
    left: 38%;
    -webkit-transform: translateX(-50%);
    -ms-transform: translateX(-50%);
    transform: translateX(-50%);
}

</style>
""", unsafe_allow_html=True)


#######################
# Load data
omega_raw = pd.read_json('data/omega_raw.json', lines=True)
est_df = pd.read_json('data/est_df.json', lines=True)
cst_df = pd.read_json('data/cst_df.json', lines=True)
mst_df = pd.read_json('data/mst_df.json', lines=True)
pst_df = pd.read_json('data/pst_df.json', lines=True)
hst_df = pd.read_json('data/hst_df.json', lines=True)


#######################
# Sidebar

with st.sidebar:
    st.header('Time Zone and Week Controls')
    ##### Defaults Below
    present=['Present']
    allPlaces=['EST','CST','MST','PST','HST']
    ###### Button Select
    sb_tz = st.multiselect("Select one or more options:",
        ['EST','CST','MST','PST','HST'], key='time zone')
    
    all_options = st.button("Select all Time Zones")
    if all_options:
        sb_tz = allPlaces

    st.header('Week')
    sb_wk = st.multiselect("Choose a Week",['Present','Week 1','Week 2', 'Week 3','Week 4','Week 5'], key='option_2')
    
    all_options_w = st.button("Select all Weeks")
    if all_options_w:
        sb_wk = ['Week 1', 'Week 2', 'Week 3','Week 4','Week 5','Present']
    
################ Begin DF corelation to feed into Dashboard
    df_seled_wk =pd.DataFrame(columns=['artist', 'song','duration','ts','sessionId','level','state','userAgent','userId','firstName','gender','week','time_zone'])
#### Have 'present as default
    if sb_wk==[]:
        sb_wk=present
    else:
        sb_wk=sb_wk
#### If no tz, then all tz to avoid errors before selections are made.
    if sb_tz==[]:
        sb_tz=allPlaces
###### If selections are made, go with the selections
    else:
        sb_tz=sb_tz
#### Now that there's a df with the right tz, narrow down to the ones with the right weeks we want    
    for i in sb_tz:
        select_tz= omega_raw.loc[omega_raw['time_zone'] == i]
        df_seled_wk=pd.concat([df_seled_wk,select_tz])
    df_selected_week= df_seled_wk[df_seled_wk['week'].isin(sb_wk)]

    # color_theme_list = ['blues', 'cividis', 'greens', 'inferno', 'magma', 'plasma', 'reds', 'rainbow', 'turbo', 'viridis']
    # selected_color_theme = st.selectbox('Select a color theme', color_theme_list)


#######################
# Plots

#1st Column - Plan level and Device Type

######## Plan Level

def paid_level(df_selected_week):
    paidlev = df_selected_week.groupby('userId')['level'].first().value_counts()

    #Titles
    label_tz = ", ".join(df_selected_week['time_zone'].unique())
    label_wk = ", ".join(df_selected_week['week'].unique())

    ## Horizontal bar chart. 
    fig, ax = plt.subplots(figsize=(8, 6))
    paidlev.plot(kind='barh', stacked=True, color=['#2ca02c', '#d62728'], ax=ax)
    ax.set_xlabel("Count")
    ax.set_ylabel("Level")
    ax.set_title(f"Paid vs Free Accounts in {label_tz} during {label_wk}") #here we need to adjust the labels to do not show all the weeks
    ax.grid(axis='x', linestyle='--', alpha=0.7)
    return fig

####### Devices

def most_used_platform(df_selected_week):
    platform=df_selected_week.groupby('userId')['userAgent'].first().value_counts()
    ##Donut Chart
    fig = px.pie(platform, names=platform.index, values=platform, hole=.6)
    fig.update_traces(textinfo='percent+label')
    # fig.update_layout(title_text=f"Most Used Platforms in {df_selected_tz.iloc[1,12]} in {selected_week}")
    return fig

#2nd Column - - User Map, Gender and Summary Table

####### State user Counts (Maisha and Sharmin)
#INSERT CODE

####### Gender
def get_gender(df_selected_week):
  gender_df = df_selected_week.groupby('userId')['gender'].first().value_counts()
  label_tz = ", ".join(df_selected_week['time_zone'].unique())
  label_wk = ", ".join(df_selected_week['week'].unique())
  ###### Vertical bar graph
  fig, ax = plt.subplots(figsize=(8, 6))
  gender_df.plot(kind='bar', stacked=True, color=['#1f77b4', '#ff7f0e'], ax=ax)
  ax.set_xlabel("Gender")
  ax.set_ylabel("Counts")
  ax.set_title(f"Gender Counts in {label_tz} during {label_wk}")
  ax.grid(axis='x', linestyle='--', alpha=0.7)
  return fig




#3rd Column -  Top 10 Songs, Duration and Artists

####### Song
def most_played(df_selected_week):
  mps=df_selected_week['song'].value_counts().nlargest(10).reset_index()
  mps.columns = ['Song', 'Plays']  
  mps['Rank'] = mps.index + 1  
  mps = mps[['Rank', 'Song', 'Plays']]
  return mps

####### Duration



####### Artist
def most_played_artist(df_selected_week):
  mpa=df_selected_week['artist'].value_counts()
# WordCloud 
  wc = WordCloud(background_color='white', colormap='winter', width=800, height=400).generate_from_frequencies(mpa)
  plt.figure(figsize=(10, 7))
  plt.imshow(wc, interpolation='bilinear')
  plt.axis("off")
  st.pyplot(plt)



#######################
# Dashboard Main Panel
#######################
col = st.columns((1, 5, 2), gap='medium') #Divide the dashboard into 3 columns - inside the () are display the relative size of the columns (portion)

#1st Column - Plan level and Device Type
with col[0]:

####PLAN LEVEL

    st.markdown('#### Account Levels')
    level_chart = paid_level(df_selected_week)

    if level_chart:
        st.pyplot(level_chart, use_container_width=True)


####DEVICES

    st.markdown('#### Platforms')
    donut = most_used_platform(df_selected_week)
    st.plotly_chart(donut, use_container_width=True)

#2nd Column - User Map, Gender and Summary Table

with col[1]:

####USER MAP

####GENDER
    st.markdown('#### Gender Distribution')
    gender_chart = get_gender(df_selected_week)

    if gender_chart:
        st.pyplot(gender_chart, use_container_width=True)

####SUMMARY TABLE



    
#3rd Column - Top 10 Songs, Duration and Artists
with col[2]:

####TOP SONGS
    st.markdown('#### Most Played Songs (Top 10)')
    most_played_songs = most_played(df_selected_week)

    if most_played_songs is not None:
        st.table(most_played_songs.reset_index(drop=True))

####DURATION
    st.markdown('#### Hours Listening')
   

####TOP ARTISTS
    st.markdown('#### Top Artists')
    wordcloud_chart = most_played_artist(df_selected_week)
    if wordcloud_chart:
        st.pyplot(plt)
    
    
    
#  with st.expander('About', expanded=True):
#     st.write('''
#             - Data: [U.S. Census Bureau](https://www.census.gov/data/datasets/time-series/demo/popest/2010s-state-total.html).
#             - :orange[**Gains/Losses**]: states with high inbound/ outbound migration for selected year
#             - :orange[**States Migration**]: percentage of states with annual inbound/ outbound migration > 50,000
#             ''')