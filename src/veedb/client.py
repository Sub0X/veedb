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
)
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
from .schema_validator import FilterValidator, SchemaCache


BASE_URL = "https://api.vndb.org/kana"
SANDBOX_URL = "https://beta.vndb.org/api/kana"

T_Entity = TypeVar("T_Entity")
T_QueryItem = TypeVar("T_QueryItem")

from dacite import from_dict, Config as DaciteConfig

dacite_config = DaciteConfig(check_types=False)


class _SSLTimeoutFilter(logging.Filter):
    """Filter to suppress harmless SSL shutdown timeout errors from aiohttp."""
    
    def filter(self, record):
        if (record.levelname == "ERROR" and 
            "Error while closing connector" in record.getMessage() and
            "SSL shutdown timed out" in record.getMessage()):
            return False
        return True

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
        session = self._client._get_session()
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

    async def validate_filters(self, filters: Union[List, str, None]) -> Dict[str, Any]:
        """Validates filters against the schema for this specific endpoint."""
        return await self._client.validate_filters(self._endpoint_path, filters)
    
    async def get_available_fields(self) -> List[str]:
        """Gets all available filterable fields for this endpoint."""
        return await self._client.get_available_fields(self._endpoint_path)


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
        session = self._client._get_session()
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
        session = self._client._get_session()
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
            raise AuthenticationError("listwrite permission and token required for ulist updates.")
        url = f"{self._client.base_url}/ulist/{vn_id}"
        session = self._client._get_session()
        await _fetch_api(
            session=session,
            method="PATCH",
            url=url,
            token=self._client.api_token,
            json_payload=payload.to_dict(),
        )

    async def delete_entry(self, vn_id: VNDBID) -> None:
        if not self._client.api_token:
            raise AuthenticationError("listwrite permission and token required for ulist deletions.")
        url = f"{self._client.base_url}/ulist/{vn_id}"
        session = self._client._get_session()
        await _fetch_api(session=session, method="DELETE", url=url, token=self._client.api_token)


class _RlistClient:
    def __init__(self, client: "VNDB"):
        self._client = client

    async def update_entry(self, release_id: VNDBID, payload: RlistUpdatePayload) -> None:
        if not self._client.api_token:
            raise AuthenticationError("listwrite permission and token required for rlist updates.")
        url = f"{self._client.base_url}/rlist/{release_id}"
        session = self._client._get_session()
        await _fetch_api(
            session=session,
            method="PATCH",
            url=url,
            token=self._client.api_token,
            json_payload=payload.to_dict(),
        )

    async def delete_entry(self, release_id: VNDBID) -> None:
        if not self._client.api_token:
            raise AuthenticationError("listwrite permission and token required for rlist deletions.")
        url = f"{self._client.base_url}/rlist/{release_id}"
        session = self._client._get_session()
        await _fetch_api(session=session, method="DELETE", url=url, token=self._client.api_token)


class VNDB:
    def __init__(
        self,
        api_token: Optional[str] = None,
        use_sandbox: bool = False,
        session: Optional[aiohttp.ClientSession] = None,
        local_schema_path: Optional[str] = None, 
        schema_cache_dir: str = ".veedb_cache", 
        schema_cache_ttl_hours: float = 24.0,
    ):
        self.api_token = api_token
        self.base_url = SANDBOX_URL if use_sandbox else BASE_URL
        self._session_param = session
        self._session_internal: Optional[aiohttp.ClientSession] = None
        self._session_owner = session is None
        
        # Store schema configuration
        self.local_schema_path = local_schema_path
        self.schema_cache_dir = schema_cache_dir
        self.schema_cache_ttl_hours = schema_cache_ttl_hours

        # Initialize SchemaCache with new parameters
        self._schema_cache_instance = SchemaCache(
            cache_dir=self.schema_cache_dir,
            local_schema_path=self.local_schema_path,
            ttl_hours=self.schema_cache_ttl_hours
        )
        # Pass the SchemaCache instance to FilterValidator
        self._filter_validator: FilterValidator = FilterValidator(schema_cache=self._schema_cache_instance)

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
                raise RuntimeError("Externally provided aiohttp.ClientSession is closed.")
            return self._session_param

        if self._session_internal is None or self._session_internal.closed:
            if self._session_owner:
                connector = aiohttp.TCPConnector(enable_cleanup_closed=True)
                self._session_internal = aiohttp.ClientSession(connector=connector)
            else:
                raise RuntimeError("aiohttp.ClientSession not available.")
        return self._session_internal

    async def close(self):
        if self._session_internal is not None and self._session_owner and not self._session_internal.closed:
            await self._session_internal.close()
            await asyncio.sleep(0.05)  # Allow time for cleanup

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def get_schema(self) -> dict:
        url = f"{self.base_url}/schema"
        session = self._get_session()
        return await _fetch_api(session=session, method="GET", url=url, token=self.api_token)

    async def get_stats(self) -> UserStats:
        url = f"{self.base_url}/stats"
        session = self._get_session()
        data = await _fetch_api(session=session, method="GET", url=url, token=self.api_token)
        return from_dict(data_class=UserStats, data=data, config=dacite_config)

    async def get_user(self, q: Union[VNDBID, List[VNDBID]], fields: Optional[str] = None) -> Dict[str, Optional[User]]:
        url = f"{self.base_url}/user"
        params: Dict[str, Any] = {"q": q}
        if fields:
            params["fields"] = fields
        session = self._get_session()
        response_data = await _fetch_api(session=session, method="GET", url=url, token=self.api_token, params=params)
        parsed_response: Dict[str, Optional[User]] = {}
        for key, value_data in response_data.items():
            parsed_response[key] = from_dict(data_class=User, data=value_data, config=dacite_config) if value_data else None
        return parsed_response

    async def get_authinfo(self) -> AuthInfo:
        if not self.api_token:
            raise AuthenticationError("API token required for /authinfo endpoint.")
        url = f"{self.base_url}/authinfo"
        session = self._get_session()
        response_data = await _fetch_api(session=session, method="GET", url=url, token=self.api_token)
        return from_dict(data_class=AuthInfo, data=response_data, config=dacite_config)
    
    def _get_filter_validator(self) -> FilterValidator:
        """Returns the FilterValidator instance."""
        # FilterValidator is now initialized in __init__
        return self._filter_validator
    
    async def validate_filters(self, endpoint: str, filters: Union[List, str, None]) -> Dict[str, Any]:
        """Validates filters against the schema for a specific endpoint."""
        validator = self._get_filter_validator()
        return await validator.validate_filters(endpoint, filters, self)
    
    async def get_available_fields(self, endpoint: str) -> List[str]:
        """Get all available filterable fields for an endpoint."""
        validator = self._get_filter_validator()
        return await validator.get_available_fields(endpoint, self)
    
    async def list_endpoints(self) -> List[str]:
        """Get all available API endpoints."""
        validator = self._get_filter_validator()
        return await validator.list_endpoints(self)
    
    def invalidate_schema_cache(self):
        """Invalidates the schema cache, forcing a refresh on next validation or schema access."""
        # The actual invalidation is handled by the SchemaCache instance
        self._schema_cache_instance.invalidate_cache()

    async def update_local_schema(self) -> Dict[str, Any]:
        """Forces a download of the latest schema and updates the local schema file (if configured) or the cache."""
        return await self._schema_cache_instance.update_local_schema_from_api(self)