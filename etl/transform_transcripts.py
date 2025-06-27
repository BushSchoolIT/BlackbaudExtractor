import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import numpy as np
import postgres_credentials

def insert_missing_transcript_categories(conn):
        '''
        This function will insert transcript categories where none exist.
        This is always the case for grade_id = 999999 as they do not exist for scheduled courses.
        The transcript categories are identified based on the course prefix, which is the first
        word in the course code. The transcript category mappings are stored in the public.course_codes table, which needs to 
        be manually kept up to date until we can get a better solution.
        '''
        # The public.course_codes table needs to be manually kept up to date until we can get a better solution.
        cursor = conn.cursor()
        print("Inserting missing transcript categories")

        # Defining the update query
        update_query = """
        WITH ranked_prefixes AS (
            SELECT
                transcripts.course_code,
                course_codes.transcript_category,
                ROW_NUMBER() OVER (PARTITION BY transcripts.course_code ORDER BY LENGTH(course_codes.course_prefix) DESC) AS rn
            FROM
                public.transcripts
            JOIN
                public.course_codes
            ON
                transcripts.course_code::text LIKE course_codes.course_prefix || '%'
            WHERE
                transcripts.transcript_category = 'NaN'
        )
        UPDATE public.transcripts
        SET transcript_category = ranked_prefixes.transcript_category
        FROM ranked_prefixes
        WHERE public.transcripts.course_code = ranked_prefixes.course_code
        AND public.transcripts.transcript_category = 'NaN'
        AND ranked_prefixes.rn = 1;
        """
        print(update_query)

        # Executing the UPDATE query
        cursor.execute(update_query)

def fall_yearlongs(conn, school_year):
        '''
        Reassigns grade_id for Fall YL grades when the year is the current year. We need to do this to
        allow them to show up in powerBI. Typically Fll YL grades are filtered out because they are overwritten
        by YL grades.
        '''
        cursor = conn.cursor()
        print("Reassigning grade_id for current Fall YL grades...")
        # Defining the UPDATE query
        update_query = """UPDATE public.transcripts
                        SET grade_description = \'current_fall_yl\',
                                grade_id = 666666
                        WHERE (school_year = \'{school_year}\' AND
                                grade_description = \'Fall Term Grades YL\');""".format(school_year = school_year)
        print(update_query)
        
        # Executing the UPDATE query
        cursor.execute(update_query)

def clean_up(conn, school_year):
        '''
        This function removes records with grade_id = 999999, 888888, 777777, 666666 and restores Fall YL grades. 
        This is done to prevent duplicates on a reimport because the grade_id is part of the primary key.
        '''
        cursor = conn.cursor()
        # TODO: Make this more flexible so it doesn't break if you import out of order
        # Current year must match the year that is in the Blackbaud advanced lists otherwise imports duplicate records and fails.
        print("Cleaning up old records...")

        end_year = int(school_year[7:])
        year_list = (end_year, end_year - 1, end_year - 2, end_year - 3, end_year - 4)
        year_list_formatted = [str(year) + " - " + str(year + 1) for year in year_list]

        # Defining the DELETE queries
        delete_scheduled_courses_query = """DELETE FROM public.transcripts
                          WHERE grade_id = 999999"""
        
        def iterate_delete_transforms_query(school_year_iterated):
                return """DELETE FROM public.transcripts
                                     WHERE (grade_id = 888888
                                     OR grade_id = 777777
                                     OR grade_id = 666666
                                     OR grade_description = \'Senior Mid-Term Grades\')
                                     AND school_year = \'{school_year}\'""".format(school_year = school_year_iterated)
        
        
        # Defining the UPDATE query
        restore_fall_yl_query = """UPDATE public.transcripts
                                   SET grade_description = \'Fall Term Grades YL\', grade_id = 2154180
                                   WHERE (school_year != \'{school_year}\' 
                                   AND grade_id = 666666);""".format(school_year = school_year)
        


        # Executing the queries
        cursor.execute(delete_scheduled_courses_query)
        print('Deleted scheduled courses.')

        for year in year_list_formatted:
                cursor.execute(iterate_delete_transforms_query(year))
        print('Deleted transforms.')
        cursor.execute(restore_fall_yl_query)
        print('Restored Fall YL grades.')

def fix_no_yearlong_possible(conn):
        '''
        This function will fix courses where no year-long grade is possible.
        '''
        cursor = conn.cursor()
        print("Fixing courses where no year-long grade is possible...")
        # Defining the SELECT query
        # We may be able to remove the grade_id = 999999 condition
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

def fix_cnc(conn):
        '''
        docstring
        '''
        cursor = conn.cursor()
        print("Fixing grades where one semester is C/CN and the other is a letter grade...")
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

        non_letter_grades = {'NC', 'CR', 'I', 'WF', 'WP', 'AU'}
        index_list = []
        
        # Check if there exist pairs of courses where one is a non-letter-grade and the other is a letter grade for each student/class/year group
        for key, group in df.groupby(['student_user_id', 'school_year', 'course_id']):
                if len(group) == 2:
                        grades = set(group['grade'])
                        has_nc = any(g in non_letter_grades for g in grades)
                        has_letter = any(g not in non_letter_grades for g in grades)
                        if has_nc and has_letter:
                                index_list.extend(group.index.tolist())

        print(f"{len(index_list)} records to fix")
        for i in index_list:
                print(df.loc[[i]])

        # Update the rows
        for i in index_list:
                row = df.loc[i]
                update_query = f"""
                UPDATE public.transcripts
                SET grade_description = 'no_yearlong_possible',
                        grade_id = 777777
                WHERE student_user_id = {row['student_user_id']} AND
                        school_year = '{row['school_year']}' AND
                        course_id = {row['course_id']} AND
                        term_id = {row['term_id']};
                """
                print(update_query)
                # Executing the UPDATE query
                cursor.execute(update_query)

if __name__ == '__main__':
        print('Connecting to postgres')
        conn = psycopg2.connect(
            database = postgres_credentials.database,
            user = postgres_credentials.user,
            password = postgres_credentials.password,
            host = postgres_credentials.host,
            port = postgres_credentials.port
            )

        conn.autocommit = True

        # The year can be changed as reqired. When running without name == main, the year will be the current year.
        # clean_up(conn, '2023 - 2024') # WARNING this will delete all records with grade_id = 999999, 888888, 777777, 666666
        # fix_no_yearlong_possible(conn)
        fix_cnc(conn)
        # fall_yearlongs(conn, '2023 - 2024')
        # insert_missing_transcript_categories(conn)
        conn.commit()
        conn.close()
