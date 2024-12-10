import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import AsIs
import postgres_credentials
from decimal import Decimal, getcontext
getcontext().prec = 4


def weighted_average(frame):
    frame['product'] = frame.score * frame.credits
    num = frame['product'].sum()
    denom = frame['credits'].sum()

    # getting rid of floating point errors by converting int64 to float and float to decimal
    return round(Decimal(float(num))/Decimal(float(denom)),2)

def run_etl(conn):
    cursor = conn.cursor()
    # Defining the SELECT query
    select_query = """SELECT student_user_id, score, grade_description
                        FROM public.transcripts 
                        WHERE grade_description != \'Fall Term Grades YL\' 
                        AND  grade_description != \'Spring Term Grades YL\'
                        AND  grade_id != 999999
                        AND (grade = \'A\' OR grade = \'A-\' OR grade = \'B+\' OR grade = \'B\' 
                        OR   grade = \'B-\' OR grade = \'C+\' OR grade = \'C\' OR grade = \'C-\'
                        OR   grade = \'D+\' OR grade = \'D\' OR grade = \'F\' OR grade = \'WF\') 
                        ORDER BY student_user_id ASC;"""

    # Executing the SELECT query
    cursor.execute(select_query)

    # Fetching and printing the results
    result = cursor.fetchall()
    df= pd.DataFrame(result, columns = ['student_user_id', 'score', 'grade_description'])
    df['credits'] = np.where(df['grade_description']=='Year-Long Grades', 2, 1)

    # for unique i in df
    GPA_dict = {}
    for id in df.student_user_id.unique():
        GPA_dict[int(id)] = weighted_average(df.loc[df['student_user_id'] == id])
    
    data = list(GPA_dict.items())
    records_list_template = ','.join(['%s'] * len(data))
    insert_statement = '''INSERT INTO public.gpa (student_user_id, calculated_gpa) VALUES {}
              ON CONFLICT (student_user_id) 
              DO UPDATE SET 
              calculated_gpa = EXCLUDED.calculated_gpa;'''.format(records_list_template)
    cursor.execute(insert_statement, data)


if __name__ == '__main__':
    print('Connecting to postgres')
    conn = psycopg2.connect(
            database = postgres_credentials.database,
            user = postgres_credentials.user,
            password = postgres_credentials.password,
            host = postgres_credentials.host,
            port = postgres_credentials.port
    )

    # what does autocommit do
    run_etl(conn)
    conn.commit()
    conn.close()
