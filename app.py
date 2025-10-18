import json
import os
from typing import Optional, List
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, DateTime, select, Text, Boolean, Float
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, current_user, LoginManager, login_required, logout_user
from flask_bootstrap import Bootstrap5
from forms import CompleteCompanyProfile, CompleteUserProfile
from openai import OpenAI
import anthropic
from flask_migrate import Migrate

app = Flask(__name__)

load_dotenv()

app.secret_key = os.environ.get("SECRET_KEY")
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DB_URI")
bootstrap = Bootstrap5(app)

login_manager = LoginManager()
login_manager.init_app(app)


class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)
migrate = Migrate(app, db)

class User(UserMixin, db.Model):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(320), nullable=False)
    phone: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    profile: Mapped[Optional["UserProfile"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        uselist=False
    )
    applications: Mapped[List["Application"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["JobRecommendation"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan"
    )
    posted_jobs: Mapped[List["Job"]] = relationship(
        back_populates="employer",
        cascade="all, delete-orphan"
    )

class UserProfile(UserMixin, db.Model):
    __tablename__ = "userprofiles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'), unique=True)
    full_name: Mapped[str] = mapped_column(String(100))
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    company_name: Mapped[str] = mapped_column(String(100))
    skills: Mapped[str] = mapped_column(String(320), nullable=True)
    role: Mapped[str] = mapped_column(String(20), default="user", nullable=False)
    bio: Mapped[str] = mapped_column(String(400), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    # resume_url: Mapped[bytes] = mapped_column
    certification: Mapped[str] = mapped_column(String(100), nullable=False)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))

    user: Mapped["User"] = relationship(back_populates="profile")


class Job(db.Model):
    __tablename__ = "jobs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    employer_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    company: Mapped[str] = mapped_column(String(200), nullable=False)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=False)
    skills_required: Mapped[str] = mapped_column(String(320), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    # employer_id: Mapped[int] = mapped_column(ForeignKey("userprofiles.id"), nullable=False)
    location: Mapped[str] = mapped_column(String(320), nullable=False)
    description: Mapped[str] = mapped_column(String(320), nullable=False)
    title: Mapped[str] = mapped_column(String(50), nullable=False)
    job_type: Mapped[str] = mapped_column(String(20), nullable=False)
    requirements: Mapped[str] = mapped_column(String(200), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    employer: Mapped["User"] = relationship(back_populates="posted_jobs")

    applications: Mapped[List["Application"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan"
    )
    recommendations: Mapped[List["JobRecommendation"]] = relationship(
        back_populates="job",
        cascade="all, delete-orphan"
    )


class Application(db.Model):
    __tablename__ = 'applications'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    job_id: Mapped[int] = mapped_column(ForeignKey('jobs.id', ondelete='CASCADE'))
    match_score: Mapped[float] = mapped_column(Float)

    cover_letter: Mapped[Optional[str]] = mapped_column(Text)
    resume_url: Mapped[Optional[str]] = mapped_column(String(500))

    # Tracking
    applied_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    reviewed_at: Mapped[Optional[datetime]]

    # Relationships
    user: Mapped["User"] = relationship(back_populates="applications")
    job: Mapped["Job"] = relationship(back_populates="applications")


class JobRecommendation(db.Model):
    __tablename__ = 'job_recommendations'

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))
    job_id: Mapped[int] = mapped_column(ForeignKey('jobs.id', ondelete='CASCADE'))

    # AI recommendation metrics
    match_score: Mapped[float] = mapped_column(Float)  # 0.0 to 1.0
    skill_match_score: Mapped[Optional[float]] = mapped_column(Float)
    location_match_score: Mapped[Optional[float]] = mapped_column(Float)
    salary_match_score: Mapped[Optional[float]] = mapped_column(Float)
    experience_match_score: Mapped[Optional[float]] = mapped_column(Float)

    # Recommendation explanation
    match_reasons: Mapped[Optional[str]] = mapped_column(Text)  # JSON format for detailed reasons
    missing_skills: Mapped[Optional[str]] = mapped_column(Text)  # JSON format for skills gap analysis

    # Metadata
    recommended_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)
    viewed_at: Mapped[Optional[datetime]]

    # Relationships
    user: Mapped["User"] = relationship(back_populates="recommendations")
    job: Mapped["Job"] = relationship(back_populates="recommendations")


@login_manager.user_loader
def load_user(user_id):
    return db.get_or_404(User, user_id)

with app.app_context():
    db.create_all()


def complete_profile_registration(form):
    try:
        if form.validate_on_submit():

            result = db.session.execute(select(User).where(User.id == current_user.id)).scalar_one()
            user_role = result.role

            new_profile = UserProfile(
                full_name=request.form.get("full_name"),
                user_id=current_user.id,
                location=request.form.get("location"),
                company_name=request.form.get("company_name"),
                skills=request.form.get("skills"),
                bio=request.form.get("bio"),
                experience_years=request.form.get("experience_years"),
                role=user_role
            )

            db.session.add(new_profile)
            db.session.commit()

    except Exception as e:
        print(f"Error submitting form: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to submit form: {str(e)}'}), 500

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

            return redirect(url_for("registration_success"))

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
                role="job_seeker"
            )

            db.session.add(new_user)
            db.session.commit()

            login_user(new_user)

            return redirect(url_for("registration_success"))

        else:
            flash("Password does not match, please try again", "error")
            return redirect(url_for("job_seeker_register"))


    return render_template("job-seeker-setup.html", current_user=current_user)

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        email = request.form.get("email")

        user = db.session.execute(db.select(User).where(User.email == email)).scalar()

        if user:
            if user.role == "company":
                if check_password_hash(user.password, request.form.get("password")):
                    login_user(user)
                    return redirect(url_for("company_dashboard"))
                else:
                    flash("Incorrect password, please try again", "error")
                    return redirect(url_for("login"))
            else:
                login_user(user)
                return redirect(url_for("job_seeker_dashboard"))

    return render_template("login.html")


@app.route("/complete-profile", methods=["GET", "POST"])
@login_required
def complete_profile():
    # Check if user is a company
    if current_user.role == "company":
        form = CompleteCompanyProfile()
        if form.validate_on_submit():
            complete_profile_registration(form)
            return redirect(url_for("company_dashboard"))
    else:
        form = CompleteUserProfile()
        if form.validate_on_submit():
            complete_profile_registration(form)
            return redirect(url_for("job_seeker_dashboard"))

    return render_template("complete-profile.html", form=form, current_user=current_user)


@app.route("/registration-success")
def registration_success():
    return render_template("registration-success.html")


@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for("login"))


@app.route("/company-dashboard")
@login_required
def company_dashboard():
    jobs = db.session.execute(
        db.select(Job)
        .where(Job.employer_id == current_user.id)
        .order_by(Job.created_at.desc())
    ).scalars().all()
    
    result = db.session.execute(db.select(UserProfile).where(UserProfile.id == current_user.id)).scalar()
    company_name = result.company_name
    return render_template("company-dashboard.html", current_user=current_user, jobs=jobs, company_name=company_name)

@app.route("/api/post-job", methods=["POST"])
@login_required
def post_job():
    try:
        data = request.get_json()

        result = db.session.execute(select(UserProfile).where(UserProfile.id == current_user.id)).scalar_one()
        company_name = result.company_name

        if not data:
            return jsonify({"status": "error", "message": "No data provided"}), 400


        new_job = Job(
            employer_id=current_user.id,
            company=company_name,
            title=data.get("job-title"),
            location=data.get("location"),
            job_type=data.get("job-type"),
            salary_range=data.get("salary-range"),
            description=data.get("description"),
            skills_required=data.get("skills"),
            requirements="vacant for now"
        )

        db.session.add(new_job)
        db.session.commit()

        return jsonify({
            "status": "success",
            "message": "Job posted successfully",
        })

    except Exception as e:
        print(f"Error posting job: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to post job: {str(e)}'}), 500


@app.route("/job-seeker-dashboard")
@login_required
def job_seeker_dashboard():

    jobs = db.session.execute(
        db.select(Job).order_by(Job.created_at.desc())).scalars().all()

    applications = db.session.execute(
        db.select(Application).where(Application.user_id == current_user.id).order_by(Application.applied_at)).scalars().all()

    result = db.session.execute(db.select(UserProfile).where(UserProfile.id == current_user.id)).scalar()
    full_name = result.full_name

    user = db.session.execute(
        db.select(UserProfile).where(UserProfile.id == current_user.id)
    ).scalar_one_or_none()

    # Get recommendations if they exist
    recommendations_query = db.session.execute(
        db.select(JobRecommendation)
        .where(JobRecommendation.user_id == user.id)
        .order_by(JobRecommendation.match_score.desc())
    ).scalars().all()

    recommendations_data = []
    for rec in recommendations_query:
        match_reasons = json.loads(rec.match_reasons) if rec.match_reasons else {}
        missing_skills = json.loads(rec.missing_skills) if rec.missing_skills else {}

        recommendations_data.append({
            'job': rec.job,
            'match_score': rec.match_score,
            'skill_match_score': rec.skill_match_score,
            'location_match_score': rec.location_match_score,
            'experience_match_score': rec.experience_match_score,
            'match_reasons': match_reasons,
            'missing_skills': missing_skills,
            'recommended_at': rec.recommended_at
        })

    return render_template("job-seeker-dashboard.html",
                           jobs=jobs,
                           current_user=current_user,
                           applications=applications,
                           full_name=full_name,recommendations=recommendations_data,
                           has_recommendations=len(recommendations_data) > 0,
                           user_skills=user.skills)


@app.route("/apply-job", methods=["POST"])
@login_required
def apply_job():
    try:
        job_id = request.form.get("job-id")

        # Validate job exists
        job = db.get_or_404(Job, job_id)
        if not job:
            flash("Job not found", "error")
            return redirect(url_for("job_seeker_dashboard"))

        # Check if user already applied
        existing_application = Application.query.filter_by(
            user_id=current_user.id,
            job_id=job_id
        ).first()

        if existing_application:
            flash("You have already applied to this job", "warning")
            return redirect(url_for("job_seeker_dashboard"))

        # Create new application
        new_application = Application(
            match_score=90.0,
            user_id=current_user.id,
            job_id=job_id
        )

        db.session.add(new_application)
        db.session.commit()

        flash("Application submitted successfully", "success")
        return redirect(url_for("job_seeker_dashboard"))

    except Exception as e:
        print(f"Error applying for job: {e}")
        db.session.rollback()
        flash("Failed to submit application. Please try again.", "error")
        return redirect(url_for("jobs"))

@app.route("/job-recommendation", methods=["GET", "POST"])
@login_required
def job_recommendation():
    # Get the current user
    user = db.session.execute(
        db.select(UserProfile).where(UserProfile.id == current_user.id)
    ).scalar_one_or_none()

    if not user:
        flash("User not found", "error")
        return redirect(url_for("job_seeker-dashboard"))

    if request.method == "POST":
        # Generate new recommendations
        jobs = db.session.execute(db.select(Job)).scalars().all()

        if not jobs:
            flash("No jobs available for recommendations", "warning")
            return render_template("job-seeker-dashboard.html",
                                   full_name=user.full_name,
                                   jobs=jobs,
                                   recommendations=[],
                                   has_recommendations=False)

        try:
            # client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
            client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
            # Create detailed job information for the prompt
            jobs_list = [
                {
                    'id': job.id,
                    'title': job.title,
                    'company': job.company,
                    'required_skills': job.skills_required,
                    'location': job.location,
                    'salary_range': job.salary_range,
                    'job_type': job.job_type,
                    'description': job.description
                }
                for job in jobs
            ]

            prompt = f"""
            You are a job recommendation assistant. Analyze and match jobs to the user based on multiple criteria.

            User Profile:
            - Skills: {user.skills}
            - Location: {getattr(user, 'location', 'Not specified')}
            - Experience Level: {getattr(user, 'experience_level', 'Not specified')}

            Available Jobs:
            {json.dumps(jobs_list, indent=2)}

            For each job, calculate match scores (0.0 to 1.0) for:
            1. skill_match_score - How well user's skills match required skills
            2. location_match_score - Location compatibility
            3. experience_match_score - Experience level match

            Then calculate an overall match_score (weighted average).

            Return ONLY valid JSON with this exact structure:
            {{
                "recommendations": [
                    {{
                        "job_id": 1,
                        "match_score": 0.85,
                        "skill_match_score": 0.9,
                        "location_match_score": 1.0,
                        "experience_match_score": 0.85,
                        "match_reasons": {{"skills": "Strong match in Python and JavaScript", "location": "Same city"}},
                        "missing_skills": {{"required": ["Docker", "AWS"], "recommendation": "Consider learning cloud technologies"}}
                    }}
                ]
            }}

            Recommend the top 5 best matching jobs, ordered by match_score (highest first).
            """

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=4000,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract JSON from response
            response_text = response.content[0].text
            recommendations_data = json.loads(response_text)

            # Delete old recommendations for this user
            db.session.execute(
                db.delete(JobRecommendation).where(JobRecommendation.user_id == user.id)
            )

            # Save new recommendations to database
            for rec in recommendations_data.get('recommendations', []):
                job_recommendation = JobRecommendation(
                    user_id=user.id,
                    job_id=rec['job_id'],
                    match_score=rec['match_score'],
                    skill_match_score=rec.get('skill_match_score'),
                    location_match_score=rec.get('location_match_score'),
                    salary_match_score=rec.get('salary_match_score'),
                    experience_match_score=rec.get('experience_match_score'),
                    match_reasons=json.dumps(rec.get('match_reasons')),
                    missing_skills=json.dumps(rec.get('missing_skills')),
                    recommended_at=lambda: datetime.now(timezone.utc)
                )
                db.session.add(job_recommendation)

            db.session.commit()
            flash("Job recommendations generated successfully!", "success")

        except json.JSONDecodeError as e:
            db.session.rollback()
            flash(f"Error parsing AI response: {e}", "error")
        except Exception as e:
            db.session.rollback()
            flash(f"Error generating recommendations: {e}", "error")

    # GET request or after POST - Display recommendations
    recommendations_query = db.session.execute(
        db.select(JobRecommendation)
        .where(JobRecommendation.user_id == user.id)
        .order_by(JobRecommendation.match_score.desc())
    ).scalars().all()

    # Prepare data for template with job details
    recommendations_data = []
    for rec in recommendations_query:
        # Parse JSON fields
        match_reasons = json.loads(rec.match_reasons) if rec.match_reasons else {}
        missing_skills = json.loads(rec.missing_skills) if rec.missing_skills else {}

        recommendations_data.append({
            'job': rec.job,
            'match_score': rec.match_score,
            'skill_match_score': rec.skill_match_score,
            'location_match_score': rec.location_match_score,
            'salary_match_score': rec.salary_match_score,
            'experience_match_score': rec.experience_match_score,
            'match_reasons': match_reasons,
            'missing_skills': missing_skills,
            'recommended_at': rec.recommended_at,
        })

    # Get all jobs for browse tab
    all_jobs = db.session.execute(db.select(Job)).scalars().all()

    return render_template(
        "job-seeker-dashboard.html",
        full_name=user.full_name,
        jobs=all_jobs,
        recommendations=recommendations_data,
        has_recommendations=len(recommendations_data) > 0,
        user_skills=user.skills
    )


if __name__ == "__main__":
    app.run(debug=True)