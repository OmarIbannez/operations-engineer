#!/user/bin/env python2.7

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from sqlalchemy.orm.exc import NoResultFound

from accounting import db
from models import Contact, Invoice, Payment, Policy

"""
#######################################################
This is the base code for the engineer project.
#######################################################
"""

BILLING_SCHEDULES = {
    "Annual": None,
    "Semi-Annual": 3,
    "Quarterly": 4,
    "Monthly": 12,
    "Two-Pay": 2,
}


class PolicyAccounting(object):
    """"
    Accounting helper for policies
    """

    def __init__(self, policy_id):
        self.policy = db.session.query(Policy).filter_by(id=policy_id).one()

        if not self.policy.invoices:
            self.make_invoices()

    def return_account_balance(self, date_cursor=None):
        """
        Returns the balance of the policy in a given point in time
        :param date_cursor:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = (
            db.session.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .filter(Invoice.bill_date <= date_cursor)
            .order_by(Invoice.bill_date)
            .all()
        )
        due_now = 0
        for invoice in invoices:
            due_now += invoice.amount_due

        payments = (
            db.session.query(Payment)
            .filter_by(policy_id=self.policy.id)
            .filter(Payment.transaction_date <= date_cursor)
            .all()
        )
        for payment in payments:
            due_now -= payment.amount_paid

        return due_now

    def make_payment(self, contact_id=None, date_cursor=None, amount=0):
        """
        Creates a payment in a given point in time
        :param contact_id:
        :param date_cursor:
        :param amount:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()
        due_to_non_pay = self.evaluate_cancellation_pending_due_to_non_pay(date_cursor)
        if not contact_id:
            try:
                contact_id = self.policy.named_insured
            except:
                pass

        try:
            contact = Contact.query.filter_by(id=contact_id).one()
        except NoResultFound:
            raise NoResultFound("We couldn't find any contact with this id")

        if due_to_non_pay and not contact.role == "Agent":
            raise UserWarning(
                "Policy has passed the due date without being "
                "paid in full, only an agent can't make a payment"
            )

        payment = Payment(self.policy.id, contact_id, amount, date_cursor)
        db.session.add(payment)
        db.session.commit()

        return payment

    def evaluate_cancellation_pending_due_to_non_pay(self, date_cursor=None):
        """
        If this function returns true, an invoice
        on a policy has passed the due date without
        being paid in full. However, it has not necessarily
        made it to the cancel_date yet.
        :param date_cursor:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = (
            db.session.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .filter(Invoice.due_date <= date_cursor)
            .filter(Invoice.cancel_date >= date_cursor)
            .order_by(Invoice.bill_date)
            .all()
        )

        for invoice in invoices:
            if not self.return_account_balance(invoice.due_date):
                continue
            else:
                return True

    def evaluate_cancel(self, date_cursor=None):
        """
        Check if there is any balance after any of the cancel dates
        of the invoices in this policy
        :param date_cursor:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = (
            db.session.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .filter(Invoice.cancel_date <= date_cursor)
            .order_by(Invoice.bill_date)
            .all()
        )

        for invoice in invoices:
            if not self.return_account_balance(invoice.cancel_date):
                continue
            else:
                print "THIS POLICY SHOULD HAVE CANCELED"
                break
        else:
            print "THIS POLICY SHOULD NOT CANCEL"

    def make_invoices(self):
        """
        Create invoices for the policy according with its billing schedule
        """
        for invoice in self.policy.invoices:
            db.session.delete(invoice)

        invoices = []
        first_invoice = Invoice(
            self.policy.id,
            self.policy.effective_date,  # bill_date
            self.policy.effective_date + relativedelta(months=1),  # due
            self.policy.effective_date + relativedelta(months=1, days=14),  # cancel
            self.policy.annual_premium,
        )
        invoices.append(first_invoice)

        if self.policy.billing_schedule == "Annual":
            pass
        elif self.policy.billing_schedule == "Two-Pay":
            first_invoice.amount_due = first_invoice.amount_due / BILLING_SCHEDULES.get(
                self.policy.billing_schedule
            )
            for i in range(1, BILLING_SCHEDULES.get(self.policy.billing_schedule)):
                months_after_eff_date = i * 6
                bill_date = self.policy.effective_date + relativedelta(
                    months=months_after_eff_date
                )
                invoice = Invoice(
                    self.policy.id,
                    bill_date,
                    bill_date + relativedelta(months=1),
                    bill_date + relativedelta(months=1, days=14),
                    self.policy.annual_premium
                    / BILLING_SCHEDULES.get(self.policy.billing_schedule),
                )
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Quarterly":
            first_invoice.amount_due = first_invoice.amount_due / BILLING_SCHEDULES.get(
                self.policy.billing_schedule
            )
            for i in range(1, BILLING_SCHEDULES.get(self.policy.billing_schedule)):
                months_after_eff_date = i * 3
                bill_date = self.policy.effective_date + relativedelta(
                    months=months_after_eff_date
                )
                invoice = Invoice(
                    self.policy.id,
                    bill_date,
                    bill_date + relativedelta(months=1),
                    bill_date + relativedelta(months=1, days=14),
                    self.policy.annual_premium
                    / BILLING_SCHEDULES.get(self.policy.billing_schedule),
                )
                invoices.append(invoice)
        elif self.policy.billing_schedule == "Monthly":
            first_invoice.amount_due = first_invoice.amount_due / BILLING_SCHEDULES.get(
                self.policy.billing_schedule
            )
            for i in range(1, BILLING_SCHEDULES.get(self.policy.billing_schedule)):
                bill_date = self.policy.effective_date + relativedelta(months=i)
                invoice = Invoice(
                    self.policy.id,
                    bill_date,
                    bill_date + relativedelta(months=1),
                    bill_date + relativedelta(months=1, days=14),
                    self.policy.annual_premium
                    / BILLING_SCHEDULES.get(self.policy.billing_schedule),
                )
                invoices.append(invoice)
        else:
            print "You have chosen a bad billing schedule."

        for invoice in invoices:
            db.session.add(invoice)
        db.session.commit()


################################
# The functions below are for the db and
# shouldn't need to be edited.
################################
def build_or_refresh_db():
    db.drop_all()
    db.create_all()
    insert_data()
    print "DB Ready!"


def insert_data():
    # Contacts
    contacts = []
    john_doe_agent = Contact("John Doe", "Agent")
    contacts.append(john_doe_agent)
    john_doe_insured = Contact("John Doe", "Named Insured")
    contacts.append(john_doe_insured)
    bob_smith = Contact("Bob Smith", "Agent")
    contacts.append(bob_smith)
    anna_white = Contact("Anna White", "Named Insured")
    contacts.append(anna_white)
    joe_lee = Contact("Joe Lee", "Agent")
    contacts.append(joe_lee)
    ryan_bucket = Contact("Ryan Bucket", "Named Insured")
    contacts.append(ryan_bucket)

    for contact in contacts:
        db.session.add(contact)
    db.session.commit()

    policies = []
    p1 = Policy('Policy One', date(2015, 1, 1), 365)
    p1.billing_schedule = 'Annual'
    p1.named_insured = john_doe_insured.id
    p1.agent = bob_smith.id
    policies.append(p1)

    p2 = Policy("Policy Two", date(2015, 2, 1), 1600)
    p2.billing_schedule = "Quarterly"
    p2.named_insured = anna_white.id
    p2.agent = joe_lee.id
    policies.append(p2)

    p3 = Policy("Policy Three", date(2015, 1, 1), 1200)
    p3.billing_schedule = "Monthly"
    p3.named_insured = ryan_bucket.id
    p3.agent = john_doe_agent.id
    policies.append(p3)

    p4 = Policy('Policy Four', date(2015, 2, 1), 500)
    p4.billing_schedule = 'Two-Pay'
    p4.named_insured = ryan_bucket.id
    p4.agent = john_doe_agent.id
    policies.append(p4)

    for policy in policies:
        db.session.add(policy)
    db.session.commit()

    for policy in policies:
        PolicyAccounting(policy.id)

    payment_for_p2 = Payment(p2.id, anna_white.id, 400, date(2015, 2, 1))
    db.session.add(payment_for_p2)
    db.session.commit()
