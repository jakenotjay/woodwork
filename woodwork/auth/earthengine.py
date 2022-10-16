import ee
from os import getenv

def get_endpoint():
    """Get the EarthEngine endpoint to use based on env variable"""
    endpoint = getenv("EE_ENDPOINT", "https://earthengine.googleapis.com")
    print(f"Using EarthEngine endpoint {endpoint}")
    return endpoint

def auth_with_service_account(service_account, service_account_key, ee_project):
    """Authenticate with a service account"""
    ee_credentials = ee.ServiceAccountCredentials(service_account, service_account_key)
    print(f"Initializing EarthEngine with service account on project {ee_project}")
    ee.Initialize(ee_credentials, project=ee_project, opt_url=get_endpoint())

def auth_with_notebook():
    """Authenticate with a notebook"""
    print("Initializing EarthEngine with notebook authentication")
    ee.Authenticate()
    ee.Initialize(opt_url=get_endpoint())

def auth_without_credentials():
    """Authenticate with credentials"""
    print("Initializing EarthEngine without credentials")
    ee.Initialize(opt_url=get_endpoint())

string_to_method = {
    "service_account": auth_with_service_account,
    "notebook": auth_with_notebook,
    "none": auth_without_credentials,
}

def authenticate_ee(method=None, service_account=None, service_account_key=None, ee_project=None):
    """Authenticate with Earth Engine, defaults to service account, looks for environment variables: EE_PROJECT, EE_SERVICE_ACCOUNT, EE_PRIVATE_KEY_FILE"""
    if method is not None:
        string_to_method[method](service_account, service_account_key, ee_project)

    EE_PROJECT = getenv("EE_PROJECT")
    EE_ACCOUNT = getenv("EE_SERVICE_ACCOUNT")
    EE_PRIVATE_KEY_FILE = getenv("EE_PRIVATE_KEY_FILE")

    if EE_PROJECT is not None and EE_ACCOUNT is not None and EE_PRIVATE_KEY_FILE is not None:
        auth_with_service_account(EE_ACCOUNT, EE_PRIVATE_KEY_FILE, EE_PROJECT)
    else:
        auth_with_notebook()
