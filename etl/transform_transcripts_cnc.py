import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import numpy as np

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
select_query = """SELECT student_user_id, school_year, course_id, grade_description, grade_id, grade, grad_year, term_id
                  FROM public.transcripts 
                  WHERE (grade_description = \'Fall Term Grades YL\' 
                  OR  grade_description = \'Spring Term Grades YL\'
                  OR  grade_description = \'Year-Long Grades\');"""

# Executing the SELECT query
cursor.execute(select_query)

# Fetching and printing the results
result = cursor.fetchall()
df= pd.DataFrame(result, columns = ['student_user_id', 'school_year', 'course_id', 'grade_description', 'grade_id', 'grade', 'grad_year', 'term_id'])

group_list = df.groupby(['student_user_id','school_year', 'course_id']).groups

def occurs_once(a, item):
    return a.count(item) == 1

def check_key(value):
    for i in value.values.astype('int'):
        if occurs_once(df['grade'][i], ("CR" or "I" or "WF" or "WP")) == True:
            return value.values.astype('int')
        else:
            pass
index_list = []
for key, value in group_list.items():
    if len(value) == 2:
        print(value)
        index_list.append(check_key(value))

index_list = list(filter(lambda item: item is not None, index_list))
if len(index_list) > 0:
    index_list = np.concatenate(index_list).ravel().tolist()
    print(index_list)

    print(str(len(index_list)) + " records to check")
    for i in index_list:
        print(df.iloc[[i]])

    for i in index_list:
        # Defining the UPDATE query
        update_query = """UPDATE public.transcripts
                            SET grade_description = \'no_yearlong_possible\',
                                grade_id = 777777
                            WHERE student_user_id = {student_user_id} AND
                                school_year = \'{school_year}\' AND
                                course_id = {course_id} AND
                                term_id = {term_id};""".format(student_user_id = df['student_user_id'][i], school_year = df['school_year'][i], course_id = df['course_id'][i], term_id = df['term_id'][i])
        print(update_query)
        # Executing the UPDATE query
        cursor.execute(update_query)

# Committing the transaction to save changes
conn.commit()