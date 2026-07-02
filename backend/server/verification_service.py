import os
import hmac
import hashlib
import json
import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# Reuse backend API_SECRET_TOKEN as the signing key for validation tokens
API_SECRET_TOKEN = os.getenv("API_SECRET_TOKEN", "civic-shield-secure-token-1234")

# SMTP Configurations
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER", "")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "")
SMTP_FROM = os.getenv("SMTP_FROM", SMTP_USER)

def generate_signed_token(aadhaar_hash: str, income: int, eligible: bool) -> str:
    """
    Generates a cryptographically signed URL-safe base64 token representing
    the citizen's eligibility state, signed by the server's private key.
    """
    payload = {
        "aadhaar_hash": aadhaar_hash,
        "income": income,
        "eligible": eligible
    }
    payload_str = json.dumps(payload, sort_keys=True)
    signature = hmac.new(
        API_SECRET_TOKEN.encode(),
        payload_str.encode(),
        hashlib.sha256
    ).hexdigest()
    
    token_data = {
        "payload": payload,
        "signature": signature
    }
    return base64.urlsafe_b64encode(json.dumps(token_data).encode()).decode()


def verify_signed_token(token_str: str) -> dict:
    """
    Verifies the cryptographic signature of an incoming base64 token.
    Returns the payload dict if valid, else None.
    """
    try:
        token_bytes = base64.urlsafe_b64decode(token_str.encode())
        token_data = json.loads(token_bytes.decode())
        payload = token_data["payload"]
        signature = token_data["signature"]
        
        payload_str = json.dumps(payload, sort_keys=True)
        expected_sig = hmac.new(
            API_SECRET_TOKEN.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        if hmac.compare_digest(signature, expected_sig):
            return payload
    except Exception as e:
        print(f"[VerificationService] Token verification failed: {e}")
    return None


def send_html_email(to_email: str, subject: str, html_body: str, attachment_bytes: bytes = None, attachment_name: str = None) -> bool:
    """
    Dispatches an HTML formatted email to the recipient.
    If SMTP credentials are not set in .env, falls back to logging/simulating.
    """
    # Check for Resend API fallback (Port 443 - bypasses Render SMTP block)
    resend_api_key = os.getenv("RESEND_API_KEY")
    if resend_api_key:
        try:
            import requests
            import base64
            headers = {
                "Authorization": f"Bearer {resend_api_key}",
                "Content-Type": "application/json"
            }
            # Resend requires standard sender domain, defaults to onboarding@resend.dev
            from_email = SMTP_FROM if (SMTP_FROM and "@resend.dev" not in SMTP_FROM and "@" in SMTP_FROM) else "onboarding@resend.dev"
            payload = {
                "from": from_email,
                "to": [to_email],
                "subject": subject,
                "html": html_body
            }
            if attachment_bytes and attachment_name:
                payload["attachments"] = [{
                    "content": base64.b64encode(attachment_bytes).decode("utf-8"),
                    "filename": attachment_name
                }]
            res = requests.post("https://api.resend.com/emails", json=payload, headers=headers, timeout=10)
            if res.status_code in [200, 201]:
                print(f"[Resend API] Successfully sent email to {to_email}")
                return True
            else:
                print(f"[Resend API] Failed to send: {res.text}")
        except Exception as resend_err:
            print(f"[Resend API] Error sending email: {resend_err}")

    if not SMTP_USER or not SMTP_PASSWORD:
        print(f"\n[SMTP Simulator] Dispatching email to: {to_email}")
        print(f"  - Subject:    {subject}")
        print(f"  - HTML Body Preview:\n{html_body[:500]}...\n")
        if attachment_name:
            print(f"  - Attachment: {attachment_name} ({len(attachment_bytes)} bytes)")
        return True

    try:
        msg = MIMEMultipart()
        msg["From"] = SMTP_FROM
        msg["To"] = to_email
        msg["Subject"] = subject

        msg.attach(MIMEText(html_body, "html"))

        if attachment_bytes and attachment_name:
            from email.mime.base import MIMEBase
            from email import encoders
            part = MIMEBase("application", "octet-stream")
            part.set_payload(attachment_bytes)
            encoders.encode_base64(part)
            part.add_header(
                "Content-Disposition",
                f"attachment; filename={attachment_name}"
            )
            msg.attach(part)

        server = smtplib.SMTP(SMTP_HOST, SMTP_PORT)
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, to_email, msg.as_string())
        server.quit()
        print(f"[SMTP] Successfully sent email to {to_email}")
        return True
    except Exception as e:
        print(f"[SMTP] Error sending email to {to_email}: {e}")
        return False


def build_tehsildar_email_body(pseudonym: str, income: int, approve_url: str, aadhaar: str = "N/A") -> str:
    """
    Constructs a professional, visually polished HTML template for the Tehsildar's approval request.
    """
    # Formatting income as Indian Rupees
    income_formatted = f"INR {income:,.2f}"
    
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333333;
                background-color: #f7f9fc;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 600px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e1e8ed;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                overflow: hidden;
            }}
            .header {{
                background-color: #1e3a8a;
                color: #ffffff;
                padding: 24px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 20px;
                letter-spacing: 0.5px;
            }}
            .content {{
                padding: 30px;
                line-height: 1.6;
            }}
            .badge {{
                display: inline-block;
                background-color: #eff6ff;
                color: #1e40af;
                padding: 4px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #bfdbfe;
            }}
            .details-table {{
                width: 100%;
                margin: 24px 0;
                border-collapse: collapse;
            }}
            .details-table th, .details-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }}
            .details-table th {{
                color: #4b5563;
                font-weight: 600;
                width: 40%;
            }}
            .details-table td {{
                color: #111827;
                font-weight: 500;
            }}
            .btn {{
                display: inline-block;
                text-align: center;
                background-color: #10b981;
                color: #ffffff !important;
                text-decoration: none;
                padding: 14px 24px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 15px;
                margin: 20px 0 10px 0;
                box-shadow: 0 2px 4px rgba(16, 185, 129, 0.2);
            }}
            .btn:hover {{
                background-color: #059669;
            }}
            .footer {{
                background-color: #f9fafb;
                padding: 20px;
                text-align: center;
                font-size: 11px;
                color: #6b7280;
                border-top: 1px solid #f3f4f6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>CIVIC-SHIELD Verification Request</h1>
            </div>
            <div class="content">
                <p>Respected Tehsildar Office,</p>
                <p>A citizen has requested income and eligibility verification for the <strong>CIVIC-SHIELD</strong> Legal Aid Redressal Platform. To protect user privacy, the citizen is represented by a secure, linkable pseudonym.</p>
                
                <table class="details-table">
                    <tr>
                        <th>Citizen Reference</th>
                        <td><span class="badge">{pseudonym}</span></td>
                    </tr>
                    <tr>
                        <th>Aadhaar Card Number</th>
                        <td><strong>{aadhaar}</strong></td>
                    </tr>
                    <tr>
                        <th>Declared Income</th>
                        <td><strong>{income_formatted}</strong></td>
                    </tr>
                    <tr>
                        <th>Scheme Target</th>
                        <td>Legal Aid Eligibility (Income &lt; INR 50,000.00)</td>
                    </tr>
                </table>
                
                <p>Please cross-reference the declared details against the revenue records. If correct, approve this verification to issue a cryptographic eligibility credential to the citizen's wallet:</p>
                
                <a href="{approve_url}" class="btn" target="_blank">Approve Eligibility & Issue Credential</a>
                
                <p style="font-size: 12px; color: #9ca3af; margin-top: 20px;">Note: Approving this request does not disclose the citizen's private identity. It signs a mathematical proof proving they satisfy legal aid conditions.</p>
            </div>
            <div class="footer">
                <p>This is a secure automated transmission from CIVIC-SHIELD Legal Redressal Service.</p>
            </div>
        </div>
    </body>
    </html>
    """


def build_officer_email_body(pseudonym: str, incident_type: str, act: str, sections: list, district: str, narrative: str) -> str:
    """
    Constructs a highly polished, professional HTML template for the departmental officer.
    """
    sections_str = ", ".join(sections) if isinstance(sections, list) else str(sections)
    return f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body {{
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                color: #333333;
                background-color: #f3f4f6;
                margin: 0;
                padding: 0;
            }}
            .container {{
                max-width: 650px;
                margin: 40px auto;
                background-color: #ffffff;
                border-radius: 8px;
                border: 1px solid #e5e7eb;
                box-shadow: 0 4px 6px rgba(0,0,0,0.05);
                overflow: hidden;
            }}
            .header {{
                background-color: #991b1b;
                color: #ffffff;
                padding: 24px;
                text-align: center;
            }}
            .header h1 {{
                margin: 0;
                font-size: 20px;
                letter-spacing: 0.5px;
            }}
            .content {{
                padding: 30px;
                line-height: 1.6;
            }}
            .badge {{
                display: inline-block;
                background-color: #fef2f2;
                color: #991b1b;
                padding: 4px 10px;
                border-radius: 4px;
                font-family: monospace;
                font-size: 13px;
                font-weight: bold;
                border: 1px solid #fee2e2;
            }}
            .zkp-badge {{
                display: inline-block;
                background-color: #d1fae5;
                color: #065f46;
                padding: 4px 10px;
                border-radius: 4px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #a7f3d0;
            }}
            .details-table {{
                width: 100%;
                margin: 24px 0;
                border-collapse: collapse;
            }}
            .details-table th, .details-table td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #e5e7eb;
            }}
            .details-table th {{
                color: #4b5563;
                font-weight: 600;
                width: 35%;
            }}
            .details-table td {{
                color: #111827;
            }}
            .narrative-box {{
                background-color: #f9fafb;
                border-left: 4px solid #991b1b;
                padding: 15px;
                margin: 20px 0;
                font-style: italic;
                border-radius: 0 4px 4px 0;
            }}
            .footer {{
                background-color: #f9fafb;
                padding: 20px;
                text-align: center;
                font-size: 11px;
                color: #6b7280;
                border-top: 1px solid #f3f4f6;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>OFFICIAL COMPLAINT ESCALATION</h1>
            </div>
            <div class="content">
                <p>Respected Officer,</p>
                <p>An official complaint has been registered and verified on the <strong>CIVIC-SHIELD</strong> Legal Redressal Platform. The details of the complaint are summarized below. The compiled legal aid petition is attached as a PDF.</p>
                
                <table class="details-table">
                    <tr>
                        <th>Complainant Reference</th>
                        <td><span class="badge">{pseudonym}</span></td>
                    </tr>
                    <tr>
                        <th>Identity Verification</th>
                        <td><span class="zkp-badge">🛡️ ZKP Verified Citizen</span></td>
                    </tr>
                    <tr>
                        <th>Incident Category</th>
                        <td>{incident_type.replace('_', ' ').title()}</td>
                    </tr>
                    <tr>
                        <th>District / Jurisdiction</th>
                        <td>{district}</td>
                    </tr>
                    <tr>
                        <th>Statute & Sections</th>
                        <td><strong>{act}</strong><br><span style="font-size: 12px; color: #4b5563;">{sections_str}</span></td>
                    </tr>
                </table>
                
                <h3>Citizen Narrative / Statement:</h3>
                <div class="narrative-box">
                    "{narrative}"
                </div>
                
                <p><strong>Required Action:</strong> Please review the attached PDF complaint file and initiate the necessary legal actions under the designated acts within the timeline guidelines.</p>
            </div>
            <div class="footer">
                <p>Escalated via CIVIC-SHIELD automated socio-legal assistance routing service.</p>
            </div>
        </div>
    </body>
    </html>
    """
