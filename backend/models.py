from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, Enum, ForeignKey, func
from sqlalchemy.orm import relationship
from database import Base
import enum


class CategoryEnum(str, enum.Enum):
    AI_Tools = "AI Tools"
    Productivity = "Productivity"
    Indian_Origin = "Indian-Origin"
    Startup_Founder = "Startup-Founder"
    Business_Owner = "Business Owner"
    Niche = "Niche"


class ContactMethodEnum(str, enum.Enum):
    Email = "Email"
    X_DM = "X DM"
    LinkedIn = "LinkedIn"
    Submission_Form = "Submission Form"


class StatusEnum(str, enum.Enum):
    New = "New"
    Email_Found = "Email Found"
    Contacted = "Contacted"
    Replied = "Replied"
    Feature_Confirmed = "Feature Confirmed"
    Not_Interested = "Not Interested"
    No_Response = "No Response"


class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    newsletter_name = Column(String(255))
    url = Column(String(500))
    estimated_audience = Column(Integer)
    category = Column(String(50))
    contact_method = Column(String(50))
    email = Column(String(255))
    linkedin_url = Column(String(500))
    twitter_handle = Column(String(100))
    notes = Column(Text)
    status = Column(String(50), default="New")
    date_contacted = Column(DateTime)
    follow_up_due = Column(DateTime)
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    ab_variant = Column(String(1))
    priority = Column(Boolean, default=False)          # manually boosted by user
    lead_timezone = Column(String(80), default="America/New_York")  # for open-rate optimisation
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    email_logs = relationship("EmailLog", back_populates="lead")
    scheduled_emails = relationship("ScheduledEmail", back_populates="lead")


class EmailLog(Base):
    __tablename__ = "email_logs"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    email_type = Column(String(20))  # initial/followup1/followup2
    sent_at = Column(DateTime, default=func.now())
    subject = Column(String(500))
    body = Column(Text)
    status = Column(String(20), default="pending")  # sent/failed/pending
    error_msg = Column(Text)

    lead = relationship("Lead", back_populates="email_logs")


class ScheduledEmail(Base):
    __tablename__ = "scheduled_emails"

    id = Column(Integer, primary_key=True, index=True)
    lead_id = Column(Integer, ForeignKey("leads.id"), nullable=False)
    email_type = Column(String(20))  # followup1/followup2
    scheduled_for = Column(DateTime, nullable=False)
    status = Column(String(20), default="pending")  # pending/sent/cancelled
    template_id = Column(Integer, ForeignKey("templates.id"), nullable=True)
    ab_variant = Column(String(1))

    lead = relationship("Lead", back_populates="scheduled_emails")


class Template(Base):
    __tablename__ = "templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    category = Column(String(50))
    subject_a = Column(String(500))
    subject_b = Column(String(500))
    body = Column(Text)
    followup1_subject = Column(String(500))
    followup1_body = Column(Text)
    followup2_subject = Column(String(500))
    followup2_body = Column(Text)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())


class AppSettings(Base):
    __tablename__ = "app_settings"

    id = Column(Integer, primary_key=True, default=1)
    gmail_email = Column(String(255))
    gmail_app_password = Column(String(255))
    sender_name = Column(String(255), default="Rishi")
    daily_send_limit = Column(Integer, default=20)
    followup1_days = Column(Integer, default=4)
    followup2_days = Column(Integer, default=9)
    send_hours_start = Column(Integer, default=9)
    send_hours_end = Column(Integer, default=17)
    timezone = Column(String(50), default="America/Los_Angeles")
    resend_api_key = Column(String(255))
    # Gmail API (OAuth2) — works on Railway; no SMTP ports needed
    gmail_client_id     = Column(String(512))
    gmail_client_secret = Column(String(512))
    gmail_refresh_token = Column(Text)
    imap_enabled = Column(Boolean, default=False)
    autopilot_enabled = Column(Boolean, default=False)
