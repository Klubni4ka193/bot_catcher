from typing import Any


def calculate_score(
    features: dict[str, bool],
    weights: dict[str, int],
) -> tuple[int, list[str]]:
    """
    Считает итоговый скоринговый балл.

    Балл = сумма весов всех сработавших признаков.
    """

    score = 0
    reasons: list[str] = []

    for feature_name, is_active in features.items():
        if not is_active:
            continue

        weight = int(weights.get(feature_name, 0))
        score += weight
        reasons.append(f"{feature_name}(+{weight})")

    return score, reasons


def classify_user(score: int, threshold: int) -> bool:
    """
    Возвращает True, если аккаунт классифицирован как бот.
    """

    return score >= threshold


def analyze_user(
    user: dict[str, Any],
    features: dict[str, bool],
    weights: dict[str, int],
    threshold: int,
) -> dict[str, Any]:
    score, reasons = calculate_score(features, weights)
    is_bot = classify_user(score, threshold)

    return {
        **user,
        "score": score,
        "is_detected_bot": is_bot,
        "reasons": "; ".join(reasons),
    }
