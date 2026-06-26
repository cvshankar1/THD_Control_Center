"""
email_service.py — SMTP email notifications for the THD HR workflow

Triggered automatically at:
  1. Application submitted  → confirmation to applicant
  2. Stage → interview      → interview invitation to applicant
  3. Stage → contract       → contract-ready notice to applicant
  4. Job created            → review request to department
"""

import os
import smtplib
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

# ── SMTP config — set in .env ─────────────────────────────────────────────────
SMTP_HOST    = os.getenv("SMTP_HOST",     "smtp.gmail.com")
SMTP_PORT    = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER    = os.getenv("SMTP_USER",     "hr@thd.de")
SMTP_PASS    = os.getenv("SMTP_PASS",     "")
FROM_NAME    = os.getenv("FROM_NAME",     "THD Human Resources")
EMAIL_ENABLED = os.getenv("EMAIL_ENABLED", "false").lower() == "true"

THD_LOGO_COLOR = "#00A3D9"
THD_DARK_COLOR = "#2D2D2D"


def _base_html(content: str) -> str:
    """Shared HTML email wrapper with THD branding."""
    return f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"></head>
<body style="margin:0;padding:0;background:#F4F4F4;font-family:'Segoe UI',Arial,sans-serif">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#F4F4F4;padding:32px 0">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,.08)">

        <!-- HEADER -->
        <tr>
          <td style="background:{THD_DARK_COLOR};padding:24px 32px;border-bottom:4px solid {THD_LOGO_COLOR}">
            <table cellpadding="0" cellspacing="0">
              <tr>
                <td style="background:{THD_LOGO_COLOR};width:44px;height:44px;border-radius:9px;text-align:center;vertical-align:middle">
                  <span style="color:#fff;font-size:16px;font-weight:900;letter-spacing:-1px">THD</span>
                </td>
                <td style="padding-left:14px">
                  <div style="color:#fff;font-size:17px;font-weight:700">THD <span style="color:{THD_LOGO_COLOR}">HR</span> System</div>
                  <div style="color:#666;font-size:10px;text-transform:uppercase;letter-spacing:.1em">Human Resources Management</div>
                </td>
              </tr>
            </table>
          </td>
        </tr>

        <!-- BODY -->
        <tr><td style="padding:32px 36px">{content}</td></tr>

        <!-- FOOTER -->
        <tr>
          <td style="background:#F9F9F9;padding:18px 36px;border-top:1px solid #E0E0E0;text-align:center">
            <p style="margin:0;font-size:11px;color:#aaa">
              Technische Hochschule Deggendorf · Dieter-Görlitz-Platz 1 · 94469 Deggendorf<br>
              This is an automated message from the THD HR System. Please do not reply directly.
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""


def _send(to_email: str, subject: str, html: str) -> bool:
    """Core SMTP send. Returns True on success, False on failure."""
    if not EMAIL_ENABLED:
        logger.info(f"[EMAIL DISABLED] Would send to {to_email}: {subject}")
        return True   # Pretend success in dev mode

    if not SMTP_PASS:
        logger.warning("SMTP_PASS not set — email not sent.")
        return False

    try:
        msg = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = f"{FROM_NAME} <{SMTP_USER}>"
        msg["To"]      = to_email
        msg.attach(MIMEText(html, "html", "utf-8"))

        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as srv:
            srv.ehlo()
            srv.starttls()
            srv.login(SMTP_USER, SMTP_PASS)
            srv.sendmail(SMTP_USER, to_email, msg.as_string())

        logger.info(f"Email sent to {to_email}: {subject}")
        return True
    except Exception as exc:
        logger.error(f"Email failed to {to_email}: {exc}")
        return False


# ── Email #1 — Application confirmation ──────────────────────────────────────

def send_application_confirmation(
    applicant_name: str,
    applicant_email: str,
    job_title: str,
    dept: str
) -> bool:
    content = f"""
        <h2 style="color:#1B3A6B;margin:0 0 6px">Application Received</h2>
        <p style="color:#888;margin:0 0 24px;font-size:14px">Confirmation of your application</p>

        <p style="color:#333;font-size:15px">Dear <strong>{applicant_name}</strong>,</p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          Thank you for submitting your application for the position of
          <strong>{job_title}</strong> in the <strong>{dept}</strong> department
          at Technische Hochschule Deggendorf.
        </p>

        <div style="background:#E8F7FD;border-left:4px solid #00A3D9;padding:16px 20px;border-radius:0 8px 8px 0;margin:20px 0">
          <p style="margin:0;font-size:14px;color:#1B3A6B">
            <strong>What happens next?</strong><br>
            Our HR team will review your application and contact you within the next few working days.
            You will receive an email if you are invited for an interview.
          </p>
        </div>

        <p style="color:#555;font-size:14px">
          If you have any questions, please contact us at
          <a href="mailto:hr@thd.de" style="color:#00A3D9">hr@thd.de</a>.
        </p>

        <p style="color:#333;font-size:14px;margin-top:28px">
          Best regards,<br>
          <strong>Dept. Human Resources Management</strong><br>
          <span style="color:#888">Technische Hochschule Deggendorf</span>
        </p>
    """
    return _send(
        applicant_email,
        f"Application Received – {job_title} | THD",
        _base_html(content)
    )


# ── Email #2 — Interview invitation ──────────────────────────────────────────

def send_interview_invitation(
    applicant_name: str,
    applicant_email: str,
    job_title: str,
    dept: str
) -> bool:
    content = f"""
        <h2 style="color:#1B3A6B;margin:0 0 6px">Interview Invitation</h2>
        <p style="color:#888;margin:0 0 24px;font-size:14px">You have been selected for an interview</p>

        <p style="color:#333;font-size:15px">Dear <strong>{applicant_name}</strong>,</p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          We are pleased to inform you that your application for
          <strong>{job_title}</strong> in the <strong>{dept}</strong> department
          has successfully passed our initial review.
        </p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          We would like to invite you to a <strong>personal interview</strong>
          with the department staff. A member of our team will contact you shortly
          with the exact date, time and location.
        </p>

        <div style="background:#EDF3FB;border-left:4px solid #1B3A6B;padding:16px 20px;border-radius:0 8px 8px 0;margin:20px 0">
          <p style="margin:0;font-size:14px;color:#1B3A6B">
            <strong>Position:</strong> {job_title}<br>
            <strong>Department:</strong> {dept}<br>
            <strong>Next step:</strong> Personal interview with department staff
          </p>
        </div>

        <p style="color:#555;font-size:14px">
          Please confirm receipt of this email by replying or contacting us at
          <a href="mailto:hr@thd.de" style="color:#00A3D9">hr@thd.de</a>.
        </p>

        <p style="color:#333;font-size:14px;margin-top:28px">
          Best regards,<br>
          <strong>Dept. Human Resources Management</strong><br>
          <span style="color:#888">Technische Hochschule Deggendorf</span>
        </p>
    """
    return _send(
        applicant_email,
        f"Interview Invitation – {job_title} | THD",
        _base_html(content)
    )


# ── Email #3 — Contract ready ─────────────────────────────────────────────────

def send_contract_ready(
    applicant_name: str,
    applicant_email: str,
    job_title: str,
    time_tracking_url: str = "https://timetracking.thd.de"
) -> bool:
    content = f"""
        <h2 style="color:#1B3A6B;margin:0 0 6px">Your Contract is Ready</h2>
        <p style="color:#888;margin:0 0 24px;font-size:14px">Please sign your employment contract</p>

        <p style="color:#333;font-size:15px">Dear <strong>{applicant_name}</strong>,</p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          Congratulations! We are delighted to confirm that your application for
          <strong>{job_title}</strong> at Technische Hochschule Deggendorf
          has been successful.
        </p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          Your employment contract has been prepared in our HR management system
          <strong>VIVA</strong>. Please visit the HR office with a valid
          <strong>student ID</strong> to sign the contract documents.
        </p>

        <div style="background:#E8F7FD;border-left:4px solid #00A3D9;padding:16px 20px;border-radius:0 8px 8px 0;margin:20px 0">
          <p style="margin:0 0 10px;font-size:14px;color:#1B3A6B"><strong>Time Tracking System</strong></p>
          <p style="margin:0;font-size:13.5px;color:#333;line-height:1.7">
            You have been registered in our time tracking system.<br>
            Access your account here:
            <a href="{time_tracking_url}" style="color:#00A3D9">{time_tracking_url}</a>
          </p>
        </div>

        <div style="background:#FFF8E6;border-left:4px solid #B35900;padding:14px 20px;border-radius:0 8px 8px 0;margin:16px 0">
          <p style="margin:0;font-size:13.5px;color:#B35900">
            <strong>⚠ Important:</strong> Please log your working hours each day.
            Monthly submissions are required for payroll processing.
            Late submissions may delay your payment.
          </p>
        </div>

        <p style="color:#555;font-size:14px;margin-top:20px">
          Welcome to the team! We look forward to working with you.
        </p>

        <p style="color:#333;font-size:14px;margin-top:28px">
          Best regards,<br>
          <strong>Dept. Human Resources Management</strong><br>
          <span style="color:#888">Technische Hochschule Deggendorf</span>
        </p>
    """
    return _send(
        applicant_email,
        f"Your Contract is Ready – {job_title} | THD",
        _base_html(content)
    )


# ── Email #4 — Department review request ─────────────────────────────────────

def send_review_request(
    dept_head_email: str,
    dept_head_name: str,
    job_title: str,
    dept: str,
    submitter_name: str
) -> bool:
    content = f"""
        <h2 style="color:#1B3A6B;margin:0 0 6px">Job Posting Requires Your Approval</h2>
        <p style="color:#888;margin:0 0 24px;font-size:14px">A new posting needs your review</p>

        <p style="color:#333;font-size:15px">Dear <strong>{dept_head_name}</strong>,</p>

        <p style="color:#555;font-size:14px;line-height:1.7">
          A new job posting has been submitted and requires your approval before
          it can be published.
        </p>

        <div style="background:#EDF3FB;border-left:4px solid #1B3A6B;padding:16px 20px;border-radius:0 8px 8px 0;margin:20px 0">
          <p style="margin:0;font-size:14px;color:#1B3A6B">
            <strong>Position:</strong> {job_title}<br>
            <strong>Department:</strong> {dept}<br>
            <strong>Submitted by:</strong> {submitter_name}
          </p>
        </div>

        <p style="color:#555;font-size:14px">
          Please log in to the THD HR System to review and approve or reject this posting.
        </p>

        <p style="color:#333;font-size:14px;margin-top:28px">
          Best regards,<br>
          <strong>THD HR System</strong><br>
          <span style="color:#888">Automated Notification</span>
        </p>
    """
    return _send(
        dept_head_email,
        f"Review Required: {job_title} | THD HR",
        _base_html(content)
    )
