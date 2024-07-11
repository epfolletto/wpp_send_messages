import os.path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import pandas as pd
from dotenv import load_dotenv
import os


load_dotenv()
SCOPES = [
    "https://www.googleapis.com/auth/drive.metadata.readonly",
    "https://www.googleapis.com/auth/spreadsheets.readonly"
]


def get_folder_id(service, folder_name):
    query = f"name = '{folder_name}' and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    items = results.get('files', [])

    if not items:
        return None
    return items[0]['id']


def list_files_in_folder(service, folder_id):
    query = f"'{folder_id}' in parents and trashed = false"
    results = service.files().list(q=query, pageSize=10, fields="nextPageToken, files(id, name, webViewLink)").execute()
    items = results.get("files", [])

    return items


def get_data_sheet(creds, sheet_id, sheet_name):
    sheet_service = build("sheets", "v4", credentials=creds)
    result = sheet_service.spreadsheets().values().get(spreadsheetId=sheet_id,
                                                       range=sheet_name).execute()
    rows = result.get('values', [])
    if sheet_name == 'confgs':
        return rows[0][1], rows[1][1]
    return rows


def main():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    with open("token.json", "w") as token:
        token.write(creds.to_json())

    try:
        drive_service = build("drive", "v3", credentials=creds)

        sheet_id = os.getenv('SHEET_ID')
        sheet_name = 'confgs'
        month, year = get_data_sheet(creds, sheet_id, sheet_name)
        sheet_name = 'clients'
        data = get_data_sheet(creds, sheet_id, sheet_name)
        df = pd.DataFrame(data[1:], columns=data[0])

        folder_name = month
        folder_id = get_folder_id(drive_service, folder_name)

        if not folder_id:
            print(f"Folder '{folder_name}' not found.")
            return

        files = list_files_in_folder(drive_service, folder_id)
        clients_send = []
        for i in files:
            doc = i['name'].split('CPF_CNPJ')[-1].lstrip().split('pdf')[
                      0].replace('.', '').replace('-', '')
            clients_send.append({
                'document': doc,
                'link': i['webViewLink']
            })

        return df, clients_send, month, year

    except HttpError as error:
        # TODO - Handle errors from drive API.
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()
