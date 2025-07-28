import requests

from core.config import settings


def get_html_from_scrappey(url: str) -> str:
    headers = {
        "Content-Type": "application/json",
    }

    params = {
        "key": settings.SCRAPPEY_API_KEY,
    }

    json_data = {"cmd": "request.get", "url": url}

    response = requests.post(
        "https://publisher.scrappey.com/api/v1",
        params=params,
        headers=headers,
        json=json_data,
    ).json()

    return str(response["solution"]["response"])
