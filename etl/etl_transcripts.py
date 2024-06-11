from BbApiConnector import BbApiConnector
import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs
import transform_transcripts
import postgres_credentials

def run_etl(conn):
  cursor = conn.cursor()

  # Should I turn this off?
  conn.autocommit = True

  # Make our connections
  path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

  api_conn = BbApiConnector(path)
  print('Connecting to Blackbaud')
  bb_session = api_conn.get_session()

  # Clean up old 999999, 888888, and 777777s. Restore Fall YL
  req = bb_session.get("https://api.sky.blackbaud.com/school/v1/years")
  current_year = [d for d in req.json()["value"] if d['current_year'] == True]
  current_year = current_year[0]['school_year_label'][0:4] + " - " + current_year[0]['school_year_label'][5:]

  transform_transcripts.clean_up(conn, current_year)
  conn.commit()

  # Import data
  list_IDs = ["153908", "154813", "154814", "154815", "154816", "154817", "154818", "154819",
              "154820", "154821", "154822", "154823", "154824", "154825", "154826", "154827",
              "154828", "154829", "154830", "154831", "154832", "154833", "154834", "154835",
              "154836", "154837"]

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

              insert_statement = '''INSERT INTO transcripts (%s) VALUES %s
                ON CONFLICT (student_user_id,term_id,group_id,course_id,grade_id) 
                DO UPDATE SET 
                (student_first,student_last,grad_year,course_title,course_code,group_description,term_name,grade_description,grade_mode,grade,score,transcript_category,school_year,address_1,address_2,address_3,address_city,address_state,address_zip) = (EXCLUDED.student_first,EXCLUDED.student_last,EXCLUDED.grad_year,EXCLUDED.course_title,EXCLUDED.course_code,EXCLUDED.group_description,EXCLUDED.term_name,EXCLUDED.grade_description,EXCLUDED.grade_mode,EXCLUDED.grade,EXCLUDED.score,EXCLUDED.transcript_category,EXCLUDED.school_year,EXCLUDED.address_1,EXCLUDED.address_2,EXCLUDED.address_3,EXCLUDED.address_city,EXCLUDED.address_state,EXCLUDED.address_zip);'''
              print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
              cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
      else:
          print('No data')
          break   
  conn.commit()

  # Transform data
  transform_transcripts.fix_no_yearlong_possible(conn)
  transform_transcripts.fix_cnc(conn)
  transform_transcripts.fall_yearlongs(conn, current_year)
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
  
  run_etl(conn)
  print('Closing connection')
  conn.close()
