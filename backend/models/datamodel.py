from backend import db
from datetime import datetime

# --- Device Security ---
class TrustedDevice(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    ip_address = db.Column(db.String(100))
    user_agent = db.Column(db.String(300))

# --- Home Section ---
class WelcomeContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    title = db.Column(db.String(150))
    sub_title = db.Column(db.Text)
    profile_image_url = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- About Section ---
class AboutMe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100))
    description = db.Column(db.Text)
    about_image_url = db.Column(db.String(255))
    Name = db.Column(db.String(100))
    Email = db.Column(db.String(150))
    Dob = db.Column(db.String(11))
    Address = db.Column(db.String(150))
    CV_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Services ---
class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    icon = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Skills ---
class Skill(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    icon = db.Column(db.String(100))
    description = db.Column(db.String(200))
    level = db.Column(db.Integer, nullable=False)  # 0-100%
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Projects ---
class Project(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(255))
    tech_stack = db.Column(db.String(255))
    github_link = db.Column(db.String(255))
    demo_link = db.Column(db.String(255))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Footer Section ---
class FooterContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    Name = db.Column(db.String(50))
    footer_text = db.Column(db.String(255))
    github_link = db.Column(db.String(255))
    linkedin_link = db.Column(db.String(255))
    Whatsapp_link = db.Column(db.String(255))
    Instagram_link = db.Column(db.String(255))
    email = db.Column(db.String(120))
    location = db.Column(db.String(120))
    mobile = db.Column(db.String(20))
    copyright_txt = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Contact Form ---
class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Client Reviews ---
class CustomerReview(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120))
    role = db.Column(db.String(120))
    rating = db.Column(db.Integer)  # Optional
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Auto-Reply Messages ---
class AutoMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)  # e.g., "contact_reply"
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Project Inquiries ---
class ProjectMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    project_type = db.Column(db.String(255))
    Message = db.Column(db.String(300))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

# --- Clients (for reviews verification) ---
class Client(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    project = db.Column(db.String(255))

    def __repr__(self):
        return f"<Client {self.name}>"
