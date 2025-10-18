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
    full_name = StringField("Full Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    company_name = StringField("Last Company worked", validators=[DataRequired()])
    skills = StringField("Skills e.g (React, AWS, Python, Docker, Java)", validators=[DataRequired()])
    bio = TextAreaField("About Me", validators=[DataRequired()])
    experience_years = StringField("Years of Experience", validators=[DataRequired()])
    degree = StringField("Degree Certificate e.g (B.Sc. Computer Science)", validators=[DataRequired()])
    salary_range = StringField("Salary Exceptation e.g ($12k - $15k)", validators=[DataRequired()])
    submit = SubmitField("Submit")