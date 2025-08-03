from flask import Blueprint, jsonify, request
from backend import db
from backend.models.datamodel import (
    WelcomeContent, AboutMe, Service, Skill, Project,AutoMessage,
    FooterContent, ContactMessage, CustomerReview, Client,ProjectMessage
)
from backend.utils.security import send_otp_email  # Reused for sending emails
from flask_cors import CORS
import os

api_bp = Blueprint("api", __name__)
CORS(api_bp)  # Allow cross-origin requests from React

# ------------ Read-only APIs ------------ #

@api_bp.route("/api/welcome")
def get_welcome():
    data = WelcomeContent.query.first()
    if not data:
        return jsonify({"error": "No content"}), 404
    return jsonify({
        "title": data.title,
        "subtitle": data.subtitle,
        "description": data.description,
        "background_image_url": f"/static/uploads/{data.background_image_url}" if data.background_image_url else None,
        "profile_image_url": f"/static/uploads/{data.profile_image_url}" if data.profile_image_url else None,
    })


@api_bp.route("/api/about")
def get_about():
    data = AboutMe.query.first()
    if not data:
        return jsonify({"error": "No content"}), 404
    return jsonify({
        "title": data.title,
        "description": data.description,
        "experience": data.experience,
        "education": data.education,
        "profile_image_url": f"/static/uploads/{data.profile_image_url}" if data.profile_image_url else None,
        "about_image_url": f"/static/uploads/{data.about_image_url}" if data.about_image_url else None,
    })


@api_bp.route("/api/skills")
def get_skills():
    skills = Skill.query.all()
    return jsonify([
        {"name": skill.name, "level": skill.level, "type": skill.type}
        for skill in skills
    ])


@api_bp.route("/api/services")
def get_services():
    services = Service.query.all()
    return jsonify([
        {"title": s.title, "description": s.description, "icon": s.icon}
        for s in services
    ])


@api_bp.route("/api/projects")
def get_projects():
    projects = Project.query.all()
    return jsonify([
        {
            "title": p.title,
            "description": p.description,
            "tech_stack": p.tech_stack,
            "image_url": f"/static/uploads/{p.image_url}" if p.image_url else None,
            "github_link": p.github_link,
            "demo_link": p.demo_link
        } for p in projects
    ])


@api_bp.route("/api/reviews", methods=["GET"])
def get_reviews():
    reviews = CustomerReview.query.order_by(CustomerReview.created_at.desc()).all()
    return jsonify([
        {
            "name": r.name,
            "image_url": f"/static/uploads/{r.image_url}" if r.image_url else None,
            "message": r.message,
            "rating": r.rating,
            "created_at": r.created_at.strftime("%Y-%m-%d")
        } for r in reviews
    ])


@api_bp.route("/api/footer")
def get_footer():
    content = FooterContent.query.first()
    if not content:
        return jsonify({"error": "No footer content"}), 404
    return jsonify({
        "footer_text": content.footer_text,
        "github_link": content.github_link,
        "linkedin_link": content.linkedin_link,
        "email": content.email,
        "location": content.location,
        "mobile": content.mobile
    })

# ------------ POST APIs ------------ #

@api_bp.route("/api/contact", methods=["POST"])
def post_contact():
    data = request.get_json()
    name = data.get("name")
    email = data.get("email")
    message = data.get("message")

    if not all([name, email, message]):
        return jsonify({"error": "All fields required"}), 400

    new_msg = ContactMessage(name=name, email=email, message=message)
    db.session.add(new_msg)
    db.session.commit()

    # Send email to admin
    body = f"New contact message:\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
    send_otp_email("youremail@example.com", body, subject="New Contact Form Submission")

    return jsonify({"success": True, "message": "Message sent"}), 200

@api_bp.route("/api/project_message", methods=["POST"])
def api_project_message():
    data = request.form
    name = data.get("name")
    email = data.get("email")
    project_type = data.get("project_type")
    message = data.get("message")

    # Save the message
    new_msg = ProjectMessage(
        name=name,
        email=email,
        project_type=project_type,
        Message=message
    )
    db.session.add(new_msg)

    # ✅ Fetch auto-response template
    auto_reply = AutoMessage.query.filter_by(key="project_reply").first()

    if auto_reply:
        # ✅ Simulate sending email or just print
        print(f"Sending auto-reply to {email}: {auto_reply.message}")
        # Optional: implement email sending logic using Flask-Mail or smtplib here
    if not auto_reply:
        print("⚠️ No auto-reply message configured with key='project_reply'")

    db.session.commit()

    return jsonify({"status": "success", "message": "Project message submitted!"}), 201


@api_bp.route("/api/reviews", methods=["POST"])
def post_review():
    data = request.get_json()
    email = data.get("email")
    message = data.get("message")
    rating = int(data.get("rating", 0))

    # Validate input
    if not all([email, message, rating]):
        return jsonify({"error": "All fields required"}), 400

    # ✅ Only allow reviews from clients
    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({
            "error": "You're not authorized to post a review. Your email is not recognized as a client."
        }), 403

    # Add review with client name
    review = CustomerReview(
        name=client.name,
        message=message,
        rating=rating
    )
    db.session.add(review)
    db.session.commit()

    # Optional: Email admin notification
    body = f"New review by client:\nName: {client.name}\nEmail: {email}\nRating: {rating}\nMessage:\n{message}"
    send_otp_email("yoogesh06@gmail.com", body, subject="Client Review Submitted")

    return jsonify({"success": True, "message": "Review submitted"}), 200
