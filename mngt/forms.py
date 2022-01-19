"""Colection of forms."""
from flask_wtf import FlaskForm
from wtforms import DateTimeLocalField, SelectField, StringField
from wtforms.validators import DataRequired
from wtforms.widgets import TextArea


class NewConferenceForm(FlaskForm):
    """Form for new conference."""

    name = StringField("Name", validators=[DataRequired()])
    description = StringField(
        "Description", validators=[DataRequired()], widget=TextArea()
    )
    begin = DateTimeLocalField(
        "Begin date", validators=[DataRequired()], format="%Y-%m-%dT%H:%M"
    )
    end = DateTimeLocalField(
        "End date", validators=[DataRequired()], format="%Y-%m-%dT%H:%M"
    )


class NewProposalForm(FlaskForm):
    """Form for new proposal."""

    author_id = SelectField("Author", coerce=int, validators=[DataRequired()])

    title = StringField("Title", validators=[DataRequired()])
    type = StringField("Type", validators=[DataRequired()])
    abstract = StringField("Abstract", validators=[DataRequired()], widget=TextArea())


class NewPanelForm(FlaskForm):
    """Form for new panel."""

    title = StringField("title", validators=[DataRequired()])
    start = DateTimeLocalField(
        "Begin date", validators=[DataRequired()], format="%Y-%m-%dT%H:%M"
    )
