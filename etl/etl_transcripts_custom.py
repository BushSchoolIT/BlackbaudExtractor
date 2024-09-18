from BbApiConnector import BbApiConnector
import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs
import transform_transcripts
import postgres_credentials

# BE SURE TO SET THE CORRECT YEAR
# BAD DO NOT USE
def run_etl(conn):
  exit()
  cursor = conn.cursor()

  # Make our connections
  path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

  api_conn = BbApiConnector(path)
  print('Connecting to Blackbaud')
  bb_session = api_conn.get_session()

  current_year = "2022 - 2023"

  # Import data
  list_IDs = ["160515"]

  print('Getting data')
  # We need to iterate through the pages of data, BB only returns 1000 rows at a time.
  for ID in list_IDs:
    print(ID)
    for i in range(1, 1500):
      print("Page " + str(i))
      req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/" + ID + "?page=" + str(i))
      
      df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()

      # Giving the planned courses a grade_ID of 999999 because it is part of the PK and cannot be blank.
      # Might want to clean out the old 999999s at the start of every year...
      # Potentially re-write using df.loc 
      for j in range(len(df)):
        if (df['name'][j] == "grade_id") and (pd.isnull(df['value'][j])==True):
          df['value'][j] = 999999

      print('Inserting data')
      col_count = 24
      if (len(df) > 0):
          for index in range(0, len(df), col_count):
              columns = df["name"][index:(index+col_count)].values
              values = df["value"][index:(index+col_count)].values

              student_user_id = values[0]

              # Defining the DELETE queries
              delete_transforms_query = """DELETE FROM public.transcripts
                                          WHERE (grade_id = 888888
                                          OR grade_id = 777777
                                          OR grade_id = 666666)
                                          AND (school_year = \'{school_year}\'
                                          AND student_user_id = \'{student_user_id}\')""".format(school_year = current_year, student_user_id = student_user_id)
              
              # Defining the UPDATE query
              restore_fall_yl_query = """UPDATE public.transcripts
                                        SET grade_description = \'Fall Term Grades YL\', grade_id = 2154180
                                        WHERE (school_year != \'{school_year}\' 
                                        AND grade_id = 666666
                                        AND student_user_id = \'{student_user_id}\');""".format(school_year = current_year, student_user_id = student_user_id)
            
              # Executing the queries
              cursor.execute(delete_transforms_query)
              print('Deleted transforms.')
              cursor.execute(restore_fall_yl_query)
              print('Restored Fall YL grades.')

              insert_statement = '''INSERT INTO transcripts (%s) VALUES %s
                ON CONFLICT (student_user_id,term_id,group_id,course_id,grade_id) 
                DO UPDATE SET 
                (student_first,student_last,grad_year,course_title,course_code,group_description,term_name,grade_description,grade_mode,grade,score,transcript_category,school_year,address_1,address_2,address_3,address_city,address_state,address_zip) = (EXCLUDED.student_first,EXCLUDED.student_last,EXCLUDED.grad_year,EXCLUDED.course_title,EXCLUDED.course_code,EXCLUDED.group_description,EXCLUDED.term_name,EXCLUDED.grade_description,EXCLUDED.grade_mode,EXCLUDED.grade,EXCLUDED.score,EXCLUDED.transcript_category,EXCLUDED.school_year,EXCLUDED.address_1,EXCLUDED.address_2,EXCLUDED.address_3,EXCLUDED.address_city,EXCLUDED.address_state,EXCLUDED.address_zip);'''
              print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
              cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))

              print("Reassigning grade_id for current Fall YL grades...")
              # Defining the UPDATE query
              update_query = """UPDATE public.transcripts
                              SET grade_description = \'current_fall_yl\',
                                      grade_id = 666666
                              WHERE (school_year = \'{school_year}\' AND
                                      grade_description = \'Fall Term Grades YL\'
                                      AND student_user_id = \'{student_user_id}\');""".format(school_year = current_year, student_user_id = student_user_id)
              print(update_query)
              
              # Executing the UPDATE query
              cursor.execute(update_query)

              print("Fixing courses where no year-long grade is possible...")
              # Defining the SELECT query
              # We may be able to remove the grade_id = 999999 condition
              select_query = """SELECT student_user_id, school_year, course_id, grade_description, grade_id, grade, grad_year
                              FROM public.transcripts 
                              WHERE (grade_description = \'Fall Term Grades YL\' 
                              OR  grade_description = \'Spring Term Grades YL\'
                              OR  grade_description = \'Year-Long Grades\'
                              OR  grade_id = 999999)
                              AND student_user_id = \'{student_user_id}\';""".format(student_user_id = student_user_id)

              # Executing the SELECT query
              cursor.execute(select_query)

              print("Fixing grades where one semester is C/CN and the other is a letter grade...")
              # Defining the SELECT query
              select_query = """SELECT student_user_id, school_year, course_id, grade_description, grade_id, grade, grad_year, term_id
                              FROM public.transcripts 
                              WHERE (grade_description = \'Fall Term Grades YL\' 
                              OR  grade_description = \'Spring Term Grades YL\'
                              OR  grade_description = \'Year-Long Grades\')
                               AND student_user_id = \'{student_user_id}\';""".format(student_user_id = student_user_id)

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
      else:
          print('No data')
          break   
  conn.commit()

  # Transform data
  transform_transcripts.insert_missing_transcript_categories(conn)
  conn.commit()

if __name__ == '__main__':
  print('Connecting to postgres')
  conn = psycopg2.connect(
          database = postgres_credentials.database,
          user = postgres_credentials.user,
          password = postgres_credentials.password,
          host = postgres_credentials.host,
          port = postgres_credentials.port
          )
  conn.autocommit = False
  
  try:
        run_etl(conn)
        conn.commit()      

  except (Exception, psycopg2.DatabaseError) as error:
        print("error in transaction, reverting")
        conn.rollback()

  print('Closing connection')
  conn.close()
