from BbApiConnector import BbApiConnector
import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs

path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

api_conn = BbApiConnector(path)
print('Connecting to Blackbaud')
bb_session = api_conn.get_session()

print('Getting data')
# We need to iterate through the pages of data, BB only returns 1000 rows at a time.
for i in range(1, 1500):
  print("Page " + str(i))
  req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/153908" + "?page=" + str(i))
  df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()

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

  print('Inserting data')
  if (len(df) > 0):
      for index in range(0, len(df), 28):
          columns = df["name"][index:(index+28)].values
          values = df["value"][index:(index+28)].values

          insert_statement = '''INSERT INTO transcripts (%s) VALUES %s
            ON CONFLICT (student_user_id,term_id,group_id,course_id,grade_id) 
            DO UPDATE SET 
            (student_first,student_last,grad_year,course_title,course_code,group_description,term_name,grade_description,grade_mode,grade,incomplete,score,final_score,transcript_category,required,school_year,grade_level,address_1,address_2,address_3,address_city,address_state,address_zip) = (EXCLUDED.student_first,EXCLUDED.student_last,EXCLUDED.grad_year,EXCLUDED.course_title,EXCLUDED.course_code,EXCLUDED.group_description,EXCLUDED.term_name,EXCLUDED.grade_description,EXCLUDED.grade_mode,EXCLUDED.grade,EXCLUDED.incomplete,EXCLUDED.score,EXCLUDED.final_score,EXCLUDED.transcript_category,EXCLUDED.required,EXCLUDED.school_year,EXCLUDED.grade_level,EXCLUDED.address_1,EXCLUDED.address_2,EXCLUDED.address_3,EXCLUDED.address_city,EXCLUDED.address_state,EXCLUDED.address_zip);'''
          print('SQL statment')
          print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
          cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
  else:
      print('No data')
      break

conn.commit()
print('Closing connection')
conn.close()
