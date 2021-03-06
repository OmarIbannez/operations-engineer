#!/user/bin/env python2.7

import unittest
from datetime import date

from accounting.sql_base import DBSession
from accounting.models import Contact, Invoice, Policy
from accounting.utils import PolicyAccounting

"""
#######################################################
Test Suite for Accounting
#######################################################
"""


class TestBillingSchedules(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_agent = Contact("Test Agent", "Agent")
        cls.test_insured = Contact("Test Insured", "Named Insured")
        DBSession.add(cls.test_agent)
        DBSession.add(cls.test_insured)
        DBSession.commit()

        cls.policy = Policy("Test Policy", date(2015, 1, 1), 1200)
        DBSession.add(cls.policy)
        cls.policy.named_insured = cls.test_insured.id
        cls.policy.agent = cls.test_agent.id
        DBSession.commit()

    @classmethod
    def tearDownClass(cls):
        DBSession.delete(cls.test_insured)
        DBSession.delete(cls.test_agent)
        DBSession.delete(cls.policy)
        DBSession.commit()

    def setUp(self):
        pass

    def tearDown(self):
        for invoice in self.policy.invoices:
            DBSession.delete(invoice)
        DBSession.commit()

    def test_annual_billing_schedule(self):
        self.policy.billing_schedule = "Annual"
        # No invoices currently exist
        self.assertFalse(self.policy.invoices)
        # Invoices should be made when the class is initiated
        pa = PolicyAccounting(self.policy.id)
        self.assertEquals(len(self.policy.invoices), 1)
        self.assertEquals(
            self.policy.invoices[0].amount_due, self.policy.annual_premium
        )


class TestReturnAccountBalance(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.test_agent = Contact("Test Agent", "Agent")
        cls.test_insured = Contact("Test Insured", "Named Insured")
        DBSession.add(cls.test_agent)
        DBSession.add(cls.test_insured)
        DBSession.commit()

        cls.policy = Policy("Test Policy", date(2015, 1, 1), 1200)
        cls.policy.named_insured = cls.test_insured.id
        cls.policy.agent = cls.test_agent.id
        DBSession.add(cls.policy)
        DBSession.commit()

    @classmethod
    def tearDownClass(cls):
        DBSession.delete(cls.test_insured)
        DBSession.delete(cls.test_agent)
        DBSession.delete(cls.policy)
        DBSession.commit()

    def setUp(self):
        self.payments = []

    def tearDown(self):
        for invoice in self.policy.invoices:
            DBSession.delete(invoice)
        for payment in self.payments:
            DBSession.delete(payment)
        DBSession.commit()

    def test_annual_on_eff_date(self):
        self.policy.billing_schedule = "Annual"
        pa = PolicyAccounting(self.policy.id)
        self.assertEquals(
            pa.return_account_balance(date_cursor=self.policy.effective_date), 1200
        )

    def test_quarterly_on_eff_date(self):
        self.policy.billing_schedule = "Quarterly"
        pa = PolicyAccounting(self.policy.id)
        self.assertEquals(
            pa.return_account_balance(date_cursor=self.policy.effective_date), 300
        )

    def test_monthly_on_eff_date(self):
        self.policy.billing_schedule = "Monthly"
        pa = PolicyAccounting(self.policy.id)
        self.assertEquals(
            pa.return_account_balance(date_cursor=self.policy.effective_date), 100
        )

    def test_quarterly_on_last_installment_bill_date(self):
        self.policy.billing_schedule = "Quarterly"
        pa = PolicyAccounting(self.policy.id)
        invoices = (
            DBSession.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .order_by(Invoice.bill_date)
            .all()
        )
        self.assertEquals(
            pa.return_account_balance(date_cursor=invoices[3].bill_date), 1200
        )

    def test_quarterly_on_second_installment_bill_date_with_full_payment(self):
        self.policy.billing_schedule = "Quarterly"
        pa = PolicyAccounting(self.policy.id)
        invoices = (
            DBSession.query(Invoice)
            .filter_by(policy_id=self.policy.id)
            .order_by(Invoice.bill_date)
            .all()
        )
        self.payments.append(
            pa.make_payment(
                contact_id=self.policy.named_insured,
                date_cursor=invoices[1].bill_date,
                amount=600,
            )
        )
        self.assertEquals(
            pa.return_account_balance(date_cursor=invoices[1].bill_date), 0
        )
