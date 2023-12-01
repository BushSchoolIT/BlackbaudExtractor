from BbApiConnector import BbApiConnector
import pandas as pd

api_conn = BbApiConnector(r'C:\Users\Michael.Lindner\Documents\BbApiConnector-Python\resources\app_secrets.json')
bb_session = api_conn.get_session()

req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/153908")

output = req.json()['results']['rows']

if (len(output) > 0):

    for i in range(len(output)):
        columns = []
        values = []
        for j in range(len(output[i]['columns'])):
            columns.append(output[i]['columns'][j]['name'])
            values.append(output[i]['columns'][j]['value'])

        print(columns)
        print(values)
            
        # insert_statement = 'insert into attendance (%s) values %s'
        # print('SQL statment')
        # print(cursor.mogrify(insert_statement, (AsIs(','.join(columns)), tuple(values))))



# df = pd.json_normalize(req.json()["results"]["rows"], "columns").reset_index()
# print(df[0:50])

