from flask_wtf import FlaskForm
from wtforms.fields.simple import StringField, SubmitField
from wtforms.validators import DataRequired

class CompleteProfile(FlaskForm):
    full_name = StringField("Full Name", validators=[DataRequired()])
    location = StringField("Location", validators=[DataRequired()])
    company_name = StringField("Company Name", validators=[DataRequired()])
    skills = StringField("Skills", validators=[DataRequired()])
    bio = StringField("Bio", validators=[DataRequired()])
    experience_years = StringField("Years of Experience", validators=[DataRequired()])
    submit = SubmitField("Submit")