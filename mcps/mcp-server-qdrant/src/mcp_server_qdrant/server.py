from mcp_server_qdrant.mcp_server import QdrantMCPServer
from fastmcp.server.auth.providers.introspection import IntrospectionTokenVerifier
from mcp_server_qdrant.settings import (
    AuthSettings,
    EmbeddingProviderSettings,
    QdrantSettings,
    ToolSettings,
)

auth_settings = AuthSettings()
auth = IntrospectionTokenVerifier(
    introspection_url=auth_settings.introspection_url,
    client_id=auth_settings.client_id,
    client_secret=auth_settings.introspection_secret,
)

mcp = QdrantMCPServer(
    tool_settings=ToolSettings(),
    qdrant_settings=QdrantSettings(),
    embedding_provider_settings=EmbeddingProviderSettings(),
    auth=auth,
)
