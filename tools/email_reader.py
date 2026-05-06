import base64
import re
import os
from bs4 import BeautifulSoup

from googleapiclient.discovery import build
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request


SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']


class EmailReader:

    # ---------------------------
    # AUTH
    # ---------------------------
    def authenticate(self):
        creds = None

        if os.path.exists('token.json'):
            creds = Credentials.from_authorized_user_file('token.json', SCOPES)

        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES
                )
                creds = flow.run_local_server(port=0)

            with open('token.json', 'w') as token:
                token.write(creds.to_json())

        return creds

    def get_service(self):
        creds = self.authenticate()
        return build('gmail', 'v1', credentials=creds)

    # ---------------------------
    # FETCH EMAILS
    # ---------------------------
    def list_messages(self, service, max_results=10):
        results = service.users().messages().list(
            userId='me',
            maxResults=max_results
        ).execute()

        return results.get('messages', [])

    def get_message(self, service, msg_id):
        return service.users().messages().get(
            userId='me',
            id=msg_id,
            format='full'
        ).execute()

    def fetch_and_process(self, max_results=20):
        service = self.get_service()
        messages = self.list_messages(service, max_results)

        results = []

        for msg in messages:
            full_msg = self.get_message(service, msg['id'])
            processed = self.process_email(full_msg)

            if processed is not None:
                results.append(processed)

        return results

    # ---------------------------
    # BODY EXTRACTION
    # ---------------------------
    def decode_base64(self, data):
        if not data:
            return ""
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    def get_body_from_payload(self, payload):
        if 'parts' in payload:
            for part in payload['parts']:
                mime = part.get('mimeType', '')

                if mime == 'text/plain':
                    return self.decode_base64(part['body'].get('data'))

                if mime == 'text/html':
                    return self.decode_base64(part['body'].get('data'))

                result = self.get_body_from_payload(part)
                if result:
                    return result
        else:
            return self.decode_base64(payload.get('body', {}).get('data'))

        return ""

    # ---------------------------
    # HEADERS
    # ---------------------------
    def extract_headers(self, message):
        headers = message['payload']['headers']

        subject = ""
        sender = ""

        for h in headers:
            if h['name'] == 'Subject':
                subject = h['value']
            if h['name'] == 'From':
                sender = h['value']

        return subject, sender

    # ---------------------------
    # HTML CLEANING + LINKS
    # ---------------------------
    def clean_html(self, html):
        soup = BeautifulSoup(html, "lxml")
        return soup.get_text(separator="\n")

    def extract_links(self, html):
        soup = BeautifulSoup(html, "lxml")

        return [
            {"text": a.get_text(strip=True), "url": a["href"]}
            for a in soup.find_all("a", href=True)
        ]
    
    import re

    def clean_email_text(self, text: str) -> str:
        # remove huge whitespace blocks
        text = re.sub(r'\n\s*\n+', '\n\n', text)

        # remove long spaces
        text = re.sub(r'[ \t]{2,}', ' ', text)

        # remove tracking / redirect links
        text = re.sub(r'https?://[^\s]+(track|click|send|google\.com/mail).*', '', text)

        # remove common junk lines
        junk_patterns = [
            r'privacy policy',
            r'copyright',
            r'unsubscribe',
            r'this e-mail is confidential',
            r'get the official gmail app',
            r'tips for using your inbox'
        ]

        for pattern in junk_patterns:
            text = re.sub(pattern, '', text, flags=re.IGNORECASE)

        return text.strip()

    # ---------------------------
    # MAIN PROCESSOR (FIXED)
    # ---------------------------

    def is_relevant_email(self, subject: str, body: str) -> bool:
        keywords = [
            "grant", "funding", "fund", "sport", "youth",
            "community", "charity", "opportunity", "deadline"
        ]

        text = (subject + " " + body).lower()

        return any(k in text for k in keywords)

    def process_email(self, message):
        subject, sender = self.extract_headers(message)

        raw_body = self.get_body_from_payload(message['payload'])

        # clean noise first
        if "<html" in raw_body.lower():
            body = self.clean_html(raw_body)
        else:
            body = raw_body

        body = self.clean_email_text(body)

        links = self.extract_links(raw_body)

        # filter junk emails early
        if not self.is_relevant_email(subject, body):
            return None

        return {
            "email_subject": subject,
            "from": sender,
            "body": body,
            "links": links
        }