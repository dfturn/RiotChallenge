from flask.ext.wtf import Form
from wtforms import StringField, BooleanField
from wtforms.validators import DataRequired

class SearchForm(Form):
    match_id = StringField('Search Value', validators=[DataRequired()], default="Match ID or Summoner Name")