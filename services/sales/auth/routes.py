from flask import Blueprint, render_template, request, session, redirect, url_for

from auth.service import authenticate_vendor

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    mail = request.form["mail"]
    password = request.form["password"]

    vendor = authenticate_vendor(mail, password)

    if vendor is None:
        return "Invalid credentials", 401

    session["vendor_id"] = vendor["vendor_id"]

    return redirect(url_for("sales.select_clients"))


@auth_bp.route("/logout")
def logout():

    session.clear()

    return redirect(url_for("auth.login"))
