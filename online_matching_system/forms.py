from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, DateField, DateTimeField, IntegerField, FloatField, SelectField
from wtforms.validators import DataRequired, Email, Length, EqualTo, ValidationError, NumberRange
from flask import copy_current_request_context
from .user import user

class LoginForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Submit')
    
class CreateBidForm(FlaskForm):
    initiator_id = StringField('Initiator ID', validators=[DataRequired()])
    date_created = DateTimeField('Date Created', validators=[DataRequired()])
    subject_id = StringField('Subject ID', validators=[DataRequired()])
    tutor_qualification = StringField('Tutor Qualification')
    lesson_needed = IntegerField('Lesson Needed', validators=[DataRequired()])
    preferred_time = SelectField('Preferred Time', choices=[('08:00','08:00'),('08:30','08:30'),('09:00','09:00'),('09:30','09:30'),('10:00','10:00'),('10:30','10:30'),('11:00','11:00'),('11:30','11:30'),('12:00','12:00')])
    preferred_day = SelectField('Preferred Day', choices=[('Monday', 'Mon'), ('Tuesday', 'Tues'), ('Wednesday', 'Wed'), ('Thursday', 'Thur'), ('Friday', 'Fri')])
    preferred_session_per_week = IntegerField('Preferred Session Per Week',validators=[NumberRange(min=1, max=6)])
    preferred_rate_choice = SelectField('Preferred Rate Choices', choices=[('per hour', 'ph'), ('per session', 'ps')])
    preferred_rate = FloatField('Preferred Rate',validators=[NumberRange(min=5, max=100)])
    submit = SubmitField('Submit')