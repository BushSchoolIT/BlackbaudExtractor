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
        SELECT student_user_id, grad_year, depart_date, graduated"
        FROM public.enrollment;"""

        # Executing the SELECT query
        cursor.execute(select_query)

        # Fetching and printing the results
        result = cursor.fetchall()

        # If graduated is false and grad year is NAN, then we use depart date
        # If graduate is false and grad year is not NAN, then we use grad year
        # If graduated is true, then we use grad year and append the depart date

        # Defining the insertion query
        insert_query = """
        
        """
        print(insert_query)

        # Executing the insertion query
        cursor.execute(insert_query)
        