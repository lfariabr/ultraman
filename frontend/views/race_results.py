import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import plotly.express as px

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.utils.results_controller import db_controller
from backend.helpers.results_controler import display_columns

@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_data():
    """Load and merge all data with caching"""
    results = pd.DataFrame(db_controller.get_all_results("athletes_results"))
    races = pd.DataFrame(db_controller.get_all_results("athletes_race"))
    athletes = pd.DataFrame(db_controller.get_all_results("athletes_athlete"))
    
    # Merge data
    df_results_races = pd.merge(
        results,
        races,
        left_on='race_id',
        right_on='id',
        how='left',
        suffixes=('', '_race')
    )
    
    df_results_athletes = pd.merge(
        df_results_races,
        athletes,
        left_on='athlete_id',
        right_on='id',
        how='left',
        suffixes=('', '_athlete')
    )
    
    return df_results_athletes[display_columns]



def plot_participants_by_year(df):
    """Plot total participants by year, handling data types explicitly and ensuring correct plotting."""
    
    # Convert the 'race_date' to year and ensure it's an integer
    df['year'] = pd.to_datetime(df['race_date']).dt.year
    df['year'] = df['year'].astype(int)

    # Group participants by year and count entries
    participants_by_year = df.groupby('year').size().reset_index(name='participants')

    # Ensure 2020 is removed if it has no data
    participants_by_year = participants_by_year[participants_by_year['year'] != 2020]

    # Display the DataFrame for verification
    st.dataframe(participants_by_year)

   # Creating a graphic to display participantes by year
    fig = px.bar(
        participants_by_year,
        x='year',
        y='participants',
        title='Total Participants by Year',
        labels={'year': 'Ano', 'participants': 'Número de Participantes'}
    )

    return fig


def plot_age_distribution(df):
    """Plot age distribution of participants"""
    df['age'] = (datetime.now() - pd.to_datetime(df['date_of_birth'])).dt.days // 365
    df = df.loc[df['age'] > 0]
    st.dataframe(df)
    fig = px.histogram(
        df,
        x='age',
        title='Age Distribution of Participants',
        labels={'age': 'Age', 'count': 'Number of Participants'},
        nbins=20
    )
    fig.update_layout(bargap=0.1)
    return fig

def time_to_minutes(time_str):
    """Convert time string to minutes"""
    if pd.isna(time_str):
        return None
    try:
        h, m, s = map(float, time_str.split(':'))
        return h * 60 + m + s / 60
    except:
        return None

def plot_average_times(df):
    """Plot average times for each segment"""
    segments = {
        'Swim': 'race_swim_10km_time',
        'Bike': 'race_bike_276km_time',
        'Run': 'race_run_84km_time',
        'Overall': 'race_overall_time'
    }

    avg_times = []
    for segment, column in segments.items():
        df[f'{column}_minutes'] = df[column].apply(time_to_minutes)
        avg_time = df[f'{column}_minutes'].mean()
        if avg_time is not None:
            avg_times.append({
                'segment': segment,
                'average_time': avg_time
            })

    df_avg_times = pd.DataFrame(avg_times)
    st.dataframe(df_avg_times)
    
    fig = px.bar(
        df_avg_times,
        x='segment',
        y='average_time',
        title='Average Time by Segment (minutes)',
        labels={'segment': 'Segment', 'average_time': 'Average Time (minutes)'}
    )
    return fig

def plot_top_athletes(df):
    """Plot top 10 athletes by participation"""
    athlete_participations = df.groupby(
        ['athlete_id', 'first_name', 'eternal_number']
    ).size().reset_index(name='participations')
    
    top_10_athletes = athlete_participations.nlargest(10, 'participations')
    st.dataframe(top_10_athletes)
    
    fig = px.bar(
        top_10_athletes,
        x='first_name',
        y='participations',
        title='Top 10 Athletes by Participation',
        labels={'first_name': 'Athlete', 'participations': 'Number of Participations'},
        hover_data=['eternal_number']
    )
    fig.update_layout(xaxis_tickangle=-45)
    return fig

def race_results_page():
    st.title("Resultado das Provas")
    st.subheader("🏊🚴🏃‍♂️")

    try:
        # Load data with caching
        with st.spinner("Loading data..."):
            df = load_data()
            
            if df.empty:
                st.info("No data found")
                return
            
            st.markdown("#### Resultados")
            st.dataframe(df)

            # Create tabs for visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "Participants by Year",
                "Age Distribution",
                "Average Times",
                "Top Athletes"
            ])

            with tab1:
                st.plotly_chart(plot_participants_by_year(df), use_container_width=True)

            with tab2:
                st.plotly_chart(plot_age_distribution(df), use_container_width=True)

            with tab3:
                st.plotly_chart(plot_average_times(df), use_container_width=True)

            with tab4:
                st.plotly_chart(plot_top_athletes(df), use_container_width=True)

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please check database connection and try again")