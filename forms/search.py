from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired


class SearchForm(FlaskForm):
    search = StringField('Search Wikipedia...', validators=[DataRequired()])
    submit = SubmitField('Search')
