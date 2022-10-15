from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from os import path, getenv


# If modifying these scopes, delete the file token.json.
# Scopes are the permissions you are requesting from the user.
SCOPES = ['https://www.googleapis.com/auth/drive']

def authenticate_drive():
    """Authenticates using a credentials.json file and saves to the local space as token.json for repeat runs.
    
    Returns:
        service: The authenticated service object.
    """
    creds = None

    if path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)

    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request()) 
        else:
            # creds folder from env or if it doesn't exist './'
            creds_folder = getenv('PERSONAL_KEYS', './')
            creds_file = path.join(creds_folder, 'drive_credentials.json')

            flow = InstalledAppFlow.from_client_secrets_file(creds_file, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())

    return build('drive', 'v3', credentials=creds)