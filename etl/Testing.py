from BbApiConnector import BbApiConnector
import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs

api_conn = BbApiConnector(r'C:\Users\Michael.Lindner\Documents\BbApiConnector-Python\resources\app_secrets.json')
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
    for index in range(0, len(df), 17):
        columns = df["name"][index:(index+17)].values
        values = df["value"][index:(index+17)].values

        print((','.join(columns)), tuple(values))

        insert_statement = 'insert into transcripts (%s) values %s'
        print('SQL statment')
        print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
        cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
    else:
        print('No data')


conn.commit()
print('Closing connection')
conn.close()

# Example SQL statment
# b"insert into attendance (id,attendance_of_record,attendance_type,block_name,comment,date,excuse_category_id,excuse_description,excuse_type_id,excused,grad_year,grade,grade_level_sort,group_name,photo_file_name,section,section_id,student_name,student_user_id,teacher_name) values (72629513, true, false, 'C', '', '2023-12-08T08:20:00+00:00', 0, 'Illness - All Day (LS, MS, US)', 395, 1, '2025', '11th Grade', 12, 'Vertebrates: Origins, Designs & Threats - Fall - C (C)', 'thumb_user_5268758_355.jpg', 'Fall - C', 113366162, 'Weintraub, GianLucca ''25', 5268758, 'Meister, Cecile')"
