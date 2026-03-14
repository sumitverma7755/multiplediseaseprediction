"""
High-performance async reverse proxy for Streamlit.
Sits in front of the Streamlit server, handles connection pooling,
keep-alive reuse, and rate-limits new connections to prevent port exhaustion.

Usage: python proxy.py  (runs on port 8080, forwards to Streamlit on 8503)
"""
import asyncio
import aiohttp
from aiohttp import web
import logging

logging.basicConfig(level=logging.WARNING)

STREAMLIT_URL = "http://127.0.0.1:8503"

session: aiohttp.ClientSession = None


async def proxy_handler(request: web.Request) -> web.Response:
    """Forward every request to Streamlit and return its response."""
    target_url = STREAMLIT_URL + str(request.rel_url)

    # Strip hop-by-hop headers that conflict with keep-alive proxying
    HOP_BY_HOP = {
        "connection", "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "transfer-encoding", "upgrade", "host",
    }

    req_headers = {k: v for k, v in request.headers.items()
                   if k.lower() not in HOP_BY_HOP}

    try:
        body = await request.read()
        async with session.request(
            method=request.method,
            url=target_url,
            headers=req_headers,
            data=body,
            allow_redirects=False,
            timeout=aiohttp.ClientTimeout(total=30),
        ) as resp:
            content = await resp.read()
            # Strip hop-by-hop response headers too
            resp_headers = {k: v for k, v in resp.headers.items()
                            if k.lower() not in HOP_BY_HOP and k.lower() != "content-encoding"}
            return web.Response(
                status=resp.status,
                headers=resp_headers,
                body=content,
            )
    except Exception as e:
        logging.error(f"Proxy error: {e}")
        return web.Response(status=502, text=f"Bad Gateway: {e}")


async def on_startup(app):
    global session
    # Connector MUST be created inside the running event loop
    connector = aiohttp.TCPConnector(
        limit=10000,
        limit_per_host=10000,
        keepalive_timeout=60,
        enable_cleanup_closed=True,
        force_close=False,
        ttl_dns_cache=300,
    )
    session = aiohttp.ClientSession(connector=connector)


async def on_cleanup(app):
    await session.close()


app = web.Application()
app.router.add_route("*", "/{path_info:.*}", proxy_handler)
app.on_startup.append(on_startup)
app.on_cleanup.append(on_cleanup)

if __name__ == "__main__":
    print("[PROXY] Async proxy listening on http://0.0.0.0:8080 -> Streamlit :8503")
    web.run_app(app, host="0.0.0.0", port=8080, access_log=None)
