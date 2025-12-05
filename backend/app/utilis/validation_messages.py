def _label(field: str, label: str | None = None) -> str:
    """Return a human-readable label for a field name.

    If `label` is provided, use it. Otherwise, derive from the field name
    (e.g. "password_confirm" -> "Password confirm").
    """
    if label:
        return label
    return field.replace("_", " ").capitalize()


def required(field: str, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} is required"


def min_length(field: str, n: int, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} must be at least {n} characters long"


def max_length(field: str, n: int, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} must be at most {n} characters long"


def greater_than(field: str, n: int, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} must be greater than {n}"


def at_most(field: str, n: int, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} must be at most {n}"


def future_date(field: str, label: str | None = None) -> str:
    name = _label(field, label)
    return f"{name} must be in the future"
