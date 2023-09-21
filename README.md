Uses authentification code forked from justein230/BbApiConnector-Python.

# Components
- For the authorization code generator, a simple HTTP server is needed in order to receive the code from Blackbaud. I used the Bottle framework, since it is easy to use and lightweight. It relies only on standard Python libraries!
- For the API connector program, I create a Session object and use a config file for storing all the secrets, keys, tokens and other supporting information.

## Prerequisites
- In your python environment run `pip install bottle`. This will install all the libraries from pip that you need to run the auth code generator (`bb_auth.py` in resources).
- Paste your Application ID and Application Secret into the placeholders in `app_secrets.json`. These will be used for authorization and authentication throughout the process. Also, paste your Blackbaud API Subscription Key in the placeholder in `app_secrets.json`.
- Choose a URL to use for testing auth codes and set it in `test_api_endpoint` field in `app_secrets.json`. I arbitrarily picked the `Role list` endpoint in the School API for my purposes, but you can pick any endpoint you wish.
- If you are an environment admin, make sure that you have connected your application to the environment from which you want to pull data. If you are not an environment admin, ask your administrator to connect your SKY API application. Instructions on how to do this are [here](https://developer.blackbaud.com/skyapi/docs/createapp). Just to clarify, steps 1 and 2 of this guide are to be performed by you (the application creator), and steps 3 and 4 are to be completed by an environment admin.
- Port 13631 is used on the local machine to run the web server. Make sure that [here](https://developer.blackbaud.com/apps/), in your application settings, under Redirect URIs, that you have `http://localhost:13631/callback` as an option.

## Obtain Authorization Code to Get Tokens
1. Once the prerequisite steps are completed, run the authorization code generator component (`bb_auth.py`).
2. When the application is running, go to `http://localhost:13631`. Here, you will find the link that you need to go to in order to authorize your application with your credentials.
3. Sign in with your Blackbaud ID, then click "Authorize". You should be taken to a screen with your authorization code. If you look at the console of the application, you will see a very long access token and a much shorter refresh token. Copy these values and paste them in `app_secrets.json`.
4. Once you have copied these values into the config file, you can terminate the bb_auth application.

## Set Up a Session for Use in Python Programs
1. When all placeholders in the `app_secrets.json` file are filled (which they should be at this point), you are ready to start authenticating with the SKY API!
2. In your query, add `from BbApiConnector import BbApiConnector` to the top of your program.
3. Create a BbApiConnector object and pass in the config file path, like so: `api_conn = BbApiConnector('app_secrets.json')`
4. In order to use the API, use the pre-authorized Session object created with this script. add the line `bb_session = api_conn.get_session()` near the top of your file.
5. You are done! In order to use the API, use bb_session like you would the normal requests library. No headers need to be specified. An example request is located below:
```python
params = {
    'base_role_ids': '1'
}
req = bb_session.get("https://api.sky.blackbaud.com/school/v1/users/extended", params=params)
```
