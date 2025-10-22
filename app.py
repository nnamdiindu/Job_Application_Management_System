import json
import os
import re
from typing import Optional, List
from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, abort
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import ForeignKey, Integer, String, DateTime, select, Text, Boolean, Float, func
from sqlalchemy.orm import Mapped, mapped_column, DeclarativeBase, relationship, joinedload
from datetime import datetime, timezone
from dotenv import load_dotenv
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin, login_user, current_user, LoginManager, login_required, logout_user
from flask_bootstrap import Bootstrap5
from forms import CompleteCompanyProfile, CompleteUserProfile
# from openai import OpenAI
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
    verified: Mapped[bool] = mapped_column(Boolean, nullable=True, default=False)
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
    bio: Mapped[str] = mapped_column(String(100), nullable=False)
    about_me: Mapped[str] = mapped_column(String(400), nullable=False)
    experience_years: Mapped[int] = mapped_column(Integer, default=0)
    certification: Mapped[str] = mapped_column(String(100), nullable=True)
    salary_range: Mapped[str] = mapped_column(String(100), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=False, default=lambda: datetime.now(timezone.utc))
    grade: Mapped[str] = mapped_column(String(100), nullable=True)
    area_of_specialization: Mapped[str] = mapped_column(String(100), nullable=True)
    year_of_graduation: Mapped[str] = mapped_column(String(20), nullable=True)
    institution: Mapped[str] = mapped_column(String(200), nullable=True)
    degree: Mapped[str] = mapped_column(String(100), nullable=True)
    duties_in_last_company: Mapped[str] = mapped_column(String(1000), nullable=True)
    position_held: Mapped[str] = mapped_column(String(50), nullable=True)
    year_start: Mapped[str] = mapped_column(String(10), nullable=True)
    year_end: Mapped[str] = mapped_column(String(10), nullable=True)

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
    status: Mapped[str] = mapped_column(String(50), default='Under Review', server_default='Under Review')
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

            user = db.session.execute(select(User).where(User.id == current_user.id)).scalar_one()
            user_role = user.role

            new_profile = UserProfile(
                full_name=request.form.get("full_name"),
                user_id=current_user.id,
                location=request.form.get("location"),
                company_name=request.form.get("company_name"),
                skills=request.form.get("skills"),
                bio=request.form.get("bio"),
                about_me=request.form.get("about_me"),
                experience_years=request.form.get("experience_years"),
                role=user_role,
                position_held=request.form.get("position_held"),
                duties_in_last_company=request.form.get("duties_in_last_company"),
                year_start=request.form.get("year_start"),
                year_end=request.form.get("year_end"),
                degree=request.form.get("degree"),
                institution=request.form.get("institution"),
                grade=request.form.get("grade"),
                year_of_graduation=request.form.get("year_of_graduation"),
                area_of_specialization=request.form.get("area_of_specialization"),
                salary_range=request.form.get("salary_range")
            )

            db.session.add(new_profile)
            db.session.commit()

            user.verified=True
            db.session.commit()

    except Exception as e:
        print(f"Error submitting form: {e}")
        db.session.rollback()
        return jsonify({'status': 'error', 'message': f'Failed to submit form: {str(e)}'}), 500

def time_ago(timestamp):
    try:
        if timestamp.tzinfo is None:
            timestamp = timestamp.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        diff = now - timestamp

        seconds = diff.total_seconds()
        minutes = seconds / 60
        hours = minutes / 60
        days = hours / 24

        if seconds < 60:
            return f"{int(seconds)} seconds ago"
        elif minutes < 60:
            return f"{int(minutes)} minutes ago"
        elif hours < 24:
            return f"{int(hours)} hours ago"
        else:
            return f"{int(days)} days ago"
    except Exception:
        return "Invalid date"

# Register the filter
app.jinja_env.filters['timeago'] = time_ago


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
                    if user.verified == True:
                        login_user(user)
                        return redirect(url_for("company_dashboard"))
                    else:
                        flash("Profile not verfied, please complete profile setup.", "warning")
                        return redirect(url_for("complete_profile"))
                else:
                    flash("Incorrect password, please try again", "error")
                    return redirect(url_for("login"))
            else:
                if user.verified == True:
                    login_user(user)
                    return redirect(url_for("job_seeker_dashboard"))
                else:
                    flash("Profile not verfied, please complete profile setup.", "warning")
                    return redirect(url_for("complete_profile"))

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
    if current_user.role != "company":
        abort(403)

    # Get jobs with application counts in one query
    jobs_query = (
        select(
            Job,
            func.count(Application.id).label('app_count')
        )
        .outerjoin(Application, Job.id == Application.job_id)
        .where(Job.employer_id == current_user.id)
        .group_by(Job.id)
        .order_by(Job.created_at.desc())
    )

    jobs_with_counts = db.session.execute(jobs_query).all()

    # Get recent applications
    recent_applications = db.session.execute(
        select(Application)
        .join(Job)
        .options(
            joinedload(Application.user).joinedload(User.profile),
            joinedload(Application.job)
        )
        .where(Job.employer_id == current_user.id)
        .order_by(Application.applied_at.desc())
        .limit(10)  # Only get recent 10
    ).scalars().all()

    # Get all applications for stats
    all_applications = db.session.execute(
        select(Application)
        .join(Job)
        .where(Job.employer_id == current_user.id)
    ).scalars().all()

    # Get company profile
    company_profile = db.session.execute(
        select(UserProfile).where(UserProfile.user_id == current_user.id)
    ).scalar()

    company_name = company_profile.company_name if company_profile else "Company"

    # Statistics
    total_applications = len(all_applications)
    under_review = sum(1 for app in all_applications if app.status == 'Under Review')
    accepted = sum(1 for app in all_applications if app.status == 'Accepted')
    rejected = sum(1 for app in all_applications if app.status == 'Rejected')

    return render_template(
        "company-dashboard.html",
        current_user=current_user,
        jobs_with_counts=jobs_with_counts,
        company_name=company_name,
        recent_applications=recent_applications,
        total_applications=total_applications,
        under_review=under_review,
        accepted=accepted,
        rejected=rejected
    )


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


# @app.route("/job-seeker-dashboard", methods=["GET", "POST"])
# @login_required
# def job_seeker_dashboard():
#
#     jobs = db.session.execute(
#         db.select(Job).order_by(Job.created_at.desc())).scalars().all()
#
#     applications = db.session.execute(
#         db.select(Application).where(Application.user_id == current_user.id).order_by(Application.applied_at)).scalars().all()
#
#     result = db.session.execute(db.select(UserProfile).where(UserProfile.id == current_user.id)).scalar()
#     full_name = result.full_name
#
#     user = db.session.execute(
#         db.select(UserProfile).where(UserProfile.user_id == current_user.id)
#     ).scalar_one_or_none()
#
#     # Get recommendations if they exist
#     recommendations_query = db.session.execute(
#         db.select(JobRecommendation)
#         .where(JobRecommendation.user_id == user.id)
#         .order_by(JobRecommendation.match_score.desc())
#     ).scalars().all()
#
#     recommendations_data = []
#     for rec in recommendations_query:
#         match_reasons = json.loads(rec.match_reasons) if rec.match_reasons else {}
#         missing_skills = json.loads(rec.missing_skills) if rec.missing_skills else {}
#
#         recommendations_data.append({
#             'job': rec.job,
#             'match_score': rec.match_score,
#             'skill_match_score': rec.skill_match_score,
#             'location_match_score': rec.location_match_score,
#             'experience_match_score': rec.experience_match_score,
#             'match_reasons': match_reasons,
#             'missing_skills': missing_skills,
#             'recommended_at': rec.recommended_at
#         })
#
#     return render_template("job-seeker-dashboard.html",
#                            jobs=jobs,
#                            current_user=current_user,
#                            applications=applications,
#                            full_name=full_name,recommendations=recommendations_data,
#                            has_recommendations=len(recommendations_data) > 0,
#                            user_skills=user.skills,
#                            user_profile=user)


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

@app.route("/job-seeker-dashboard", methods=["GET", "POST"])
@login_required
def job_seeker_dashboard():
    # Get the current user
    user = db.session.execute(
        db.select(UserProfile).where(UserProfile.user_id == current_user.id)
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
                        Analyze and match jobs to this user.

                        User Profile:
                        - Skills: {user.skills}
                        - Location: {getattr(user.location, 'location', 'Not specified')}

                        Available Jobs:
                        {json.dumps(jobs_list, indent=2)}

                        Calculate match scores (0.0 to 1.0) for:
                        - skill_match_score: How well user's skills match required skills
                        - location_match_score: Location compatibility
                        - experience_match_score: Experience level match
                        - Overall match_score (weighted average)

                        CRITICAL: Return ONLY valid JSON, no other text. Use this exact structure:

                        {{
                            "recommendations": [
                                {{
                                    "job_id": 1,
                                    "match_score": 0.85,
                                    "skill_match_score": 0.9,
                                    "location_match_score": 1.0,
                                    "experience_match_score": 0.85,
                                    "match_reasons": {{"skills": "Strong Python and JavaScript match", "location": "Same city"}},
                                    "missing_skills": {{"required": ["Docker", "AWS"], "recommendation": "Consider learning cloud technologies"}}
                                }}
                            ]
                        }}

                        Recommend the top 5 best matching jobs, ordered by match_score (highest first).
                        Return ONLY the JSON, nothing else.
                        """

            response = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=1024,
                messages=[{"role": "user", "content": prompt}]
            )

            # Extract response text
            response_text = response.content[0].text.strip()

            print("=" * 50)
            print("Claude Response:")
            print(response_text)
            print("=" * 50)

            # Try to extract JSON from the response
            # Method 1: Check if it's already pure JSON
            try:
                recommendations_data = json.loads(response_text)
            except json.JSONDecodeError:
                # Method 2: Extract JSON using regex (find content between { and })
                json_match = re.search(r'\{[\s\S]*\}', response_text)
                if json_match:
                    json_str = json_match.group(0)
                    recommendations_data = json.loads(json_str)
                else:
                    # Method 3: Try to find JSON in code blocks
                    code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
                    if code_block_match:
                        json_str = code_block_match.group(1)
                        recommendations_data = json.loads(json_str)
                    else:
                        raise ValueError("Could not extract valid JSON from response")

            # Validate response structure
            if 'recommendations' not in recommendations_data:
                raise ValueError("Response missing 'recommendations' key")

            # Delete old recommendations
            db.session.execute(
                db.delete(JobRecommendation).where(JobRecommendation.user_id == user.id)
            )

            # Save new recommendations
            saved_count = 0
            for rec in recommendations_data.get('recommendations', []):
                # Validate required fields
                if 'job_id' not in rec or 'match_score' not in rec:
                    print(f"Skipping invalid recommendation: {rec}")
                    continue

                job_recommendation = JobRecommendation(
                    user_id=user.id,
                    job_id=rec['job_id'],
                    match_score=rec['match_score'],
                    skill_match_score=rec.get('skill_match_score'),
                    location_match_score=rec.get('location_match_score'),
                    salary_match_score=rec.get('salary_match_score'),
                    experience_match_score=rec.get('experience_match_score'),
                    match_reasons=json.dumps(rec.get('match_reasons', {})),
                    missing_skills=json.dumps(rec.get('missing_skills', {})),
                )
                db.session.add(job_recommendation)
                saved_count += 1

            db.session.commit()

            if saved_count > 0:
                flash(f"Generated {saved_count} job recommendations successfully!", "success")
            else:
                flash("No valid recommendations were generated. Please try again.", "warning")

        except json.JSONDecodeError as e:
            db.session.rollback()
            print(f"JSON Decode Error: {e}")
            print(f"Response text was: {response_text[:500]}")  # Print first 500 chars
            flash(f"Error parsing AI response. Please try again.", "error")
        except ValueError as e:
            db.session.rollback()
            print(f"Value Error: {e}")
            flash(f"Invalid AI response format. Please try again.", "error")
        except Exception as e:
            db.session.rollback()
            print(f"Unexpected Error: {e}")
            flash(f"Error generating recommendations: {str(e)}", "error")

    # GET request or after POST - Display recommendations
    jobs = db.session.execute(
        db.select(Job).order_by(Job.created_at.desc())).scalars().all()

    applications = db.session.execute(
        db.select(Application).where(Application.user_id == current_user.id).order_by(
            Application.applied_at)).scalars().all()

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
            'salary_match_score': rec.salary_match_score,
            'experience_match_score': rec.experience_match_score,
            'match_reasons': match_reasons,
            'missing_skills': missing_skills,
            'recommended_at': rec.recommended_at
        })

    # all_jobs = db.session.execute(db.select(Job)).scalars().all()

    return render_template(
        "job-seeker-dashboard.html",
        full_name=user.full_name,
        jobs=jobs,
        current_user=current_user,
        applications=applications,
        recommendations=recommendations_data,
        has_recommendations=len(recommendations_data) > 0,
        user_skills=user.skills,
        user_profile=user
    )


if __name__ == "__main__":
    app.run(debug=True)