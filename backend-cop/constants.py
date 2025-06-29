DEFAULT_PAGE_SIZE = 6
NAME_MAX_LENGTH = 200
UNIT_MAX_LENGTH = 50

MAX_LENGTH_USERNAME = 150
MAX_LENGTH_FIRSTNAME = 150
MAX_LENGTH_LASTNAME = 150

MIN_COOKING_TIME = 1

ERROR_MESSAGES = {
    "first_name_required": "Поле 'first_name' обязательно.",
    "first_name_blank": "Поле 'first_name' не может быть пустым.",
    "first_name_max_length": (
        "Максимальная длина поля 'first_name' - "
        f"{MAX_LENGTH_FIRSTNAME} символов."
    ),
    "last_name_required": "Поле 'last_name' обязательно.",
    "last_name_blank": "Поле 'last_name' не может быть пустым.",
    "last_name_max_length": (
        "Максимальная длина поля 'last_name' - "
        f"{MAX_LENGTH_LASTNAME} символов."
    ),
    "username_max_length": (
        "Максимальная длина поля 'username' - "
        f"{MAX_LENGTH_USERNAME} символов."
    ),
}
