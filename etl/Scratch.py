from BbApiConnector import BbApiConnector
import pandas as pd
import psycopg2
from psycopg2.extensions import AsIs

path = r'C:\Users\Install\BlackbaudExtractor\config\app_secrets.json'

api_conn = BbApiConnector(path)
print('Connecting to Blackbaud')
bb_session = api_conn.get_session()

print('Getting data')
req = bb_session.get("https://api.sky.blackbaud.com/school/v1/lists/advanced/153908")