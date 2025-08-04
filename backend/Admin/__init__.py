from backend.utils.security import get_client_ip, get_user_agent, generate_otp, send_otp_email
from flask import Blueprint, render_template, session, redirect, url_for, request, flash
from backend import db
import os
from werkzeug.utils import secure_filename
from sqlalchemy import func
from backend.models.datamodel import (AboutMe, AutoMessage, Client, ContactMessage, CustomerReview,
    FooterContent, Project, ProjectMessage, Service, Skill, TrustedDevice, WelcomeContent)

admin_bp = Blueprint('admin', __name__, 
                    static_folder='static',
                    static_url_path='/admin/static',
                    template_folder='templates')

@admin_bp.route('/admin/fake_login')
def fake_login():
    session['admin_authenticated'] = True
    return redirect(url_for('admin.dashboard'))


@admin_bp.route('/admin/dashboard', methods=["GET", "POST"])
def dashboard():
    if not session.get('admin_authenticated'):
        ip = get_client_ip()
        ua = get_user_agent()

        trusted = TrustedDevice.query.filter_by(ip_address=ip, user_agent=ua).first()
        if trusted:
            session['admin_authenticated'] = True
        else:
            # Not trusted, send OTP
            otp = generate_otp()
            session['otp'] = otp
            session['temp_ip'] = ip
            session['temp_ua'] = ua

            send_otp_email("yoogesh06@gmail.com", otp)
            flash("Unrecognized device. OTP sent to your email.")
            return redirect(url_for("admin.otp_verify"))


    page = request.args.get("page", "dashboard")
    content = None
    UPLOAD_FOLDER = os.path.join("backend", "static", "uploads")  # Adjusted path
    os.makedirs(UPLOAD_FOLDER, exist_ok=True)

    # Allowed file extensions
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
    
    def allowed_file(filename):
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    if page == "dashboard":
        stats = {
            "total_messages": ContactMessage.query.count(),
            "total_reviews": CustomerReview.query.count(),
            "total_projects": Project.query.count(),
            "total_skills": Skill.query.count(),
            "total_project_messages": ProjectMessage.query.count(),
        }

        recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()

        # Rating chart data
        rating_counts = db.session.query(CustomerReview.rating, func.count(CustomerReview.id))\
                        .group_by(CustomerReview.rating).order_by(CustomerReview.rating).all()
        rating_data = {
            "labels": [str(r[0]) for r in rating_counts],
            "counts": [r[1] for r in rating_counts]
        }

        return render_template("dashboard.html", page=page, stats=stats, 
                             recent_messages=recent_messages, rating_data=rating_data)

    # --- Welcome Section ---
    if page == "welcome":
        content = WelcomeContent.query.first()

        if request.method == "POST":
            # Get form data
            name = request.form.get("name")
            title = request.form.get("title")
            sub_title = request.form.get("sub_title")

            # Initialize with existing values
            profile_filename = content.profile_image_url if content else None

            # Handle profile image upload
            if 'profile_image_url' in request.files:
                profile_file = request.files['profile_image_url']
                if profile_file and profile_file.filename and allowed_file(profile_file.filename):
                    # Delete old file if exists
                    if profile_filename and os.path.exists(os.path.join(UPLOAD_FOLDER, profile_filename)):
                        os.remove(os.path.join(UPLOAD_FOLDER, profile_filename))
                    # Save new file
                    profile_filename = secure_filename(profile_file.filename)
                    profile_file.save(os.path.join(UPLOAD_FOLDER, profile_filename))

            # Create or update content
            if content:
                content.name = name
                content.title = title
                content.sub_title = sub_title
                if profile_filename:
                    content.profile_image_url = profile_filename
            else:
                content = WelcomeContent(
                    name = name,
                    title=title,
                    sub_title=sub_title,
                    profile_image_url=profile_filename
                )
                db.session.add(content)

            db.session.commit()
            flash('Welcome content updated successfully!', 'success')
            return redirect(url_for("admin.dashboard", page="welcome"))

        return render_template("dashboard.html", page=page, content=content)

    # --- About Me Section ---
    if page == "about":
        content = AboutMe.query.first()
        UPLOAD_FOLDER = os.path.join("backend", "static", "uploads")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if request.method == "POST":
            # Get form data
            title = request.form.get("title")
            description = request.form.get("description")
            Name = request.form.get("Name")
            Email = request.form.get("Email")
            Dob = request.form.get("Dob")
            Address = request.form.get("Address")
            CV_link = request.form.get("CV_link")

            # Initialize with existing image filename
            about_filename = content.about_image_url if content else None

            # Handle about image upload
            if 'about_image_url' in request.files:
                about_file = request.files['about_image_url']
                if about_file and about_file.filename and allowed_file(about_file.filename):
                    # Delete old image if exists
                    if about_filename and os.path.exists(os.path.join(UPLOAD_FOLDER, about_filename)):
                        os.remove(os.path.join(UPLOAD_FOLDER, about_filename))
                    # Save new image
                    about_filename = secure_filename(about_file.filename)
                    about_file.save(os.path.join(UPLOAD_FOLDER, about_filename))

            # Create or update content
            if content:
                content.title = title
                content.description = description
                content.Name = Name
                content.Email = Email
                content.Dob = Dob
                content.Address = Address
                content.CV_link = CV_link
                content.about_image_url = about_filename
            else:
                content = AboutMe(
                    title=title,
                    description=description,
                    Name=Name,
                    Email=Email,
                    Dob=Dob,
                    Address=Address,
                    CV_link=CV_link,
                    about_image_url=about_filename
                )
                db.session.add(content)

            db.session.commit()
            flash('About Me content updated successfully!', 'success')
            return redirect(url_for("admin.dashboard", page="about"))

        return render_template("dashboard.html", page=page, content=content)

    # --- Services Section ---
    if page == "services":
        if request.method == "POST":
            if request.form.get("delete_id"):
                service = Service.query.get(request.form["delete_id"])
                if service:
                    db.session.delete(service)
            else:
                new_service = Service(
                    title=request.form["title"],
                    description=request.form["description"],
                    icon=request.form["icon"]
                )
                db.session.add(new_service)
            db.session.commit()
            return redirect(url_for("admin.dashboard", page="services"))

        services = Service.query.all()
        return render_template("dashboard.html", page=page, services=services)

    # --- Skills Section ---
    if page == "skills":
        if request.method == "POST":
            # Delete operation
            if request.form.get("delete_id"):
                skill = Skill.query.get(request.form["delete_id"])
                if skill:
                    db.session.delete(skill)
                    db.session.commit()
                    flash("Skill deleted successfully.", "success")

            # Create operation
            else:
                name = request.form.get("name")
                icon = request.form.get("icon")
                description = request.form.get("description")
                level = request.form.get("level")

                if not all([name, level]):
                    flash("Skill name and level are required.", "warning")
                else:
                    try:
                        level = int(level)
                        new_skill = Skill(name=name, icon=icon, description=description, level=level)
                        db.session.add(new_skill)
                        db.session.commit()
                        flash("New skill added.", "success")
                    except ValueError:
                        flash("Level must be a number.", "danger")

            return redirect(url_for("admin.dashboard", page="skills"))

        skills = Skill.query.all()
        return render_template("dashboard.html", page=page, skills=skills)

    # --- Projects Section ---
    if page == "projects":
        UPLOAD_FOLDER = os.path.join("backend", "static", "uploads")
        os.makedirs(UPLOAD_FOLDER, exist_ok=True)
        ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

        def allowed_file(filename):
            return '.' in filename and \
                filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

        if request.method == "POST":
            if request.form.get("delete_id"):
                # Handle project deletion
                project = Project.query.get(request.form["delete_id"])
                if project:
                    # Delete associated image file if exists
                    if project.image_url and os.path.exists(os.path.join(UPLOAD_FOLDER, project.image_url)):
                        os.remove(os.path.join(UPLOAD_FOLDER, project.image_url))
                    db.session.delete(project)
            else:
                # Handle project creation/update
                title = request.form.get("title")
                description = request.form.get("description")
                tech_stack = request.form.get("tech_stack")
                github_link = request.form.get("github_link")
                demo_link = request.form.get("demo_link")

                # Handle image upload
                image_filename = None
                if 'image_url' in request.files:
                    image_file = request.files['image_url']
                    if image_file and image_file.filename and allowed_file(image_file.filename):
                        image_filename = secure_filename(image_file.filename)
                        image_file.save(os.path.join(UPLOAD_FOLDER, image_filename))

                # Create new project
                new_project = Project(
                    title=title,
                    description=description,
                    image_url=image_filename,
                    tech_stack=tech_stack,
                    github_link=github_link,
                    demo_link=demo_link
                )
                db.session.add(new_project)

            db.session.commit()
            flash('Projects updated successfully!', 'success')
            return redirect(url_for("admin.dashboard", page="projects"))

        projects = Project.query.all()
        return render_template("dashboard.html", page=page, projects=projects)
    if page == "project_message":
        messages = ProjectMessage.query.order_by(ProjectMessage.created_at.desc()).all()
        return render_template("dashboard.html",page = page, messages = messages)
    # --- Clients Section ---
    if page == "clients":
        if request.method == "POST":
            if request.form.get("delete_id"):
                client = Client.query.get(request.form["delete_id"])
                if client:
                    db.session.delete(client)
                    db.session.commit()
                    flash("Client deleted.", "success")
            else:
                name = request.form["name"]
                email = request.form["email"]
                project = request.form["project"]

                # Check if email already exists
                if Client.query.filter_by(email=email).first():
                    flash("Client with this email already exists.", "warning")
                else:
                    new_client = Client(name=name, email=email, project=project)
                    db.session.add(new_client)
                    db.session.commit()
                    flash("Client added successfully.", "success")

            return redirect(url_for("admin.dashboard", page="clients"))

        clients = Client.query.all()
        return render_template("dashboard.html", page=page, clients=clients)

    
    # --- Footer Section ---
    if page == "footer":
        content = FooterContent.query.first()
        if request.method == "POST":
            if content:
                content.Name = request.form["Name"]
                content.footer_text = request.form["footer_text"]
                content.github_link = request.form["github_link"]
                content.linkedin_link = request.form["linkedin_link"]
                content.Whatsapp_link = request.form["Whatsapp_link"]
                content.Instagram_link = request.form["Instagram_link"]
                content.email = request.form["email"]
                content.location = request.form["location"]
                content.mobile = request.form["mobile"]
                content.copyright_txt = request.form["copyright_txt"]
            else:
                content = FooterContent(
                    Name = request.form["Name"],
                    footer_text=request.form["footer_text"],
                    github_link=request.form["github_link"],
                    linkedin_link=request.form["linkedin_link"],
                    Whatsapp_link = request.form["Whatsapp_link"],
                    Instagram_link = request.form["Instagram_link"],
                    email=request.form["email"],
                    location=request.form["location"],
                    mobile=request.form["mobile"],
                    copyright_txt = request.form["copyright_txt"],
                )
                db.session.add(content)
            db.session.commit()
            return redirect(url_for("admin.dashboard", page="footer"))
        footers = FooterContent.query.all()
        return render_template("dashboard.html", page=page, content=content,footers = footers)

    # --- Contact Messages Section ---
    if page == "messages":
        if request.method == "POST" and request.form.get("delete_id"):
            msg = ContactMessage.query.get(request.form["delete_id"])
            if msg:
                db.session.delete(msg)
                db.session.commit()
            return redirect(url_for("admin.dashboard", page="messages"))
        
        messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).all()
        return render_template("dashboard.html", page=page, messages=messages)
    
    # page client message
    if page == "clientmessage":
        if request.method == "POST" and request.form.get("delete_id"):
            msg = ProjectMessage.query.get(request.form["delete_id"])
            if msg:
                db.session.delete(msg)
                db.session.commit()
            return redirect(url_for("admin.dashboard",page="clientmessage"))
        
        messages = ProjectMessage.query.order_by(ProjectMessage.created_at.desc()).all()
        return render_template("dashboard.html",page=page,messages=messages )
    
    # --- Reviews Section (Read Only) ---
    if page == "reviews":
        reviews = CustomerReview.query.order_by(CustomerReview.created_at.desc()).all()
        return render_template("dashboard.html", page=page, reviews=reviews)

    # --- Auto Messages Section ---
    if page == "automessage":
        if request.method == "POST":
            key = request.form["key"]
            msg = AutoMessage.query.filter_by(key=key).first()
            if msg:
                msg.message = request.form["message"]
            else:
                msg = AutoMessage(key=key, message=request.form["message"])
                db.session.add(msg)
            db.session.commit()
            return redirect(url_for("admin.dashboard", page="automessage"))

        messages = AutoMessage.query.all()
        return render_template("dashboard.html", page=page, messages=messages)

    # Fallback if no page matched
    return render_template("dashboard.html", page=page)

@admin_bp.route('/admin/otp-verify', methods=["GET", "POST"])
def otp_verify():
    if request.method == "POST":
        entered = request.form.get("otp")
        if entered == session.get("otp"):
            trusted = TrustedDevice(ip_address=session["temp_ip"], 
                                    user_agent=session["temp_ua"])
            db.session.add(trusted)
            db.session.commit()
            
            session['admin_authenticated'] = True
            flash("OTP verified. Logged in successfully.")
            return redirect(url_for("admin.dashboard"))
        else:
            flash("Invalid OTP. Try again.")
    return render_template("otp_verify.html")

@admin_bp.route('/admin/logout')
def logout():
    session.pop('admin_authenticated', None)
    flash('You have been logged out.', 'info')
    return redirect(url_for('admin.dashboard'))
