import asyncio
import aiohttp
import logging
from typing import List, Optional, Union, TypeVar, Type, Dict, Any, Generic

from .methods.fetch import _fetch_api
from .apitypes.common import (
    QueryRequest,
    QueryResponse,
    VNDBID,
    LanguageEnum,
    PlatformEnum,
)  # etc.
from .apitypes.entities import (
    VN,
    Release,
    Producer,
    Character,
    Staff,
    Tag,
    Trait,
    Quote,
    User,
    AuthInfo,
    UlistItem,
    UlistLabel,
    UserStats,
)
from .apitypes.requests import UlistUpdatePayload, RlistUpdatePayload
from .exceptions import (
    AuthenticationError,
    VNDBAPIError,
    InvalidRequestError,
    NotFoundError,
    RateLimitError,
    ServerError,
)

BASE_URL = "https://api.vndb.org/kana"
SANDBOX_URL = "https://beta.vndb.org/api/kana"

T_Entity = TypeVar("T_Entity")
T_QueryItem = TypeVar("T_QueryItem")

from dacite import from_dict, Config as DaciteConfig

dacite_config = DaciteConfig(check_types=False)


class _SSLTimeoutFilter(logging.Filter):
    """Filter to suppress harmless SSL shutdown timeout errors from aiohttp."""
    
    def filter(self, record):
        # Suppress the specific SSL shutdown timeout error
        if (record.levelname == "ERROR" and 
            "Error while closing connector" in record.getMessage() and
            "SSL shutdown timed out" in record.getMessage()):
            return False
        return True


# Apply the filter to suppress SSL timeout errors
_ssl_filter = _SSLTimeoutFilter()
logging.getLogger().addFilter(_ssl_filter)
logging.getLogger("aiohttp").addFilter(_ssl_filter)
logging.getLogger("asyncio").addFilter(_ssl_filter)


class _BaseEntityClient(Generic[T_Entity, T_QueryItem]):
    def __init__(
        self,
        client: "VNDB",
        endpoint_path: str,
        entity_dataclass: Type[T_Entity],
        query_item_dataclass: Type[T_QueryItem],
    ):
        self._client = client
        self._endpoint_path = endpoint_path
        self.entity_dataclass = entity_dataclass
        self.query_item_dataclass = query_item_dataclass

    async def _post_query(
        self, query_options: QueryRequest
    ) -> QueryResponse[T_QueryItem]:
        url = f"{self._client.base_url}{self._endpoint_path}"
        payload = query_options.to_dict()

        # Use the session managed by the main VNDB client
        session = self._client._get_session()  # Ensures session is available
        response_data = await _fetch_api(
            session=session,
            method="POST",
            url=url,
            token=self._client.api_token,
            json_payload=payload,
        )
        results_data = response_data.get("results", [])
        parsed_results = [
            from_dict(
                data_class=self.query_item_dataclass, data=item, config=dacite_config
            )
            for item in results_data
        ]

        return QueryResponse[T_QueryItem](
            results=parsed_results,
            more=response_data.get("more", False),
            count=response_data.get("count"),
            compact_filters=response_data.get("compact_filters"),
            normalized_filters=response_data.get("normalized_filters"),
        )

    async def query(
        self, query_options: QueryRequest = QueryRequest()
    ) -> QueryResponse[T_QueryItem]:
        if not query_options.fields:
            query_options.fields = "id"
        return await self._post_query(query_options)


class _VNClient(_BaseEntityClient[VN, VN]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/vn", VN, VN)


class _ReleaseClient(_BaseEntityClient[Release, Release]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/release", Release, Release)


class _ProducerClient(_BaseEntityClient[Producer, Producer]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/producer", Producer, Producer)


class _CharacterClient(_BaseEntityClient[Character, Character]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/character", Character, Character)


class _StaffClient(_BaseEntityClient[Staff, Staff]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/staff", Staff, Staff)


class _TagClient(_BaseEntityClient[Tag, Tag]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/tag", Tag, Tag)


class _TraitClient(_BaseEntityClient[Trait, Trait]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/trait", Trait, Trait)


class _QuoteClient(_BaseEntityClient[Quote, Quote]):
    def __init__(self, client: "VNDB"):
        super().__init__(client, "/quote", Quote, Quote)


class _UlistClient:
    def __init__(self, client: "VNDB"):
        self._client = client

    async def query(
        self, user_id: VNDBID, query_options: QueryRequest = QueryRequest()
    ) -> QueryResponse[UlistItem]:
        url = f"{self._client.base_url}/ulist"
        payload = query_options.to_dict()
        payload["user"] = user_id

        session = self._client._get_session()  # Use managed session
        response_data = await _fetch_api(
            session=session,
            method="POST",
            url=url,
            token=self._client.api_token,
            json_payload=payload,
        )
        results_data = response_data.get("results", [])
        parsed_results = [
            from_dict(data_class=UlistItem, data=item, config=dacite_config)
            for item in results_data
        ]
        return QueryResponse[UlistItem](
            results=parsed_results,
            more=response_data.get("more", False),
            count=response_data.get("count"),
            compact_filters=response_data.get("compact_filters"),
            normalized_filters=response_data.get("normalized_filters"),
        )

    async def get_labels(
        self, user_id: Optional[VNDBID] = None, fields: Optional[str] = None
    ) -> List[UlistLabel]:
        url = f"{self._client.base_url}/ulist_labels"
        params: Dict[str, Any] = {}
        if user_id:
            params["user"] = user_id
        if fields:
            params["fields"] = fields

        session = self._client._get_session()  # Use managed session
        response_data = await _fetch_api(
            session=session,
            method="GET",
            url=url,
            token=self._client.api_token,
            params=params,
        )

        return [
            from_dict(data_class=UlistLabel, data=label, config=dacite_config)
            for label in response_data.get("labels", [])
        ]

    async def update_entry(self, vn_id: VNDBID, payload: UlistUpdatePayload) -> None:
        if not self._client.api_token:
            raise AuthenticationError(
                "listwrite permission and token required for ulist updates."
            )
        url = f"{self._client.base_url}/ulist/{vn_id}"
        session = self._client._get_session()  # Use managed session
        await _fetch_api(
            session=session,
            method="PATCH",
            url=url,
            token=self._client.api_token,
            json_payload=payload.to_dict(),
        )

    async def delete_entry(self, vn_id: VNDBID) -> None:
        if not self._client.api_token:
            raise AuthenticationError(
                "listwrite permission and token required for ulist deletions."
            )
        url = f"{self._client.base_url}/ulist/{vn_id}"
        session = self._client._get_session()  # Use managed session
        await _fetch_api(
            session=session, method="DELETE", url=url, token=self._client.api_token
        )


class _RlistClient:
    def __init__(self, client: "VNDB"):
        self._client = client

    async def update_entry(
        self, release_id: VNDBID, payload: RlistUpdatePayload
    ) -> None:
        if not self._client.api_token:
            raise AuthenticationError(
                "listwrite permission and token required for rlist updates."
            )
        url = f"{self._client.base_url}/rlist/{release_id}"
        session = self._client._get_session()  # Use managed session
        await _fetch_api(
            session=session,
            method="PATCH",
            url=url,
            token=self._client.api_token,
            json_payload=payload.to_dict(),
        )

    async def delete_entry(self, release_id: VNDBID) -> None:
        if not self._client.api_token:
            raise AuthenticationError(
                "listwrite permission and token required for rlist deletions."
            )
        url = f"{self._client.base_url}/rlist/{release_id}"
        session = self._client._get_session()  # Use managed session
        await _fetch_api(
            session=session, method="DELETE", url=url, token=self._client.api_token
        )


class VNDB:
    def __init__(
        self,
        api_token: Optional[str] = None,
        use_sandbox: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
    ):
        self.api_token = api_token
        self.base_url = SANDBOX_URL if use_sandbox else BASE_URL
        self._session_param = session
        self._session_internal: Optional[aiohttp.ClientSession] = None
        self._session_owner = session is None

        self.vn = _VNClient(self)
        self.release = _ReleaseClient(self)
        self.producer = _ProducerClient(self)
        self.character = _CharacterClient(self)
        self.staff = _StaffClient(self)
        self.tag = _TagClient(self)
        self.trait = _TraitClient(self)
        self.quote = _QuoteClient(self)
        self.ulist = _UlistClient(self)
        self.rlist = _RlistClient(self)

    def _get_session(self) -> aiohttp.ClientSession:
        if self._session_param is not None:
            if self._session_param.closed:
                raise RuntimeError(
                    "Externally provided aiohttp.ClientSession is closed."
                )
            return self._session_param

        if self._session_internal is None or self._session_internal.closed:
            if self._session_owner:                # Configure TCPConnector with settings to improve SSL shutdown handling
                connector = aiohttp.TCPConnector(
                    enable_cleanup_closed=True,
                    ttl_dns_cache=60,
                    use_dns_cache=True,
                    force_close=True,  # Force close connections instead of keeping them alive
                    limit_per_host=10  # Limit concurrent connections per host
                )
                
                # Set a more reasonable timeout for the entire session
                timeout = aiohttp.ClientTimeout(
                    total=30,  # Total timeout
                    connect=10,  # Connection timeout
                    sock_read=10  # Socket read timeout
                )
                
                self._session_internal = aiohttp.ClientSession(
                    connector=connector,
                    timeout=timeout
                )
            else:                raise RuntimeError(
                    "aiohttp.ClientSession not available. "
                    "VNDB client was not provided a session and does not own one to create."
                )
        return self._session_internal

    async def close(self):
        if (
            self._session_internal is not None
            and self._session_owner
            and not self._session_internal.closed
        ):
            # Yield control to the event loop to allow pending operations
            await asyncio.sleep(0)
            
            try:
                # Close the session with a timeout to prevent hanging
                await asyncio.wait_for(
                    self._session_internal.close(), 
                    timeout=2.0  # Reduced timeout for session close
                )
                
                # Also close the underlying connector if available
                if hasattr(self._session_internal, 'connector') and self._session_internal.connector:
                    await asyncio.wait_for(
                        self._session_internal.connector.close(),
                        timeout=1.0  # Short timeout for connector close
                    )
                    
            except asyncio.TimeoutError:
                # If close times out, we can't do much more
                # The session will eventually be cleaned up by the garbage collector
                pass
            except Exception:
                # Ignore other exceptions during close (e.g., SSL errors)
                # These are usually harmless cleanup issues
                pass
                
            # Brief delay to allow final cleanup
            await asyncio.sleep(0.05)

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_schema(self) -> dict:
        url = f"{self.base_url}/schema"
        session = self._get_session()
        return await _fetch_api(
            session=session, method="GET", url=url, token=self.api_token
        )

    async def get_stats(self) -> UserStats:
        url = f"{self.base_url}/stats"
        session = self._get_session()
        data = await _fetch_api(
            session=session, method="GET", url=url, token=self.api_token
        )
        return from_dict(data_class=UserStats, data=data, config=dacite_config)

    async def get_user(
        self, q: Union[VNDBID, List[VNDBID]], fields: Optional[str] = None
    ) -> Dict[str, Optional[User]]:
        url = f"{self.base_url}/user"
        params: Dict[str, Any] = {"q": q}
        if fields:
            params["fields"] = fields

        session = self._get_session()
        response_data = await _fetch_api(
            session=session, method="GET", url=url, token=self.api_token, params=params
        )

        parsed_response: Dict[str, Optional[User]] = {}
        for key, value_data in response_data.items():
            if value_data:
                try:
                    parsed_response[key] = from_dict(
                        data_class=User, data=value_data, config=dacite_config
                    )
                except Exception: # Catch parsing errors
                    parsed_response[key] = None
            else:
                parsed_response[key] = None
        return parsed_response

    async def get_authinfo(self) -> AuthInfo:
        if not self.api_token:
            raise AuthenticationError("API token required for /authinfo endpoint.")
        url = f"{self.base_url}/authinfo"
        session = self._get_session()
        response_data = await _fetch_api(
            session=session, method="GET", url=url, token=self.api_token
        )
        return from_dict(data_class=AuthInfo, data=response_data, config=dacite_config)
