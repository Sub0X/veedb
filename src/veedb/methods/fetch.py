# src/veedb/methods/fetch.py
import aiohttp
import asyncio
from typing import Optional, Dict, Any

# Import exceptions from the main package level (src/veedb/exceptions.py)
from ..exceptions import (
    VNDBAPIError,
    AuthenticationError,
    RateLimitError,
    InvalidRequestError,
    NotFoundError,
    ServerError,
    TooMuchDataSelectedError,
)

# Default timeout for requests. VNDB server might abort long requests sooner (e.g., >3s).
# This timeout is for the client-side operation.
CLIENT_TIMEOUT_SECONDS = 30
VNDB_TIMEOUT = aiohttp.ClientTimeout(total=CLIENT_TIMEOUT_SECONDS)


async def _fetch_api(
    session: aiohttp.ClientSession,
    method: str,
    url: str,
    token: Optional[str] = None,
    json_payload: Optional[Dict[str, Any]] = None,
    params: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Internal function to make API requests to VNDB and handle responses.
    """
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = (
            f"Token {token.strip()}"  # Ensure no leading/trailing whitespace in token
        )

    try:
        async with session.request(
            method,
            url,
            headers=headers,
            json=json_payload,
            params=params,
            timeout=VNDB_TIMEOUT,
        ) as resp:
            # Handle 204 No Content for successful PATCH/DELETE operations
            if resp.status == 204:
                return None

            # Attempt to parse JSON, but prepare for plain text errors or HTML error pages
            response_text = await resp.text()
            try:
                # VNDB usually returns JSON, even for errors (e.g., {"id": "error", "msg": "..."})
                # or {"detail": "Not found."}
                data = await resp.json(
                    content_type=None
                )  # Allow any content type if server misreports
            except aiohttp.ContentTypeError:
                # If it's not JSON, it's likely an HTML error page or a plain text error.
                # We'll use the raw text for the error message.
                data = None  # No structured JSON data
            except Exception:  # Includes json.JSONDecodeError
                data = None

            if 200 <= resp.status < 300:
                if data is not None:
                    return data
                # If status is 2xx but no JSON data and not 204, it's unusual.
                # However, for VNDB, successful GET/POST should return JSON.
                # If it's a 200 with non-JSON text, it might be an issue, but we pass text.
                return response_text

            # Error Handling based on status code
            # Extract error message preferentially from JSON `detail` or `msg` field,
            # then from `id` and `msg` (older error format), otherwise use raw text.
            error_message = response_text  # Default to raw text
            if isinstance(data, dict):
                if "detail" in data:
                    error_message = str(data["detail"])
                elif (
                    "id" in data and data["id"] == "error" and "msg" in data
                ):  # Old error format
                    error_message = str(data["msg"])
                elif "error" in data:  # Generic error key
                    error_message = str(data["error"])

            if resp.status == 400:
                if "Too much data selected" in error_message:
                    raise TooMuchDataSelectedError(error_message, resp.status)
                raise InvalidRequestError(error_message, resp.status)
            elif resp.status == 401:
                raise AuthenticationError(error_message, resp.status)
            elif resp.status == 404:
                raise NotFoundError(error_message, resp.status)
            elif resp.status == 429:
                raise RateLimitError(error_message, resp.status)
            elif resp.status >= 500:
                raise ServerError(f"Server error: {error_message}", resp.status)
            else:
                # For other client-side errors not specifically handled
                raise VNDBAPIError(f"API request failed: {error_message}", resp.status)

    except asyncio.TimeoutError:
        raise VNDBAPIError(
            f"Request to {url} timed out after {CLIENT_TIMEOUT_SECONDS} seconds.",
            status_code=None,
        )
    except aiohttp.ClientConnectionError as e:
        raise VNDBAPIError(f"Connection error to {url}: {e}", status_code=None)
    except aiohttp.ClientError as e:  # Catch other aiohttp client errors
        raise VNDBAPIError(
            f"AIOHTTP client error during request to {url}: {e}", status_code=None
        )
