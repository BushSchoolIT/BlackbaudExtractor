from BbApiConnector import BbApiConnector
import os
import psycopg2
from psycopg2.extensions import AsIs
from datetime import date
import postgres_credentials


def run_etl(conn):
    cursor = conn.cursor()
    # Level IDs: [{'id': 781, 'abbreviation': 'LS', 'name': 'Lower School'}, {'id': 780, 'abbreviation': 'MS', 'name': 'Middle School'}, {'id': 779, 'abbreviation': 'US', 'name': 'Upper School'}]
    # Offering types: [{'id': 0, 'description': 'School'}, {'id': 1, 'description': 'Academics'}, {'id': 2, 'description': 'Activities'}, {'id': 3, 'description': 'Advisory'}, {'id': 4, 'description': 'Dorms'}, {'id': 5, 'description': 'Transcript'}, {'id': 6, 'description': 'OfferedCourse'}, {'id': 8, 'description': 'SchoolWideAwards'}, {'id': 9, 'description': 'Athletic'}, {'id': 10, 'description': 'Admissions'}, {'id': 11, 'description': 'Community groups'}, {'id': 12, 'description': 'Mentor'}, {'id': 13, 'description': 'Events'}]

    today = date.today()
    d1 = today.strftime('%m/%d/%Y')


    print('Connecting to Blackbaud')

    #path = os.path.join(os.pardir, r'\config\app_secrets.json')
    path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

    api_conn = BbApiConnector(path)
    bb_session = api_conn.get_session()


    print('Getting data')

    # catch_up_days = ['08/30/2023', '08/31/2023', '09/01/2023', '09/04/2023', '09/05/2023', '09/06/2023', '09/07/2023', '09/08/2023', '09/11/2023', '09/12/2023', '09/13/2023']

    level_ids = ['781', '780', '779']
    for id in level_ids:
        print(id)
        
        params = {
            'level_id': id,
            'day': d1,
            'offering_type': 1
        }
        req = bb_session.get("https://api.sky.blackbaud.com/school/v1/attendance", params=params)

        output = req.json()['value']

        if (len(output) > 0):
            for i in range(len(output)):
                print(output[i])
                columns = output[i].keys()
                values = [output[i][column] for column in columns]

                insert_statement = '''insert into attendance (%s) values %s
                                    ON CONFLICT (id) DO NOTHING;'''
                print('SQL statment')
                print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))
                cursor.execute(insert_statement, (AsIs(','.join(columns)), tuple(values)))
        else:
            print('No data')

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
    run_etl(conn)
    conn.commit()
    print('Closing connection')
    conn.close()
