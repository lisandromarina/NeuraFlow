import json
from dependencies import get_db_session
from repositories.sqlalchemy_user_credential_repository import SqlAlchemyUserCredentialRepository
from core.node_factory import NodeFactory
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # type: ignore

# Assuming you have a service to fetch user credentials from DB
from services.user_credential_service import UserCredentialService  

@NodeFactory.register("GoogleSheetsNode")
class GoogleSheetsExecutor:

    @staticmethod
    def run(config, context):
        """
        Reads or writes data from/to a Google Sheet using credentials stored in the database.

        Config expected:
          - user_id: identifier for the user whose credentials are stored in the DB
          - spreadsheet_id: Google Sheets document ID
          - range: range in A1 notation, e.g. "Sheet1!A1:C10"
          - action: "read" or "write"
          - values: list of lists (only required for write)
        """
        print("=== CONTEXT ===", flush=True)
        print(json.dumps(context, indent=2, default=str), flush=True)

        user_id = config.get("user_id")
        spreadsheet_id = config.get("spreadsheet_id")
        range_name = config.get("range")
        action = config.get("action", "read").lower()

        if not all([user_id, spreadsheet_id, range_name]):
            raise ValueError("Missing required config keys: user_id, spreadsheet_id, range")
        
        services = context.get("services", {})

        # Example: use a custom service (like UserCredentialService)
        user_credential_service: UserCredentialService = services.get("user_credentials")

        # Fetch credentials from DB
        creds_data = user_credential_service.get_credentials(user_id)
        if not creds_data:
            raise ValueError(f"No credentials found for user_id {user_id}")

        # Create Credentials object
        credentials = Credentials(
            token=creds_data["access_token"],
            refresh_token=creds_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=creds_data.get("client_id"),        # optional
            client_secret=creds_data.get("client_secret"),# optional
            scopes=[creds_data.get("scope", "https://www.googleapis.com/auth/spreadsheets")]
        )

        service = build("sheets", "v4", credentials=credentials)
        sheet = service.spreadsheets()

        # Read or write data
        if action == "read":
            result = sheet.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
            values = result.get("values", [])
            print(f"[GoogleSheetsNode] Read {len(values)} rows from {range_name}")
            return values

        elif action == "write":
            values = config.get("values")
            if not values:
                raise ValueError("Missing 'values' in config for write action")
            body = {"values": values}
            result = sheet.values().update(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body=body
            ).execute()
            print(f"[GoogleSheetsNode] Wrote {len(values)} rows to {range_name}")
            return result

        else:
            raise ValueError(f"Unsupported action: {action}")
