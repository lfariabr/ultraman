import streamlit as st
import os
import sys
from views.race_results import race_results_page

# Add the project root to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from backend.utils.results_controller import db_controller

# Configure the app
st.set_page_config(
    page_title="UB515",
    page_icon="🇧🇷",
    layout="wide",
    initial_sidebar_state='collapsed'
)

def main():
    # Sidebar
    st.sidebar.header("Navigation")
    page = st.sidebar.radio("Choose a page", [
        # "Database Explorer",
        "Races",
    ])

    if page == "Races":
        race_results_page()

    elif page == "Database Explorer":
        database_explorer_page()

    else:
        st.warning("Please select a page")

def database_explorer_page():
    st.header("Database Explorer")

    try:
        # Get all tables in the database
        tables = db_controller.get_all_tables()
        
        if not tables:
            st.warning("No tables found in the database")
            return

        # Let user select a table
        selected_table = st.selectbox("Select a table to explore", tables)
        
        if selected_table:
            # Special handling for athletes_results table
            if selected_table == "athletes_results":
                display_athletes_results()
            else:
                display_generic_table(selected_table)

    except Exception as e:
        st.error(f"Error accessing database: {str(e)}")
        st.error("Please check your database connection and permissions")

def display_athletes_results():
    """Special handling for athletes_results table"""
    st.subheader("Athletes Results")
    
    try:
        # Get initial data
        results = db_controller.get_all_results("athletes_results")
        
        if not results:
            st.info("No athlete results found")
            return
        
        # Create filter options
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Get unique athlete IDs
            athlete_ids = ["All"] + sorted(list(set(str(r['athlete_id']) for r in results if 'athlete_id' in r)))
            selected_athlete = st.selectbox("Select Athlete ID", athlete_ids)
        
        with col2:
            # Get unique years
            years = ["All"] + sorted(list(set(str(r['year']) for r in results if 'year' in r)))
            selected_year = st.selectbox("Select Year", years)
        
        with col3:
            # Get unique events if available
            events = ["All"]
            if 'event' in results[0]:
                events += sorted(list(set(str(r['event']) for r in results if r['event'])))
            selected_event = st.selectbox("Select Event", events)
        
        # Apply filters
        filters = {}
        if selected_athlete != "All":
            filters["athlete_id"] = int(selected_athlete)
        if selected_year != "All":
            filters["year"] = int(selected_year)
        if selected_event != "All" and 'event' in results[0]:
            filters["event"] = selected_event
        
        # Get filtered results
        filtered_results = db_controller.get_results_by_filter("athletes_results", filters) if filters else results
        
        if filtered_results:
            st.subheader("Results")
            st.dataframe(filtered_results)
            
            # Add statistics
            st.subheader("Statistics")
            col1, col2, col3 = st.columns(3)
            
            with col1:
                st.metric("Total Results", len(filtered_results))
            
            with col2:
                if 'position' in filtered_results[0]:
                    valid_positions = [float(r['position']) for r in filtered_results if r['position'] and str(r['position']).replace('.', '').isdigit()]
                    if valid_positions:
                        avg_position = sum(valid_positions) / len(valid_positions)
                        st.metric("Average Position", f"{avg_position:.2f}")
            
            with col3:
                if 'points' in filtered_results[0]:
                    total_points = sum(float(r['points']) for r in filtered_results if r['points'] and str(r['points']).replace('.', '').isdigit())
                    st.metric("Total Points", f"{total_points:.0f}")
        
    except Exception as e:
        st.error(f"Error displaying results: {str(e)}")
        st.error("Please check the data format and try again")

def display_generic_table(table_name: str):
    """Display any other table in a generic way"""
    results = db_controller.get_all_results(table_name)
    
    if results:
        st.subheader(f"Data from {table_name}")
        st.info(f"Found {len(results)} records")
        st.dataframe(results)
        
        # Get column names from the first result
        if results:
            columns = list(results[0].keys())
            
            # Add filtering options
            st.subheader("Filter Data")
            selected_column = st.selectbox("Select column to filter", columns)
            
            if selected_column:
                unique_values = list(set(str(r[selected_column]) for r in results))
                filter_value = st.selectbox(f"Select {selected_column}", unique_values)
                
                if filter_value:
                    filtered_results = db_controller.get_results_by_filter(
                        table_name,
                        {selected_column: filter_value}
                    )
                    st.subheader(f"Filtered Results for {selected_column} = {filter_value}")
                    st.dataframe(filtered_results)
    else:
        st.info(f"No data found in table {table_name}")

if __name__ == "__main__":
    main()