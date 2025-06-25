import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import numpy as np
import postgres_credentials

def concatenate_graduated_status(conn):
        '''
        asdf
        '''
        # The public.course_codes table needs to be manually kept up to date until we can get a better solution.
        cursor = conn.cursor()
        print("Concatenating graduated status")
        # Defining the SELECT query
        select_query = """
        SELECT student_user_id, grad_year, depart_date, graduated
        FROM public.enrollment;"""

        # Executing the SELECT query
        cursor.execute(select_query)

        # Fetching and printing the results
        result = cursor.fetchall()

        # If graduated is false and grad year is NAN, then we use depart date
        # If graduate is false and grad year is not NAN, then we use grad year
        # If graduated is true, then we use grad year and append the depart date

        # Get column names
        colnames = [desc[0] for desc in cursor.description]
        df = pd.DataFrame(result, columns=colnames)

        # Ensure date columns are datetime
        df['depart_date'] = pd.to_datetime(df['depart_date'], errors='coerce')

        def build_status(row):
                print("building status")
                if not row['graduated']:
                        if pd.isna(row['grad_year']):
                                return f"Departure date: {row['depart_date'].strftime('%d-%m-%Y')}" if pd.notna(row['depart_date']) else None
                        else:
                                return f"Class of {str(int(row['grad_year']))}"
                else:
                        depart_str = row['depart_date'].strftime('%d-%m-%Y') if pd.notna(row['depart_date']) else ""
                        return f"Graduation date: {depart_str}" if depart_str else None

        df['graduated_status'] = df.apply(build_status, axis=1)

        # Insert processed data
        print("inserting data")
        for _, row in df.iterrows():
                cursor.execute("""
                INSERT INTO public.enrollment (student_user_id, graduated_status)
                VALUES (%s, %s)
                ON CONFLICT (student_user_id) DO UPDATE SET graduated_status = EXCLUDED.graduated_status;
                """, (row['student_user_id'], row['graduated_status']))

if __name__ == '__main__':
        print('Connecting to postgres')
        conn = psycopg2.connect(
            database = postgres_credentials.database,
            user = postgres_credentials.user,
            password = postgres_credentials.password,
            host = postgres_credentials.host,
            port = postgres_credentials.port
            )
        
        concatenate_graduated_status(conn)

        conn.commit()
        conn.close()