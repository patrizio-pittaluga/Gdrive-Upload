from googleapiclient import discovery
from apiclient.http import MediaFileUpload
import os
import ssl
from datetime import datetime
from time import sleep
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.http import MediaFileUpload
import requests
import logging 
logging.basicConfig(filename='app.log',filemode='a',format='%(message)s')

# Disable SSL certificate verification
requests.packages.urllib3.disable_warnings()
ssl.SSLContext.verify_mode = property(lambda self: ssl.CERT_NONE, lambda self, newval: None)

SCOPES = ['https://www.googleapis.com/auth/drive']

# Loading credentials- If not present the token.json file will open you a web page for permission.
creds = None
if os.path.exists('token.json'):
    creds = Credentials.from_authorized_user_file('token.json')
if not creds or not creds.valid:
    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
    else:
        flow = InstalledAppFlow.from_client_secrets_file(
            'credentials.json', SCOPES)  
        creds = flow.run_local_server(port=8080)
    with open('token.json', 'w') as token:
        token.write(creds.to_json())

drive_service = discovery.build('drive', 'v3', credentials=creds)

def checkFileUploaded(filename):
    if not os.path.exists(log_file_path):
        return False
    with open(log_file_path, 'r') as log_file:
        for line in log_file:
            if filename in line:
                return True
    return False

def uploadFile(filename, filepath, mimetype, folderid):
    local_filename = os.path.basename(filepath)
    if checkFileUploaded(local_filename):
        print(f"The file: '{local_filename}'has already been loaded.")
        return
    
    file_metadata = {'name': filename,
                     "parents": [folderid]
                     }
    media = MediaFileUpload(filepath,
                            mimetype=mimetype)
    try:
        file = drive_service.files().create(body=file_metadata,
                                            media_body=media,
                                            fields='id', supportsAllDrives=True).execute()
        print('File ID: %s' % file.get('id'))
    except PermissionError as e:
        error_message = f"File '{local_filename}'Upload KO for permissions error: {e}"
        print(error_message)
    else:
        print(f"File '{local_filename}' upload successful.")
        log_info = f"Date & hour: {datetime.now()}, File Name: {local_filename}, Upload Status: OK"
        logging.warning(log_info)
          #  sleep(0)

folder_path = 'Upload'  #Folder path 
log_file_path = 'app.log'  #Log file path

if not os.path.exists(log_file_path):
    with open(log_file_path, 'w') as log_file:
        log_file.write("Log degli upload:\n")

for filename in os.listdir(folder_path):
    #print(filename)
    file_path = os.path.join(folder_path, filename)

    #mimetype = 'application/pdf'
    mimetype = '*/*'
    folderid = '' #ID folder on Gdrive/Gsharedrive. The account that creates the token must have permissions to modify the folder
    
    uploadFile(filename, file_path, mimetype, folderid)
    #sleep(0)
