from flask import Blueprint, jsonify, request
from backend import db
from backend.models.datamodel import (
    WelcomeContent, AboutMe, Service, Skill, Project, AutoMessage,
    FooterContent, ContactMessage, CustomerReview, Client, ProjectMessage
)
from backend.utils.security import send_otp_email
from flask_cors import CORS

api_bp = Blueprint("api", __name__)
CORS(api_bp)

# ------------ Read-only APIs ------------ #

@api_bp.route("/api/welcome")
def get_welcome():
    data = WelcomeContent.query.first()
    if not data:
        return jsonify({"error": "No content"}), 404
    return jsonify({
        "name": data.name,
        "title": data.title,
        "sub_title": data.sub_title,
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
        "name": data.Name,
        "email": data.Email,
        "dob": data.Dob,
        "address": data.Address,
        "cv_link": data.CV_link,
        "about_image_url": f"/static/uploads/{data.about_image_url}" if data.about_image_url else None,
    })


@api_bp.route("/api/skills")
def get_skills():
    skills = Skill.query.all()
    return jsonify([
        {
            "name": skill.name,
            "description": skill.description,
            "level": skill.level,
            "icon": skill.icon
        } for skill in skills
    ])


@api_bp.route("/api/services")
def get_services():
    services = Service.query.all()
    return jsonify([
        {
            "title": s.title,
            "description": s.description,
            "icon": s.icon
        } for s in services
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
            "message": r.message,
            "rating": r.rating,
            "created_at": r.created_at.strftime("%Y-%m-%d")
        } for r in reviews
    ])


@api_bp.route("/api/footer", methods=["GET"])
def get_footer():
    content = FooterContent.query.first()

    if not content:
        return jsonify({"error": "No footer content"}), 404

    return jsonify({
        "id": content.id,
        "name": content.name,
        "footer_text": content.footer_text,
        "github_link": content.github_link,
        "linkedin_link": content.linkedin_link,
        "whatsapp_link": content.whatsapp_link,
        "instagram_link": content.instagram_link,
        "email": content.email,
        "location": content.location,
        "mobile": content.mobile,
        "copyright_txt": content.copyright_txt
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

    body = f"New contact message:\n\nName: {name}\nEmail: {email}\nMessage:\n{message}"
    send_otp_email("yoogesh06@gmail.com", body, subject="New Contact Form Submission")

    return jsonify({"success": True, "message": "Message sent"}), 200


@api_bp.route("/api/project_message", methods=["POST"])
def api_project_message():
    data = request.form
    name = data.get("name")
    email = data.get("email")
    project_type = data.get("project_type")
    message = data.get("message")

    new_msg = ProjectMessage(
        name=name,
        email=email,
        project_type=project_type,
        Message=message
    )
    db.session.add(new_msg)

    auto_reply = AutoMessage.query.filter_by(key="project_reply").first()
    if auto_reply:
        print(f"Sending auto-reply to {email}: {auto_reply.message}")
    else:
        print("⚠️ No auto-reply message configured with key='project_reply'")

    db.session.commit()

    return jsonify({"status": "success", "message": "Project message submitted!"}), 201


@api_bp.route("/api/reviews", methods=["POST"])
def post_review():
    data = request.get_json()
    email = data.get("email")
    message = data.get("message")
    rating = int(data.get("rating", 0))

    if not all([email, message, rating]):
        return jsonify({"error": "All fields required"}), 400

    client = Client.query.filter_by(email=email).first()
    if not client:
        return jsonify({
            "error": "You're not authorized to post a review. Your email is not recognized as a client."
        }), 403

    review = CustomerReview(
        name=client.name,
        email=email,
        message=message,
        rating=rating
    )
    db.session.add(review)
    db.session.commit()

    body = f"New review by client:\nName: {client.name}\nEmail: {email}\nRating: {rating}\nMessage:\n{message}"
    send_otp_email("yoogesh06@gmail.com", body, subject="Client Review Submitted")

    return jsonify({"success": True, "message": "Review submitted"}), 200

