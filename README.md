# BlackbaudExtractor
This repository is for performing ETL on a Blackbaud Education Management environment. This project uses python for handling ETL pipelines, and a PostgresQL server for storing data.

## Setting up Blackbaud
- Register app
- Create advanced lists

Currently, the lists in blackbaud must be manually rolled over each year (pending a better solution). Time this with the registrar rolling over the year because the cleanup scripts could otherwise cause you to import duplicate records and cause errors. Be wary of schedueld runs.

## Authorizing with Blackbaud
The OAuth Authentication is handled by justein230's Blackbaud API Connector. See justein230/BbApiConnector-Python. I have slightly changed his code to work with my environment. The following section of documentaion is mostly taken from justein230/BbApiConnector-Python.

- For the authorization code generator, a simple HTTP server is needed in order to receive the code from Blackbaud.
- For the API connector program, I create a Session object and use a config file for storing all the secrets, keys, tokens and other supporting information.

### Prerequisites
- In your python environment run `pip install bottle`. This will install all the libraries from pip that you need to run the auth code generator (`bb_auth.py` in resources).
- Paste your Application ID and Application Secret into the placeholders in `app_secrets.py`. These will be used for authorization and authentication throughout the process. Also, paste your Blackbaud API Subscription Key in the placeholder in `app_secrets.py`. Put these fields in 'app_secrets.json' as well. Other fields for that file will come later.
- Choose a URL to use for testing auth codes and set it in `test_api_endpoint` field in `app_secrets.py`. 
- If you are an environment admin, make sure that you have connected your application to the environment from which you want to pull data. If you are not an environment admin, ask your administrator to connect your SKY API application
- Port 13631 is used on the local machine to run the web server. Make sure that [here](https://developer.blackbaud.com/apps/), in your application settings, under Redirect URIs, that you have `http://localhost:13631/callback` as an option.

### Obtain Authorization Code to Get Tokens
1. Once the prerequisite steps are completed, run the authorization code generator component (`bb_auth.py`).
2. When the application is running, go to `http://localhost:13631`. Here, you will find the link that you need to go to in order to authorize your application with your credentials.
3. Sign in with your Blackbaud ID, then click "Authorize". You should be taken to a screen with your authorization code. If you look at the console of the application, you will see a very long access token and a much shorter refresh token. Copy these values and paste them in `app_secrets.json`.
4. Once you have copied these values into the config file, you can terminate the bb_auth application.

## Settting up the PostgresQL server
wordswords

## ETL scripts
Currently, the following ETL Pipelines are included:
Attendance data 
Transcript data
GPA calculation
Enrollment data
