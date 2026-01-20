"""DataHub client for governance context retrieval."""

from typing import Any, Dict, List, Optional
import requests

from ..models.dbt_models import dbtModel
from .urn_mapper import URNMapper


class DataHubClient:
    """Client for interacting with DataHub."""

    def __init__(
        self,
        server: str,
        token: str,
        timeout: int = 30,
    ):
        """Initialize DataHub client.

        Args:
            server: DataHub server URL.
            token: DataHub access token.
            timeout: Request timeout in seconds.
        """
        self.server = server.rstrip("/")
        self.token = token
        self.timeout = timeout
        self.headers = {
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        }

    def health_check(self) -> bool:
        """Check if DataHub is reachable.

        Returns:
            True if DataHub is healthy.
        """
        try:
            response = requests.get(
                f"{self.server}/health",
                headers=self.headers,
                timeout=self.timeout,
            )
            return response.status_code == 200
        except Exception:
            return False

    def get_governance_context(self) -> Dict[str, Any]:
        """Retrieve governance context from DataHub.

        Returns:
            Dictionary containing ownership, tags, and other governance data.
        """
        context = {
            "ownership": {},
            "tags": {},
            "descriptions": {},
            "lineage": {},
        }
        return context

    def get_model_ownership(self, urn: str) -> List[Dict[str, str]]:
        """Get ownership information for a model.

        Args:
            urn: DataHub URN for the model.

        Returns:
            List of ownership objects.
        """
        try:
            response = requests.get(
                f"{self.server}/aspects/urn:li:dataset({urn})",
                params={
                    "aspect": "ownership",
                    "version": "0",
                },
                headers=self.headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("ownership", {}).get("owners", [])
        except Exception:
            pass
        return []

    def get_model_tags(self, urn: str) -> List[str]:
        """Get tags for a model.

        Args:
            urn: DataHub URN for the model.

        Returns:
            List of tag names.
        """
        try:
            response = requests.get(
                f"{self.server}/aspects/urn:li:dataset({urn})",
                params={
                    "aspect": "globalTags",
                    "version": "0",
                },
                headers=self.headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                tags = data.get("globalTags", {}).get("tags", [])
                return [tag.get("tag", {}).get("name") for tag in tags]
        except Exception:
            pass
        return []

    def get_model_description(self, urn: str) -> Optional[str]:
        """Get description for a model.

        Args:
            urn: DataHub URN for the model.

        Returns:
            Model description or None.
        """
        try:
            response = requests.get(
                f"{self.server}/aspects/urn:li:dataset({urn})",
                params={
                    "aspect": "datasetProperties",
                    "version": "0",
                },
                headers=self.headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("datasetProperties", {}).get("description")
        except Exception:
            pass
        return None

    def search_datasets(
        self,
        query: str,
        platform: Optional[str] = None,
        limit: int = 100,
    ) -> List[Dict[str, Any]]:
        """Search for datasets in DataHub.

        Args:
            query: Search query.
            platform: Optional platform filter.
            limit: Maximum number of results.

        Returns:
            List of matching datasets.
        """
        try:
            params = {
                "type": "dataset",
                "query": query,
                "limit": limit,
            }
            if platform:
                params["platform"] = platform

            response = requests.get(
                f"{self.server}/search",
                params=params,
                headers=self.headers,
                timeout=self.timeout,
            )
            if response.status_code == 200:
                data = response.json()
                return data.get("hits", [])
        except Exception:
            pass
        return []

    def create_urn_mapper(self, platform: str = "dbt") -> URNMapper:
        """Create a URN mapper for dbt models.

        Args:
            platform: Data platform name.

        Returns:
            URNMapper instance.
        """
        return URNMapper(platform=platform, datahub_client=self)

    def emit_entities(self, entities: List[Dict[str, Any]]) -> bool:
        """Emit entities to DataHub.

        Args:
            entities: List of entities to emit.

        Returns:
            True if successful.
        """
        try:
            response = requests.post(
                f"{self.server}/entities",
                json={"entities": entities},
                headers=self.headers,
                timeout=self.timeout,
            )
            return response.status_code in (200, 201)
        except Exception:
            return False

    def emit_entity(self, entity: Dict[str, Any]) -> bool:
        """Emit a single entity to DataHub.

        Args:
            entity: Entity to emit.

        Returns:
            True if successful.
        """
        try:
            response = requests.post(
                f"{self.server}/entities",
                json={"entities": [entity]},
                headers=self.headers,
                timeout=self.timeout,
            )
            return response.status_code in (200, 201)
        except Exception:
            return False


class DataHubGraph:
    """DataHub graph client for complex queries."""

    def __init__(self, client: DataHubClient):
        """Initialize graph client.

        Args:
            client: DataHubClient instance.
        """
        self.client = client

    def get_lineage(
        self,
        urn: str,
        direction: str = "downstream",
        depth: int = 1,
    ) -> Dict[str, Any]:
        """Get lineage information for an entity.

        Args:
            urn: Entity URN.
            direction: Lineage direction (upstream or downstream).
            depth: Lineage depth.

        Returns:
            Lineage information dictionary.
        """
        try:
            response = requests.get(
                f"{self.client.server}/lineage/{urn}",
                params={"direction": direction, "depth": depth},
                headers=self.client.headers,
                timeout=self.client.timeout,
            )
            if response.status_code == 200:
                return response.json()
        except Exception:
            pass
        return {"nodes": [], "edges": []}
