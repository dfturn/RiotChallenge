from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(Form):
    match_id = StringField(label='', validators=[DataRequired()], default="Match ID or Summoner Name")