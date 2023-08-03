from BbApiConnector import BbApiConnector

print('hello world')
api_conn = BbApiConnector(r'C:\Users\Michael.Lindner\Documents\BbApiConnector-Python\resources\app_secrets.json')
bb_session = api_conn.get_session()

req = bb_session.get("https://api.sky.blackbaud.com/school/v1/levels")

print(req.encoding)
print(req.json())


