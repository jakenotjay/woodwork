# Various authentication methods for woodwork

## For Drive:
1. Follow instructions for getting credentials for your own [Google API account] (https://developers.google.com/drive/api/quickstart/python#authorize_credentials_for_a_desktop_application)
2. Save the credentials.json as 'credentials.json'
3. Put file in same directory as auth, or specify a path in the PERSONAL_KEYS environment variable

## For EE:
1. Get valid credentials
2. Set     EE_PROJECT, EE_SERVICE_ACCOUNT, and EE_PRIVATE_KEY_FILE
3. Auth

OR

1. Don't set above env vars and authenticate using oauth via url in console