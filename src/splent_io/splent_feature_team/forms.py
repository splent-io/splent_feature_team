from flask_wtf import FlaskForm
from wtforms import SubmitField


class SplentFeatureTeamForm(FlaskForm):
    submit = SubmitField("Save splent_feature_team")
