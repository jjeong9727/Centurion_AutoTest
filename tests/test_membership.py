from playwright.sync_api import Page
from helpers.homepage_utils import verify_membership_balance
from config import Account


def test_check_membership_balance(page: Page):
    expected_customer_name = Account["cust_name"]
    expected_balance = 150000

    verify_membership_balance(page, expected_customer_name, expected_balance)