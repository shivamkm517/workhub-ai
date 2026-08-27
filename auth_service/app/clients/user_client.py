import httpx

from app.config import USER_SERVICE_URL


def get_user_by_email(email: str):

    response = httpx.get(
        f"{USER_SERVICE_URL}/internal/users/by-email/{email}"
    )

    if response.status_code == 404:
        return None

    response.raise_for_status()

    return response.json()