from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

class SearchBar(FlaskForm):
    user_search = StringField('Provide street, city, and state, or just a zipcode', validators=[DataRequired()])
    user_submit = SubmitField('Search', validators=[DataRequired()])

class HomePage(FlaskForm):
    get_started = SubmitField('Get Started', validators=[DataRequired()])
