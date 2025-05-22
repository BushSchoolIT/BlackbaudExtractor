import psycopg2
from psycopg2.extensions import AsIs
import pandas as pd
import studentdev_credentials
from BbApiConnector import BbApiConnector
import numpy as np

def convert_year(x, current_year):
    return (str(12 - (int(x) - int(current_year))))

def run_etl(conn):
  cursor = conn.cursor()

  # Make our connections
  path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'
  api_conn = BbApiConnector(path)
  print('Connecting to Blackbaud')
  bb_session = api_conn.get_session()

  # get current school year
  req = bb_session.get("https://api.sky.blackbaud.com/school/v1/years")
  current_year = [d for d in req.json()["value"] if d['current_year'] == True]
  current_year = current_year[0]['school_year_label'][5:]

  print('Getting contact data data')
  # We need to iterate through the pages of data, BB only returns 1000 rows at a time
  for i in range(1, 1500):
    print("Page " + str(i))
    req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/" + "166297" + "?page=" + str(i))
    df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()

    # TODO: Create col for array of grade level ints
    for j in range(len(df)):
        if (df['name'][j][0:3] == "grad"):
          df['value'][j] = 12 - (int(df['value'][j]) - int(current_year))

    # Insert data
    print('Inserting data')
    col_count = 8
    if (len(df) > 0):
        for index in range(0, len(df), col_count):
            columns = df["name"][index:(index+col_count)].values
            print(columns)
            values = df["value"][index:(index+col_count)].values

            # TODO: POSTGRES QUERY HERE
            insert_statement = '''INSERT INTO parents (%s) VALUES %s
                ON CONFLICT (email) 
                DO UPDATE SET 
                (first_name, last_name, grade) = (EXCLUDED.first_name, EXCLUDED.last_name, EXCLUDED.grade);
            '''

            print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
            # TODO: make this insert the grade levels as a list of integers
            trans_cols = np.append(columns[0:3], "grade")
            trans_vals =np.append(values[0:3], '{' + ', '.join([convert_year(x, current_year) for x in values[3:] if type(x) == str and -1 < int(convert_year(x, current_year)) < 12]) + '}')
            print("trans_cols:")
            print(trans_cols)
            print("trans_vals")
            print(trans_vals)
            cursor.execute(insert_statement, (AsIs(','.join(trans_cols)), tuple(trans_vals)))
    else:
        print('No data')
        break

    update_query = """DELETE FROM parents WHERE grade = '{}'"""
    cursor.execute(update_query)   

if __name__ == '__main__':
    print('Connecting to postgres')
    conn = psycopg2.connect(
            database = studentdev_credentials.database,
            user = studentdev_credentials.user,
            password = studentdev_credentials.password,
            host = studentdev_credentials.host,
            port = studentdev_credentials.port
          )
  
    run_etl(conn)
    conn.commit()
    print('Closing connection')
    conn.close()