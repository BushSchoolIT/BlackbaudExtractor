import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import postgres_credentials
from BbApiConnector import BbApiConnector
import transform_enrollment

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
    req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/" + "159436" + "?page=" + str(i))
      
    df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()
    print('Inserting data')
    col_count = 9
    if (len(df) > 0):
        for index in range(0, len(df), col_count):
            columns = df["name"][index:(index+col_count)].values
            values = df["value"][index:(index+col_count)].values

            insert_statement = '''INSERT INTO enrollment (%s) VALUES %s
                ON CONFLICT (student_user_id) 
                DO UPDATE SET 
                (student_first,student_last,grad_year,enroll_date, graduated, enroll_grade, enroll_year, email) = (EXCLUDED.student_first,EXCLUDED.student_last,EXCLUDED.grad_year,EXCLUDED.enroll_date, EXCLUDED.graduated, EXCLUDED.enroll_grade, EXCLUDED.enroll_year, EXCLUDED.email);'''
            print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
            cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    else:
        print('No data')
        break   

  print('Getting departed student data')
  # We need to iterate through the pages of data, BB only returns 1000 rows at a time
  for i in range(1, 1500):
    print("Page " + str(i))
    req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/" + "159435" + "?page=" + str(i))
      
    df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()
    print('Inserting data')
    col_count = 5
    if (len(df) > 0):
        for index in range(0, len(df), col_count):
            columns = df["name"][index:(index+col_count)].values
            values = df["value"][index:(index+col_count)].values

            insert_statement = '''INSERT INTO enrollment (%s) VALUES %s
                ON CONFLICT (student_user_id) 
                DO UPDATE SET 
                (depart_date,graduated,depart_year, email) = (EXCLUDED.depart_date, EXCLUDED.graduated, EXCLUDED.depart_year, EXCLUDED.email);'''
            print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
            cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    else:
        print('No data')
        break   

    transform_enrollment.concatenate_graduated_status(conn)

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