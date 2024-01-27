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

# TODO Add a delete query to remove old 999999s

# Defining the SELECT query
select_query = """SELECT student_user_id, school_year, course_id, grade_description, grade_id, grade, grad_year
                  FROM public.transcripts 
                  WHERE grade_description = \'Fall Term Grades YL\' 
                  OR  grade_description = \'Spring Term Grades YL\'
                  OR  grade_description = \'Year-Long Grades\'
                  OR  grade_id = 999999;"""

# Executing the SELECT query
cursor.execute(select_query)

# Fetching and printing the results
result = cursor.fetchall()
df= pd.DataFrame(result, columns = ['student_user_id', 'school_year', 'course_id', 'grade_description', 'grade_id', 'grade', 'grad_year'])

group_list = df.groupby(['student_user_id','school_year', 'course_id']).groups

index_list = []
for key, value in group_list.items():
    if len(value) == 1:
        index_list.append(value.values.astype('int')[0])
index_list = list(dict.fromkeys(index_list))

print(str(len(index_list)) + " records to check")
for i in index_list:
        if (df['grade_id'][i] != 999999) and (df['grade_description'][i] != 'Year-Long Grades'):
                print(df['grade_id'][i])
                # Defining the UPDATE query
                update_query = """UPDATE public.transcripts
                                  SET grade_description = \'no_yearlong_possible\',
                                      grade_id = 888888
                                  WHERE student_user_id = {student_user_id} AND
                                        school_year = \'{school_year}\' AND
                                        course_id = {course_id};""".format(student_user_id = df['student_user_id'][i], school_year = df['school_year'][i], course_id = df['course_id'][i])
                print(update_query)
                # Executing the UPDATE query
                cursor.execute(update_query)

# Committing the transaction to save changes
conn.commit()