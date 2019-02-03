from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, VARCHAR, INTEGER, DATE, Enum, ForeignKey, Boolean
from sqlalchemy.orm import relation
from sqlalchemy import create_engine
from accounting.config import SQLALCHEMY_DATABASE_URI


Base = declarative_base()


class Policy(Base):
    __tablename__ = "policies"

    __table_args__ = {}

    # column definitions
    id = Column(u"id", INTEGER(), primary_key=True, nullable=False)
    policy_number = Column(u"policy_number", VARCHAR(length=128), nullable=False)
    effective_date = Column(u"effective_date", DATE(), nullable=False)
    status = Column(
        u"status",
        Enum(u"Active", u"Canceled", u"Expired"),
        default=u"Active",
        nullable=False,
    )
    billing_schedule = Column(
        u"billing_schedule",
        Enum(u"Annual", u"Two-Pay", u"Quarterly", u"Monthly"),
        default=u"Annual",
        nullable=False,
    )
    annual_premium = Column(u"annual_premium", INTEGER(), nullable=False)
    named_insured = Column(u"named_insured", INTEGER(), ForeignKey("contacts.id"))
    agent = Column(u"agent", INTEGER(), ForeignKey("contacts.id"))
    cancel_date = Column(u"cancel_date", DATE(), nullable=True, default=None)
    cancel_reason = Column(
        u"cancel_reason", VARCHAR(length=128), nullable=True, default=None
    )

    def __init__(self, policy_number, effective_date, annual_premium):
        self.policy_number = policy_number
        self.effective_date = effective_date
        self.annual_premium = annual_premium

    invoices = relation(
        "Invoice",
        primaryjoin="and_(Invoice.policy_id==Policy.id, Invoice.deleted == 0)",
    )


class Contact(Base):
    __tablename__ = "contacts"

    __table_args__ = {}

    # column definitions
    id = Column(u"id", INTEGER(), primary_key=True, nullable=False)
    name = Column(u"name", VARCHAR(length=128), nullable=False)
    role = Column(u"role", Enum(u"Named Insured", u"Agent"), nullable=False)

    def __init__(self, name, role):
        self.name = name
        self.role = role


class Invoice(Base):
    __tablename__ = "invoices"

    __table_args__ = {}

    # column definitions
    id = Column(u"id", INTEGER(), primary_key=True, nullable=False)
    policy_id = Column(
        u"policy_id", INTEGER(), ForeignKey("policies.id"), nullable=False
    )
    bill_date = Column(u"bill_date", DATE(), nullable=False)
    due_date = Column(u"due_date", DATE(), nullable=False)
    cancel_date = Column(u"cancel_date", DATE(), nullable=False)
    amount_due = Column(u"amount_due", INTEGER(), nullable=False)
    deleted = Column(
        u"deleted", Boolean, default=False, server_default="0", nullable=False
    )

    def __init__(self, policy_id, bill_date, due_date, cancel_date, amount_due):
        self.policy_id = policy_id
        self.bill_date = bill_date
        self.due_date = due_date
        self.cancel_date = cancel_date
        self.amount_due = amount_due

    def serialize(self):
        return {
            "id": self.id,
            "bill_date": self.bill_date.strftime("%Y-%m-%d"),
            "due_date": self.due_date.strftime("%Y-%m-%d"),
            "amount_due": self.amount_due,
        }


class Payment(Base):
    __tablename__ = "payments"

    __table_args__ = {}

    # column definitions
    id = Column(u"id", INTEGER(), primary_key=True, nullable=False)
    policy_id = Column(
        u"policy_id", INTEGER(), ForeignKey("policies.id"), nullable=False
    )
    contact_id = Column(
        u"contact_id", INTEGER(), ForeignKey("contacts.id"), nullable=False
    )
    amount_paid = Column(u"amount_paid", INTEGER(), nullable=False)
    transaction_date = Column(u"transaction_date", DATE(), nullable=False)

    def __init__(self, policy_id, contact_id, amount_paid, transaction_date):
        self.policy_id = policy_id
        self.contact_id = contact_id
        self.amount_paid = amount_paid
        self.transaction_date = transaction_date


engine = create_engine(SQLALCHEMY_DATABASE_URI)
Base.metadata.create_all(engine)
