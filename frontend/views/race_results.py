import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
import plotly.express as px
import altair as alt
from backend.utils.time_conversor import time_to_minutes, time_to_hours
import time

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

    # Replace year "2,016" to "2016"
    df['year'] = df['year'].replace(",", "")

    # Group participants by year and count entries
    participants_by_year = df.groupby('year').agg({'id': 'count'}).reset_index()
    participants_by_year.columns = ['Ano', 'Participantes']  # Rename for clarity

    # Ensure 2020 is removed if it has no data
    participants_by_year = participants_by_year[participants_by_year['Ano'] != 2020]

    # st.dataframe(participants_by_year, hide_index=True)
    st.bar_chart(participants_by_year, x='Ano', y='Participantes')

    return participants_by_year


def plot_average_times(df):
    """Plot average times for each segment"""
    segments = {
        'Dia 1': 'race_swim_10km_time',
        'Dia 2': 'race_bike_276km_time',
        'Dia 3': 'race_run_84km_time',
        'Total': 'race_overall_time'
    }

    avg_times = []
    for segment, column in segments.items():
        # Convert time strings to hours and handle missing values
        times = []
        for time_str in df[column].dropna():
            try:
                h, m, s = map(float, time_str.split(':'))
                hours = h + m/60 + s/3600
                times.append(hours)
            except:
                continue
        
        if times:
            avg_time = sum(times) / len(times)
            # Convert to hours and minutes for display
            hours = int(avg_time)
            minutes = int((avg_time - hours) * 60)
            time_str = f"{hours}h {minutes}m"
            avg_times.append({
                'categoria': segment,
                'tempo médio': round(avg_time, 2),
                'tempo_formatado': time_str
            })

    df_avg_times = pd.DataFrame(avg_times)
    
    st.dataframe(df_avg_times, hide_index=True)
        
    # Create the base chart
    chart = alt.Chart(df_avg_times).mark_bar(
        cornerRadius=10,
        height=30
    ).encode(
        x=alt.X('tempo médio:Q', title='Tempo Médio (horas)'),
        y=alt.Y('categoria:N', title=None, sort=['Dia 1', 'Dia 2', 'Dia 3', 'Total']),
        color=alt.Color('categoria:N', 
                       scale=alt.Scale(scheme='blues'),
                       legend=None),
        tooltip=['categoria', 'tempo_formatado']
    ).properties(
        width=600,
        height=200,
        title='Tempo Médio por Dia'
    )
    
    # Add text labels
    text = chart.mark_text(
        align='left',
        baseline='middle',
        dx=5,
        color='white'
    ).encode(
        text='tempo_formatado:N'
    )
    
    # Combine the chart and text
    final_chart = (chart + text)
    
    st.altair_chart(final_chart, use_container_width=True)
    
    # Calculate overall average time for the message
    total_times = []
    for time_str in df['race_overall_time'].dropna():
        try:
            h, m, s = map(float, time_str.split(':'))
            total_times.append(f"{int(h)}:{int(m)}:{int(s)}")
        except:
            continue
    
    return df_avg_times, total_times[0] if total_times else "N/A"

def plot_top_athletes(df_results_athletes):
    """Plot top 10 athletes by participation"""
    # Get participation counts
    athlete_participations = df_results_athletes.groupby(
        ['athlete_id', 'first_name', 'eternal_number']
    ).agg({'id': 'count'}).reset_index()
    
    # Get top 10 and sort
    top_10_athletes = athlete_participations.nlargest(10, 'id').sort_values('id', ascending=False).reset_index(drop=True)
    
    # Rename columns
    top_10_athletes.columns = ['Atleta', 'Nome', 'Número Eterno', 'Participações']
    # Drop column "Atleta"
    top_10_athletes = top_10_athletes.drop(columns=['Atleta'])
    
    # Show the dataframe
    st.dataframe(top_10_athletes, hide_index=True)
    
    return top_10_athletes

def plot_age_distribution(df):
    """Plot age distribution of participants"""
    df['age'] = (datetime.now() - pd.to_datetime(df['date_of_birth'])).dt.days // 365
    df = df.loc[df['age'] > 22]
    
    # Group by age and count participants
    age_counts = df.groupby('age').size().reset_index(name='quantidade')
    
    # st.dataframe(age_counts)
    
    # Create scatter plot using Altair
    import altair as alt
    
    chart = alt.Chart(age_counts).mark_circle(size=60).encode(
        x=alt.X('age:Q', scale=alt.Scale(domain=[22, max(df['age']) + 3])),
        y='quantidade:Q',
        tooltip=['age', 'quantidade']
    ).properties(
        width=600,
        height=400,
        title='Quantidade de Participantes por Idade'
    )
    
    st.altair_chart(chart, use_container_width=True)

    return df

def race_results_page():
    st.title("UB515 - Ultraman Brasil")
    st.subheader("Curiosidades sobre a Prova")
    st.markdown("#### 🏊🚴🏃‍♂️💨")

    try:
        # Load data with caching
        with st.spinner("Carregando os dados... ⌛"):
            time.sleep(5)
            df = load_data()
            
            if df.empty:
                st.info("Nenhum dado encontrado... ⚠️")
                return
            
            # st.markdown("#### Resultados")
            # st.dataframe(df)

            # Create tabs for visualizations
            tab1, tab2, tab3, tab4 = st.tabs([
                "Participantes por Ano",
                "Tempo Médio",
                "Atletas em Destaque",
                "Distribuição de Idade"
            ])

            with tab1:
                st.write("Este evento é único, cujos principais valores são superação, simplicidade, solidariedade, companhia e lealdade, valores representados pelas palavras hawaianas ALOHA (AMOR), OHANA (FAMILIA) e KOKUA (SOLIDARIDADE).")
                plot_participants_by_year(df)
                st.write("### Cruzaram a linha de chegada até agora: ", len(df))

            with tab2:
                avg_times, total_time = plot_average_times(df)
                st.write("### Tempo médio de conclusão da prova: ", "28h")

            with tab3:
                st.write("Uma menção honrosa para os Ultra Atletas que participaram em várias edições do UB515 💌")
                plot_top_athletes(df)

            with tab4:
                
                plot_age_distribution(df)
                df = df.loc[df['age'] > 20]
                # Removing decimal case from age
                st.write("### Idade média dos participantes: ", round(df['age'].mean()))

    except Exception as e:
        st.error(f"Error loading data: {str(e)}")
        st.error("Please check database connection and try again")