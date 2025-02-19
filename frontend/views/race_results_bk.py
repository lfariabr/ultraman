import streamlit as st
import pandas as pd
import os
import sys

project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, project_root)

from backend.utils.results_controller import db_controller
from backend.helpers.results_controler import display_columns


def race_results_page():
    st.title("Resultado das Provas")
    st.subheader("🏊🚴🏃‍♂️")

    try:
        # Get data and convert lists to DataFrames
        results = pd.DataFrame(db_controller.get_all_results("athletes_results"))
        races = pd.DataFrame(db_controller.get_all_results("athletes_race"))
        athletes = pd.DataFrame(db_controller.get_all_results("athletes_athlete"))
        
        if len(results) == 0 or len(races) == 0 or len(athletes) == 0:
            st.info("No data found in one or more tables")
            return
            
        ## DEBUGGING
        # st.dataframe(results)        
        # st.dataframe(races)
        # st.dataframe(athletes)

        # First join: results with races (race_id = id)
        df_results_races = pd.merge(
            results,
            races,
            left_on='race_id',
            right_on='id',
            how='left',
            suffixes=('', '_race')
        )

        # Second join: with athletes (athlete_id = id)
        df_results_athletes = pd.merge(
            df_results_races,
            athletes,
            left_on='athlete_id',
            right_on='id',
            how='left',
            suffixes=('', '_athlete')
        )
        
        df_results_races_athletes = df_results_athletes[display_columns]
        
        st.markdown("#### Resultados")
        st.dataframe(df_results_races_athletes)
        
        # # Display column information for debugging
        # if st.checkbox("Show Column Information"):
        #     st.info("Results columns: " + ', '.join(results.columns))
        #     st.info("Races columns: " + ', '.join(races.columns))
        #     st.info("Athletes columns: " + ', '.join(athletes.columns))
        #     st.info("Final DataFrame columns: " + ', '.join(df.columns))

        # AWESOME VIEWS:
        # GRAPHIC 1:
        # TOTAL PARTICIPANTS BY YEAR (from race_date field)

        # GRAPHIC 2:
        # TOTAL PARTICIPANTS BY AGE (from date_of_birth field: today - date_of_birth to calculate athlete's age)

        # GRAPHIC 3:
        # AVERAGE taken time for the three days of the race + overall time
        # "race_swim_10km_time",
        # "race_bike_276km_time",
        # "race_run_84km_time",
        # "race_overall_time",

        # BAR GRAPHIC WITH 
        # TOP 10 most repeated athlete_id grouping by race_edition (a few of them have done 3, 4 ,5 times!)

    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        st.error("Please check your database connection and permissions")