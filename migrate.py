from backend import create_app, db
from backend.models.datamodel import WelcomeContent, AboutMe,Service,Skill,Project,FooterContent,ContactMessage,CustomerReview,AutoMessage,TrustedDevice,Client,ProjectMessage

app = create_app()

with app.app_context():
    db.create_all()
    print("✅ Tables created successfully.")
