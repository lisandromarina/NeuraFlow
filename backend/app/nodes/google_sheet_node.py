import os
import json
from core.node_factory import NodeFactory
from core.logger import Logger
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build  # type: ignore
from googleapiclient.errors import HttpError
from services.user_credential_service import UserCredentialService


@NodeFactory.register("GoogleSheetsNode")
class GoogleSheetsExecutor:
    """
    A flexible node to perform Google Sheets operations:
    - Create, delete spreadsheets or sheets
    - Append, update, clear, or get rows
    - Append or update row (smart match)
    """

    @staticmethod
    def run(config, context):
        # === Extract Services ===
        services = context.get("services", {})
        logger: Logger = services.get("logger")
        user_credential_service: UserCredentialService = services.get("user_credentials")

        user_id = config.get("user_id")
        operation = config.get("operation")

        if not user_id or not operation:
            raise ValueError("Missing required config keys: 'user_id' and 'operation'")

        # === Load User Credentials ===
        creds_data = user_credential_service.get_credentials(user_id)
        if not creds_data:
            raise ValueError(f"No Google credentials found for user_id {user_id}")

        client_id = os.getenv("GOOGLE_CLIENT_ID")
        client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
        
        if not client_id:
            raise ValueError("Missing environment variable: GOOGLE_CLIENT_ID")
        if not client_secret:
            raise ValueError("Missing environment variable: GOOGLE_CLIENT_SECRET")
            
        credentials = Credentials(
            token=creds_data["access_token"],
            refresh_token=creds_data.get("refresh_token"),
            token_uri="https://oauth2.googleapis.com/token",
            client_id=client_id,
            client_secret=client_secret,
            scopes=[creds_data.get("scope", "https://www.googleapis.com/auth/spreadsheets")]
        )

        service = build("sheets", "v4", credentials=credentials)
        sheets = service.spreadsheets()

        logger.log(f"[GoogleSheetsNode] Running operation '{operation}'")

        try:
            # === Operation Routing ===
            if operation == "create_spreadsheet":
                return GoogleSheetsExecutor._create_spreadsheet(sheets, config)

            elif operation == "delete_spreadsheet":
                return GoogleSheetsExecutor._delete_spreadsheet(credentials, config)

            elif operation == "create_sheet":
                return GoogleSheetsExecutor._create_sheet(sheets, config)

            elif operation == "delete_sheet":
                return GoogleSheetsExecutor._delete_sheet(sheets, config)

            elif operation == "clear_sheet":
                return GoogleSheetsExecutor._clear_sheet(sheets, config)

            elif operation == "get_rows":
                return GoogleSheetsExecutor._get_rows(sheets, config)

            elif operation == "append_row":
                return GoogleSheetsExecutor._append_row(sheets, config)

            elif operation == "update_row":
                return GoogleSheetsExecutor._update_row(sheets, config)

            elif operation == "append_or_update":
                return GoogleSheetsExecutor._append_or_update(sheets, config, logger)

            elif operation == "delete_rows_or_columns":
                return GoogleSheetsExecutor._delete_rows_or_columns(sheets, config)

            else:
                raise ValueError(f"Unsupported operation: {operation}")

        except HttpError as e:
            logger.log(f"[GoogleSheetsNode] HTTP error: {e}")
            raise

        except Exception as e:
            logger.log(f"[GoogleSheetsNode] Error: {e}")
            raise

    # === Helper Methods ===

    @staticmethod
    def _create_spreadsheet(sheets, config):
        title = config.get("title", "New Spreadsheet")
        body = {"properties": {"title": title}}
        return sheets.create(body=body).execute()

    @staticmethod
    def _delete_spreadsheet(credentials, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        drive_service = build("drive", "v3", credentials=credentials)
        drive_service.files().delete(fileId=spreadsheet_id).execute()
        return {"status": "deleted", "spreadsheet_id": spreadsheet_id}

    @staticmethod
    def _create_sheet(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        sheet_title = config.get("sheet_title", "Sheet1")
        requests = [{"addSheet": {"properties": {"title": sheet_title}}}]
        return sheets.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()

    @staticmethod
    def _delete_sheet(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        sheet_id = config.get("sheet_id")
        requests = [{"deleteSheet": {"sheetId": sheet_id}}]
        return sheets.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()

    @staticmethod
    def _clear_sheet(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        range_name = config.get("range", "Sheet1")
        return sheets.values().clear(spreadsheetId=spreadsheet_id, range=range_name, body={}).execute()

    @staticmethod
    def _get_rows(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        range_name = config["range"]
        result = sheets.values().get(spreadsheetId=spreadsheet_id, range=range_name).execute()
        return result.get("values", [])

    @staticmethod
    def _append_row(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        range_name = config["range"]
        values = config["values"]
        body = {"values": values}
        return sheets.values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()

    @staticmethod
    def _update_row(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        range_name = config["range"]
        values = config["values"]
        body = {"values": values}
        return sheets.values().update(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption="RAW",
            body=body
        ).execute()

    @staticmethod
    def _append_or_update(sheets, config, logger):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        range_name = config["range"]
        new_row = config["values"][0]
        key_column = config.get("key_column", 0)

        # Fetch all current values
        existing = sheets.values().get(
            spreadsheetId=spreadsheet_id, range=range_name
        ).execute().get("values", [])

        found_index = None
        for i, row in enumerate(existing):
            if len(row) > key_column and row[key_column] == new_row[key_column]:
                found_index = i
                break

        if found_index is not None:
            update_range = f"{range_name.split('!')[0]}!A{found_index + 1}"
            logger.log(f"Updating existing row {found_index + 1}")
            return sheets.values().update(
                spreadsheetId=spreadsheet_id,
                range=update_range,
                valueInputOption="RAW",
                body={"values": [new_row]},
            ).execute()
        else:
            logger.log("Appending new row at the end of the sheet")
            return sheets.values().append(
                spreadsheetId=spreadsheet_id,
                range=range_name,
                valueInputOption="RAW",
                body={"values": [new_row]},
            ).execute()

    @staticmethod
    def _delete_rows_or_columns(sheets, config):
        spreadsheet_id = GoogleSheetsExecutor._extract_spreadsheet_id(config)
        sheet_id = config["sheet_id"]
        dimension = config.get("dimension", "ROWS")
        start_index = config.get("start_index")
        end_index = config.get("end_index")
        requests = [{
            "deleteDimension": {
                "range": {
                    "sheetId": sheet_id,
                    "dimension": dimension,
                    "startIndex": start_index,
                    "endIndex": end_index
                }
            }
        }]
        return sheets.batchUpdate(spreadsheetId=spreadsheet_id, body={"requests": requests}).execute()

    # === Helpers ===

    @staticmethod
    def _extract_spreadsheet_id(config):
        """
        Extracts spreadsheetId from URL, ID, or direct input.
        """
        spreadsheet_id = config.get("spreadsheet_id")
        if not spreadsheet_id:
            raise ValueError("Missing 'spreadsheet_id'")

        # Handle URLs like https://docs.google.com/spreadsheets/d/<id>/edit#gid=0
        if "spreadsheets/d/" in spreadsheet_id:
            return spreadsheet_id.split("/spreadsheets/d/")[1].split("/")[0]
        return spreadsheet_id
