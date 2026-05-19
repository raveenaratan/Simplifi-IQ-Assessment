import os
import smtplib
import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from google.oauth2.service_account import Credentials
from googleapiclient.discovery import build

from enricher import enrich_company_data
from reporter import generate_pdf_report

def processing_pipeline(lead, task_id: str):
    pdf_filename = f"reports/Audit_{task_id}.pdf"
    os.makedirs("reports", exist_ok=True)
    
    try:
        # 1. Scraping and AI Processing
        insights = enrich_company_data(lead.company_name, lead.company_website)
        
        # 2. Compile Document
        generate_pdf_report(lead.name, lead.company_name, insights, pdf_filename)
        
        # 3. Disseminate Email Attachment
        send_email_with_attachment(lead.email, lead.name, pdf_filename)
        
        # 4. Failsafes wrapped to prevent blocking the core pipeline
        try:
            log_to_google_sheets(lead, "Success")
            upload_to_google_drive(pdf_filename, lead.company_name)
        except Exception as google_err:
            print(f"[Warning] Bonus integration failed: {google_err}")
            
    except Exception as e:
        print(f"[Error] Core Processing Pipeline collapsed for task {task_id}: {e}")
        try:
            log_to_google_sheets(lead, f"Failed: {str(e)}")
        except:
            pass

def send_email_with_attachment(to_email: str, recipient_name: str, file_path: str):
    smtp_server = "smtp.sendgrid.net"  
    smtp_port = 587
    sender_email = os.getenv("SENDER_EMAIL")
    password = os.getenv("SENDGRID_API_KEY")
    
    if not password or not sender_email:
        print("[Warning] Email credentials missing in environment. Skipping email dispatch phase.")
        return

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = to_email
    msg['Subject'] = "Your Personalized Operational Audit Report"
    
    body = f"Hi {recipient_name},\n\nThank you for reaching out to us. Our automated discovery engine has compiled a customized structural analysis report for your organization. Please review the attached PDF.\n\nBest regards,\nAutomation System Team"
    msg.attach(MIMEText(body, 'plain'))
    
    with open(file_path, "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header("Content-Disposition", f"attachment; filename={os.path.basename(file_path)}")
        msg.attach(part)
        
    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login("apikey", password) # Standard SendGrid username configuration
        server.send_message(msg)
    print(f"[Success] Report dispatched to {to_email}")

# GOOGLE OAUTH INTERACTION METHODS
def get_google_creds():
    # Looks for your Google Service Account JSON configuration file in root directory
    if os.path.exists("service_account.json"):
        scopes = ['[https://www.googleapis.com/auth/spreadsheets](https://www.googleapis.com/auth/spreadsheets)', '[https://www.googleapis.com/auth/drive.file](https://www.googleapis.com/auth/drive.file)']
        return Credentials.from_service_account_file('service_account.json', scopes=scopes)
    return None

def log_to_google_sheets(lead, status: str):
    creds = get_google_creds()
    spreadsheet_id = os.getenv("GOOGLE_SHEET_ID")
    if not creds or not spreadsheet_id:
        return
        
    service = build('sheets', 'v4', credentials=creds)
    row_values = [lead.name, lead.email, lead.company_name, datetime.datetime.utcnow().isoformat(), status]
    
    service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id,
        range="Sheet1!A:E",
        valueInputOption="USER_ENTERED",
        body={"values": [row_values]}
    ).execute()

def upload_to_google_drive(file_path: str, company_name: str):
    creds = get_google_creds()
    if not creds:
        return
        
    service = build('drive', 'v3', credentials=creds)
    file_metadata = {'name': f"Audit_{company_name}.pdf", 'mimeType': 'application/pdf'}
    
    from googleapiclient.http import MediaFileUpload
    media = MediaFileUpload(file_path, mimetype='application/pdf')
    service.files().create(body=file_metadata, media_body=media, fields='id').execute()
