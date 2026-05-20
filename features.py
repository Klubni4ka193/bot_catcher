import re
from typing import Any


def extract_features(user: dict[str, Any]) -> dict[str, bool]:
    """
    Извлекает бинарные признаки аккаунта.

    Каждый признак возвращает True или False.
    True означает, что признак ботоподобности сработал.
    """

    username = normalize(user.get("username"))
    first_name = normalize(user.get("first_name"))
    last_name = normalize(user.get("last_name"))
    bio = normalize(user.get("bio"))

    return {
        "no_photo": not bool(user.get("has_photo")),
        "random_username": is_random_username(username),
        "empty_bio": bio == "",
        "missing_last_name": last_name == "",
        "username_matches_firstname": username_matches_firstname(username, first_name),
        "hidden_status": bool(user.get("hidden_status")),
        "default_first_name": is_default_first_name(first_name),
        "no_username": username == "",
    }


def normalize(value: Any) -> str:
    if value is None:
        return ""

    return str(value).strip().lower()


def is_random_username(username: str) -> bool:
    """
    Признак случайного username.

    Логика:
    - длина username >= 6;
    - в username есть цифры;
    - либо цифр слишком много,
    - либо букв слишком мало,
    - либо строка похожа на случайную смесь букв и цифр.
    """

    if not username:
        return False

    username = username.replace("@", "").lower()

    if len(username) < 6:
        return False

    letters = re.findall(r"[a-zа-яё]", username)
    digits = re.findall(r"\d", username)

    letters_count = len(letters)
    digits_count = len(digits)

    if digits_count == 0:
        return False

    digit_ratio = digits_count / len(username)

    if digit_ratio >= 0.35:
        return True

    if letters_count < 3 and digits_count > 0:
        return True

    if has_many_consonants_in_row(username):
        return True

    return False


def has_many_consonants_in_row(value: str) -> bool:
    """
    Дополнительная эвристика:
    если в username много согласных подряд, он может быть случайным.
    """

    consonants_pattern = r"[bcdfghjklmnpqrstvwxyzбвгджзйклмнпрстфхцчшщ]{5,}"

    return re.search(consonants_pattern, value.lower()) is not None


def username_matches_firstname(username: str, first_name: str) -> bool:
    """
    Проверяет, совпадает ли username с именем.
    Например:
    username = ivan
    first_name = Ivan
    """

    if not username or not first_name:
        return False

    username = username.replace("@", "").lower()
    first_name = first_name.lower()

    return username == first_name


def is_default_first_name(first_name: str) -> bool:
    """
    Признак дефолтного или подозрительного имени.

    Срабатывает, если:
    - имя отсутствует;
    - имя состоит из одного символа;
    - имя похоже на deleted account;
    - имя состоит в основном из цифр или спецсимволов.
    """

    if not first_name:
        return True

    value = first_name.strip().lower()

    if len(value) <= 1:
        return True

    if value in {"deleted account", "deleted", "account", "user"}:
        return True

    letters = re.findall(r"[a-zа-яё]", value)
    digits = re.findall(r"\d", value)

    if digits and len(letters) <= 1:
        return True

    return False
