import httpx

from core.config import settings


async def get_html_from_scrappey(url: str) -> str:
    headers = {
        "Content-Type": "application/json",
    }

    params = {
        "key": settings.SCRAPPEY_API_KEY,
    }

    json_data = {"cmd": "request.get", "url": url}

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://publisher.scrappey.com/api/v1",
                params=params,
                headers=headers,
                json=json_data,
            )
            response.raise_for_status()
            response_data = response.json()
        except httpx.HTTPStatusError as e:
            raise ValueError(
                f"Scrappey API error (HTTP {e.response.status_code}): {e.response.text}"
            )
        except httpx.RequestError as e:
            raise ValueError(f"Scrappey request failed: {e}")
        except Exception as e:
            raise ValueError(f"Unexpected error with Scrappey: {e}")

    if "solution" not in response_data:
        raise ValueError(f"Unexpected Scrappey response structure: {response_data}")

    if "response" not in response_data["solution"]:
        raise ValueError(
            f"No 'response' field in Scrappey solution: {response_data['solution']}"
        )

    return str(response_data["solution"]["response"])
