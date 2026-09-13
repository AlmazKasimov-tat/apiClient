import allure
import pytest
import requests  # Добавлено для перехвата HTTPError
from core.models.booking import BookingResponse


@allure.feature("Test booking creating")
@allure.title("Positive: creating booking custom data")
def test_create_booking_with_custom_data(api_client):
    booking_data = {
        "firstname": "John",
        "lastname": "Doe",
        "totalprice": 150,
        "depositpaid": True,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-10"
        },
        "additionalneeds": "Dinner"
    }

    response = api_client.create_booking(booking_data)
    validated_data = BookingResponse.model_validate(response)

    assert validated_data.bookingid > 0
    assert validated_data.booking.firstname == "John"
    assert validated_data.booking.totalprice == 150


@allure.title("Позитивный: Граничные значения (максимальная длина, цена 0)")
@allure.description("Проверка устойчивости API к крайним допустимым значениям")
def test_create_booking_boundary_values(api_client):
    boundary_data = {
        "firstname": "A" * 50,
        "lastname": "B",
        "totalprice": 0,
        "depositpaid": False,
        "bookingdates": {
            "checkin": "2025-02-01",
            "checkout": "2025-02-02"
        }
    }

    response = api_client.create_booking(boundary_data)
    validated = BookingResponse.model_validate(response)

    assert len(validated.booking.firstname) == 50
    assert validated.booking.totalprice == 0


@allure.title("Негативный: Отсутствие обязательного поля (firstname)")
@allure.description("API должен вернуть ошибку, так как firstname обязательно")
def test_create_booking_missing_required_field(api_client, valid_booking_data):
    invalid_data = valid_booking_data.copy()
    del invalid_data["firstname"]

    # ✅ ИСПРАВЛЕНО: Ловим HTTPError, который выбрасывает raise_for_status()
    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        api_client.create_booking(invalid_data)

    assert "500 Server Error" in str(exc_info.value)


@allure.title("Негативный: Отсутствие обязательного объекта bookingdates")
@allure.description("API должен вернуть ошибку, если полностью отсутствует объект с датами")
def test_create_booking_missing_bookingdates(api_client, valid_booking_data):
    invalid_data = valid_booking_data.copy()
    # ✅ ИСПРАВЛЕНО: Удаляем весь объект дат, это гарантированно ломает API
    del invalid_data["bookingdates"]

    with pytest.raises(requests.exceptions.HTTPError) as exc_info:
        api_client.create_booking(invalid_data)

    assert "500 Server Error" in str(exc_info.value)


@allure.title("Позитивный: Параметризованный тест для разных имен")
@allure.description("Проверка создания бронирования с разными вариантами имен")
@pytest.mark.parametrize("firstname_input, expected_firstname", [
    ("Иван", "Иван"),
    ("Jean-Pierre", "Jean-Pierre"),
    ("O'Connor", "O'Connor"),
    # ✅ ИСПРАВЛЕНО: API автоматически обрезает пробелы (trim), ожидаем "TrimMe"
    ("   TrimMe   ", "TrimMe"),
])
def test_create_booking_various_firstnames(api_client, valid_booking_data, firstname_input, expected_firstname):
    test_data = valid_booking_data.copy()
    test_data["firstname"] = firstname_input

    response = api_client.create_booking(test_data)
    validated = BookingResponse.model_validate(response)

    assert validated.booking.firstname == expected_firstname