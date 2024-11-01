import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import postgres_credentials
from BbApiConnector import BbApiConnector

def run_etl(conn):
  cursor = conn.cursor()

  # Make our connections
  path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

  api_conn = BbApiConnector(path)
  print('Connecting to Blackbaud')
  bb_session = api_conn.get_session()

  print('Getting enrollment data')
  # We need to iterate through the pages of data, BB only returns 1000 rows at a time
  for i in range(1, 1500):
    print("Page " + str(i))
    req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/" + "162852" + "?page=" + str(i))
      
    df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()
    print('Inserting data')
    col_count = 5
    if (len(df) > 0):
        for index in range(0, len(df), col_count):
            columns = df["name"][index:(index+col_count)].values
            values = df["value"][index:(index+col_count)].values

            insert_statement = '''INSERT INTO transcript_comments (%s) VALUES %s
                ON CONFLICT (student_user_id) 
                DO UPDATE SET 
                (student_first,student_last,comment,comment_insert_date) = (EXCLUDED.student_first,EXCLUDED.student_last,EXCLUDED.comment,EXCLUDED.comment_insert_date);'''
            print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
            cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    else:
        print('No data')
        break   

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
    conn.commit()
    print('Closing connection')
    conn.close()