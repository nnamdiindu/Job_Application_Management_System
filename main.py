import os
from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, DateTime, select, nullsfirst, nulls_last
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase
from datetime import datetime, timezone
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")


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

class UserProfile(db.Model):
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



with app.app_context():
    db.create_all()


@app.route("/")
def index():
    return render_template("index.html")

@app.route("/company-register", methods=["GET", "POST"])
def company_register():
    company = db.session.execute(select(User.email == request.form.get("company-email"))).scalar()

    if request.method == "POST":
        if company:
            flash("Email has already been registered, please login", "success")
            return redirect(url_for("login"))

        new_company = UserProfile(
            full_name=request.form.get("full-name"),
            location=request.form.get("location"),
            company_name=request.form.get("company-name"),
            bio=request.form.get("bio"),
            role="company",
        )
        db.session.add(new_company)
        db.session.commit()

        return redirect(url_for("company_dashboard"))

    return render_template("company-setup.html")

@app.route("/user-register", methods=["GET", "POST"])
def job_seeker_register():
    return render_template("job-seeker-setup.html")

@app.route("/login")
def login():
    return None

@app.route("/company-dashboard")
def company_dashboard():
    return render_template("company-dashboard.html")

@app.route("/register-dashboard")
def job_seeker_dashboard():
    return render_template("job-seeker-dashboard.html")

if __name__ == "__main__":
    app.run(debug=True)