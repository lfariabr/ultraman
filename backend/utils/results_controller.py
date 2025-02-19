from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
import os
from dotenv import load_dotenv
from typing import List, Dict, Any, Optional
from datetime import datetime

# Load environment variables
load_dotenv()

class DatabaseController:
    def __init__(self):
        # Construct Database URL
        self.database_url = f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)

    def get_db_session(self):
        """Create and return a new database session"""
        return self.SessionLocal()

    def execute_query(self, query: str, params: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Execute a raw SQL query and return results as a list of dictionaries
        """
        try:
            with self.get_db_session() as session:
                result = session.execute(text(query), params or {})
                columns = result.keys()
                
                # Convert row results to list of dicts with proper type handling
                formatted_results = []
                for row in result.fetchall():
                    formatted_row = {}
                    for idx, (column, value) in enumerate(zip(columns, row)):
                        if value is None:
                            formatted_row[column] = None
                        elif hasattr(value, 'total_seconds'):  # Check if it's a duration/interval
                            # Convert to HH:MM:SS.mmm format
                            total_seconds = value.total_seconds()
                            hours = int(total_seconds // 3600)
                            minutes = int((total_seconds % 3600) // 60)
                            seconds = total_seconds % 60
                            formatted_row[column] = f"{hours:02d}:{minutes:02d}:{seconds:06.3f}"
                        else:
                            formatted_row[column] = value
                    formatted_results.append(formatted_row)
                
                return formatted_results
        except Exception as e:
            print(f"Error executing query: {str(e)}")
            raise

    def get_all_results(self, table_name: str, limit: int = 500) -> List[Dict[str, Any]]:
        """Get all results from a specific table"""
        query = f"SELECT * FROM {table_name} LIMIT :limit"
        return self.execute_query(query, {"limit": limit})

    def get_results_by_filter(self, 
                            table_name: str, 
                            filters: Dict[str, Any],
                            limit: int = 500) -> List[Dict[str, Any]]:
        """Get filtered results from a specific table"""
        conditions = " AND ".join([f"{key} = :{key}" for key in filters.keys()])
        query = f"SELECT * FROM {table_name} WHERE {conditions} LIMIT :limit"
        params = {**filters, "limit": limit}
        return self.execute_query(query, params)

    def get_results_by_date_range(self,
                                table_name: str,
                                date_column: str,
                                start_date: datetime,
                                end_date: datetime,
                                limit: int = 500) -> List[Dict[str, Any]]:
        """Get results within a date range"""
        query = f"""
            SELECT * FROM {table_name}
            WHERE {date_column} BETWEEN :start_date AND :end_date
            LIMIT :limit
        """
        params = {
            "start_date": start_date,
            "end_date": end_date,
            "limit": limit
        }
        return self.execute_query(query, params)

    def get_table_schema(self, table_name: str) -> List[Dict[str, str]]:
        """
        Get the schema information for a table
        
        Args:
            table_name (str): Name of the table
            
        Returns:
            List[Dict[str, str]]: List of column information
        """
        query = """
            SELECT column_name, data_type, udt_name
            FROM information_schema.columns
            WHERE table_name = :table_name
            ORDER BY ordinal_position;
        """
        return self.execute_query(query, {"table_name": table_name})

    def get_all_tables(self) -> List[str]:
        """
        Get all table names from the database
        
        Returns:
            List[str]: List of table names
        """
        query = """
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
        """
        try:
            results = self.execute_query(query)
            return [result['table_name'] for result in results]
        except Exception as e:
            print(f"Error getting tables: {str(e)}")
            raise

    def get_results_by_year(self, request):
        """
        Get race results filtered by year.
        Query Parameters:
            year (int): The year to filter results
        """
        try:
            year = request.query_params.get('year', None)
            if not year:
                return Response(
                    {'error': 'Year parameter is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            results = self.queryset.filter(race__race_date__year=year).order_by('race_overall_rank')
            page = self.paginate_queryset(results)

            if page is not None:
                serializer = self.get_serializer(page, many=True)
                return self.get_paginated_response(serializer.data)

            serializer = self.get_serializer(results, many=True)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    def get_aggregated_results(self,
                             table_name: str,
                             group_by_column: str,
                             agg_column: str,
                             agg_function: str = 'COUNT',
                             limit: int = 500) -> List[Dict[str, Any]]:
        """
        Get aggregated results from a specific table
        
        Args:
            table_name (str): Name of the table to query
            group_by_column (str): Column to group by
            agg_column (str): Column to aggregate
            agg_function (str): Aggregation function to use (COUNT, SUM, AVG, etc.)
            limit (int): Maximum number of results to return
            
        Returns:
            List[Dict[str, Any]]: Aggregated query results
        """
        query = f"""
            SELECT {group_by_column},
                   {agg_function}({agg_column}) as aggregated_value
            FROM {table_name}
            GROUP BY {group_by_column}
            LIMIT :limit
        """
        return self.execute_query(query, {"limit": limit})

# Create a singleton instance
db_controller = DatabaseController()