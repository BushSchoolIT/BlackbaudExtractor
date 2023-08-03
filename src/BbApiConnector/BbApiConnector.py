import requests
import json

class BbApiConnector(object):
    """
    This class is used to establish and maintain a connection to the Blackbaud SKY API using a previously generated
    .ini file.
    """
    def __init__(self, config_file_name):
        self.config_file_name = config_file_name
        self._config = json.load(open(self.config_file_name, 'r'))

    def get_session(self):
        session = requests.Session()
        session.headers = {
            'Bb-Api-Subscription-Key': self._config['other']['api_subscription_key'],
            'Host': 'api.sky.blackbaud.com',
            'Authorization': f"Bearer {self._config['tokens']['access_token']}"
        }
        while True:
            get_result = session.get(self._config['other']['test_api_endpoint'])
            if get_result.status_code == 401:
                print("401: Unauthorized. Retrieving updated access token...")
                self.update_access_token()
                session.headers.update({'Authorization': f"Bearer {self._config['tokens']['access_token']}"})

            elif get_result.status_code == 200:
                print("200: The access token is live!")
                return session

            else:
                print(f"Unknown error with the API. Status code is {get_result.status_code}.")
                print(get_result.text)
                return None

        return session

    def update_access_token(self):
        token_uri = f'https://oauth2.sky.blackbaud.com/token'
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded'
        }
        params = {
            'grant_type': 'refresh_token',
            'refresh_token': self._config['tokens']['refresh_token'],
            'preserve_refresh_token': True,
            'client_id': self._config['sky_app_information']['app_id'],
            'client_secret': self._config['sky_app_information']['app_secret']
        }
        codes = requests.post(token_uri, data=params, headers=headers)

        self._config['tokens']['access_token'] = codes.json()['access_token']
        with open(self.config_file_name, 'w') as config_file:
            json.dump(self._config, config_file, indent=4)
            config_file.close()
        
        print("Access token updated.")
        return codes.json()['access_token']