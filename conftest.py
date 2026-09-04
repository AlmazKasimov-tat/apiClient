from core.clients.api_client import APIClient
import pytest
from datetime import datetime, timedelta
from faker import Faker

@pytest.fixture(scope="session")
def api_client():
    client = APIClient()
    client.auth()
    return client

@pytest.fixture()
def booking_dates():
    today = datetime.today()
    checkin_date = today + timedelta(days = 10)
    checkout_date = today + timedelta(days = 5)

    return {
        "checkin": checkin_date.strftime("%Y-%m-%d"),
        "checkout": checkout_date.strftime("%Y-%m-%d")
    }

@pytest.fixture()
def generate_random_booking_data(booking_dates):
    faker = Faker()
    first_name = faker.first_name()
    last_name = faker.last_name()
    total_price = faker.random_number(digits=3)
    deposit_paid = faker.boolean()
    additional_needs = faker.sentence()

    data = {
        "first_name": first_name,
        "last_name": last_name,
        "total_price": total_price,
        "deposit_paid": deposit_paid,
        "additional_needs": additional_needs,
        "booking_dates": booking_dates
    }
    
    return data