import csv
from pathlib import Path
from datetime import datetime
from utils.config import get_setting

def save_lead(lead):
    # Google Sheets is optional. If credentials are absent or integration fails,
    # save to local CSV for local development.
    service_json = get_setting("GOOGLE_SERVICE_ACCOUNT_JSON")
    sheet_id = get_setting("GOOGLE_SHEET_ID")
    if service_json and sheet_id:
        try:
            import json, gspread
            from google.oauth2.service_account import Credentials
            info = json.loads(service_json) if isinstance(service_json, str) else dict(service_json)
            scopes = ["https://www.googleapis.com/auth/spreadsheets",
                      "https://www.googleapis.com/auth/drive"]
            creds = Credentials.from_service_account_info(info, scopes=scopes)
            client = gspread.authorize(creds)
            sheet = client.open_by_key(sheet_id).sheet1
            if not sheet.get_all_values():
                sheet.append_row(["Timestamp","Name","Email","Phone","College","Branch",
                                  "Year","CGPA","Program","Message","Consent"])
            sheet.append_row([lead.get(k, "") for k in [
                "timestamp","name","email","phone","college","branch","year","cgpa",
                "program","message","consent"
            ]])
            return "Google Sheets"
        except Exception:
            pass
    path = Path(__file__).resolve().parents[1] / "leads.csv"
    exists = path.exists()
    with path.open("a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(lead.keys()))
        if not exists:
            writer.writeheader()
        writer.writerow(lead)
    return "local leads.csv"