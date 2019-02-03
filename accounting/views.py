# You will probably need more methods from flask but this one is a good start.
from flask import render_template, jsonify, request
from sqlalchemy.orm.exc import NoResultFound
from datetime import datetime

# Import things from Flask that we need.
from accounting import app, db

# Import our models
from models import Policy
from utils import PolicyAccounting


class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        rv = dict(self.payload or ())
        rv["message"] = self.message
        return rv


@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response


# Routing for the server.
@app.route("/")
def index():
    return render_template("index.html")


@app.route("/policy/api/invoices", methods=["GET"])
def get_tasks():
    policy_number = request.args.get("policy_number", None)
    try:
        date_cursor = datetime.strptime(
            request.args.get("date_cursor", None), "%Y-%m-%d"
        )
    except ValueError:
        raise InvalidUsage("Bad date format", status_code=400)
    try:
        policy = (
            db.session.query(Policy).filter(Policy.policy_number == policy_number).one()
        )
    except NoResultFound:
        raise InvalidUsage("Policy Not Found", status_code=404)
    invoices = policy.invoices
    pa = PolicyAccounting(policy.id)
    balance = pa.return_account_balance(date_cursor=date_cursor)
    data = {"balance": balance, "invoices": [i.serialize() for i in invoices]}
    return jsonify(data)
