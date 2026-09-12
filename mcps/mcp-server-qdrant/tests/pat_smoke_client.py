import argparse
import asyncio

from fastmcp import Client
from fastmcp.client.transports import StreamableHttpTransport


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--token", required=True)
    parser.add_argument("--store")
    parser.add_argument("--find")
    args = parser.parse_args()

    transport = StreamableHttpTransport(
        args.url,
        headers={"Authorization": f"Bearer {args.token}"},
    )
    async with Client(transport) as client:
        if args.store:
            result = await client.call_tool(
                "qdrant-store",
                {"information": args.store, "metadata": None},
            )
            print(result)
        if args.find:
            result = await client.call_tool("qdrant-find", {"query": args.find})
            print(result)


if __name__ == "__main__":
    asyncio.run(main())
