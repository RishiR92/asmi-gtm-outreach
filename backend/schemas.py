from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class LeadCreate(BaseModel):
    name: str
    newsletter_name: Optional[str] = None
    url: Optional[str] = None
    estimated_audience: Optional[int] = None
    category: Optional[str] = None
    contact_method: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = "New"
    template_id: Optional[int] = None
    ab_variant: Optional[str] = None


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    newsletter_name: Optional[str] = None
    url: Optional[str] = None
    estimated_audience: Optional[int] = None
    category: Optional[str] = None
    contact_method: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    template_id: Optional[int] = None
    ab_variant: Optional[str] = None
    follow_up_due: Optional[datetime] = None


class LeadStatusUpdate(BaseModel):
    status: str


class BulkEmailStatusUpdate(BaseModel):
    emails: List[str]          # list of email addresses to match
    status: str = "Contacted"  # target status to set


class LeadResponse(BaseModel):
    id: int
    name: str
    newsletter_name: Optional[str] = None
    url: Optional[str] = None
    estimated_audience: Optional[int] = None
    category: Optional[str] = None
    contact_method: Optional[str] = None
    email: Optional[str] = None
    linkedin_url: Optional[str] = None
    twitter_handle: Optional[str] = None
    notes: Optional[str] = None
    status: Optional[str] = None
    date_contacted: Optional[datetime] = None
    follow_up_due: Optional[datetime] = None
    template_id: Optional[int] = None
    ab_variant: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class TemplateCreate(BaseModel):
    name: str
    category: Optional[str] = None
    subject_a: Optional[str] = None
    subject_b: Optional[str] = None
    body: Optional[str] = None
    followup1_subject: Optional[str] = None
    followup1_body: Optional[str] = None
    followup2_subject: Optional[str] = None
    followup2_body: Optional[str] = None


class TemplateUpdate(BaseModel):
    name: Optional[str] = None
    category: Optional[str] = None
    subject_a: Optional[str] = None
    subject_b: Optional[str] = None
    body: Optional[str] = None
    followup1_subject: Optional[str] = None
    followup1_body: Optional[str] = None
    followup2_subject: Optional[str] = None
    followup2_body: Optional[str] = None


class TemplateResponse(BaseModel):
    id: int
    name: str
    category: Optional[str] = None
    subject_a: Optional[str] = None
    subject_b: Optional[str] = None
    body: Optional[str] = None
    followup1_subject: Optional[str] = None
    followup1_body: Optional[str] = None
    followup2_subject: Optional[str] = None
    followup2_body: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class SendEmailRequest(BaseModel):
    lead_id: int
    template_id: int
    ab_variant: str = "A"
    custom_line: Optional[str] = ""


class SendFollowupRequest(BaseModel):
    scheduled_email_id: int


class GuessPatternRequest(BaseModel):
    first_name: str
    last_name: Optional[str] = ""
    domain: str


class AppSettingsUpdate(BaseModel):
    gmail_email: Optional[str] = None
    gmail_app_password: Optional[str] = None
    resend_api_key: Optional[str] = None
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    sender_name: Optional[str] = None
    daily_send_limit: Optional[int] = None
    followup1_days: Optional[int] = None
    followup2_days: Optional[int] = None
    send_hours_start: Optional[int] = None
    send_hours_end: Optional[int] = None
    timezone: Optional[str] = None
    imap_enabled: Optional[bool] = None
    autopilot_enabled: Optional[bool] = None


class AppSettingsResponse(BaseModel):
    id: int
    gmail_email: Optional[str] = None
    gmail_app_password: Optional[str] = None
    resend_api_key: Optional[str] = None
    gmail_client_id: Optional[str] = None
    gmail_client_secret: Optional[str] = None
    gmail_refresh_token: Optional[str] = None
    sender_name: Optional[str] = None
    # Nullable-safe integers (DB row may predate defaults)
    daily_send_limit: Optional[int] = 20
    followup1_days: Optional[int] = 4
    followup2_days: Optional[int] = 9
    send_hours_start: Optional[int] = 9
    send_hours_end: Optional[int] = 17
    timezone: Optional[str] = "America/Los_Angeles"
    imap_enabled: Optional[bool] = False
    autopilot_enabled: Optional[bool] = False

    class Config:
        from_attributes = True


class EmailLogResponse(BaseModel):
    id: int
    lead_id: int
    email_type: Optional[str] = None
    sent_at: Optional[datetime] = None
    subject: Optional[str] = None
    body: Optional[str] = None
    status: Optional[str] = None
    error_msg: Optional[str] = None
    lead_name: Optional[str] = None

    class Config:
        from_attributes = True


class ScheduledEmailResponse(BaseModel):
    id: int
    lead_id: int
    email_type: Optional[str] = None
    scheduled_for: datetime
    status: Optional[str] = None
    template_id: Optional[int] = None
    ab_variant: Optional[str] = None
    lead_name: Optional[str] = None
    lead_email: Optional[str] = None

    class Config:
        from_attributes = True
