from datetime import datetime, UTC


def get_dt_utc() -> datetime:
    return datetime.now(UTC)
