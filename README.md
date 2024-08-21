# BlackbaudExtractor

**BlackbaudExtractor** is an ETL tool designed to extract, transform, and load data from a Blackbaud Education Management environment into a PostgreSQL database. The tool leverages Python for managing ETL pipelines and Prefect for orchestration.

## Features
Data Extraction: Extracts data such as attendance, transcripts, GPA, and enrollment from Blackbaud Education Management.
Data Transformation: Customizable transformations to align with specific data models or requirements.
Load to PostgreSQL: Seamless loading of transformed data into a PostgreSQL database for further analysis or reporting.
Orchestration with Prefect: Manages and monitors ETL flows using Prefect, with options for automatic server restarts.
OAuth Authentication: Secure access to Blackbaud’s APIs using OAuth tokens.

## Prerequisites
- Python 3.x: Ensure you have Python installed.
- PostgreSQL: Install and configure PostgreSQL.
- Prefect: Install Prefect to manage and monitor ETL flows.
- Blackbaud SKY API access.

Additionally you will need the following Python libraries:
- bottle
- requests
- psycopg2
- pandas

## Setting up Blackbaud
### Register an app with Blackbaud
To register an app with Blackbaud:
1. Sign in to Blackbaud Developer Portal: Go to Blackbaud Developer Portal and sign in with your Blackbaud ID.
2. Create a New App:
- Navigate to the "Applications" section and click "Create New Application."
- Fill in the app name, description, and redirect URL.
- Set permissions required for your app.
3. Obtain API Keys:
- After creating the app, you'll receive a Client ID and Client Secret.
- Use these for OAuth authentication in your app

If you are using any of the inlcuded ETL files that pull advanced lists, create advanced lists in blackbaud with each field found in the sql statements for the ETL python files that you intend to use. Replace the List IDs in the list id array with the list IDs for your advanced lists.

Currently, the lists in Blackbaud must be manually rolled over each year (pending a better solution). Time this with the registrar rolling over the year because the cleanup scripts could otherwise cause you to import duplicate records and cause errors. Be wary of schedueld runs.

### Authorizing with Blackbaud
The OAuth Authentication is handled by justein230's Blackbaud API Connector. See justein230/BbApiConnector-Python. I have reused some of their documentation here, though I have slightly changed his code to work with my environment.

### Prerequisites for Authorization
-  Rename the template app secrets files to app_secrets.py and app_secrets.json. At some point I'll make it so there's only one file.
- Paste your Application ID, Application Secret, and your Blackbaud API Subscription Key into the placeholders in `app_secrets.py`. These will be used for authorization and authentication throughout the process. Put these fields in 'app_secrets.json' as well. The other fields for that file will come later.
- Choose a URL to use for testing auth codes and set it in `test_api_endpoint` field in `app_secrets.py`. 
- If you are an environment admin, make sure that you have connected your application to the environment from which you want to pull data. If you are not an environment admin, ask your administrator to connect your SKY API application
- Port 13631 is used on the local machine to run the web server. Make sure that [here](https://developer.blackbaud.com/apps/), in your application settings, under Redirect URIs, that you have `http://localhost:13631/callback` as an option.

### Obtain Authorization Code to Get Tokens
1. Once the prerequisite steps are completed, run the authorization code generator component (`bb_auth.py`).
2. When the application is running, go to `http://localhost:13631`. Here, you will find the link that you need to go to in order to authorize your application with your credentials.
3. Sign in with your Blackbaud ID, then click "Authorize". You should be taken to a screen with your authorization code. If you look at the console of the application, you will see a very long access token and a much shorter refresh token. Copy these values and paste them in `app_secrets.json`.
4. Once you have copied these values into the config file, you can terminate the bb_auth application.

## Settting up the PostgresQL server
Follow the standard PostgresQL installation process. Create tables that align with the data that you are pulling from Blackbaud.

## Using Prefect for orchestration
Conda install Prefect or pip install prefect depending on your dev environment. prefect server start runs the server, and excecuting flow.py in your python env starts polling the deployments. Alternativly, on windows you can use the included .bat files. In our implimentatnion, the prefect server and polling are set to automatically restart whenever the server restarts using windows scheduler. Currently this is a little buggy. Open http://127.0.0.1:4200/dashboard on the machine where the Prefect server is running to view runs of the ETL flows.

## Contributing
Contributions are welcome! Please fork the repository and submit a pull request. Please be aware that much of the ETL code will be Blackbaud environment dependant. 

