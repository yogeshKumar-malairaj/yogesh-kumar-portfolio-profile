from flask import Blueprint

bp = Blueprint("admin_routes", __name__, url_prefix="/admin")

@bp.route("/login")
def login():
    return "Admin login page"
