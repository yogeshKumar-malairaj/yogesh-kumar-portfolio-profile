from flask import Blueprint

bp = Blueprint("public_routes", __name__)

@bp.route("/")
def home():
    return "Welcome to the public portfolio API"
