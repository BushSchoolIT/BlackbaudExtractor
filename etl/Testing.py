from BbApiConnector import BbApiConnector
import pandas as pd
import numpy as np
import psycopg2
from psycopg2.extensions import AsIs

path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

api_conn = BbApiConnector(path)
print('Connecting to Blackbaud')
bb_session = api_conn.get_session()

print('Getting data')
req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/153908")
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
    for index in range(0, len(df), 20):
        columns = df["name"][index:(index+20)].values
        values = df["value"][index:(index+20)].values

        print((','.join(columns)), tuple(values))

        # insert_statement = 'insert into transcripts (%s) values %s'
        insert_statement = 'INSERT INTO transcripts (%s) VALUES %s ON CONFLICT (student_user_id,term_id,group_id,course_id,grade_id) DO UPDATE SET transcripts = EXCLUDED.transcripts;'
        print('SQL statment')
        print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
        cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
else:
    print('No data')

conn.commit()
print('Closing connection')
conn.close()

# INSERT INTO transcripts (%s) VALUES %s ON CONFLICT (student_user_id,term_id,group_id,course_id,grade_id) DO UPDATE SET transcripts = EXCLUDED.transcripts; 