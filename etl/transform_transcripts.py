import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd

print('Connecting to postgres')
conn = psycopg2.connect(
        database='postgres',
        user='postgres',
        password='Kto12SQL',
        host='localhost',
        port='5432'
)

conn.autocommit = True
cursor = conn.cursor()

# Defining the SELECT query
select_query = "SELECT student_user_id, school_year, course_id, grade_description, grade_id, grade FROM public.transcripts WHERE grade_id != 999999;"

# Executing the SELECT query
cursor.execute(select_query)

# Fetching and printing the results
result = cursor.fetchall()
df= pd.DataFrame(result, columns = ['student_user_id', 'school_year', 'course_id', 'grade_description', 'grade_id', 'grade'])

group_list = df.groupby(['student_user_id','school_year', 'course_id']).groups

for key, value in group_list.items():
    if len(value) == 1:
        print((key,value))


# # Defining the UPDATE query
# update_query = "UPDATE public.transcripts SET grade_description, grade_id = no_yearlong_possible, 888888 WHERE condition;"

# # Executing the UPDATE query
# cursor.execute(update_query)

# # Committing the transaction to save changes
# connection.commit()

      
    