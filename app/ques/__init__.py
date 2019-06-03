from flask import Blueprint
from collections import defaultdict


QUESTIONNAIRE_DEFAULTS = {
    "submit": "Submitttttt",
    "messages": {
        "error": {
            "required": "Field is required",
            "invalid": "Invalid value"
        },
        "success": "Thank you! Your form has been submitted!"
    }
}

SUBMISSION_DATEFMT = '%Y%m%d%H%M%S%f'


ques = Blueprint('ques', __name__, template_folder='templates')

from . import views

