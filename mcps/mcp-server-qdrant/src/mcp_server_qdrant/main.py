import argparse
import os


def main():
    """
    Main entry point for the mcp-server-qdrant script defined
    in pyproject.toml. It runs the MCP server with a specific transport
    protocol.
    """

    # Parse the command-line arguments to determine the transport protocol.
    parser = argparse.ArgumentParser(description="mcp-server-qdrant")
    parser.add_argument(
        "--transport",
        choices=["stdio", "sse", "streamable-http"],
        default="stdio",
    )
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8000)
    args = parser.parse_args()

    # Import is done here to make sure environment variables are loaded
    # only after we make the changes.
    from mcp_server_qdrant.server import mcp

    middleware = None
    cors_origins = [
        origin.strip()
        for origin in os.getenv("MCP_CORS_ORIGINS", "").split(",")
        if origin.strip()
    ]
    if cors_origins:
        from starlette.middleware import Middleware
        from starlette.middleware.cors import CORSMiddleware

        middleware = [
            Middleware(
                CORSMiddleware,
                allow_origins=cors_origins,
                allow_methods=["GET", "POST", "DELETE", "OPTIONS"],
                allow_headers=[
                    "Authorization",
                    "Content-Type",
                    "MCP-Protocol-Version",
                    "Mcp-Session-Id",
                    "Last-Event-ID",
                ],
                expose_headers=["Mcp-Session-Id"],
                max_age=600,
            )
        ]

    mcp.run(
        transport=args.transport,
        host=args.host,
        port=args.port,
        middleware=middleware,
    )
