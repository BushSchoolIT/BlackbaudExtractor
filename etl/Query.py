from BbApiConnector import BbApiConnector
import os

print('hello world')

#path = os.path.join(os.pardir, r'\config\app_secrets.json')
path = r'C:\Users\Michael.Lindner\Documents\BlackbaudExtractor\config\app_secrets.json'

api_conn = BbApiConnector(path)
bb_session = api_conn.get_session()


# Get attendance data
# https://api.sky.blackbaud.com/school/v1/attendance?level_id={level_id}&day={day}&offering_type={offering_type}[&excuse_type]
# level_id, required, integer	
# The ID of the school level to retrieve attendance records.

# day, required, string
#The date to return attendance for.

# offering_type, required, integer
# The offering type to retrieve records for.

# excuse_type, optional, integer
# Filters results to a specific excuse type.
params = {
    'level_id': 779,
    'day': '3/14/2022',
    'offering_type': 1
 }
req = bb_session.get("https://api.sky.blackbaud.com/school/v1/attendance", params=params)

print(req.encoding)
print(req.json())


