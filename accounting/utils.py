from datetime import date, datetime
from dateutil.relativedelta import relativedelta
from decimal import Decimal

from sqlalchemy.orm.exc import NoResultFound
from accounting.models import Base
from sqlalchemy import create_engine
from accounting.config import SQLALCHEMY_DATABASE_URI
from typing import Union

from accounting.sql_base import DBSession
from accounting.models import Contact, Invoice, Payment, Policy

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

    def __init__(self, policy_id: int) -> None:
        self.policy = DBSession.query(Policy).filter_by(id=policy_id).one()
        if self.policy.status == "Canceled":
            raise UserWarning(
                "This policy canceled \nCancel date: {0} \nReason: {1}".format(
                    self.policy.cancel_date.strftime("%Y-%m-%d"),
                    self.policy.cancel_reason,
                )
            )

        if not self.policy.invoices:
            self.make_invoices()

    def return_account_balance(
        self, date_cursor: Union[str, date, datetime] = None
    ) -> Decimal:
        """
        Returns the balance of the policy in a given point in time
        :param date_cursor:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = (
            DBSession.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .filter(Invoice.bill_date <= date_cursor)
            .order_by(Invoice.bill_date)
            .all()
        )
        due_now = 0
        for invoice in invoices:
            due_now += invoice.amount_due

        payments = (
            DBSession.query(Payment)
            .filter_by(policy_id=self.policy.id)
            .filter(Payment.transaction_date <= date_cursor)
            .all()
        )
        for payment in payments:
            due_now -= payment.amount_paid

        return Decimal(due_now)

    def make_payment(
        self,
        contact_id: int = 0,
        date_cursor: Union[str, date, datetime] = None,
        amount: Decimal = Decimal(0),
    ) -> Payment:
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
            contact = DBSession.query(Contact).filter_by(id=contact_id).one()
        except NoResultFound:
            raise NoResultFound("We couldn't find any contact with this id")

        if due_to_non_pay and not contact.role == "Agent":
            raise UserWarning(
                "Policy has passed the due date without being "
                "paid in full, only an agent can't make a payment"
            )

        payment = Payment(self.policy.id, contact_id, amount, date_cursor)
        DBSession.add(payment)
        DBSession.commit()

        return payment

    def evaluate_cancellation_pending_due_to_non_pay(
        self, date_cursor: Union[str, date, datetime] = None
    ) -> bool:
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
            DBSession.query(Invoice)
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
        return False

    def evaluate_cancel(self, date_cursor: Union[str, date, datetime] = None) -> bool:
        """
        Check if there is any balance after any of the cancel dates
        of the invoices in this policy
        :param date_cursor:
        :return:
        """
        if not date_cursor:
            date_cursor = datetime.now().date()

        invoices = (
            DBSession.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .filter(Invoice.cancel_date <= date_cursor)
            .order_by(Invoice.bill_date)
            .all()
        )

        for invoice in invoices:
            if not self.return_account_balance(invoice.cancel_date):
                continue
            else:
                return True
        else:
            return False

    def switch_billing_schedule(self, new_billing_schedule: str) -> None:
        """
        Move a policy to a different billing schedule
        :param new_billing_schedule:
        :return:
        """
        try:
            BILLING_SCHEDULES[new_billing_schedule]
        except KeyError:
            raise KeyError("Invalid billing schedule")
        if self.policy.billing_schedule == new_billing_schedule:
            raise UserWarning(
                "This policy is already on {0}".format(new_billing_schedule)
            )
        for invoice in self.policy.invoices:
            invoice.deleted = 1
            DBSession.add(invoice)
        self.policy.billing_schedule = new_billing_schedule
        DBSession.add(self.policy)
        DBSession.flush()
        self.make_invoices()

    def make_invoices(self) -> None:
        """
        Create invoices for the policy according with its billing schedule
        """
        for invoice in self.policy.invoices:
            DBSession.delete(invoice)

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
            print("You have chosen a bad billing schedule.")

        for invoice in invoices:
            DBSession.add(invoice)
        DBSession.commit()

    def cancel_policy(
        self, reason: str, date_cursor: Union[str, date, datetime] = None
    ):
        if not date_cursor:
            date_cursor = datetime.now().date()
        self.policy.cancel_reason = reason
        self.policy.cancel_date = date_cursor
        self.policy.status = "Canceled"
        DBSession.add(self.policy)
        DBSession.commit()
        self.policy = None
        print("Policy successfully canceled!")


################################
# The functions below are for the db and
# shouldn't need to be edited.
################################
def build_or_refresh_db():
    engine = create_engine(SQLALCHEMY_DATABASE_URI)
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    insert_data()
    print("DB Ready!")


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
        DBSession.add(contact)
    DBSession.commit()

    policies = []
    p1 = Policy("Policy One", date(2015, 1, 1), 365)
    p1.billing_schedule = "Annual"
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

    p4 = Policy("Policy Four", date(2015, 2, 1), 500)
    p4.billing_schedule = "Two-Pay"
    p4.named_insured = ryan_bucket.id
    p4.agent = john_doe_agent.id
    policies.append(p4)

    for policy in policies:
        DBSession.add(policy)
    DBSession.commit()

    for policy in policies:
        PolicyAccounting(policy.id)

    payment_for_p2 = Payment(p2.id, anna_white.id, 400, date(2015, 2, 1))
    DBSession.add(payment_for_p2)
    DBSession.commit()
