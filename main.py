import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, DateTime, select
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, login_manager, current_user, LoginManager, login_required

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")

login_manager = LoginManager()
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

class User(db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class UserProfile(UserMixin, db.Model):
    __tablename__ = "userprofiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    full_name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    company_name: Mapped[str] = mapped_column(String(100))
    skills: Mapped[str] = mapped_column(String(320), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    bio: Mapped[str] = mapped_column(String(400), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    # resume_url: Mapped[bytes] = mapped_column
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

class Job(db.Model):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=False)
    skills_required: Mapped[str] = mapped_column(String(320), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    employer_id: Mapped[int] = mapped_column(ForeignKey("userprofiles.id"), nullable=False)
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    description: Mapped[str] = mapped_column(String(320), nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)
    requirements: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/company-register", methods=["GET", "POST"])
def company_register():

    if request.method == "POST":
        company = db.session.execute(db.select(User).where(User.email == request.form.get("company-email"))).scalar()

        if company:
            flash("Email has already been registered, please login", "error")
            return redirect(url_for("login"))

        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password == confirm_password:
            halted_and_salted_password = generate_password_hash(
                password=password,
                salt_length=8,
                method="pbkdf2:sha256"
            )

            new_user = User(
                password=halted_and_salted_password,
                phone=request.form.get("phone"),
                email=request.form.get("company-email"),
                role="company"
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("company_dashboard"))

        else:
            flash("Password does not match, please try again", "error")
            return redirect(url_for("company_register"))

    return render_template("company-setup.html")


@app.route("/user-register", methods=["GET", "POST"])
def job_seeker_register():

    if request.method == "POST":
        job_seeker = db.session.execute(db.select(User).where(User.email == request.form.get("email"))).scalar()

        if job_seeker:
            flash("Email has already been registered, please login", "error")
            return redirect(url_for("login"))

        password = request.form.get("password")
        confirm_password = request.form.get("confirm-password")

        if password == confirm_password:
            halted_and_salted_password = generate_password_hash(
                password=password,
                salt_length=8,
                method="pbkdf2:sha256"
            )

            new_user = User(
                password=halted_and_salted_password,
                phone=request.form.get("phone"),
                email=request.form.get("email"),
                # full_name=request.form.get("full-name"),
                # location = request.form.get("location"),
                # skills = request.form.get("skills"),
                # years_experience = request.form.get("years-experience"),
                # bio = request.form.get("bio"),
                role="job_seeker"
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("job_seeker_dashboard"))

        else:
            flash("Password does not match, please try again", "error")
            return redirect(url_for("job_seeker_register"))


    return render_template("job-seeker-setup.html", current_user=current_user)

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/company-dashboard")
def company_dashboard():
    return render_template("company-dashboard.html", current_user=current_user)

@app.route("/register-dashboard")
def job_seeker_dashboard():
    return render_template("job-seeker-dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)