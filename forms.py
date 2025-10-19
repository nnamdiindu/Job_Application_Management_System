from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired

class CompleteCompanyProfile(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    company_name = StringField("Company Name", validators=[DataRequired()])
    bio = TextAreaField("Company Profile", validators=[DataRequired()])
    submit = SubmitField("Submit")

class CompleteUserProfile(FlaskForm):
    full_name = StringField("Full Name", render_kw={"placeholder": "John Doe"}, validators=[DataRequired()])
    location = StringField("Location", render_kw={"placeholder": "Lagos, NG"}, validators=[DataRequired()])
    company_name = StringField("Last Company worked", render_kw={"placeholder": "Microsoft"},validators=[DataRequired()])
    duties_in_last_company = TextAreaField("Roles and Responsibilities in place last worked")
    skills = StringField("Skills", render_kw={"placeholder": "React, AWS, Python, Docker, Java"}, validators=[DataRequired()])
    bio = TextAreaField("About Me", validators=[DataRequired()])
    experience_years = StringField("Years of Experience")
    degree = StringField("Degree Certificate", render_kw={"placeholder": "B.Sc. Computer Science"},validators=[DataRequired()])
    institution = StringField("Institution Attended: ", render_kw={"placeholder": "University of Nigeria, Nsukka"}, validators=[DataRequired()])
    year_of_graduation = StringField("Year of Graduation", validators=[DataRequired()])
    area_of_specialization = StringField("Area of Specialization", render_kw={"placeholder": "Software Engineering and Web Technologies"},validators=[DataRequired()])
    grade = StringField("Degree Grade", render_kw={"placeholder": "First Class"},validators=[DataRequired()])
    salary_range = StringField("Salary Exceptation", render_kw={"placeholder": "₦200k - ₦250k"},validators=[DataRequired()])
    submit = SubmitField("Submit")