import gspread
from google.oauth2.service_account import Credentials

# Define scope for Google Sheets + Drive
SCOPES = ["https://www.googleapis.com/auth/spreadsheets",
          "https://www.googleapis.com/auth/drive"]

# Load credentials from your downloaded JSON
creds = Credentials.from_service_account_file("service_account.json", scopes=SCOPES)

# Authorize client
client = gspread.authorize(creds)

# Open Google Sheet (use your sheet name or URL)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1ZvnFO2YCTxH56SR03Jyr3ovRBm58ZBK28WWAcTKNrqs/edit#gid=0"
sheet = client.open_by_url(SHEET_URL).sheet1  # sheet1 = first tab

# Example: write a row
sheet.append_row(["2025-08-17", "Breakfast", 600, "Cardio", 200, "Net -400"])

# Example: read rows
rows = sheet.get_all_values()
for row in rows:
    print(row)
