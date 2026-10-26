"""
Brotli response compression middleware.

Mirrors C# BrotliCompressionProvider. Properly handles streaming ASGI responses
by collecting body chunks before compression.
"""

import brotli


class BrotliCompressionMiddleware:
    """ASGI middleware that compresses responses with Brotli when client supports it."""

    def __init__(self, app, minimum_size: int = 500):
        self.app = app
        self.minimum_size = minimum_size

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            return await self.app(scope, receive, send)

        # Check if client accepts br encoding
        accept_encoding = ""
        for name, value in scope.get("headers", []):
            if name == b"accept-encoding":
                accept_encoding = value.decode("latin-1")
                break

        if "br" not in accept_encoding:
            return await self.app(scope, receive, send)

        # Collect the full response, then compress
        response_started = False
        response_headers = []
        status_code = 200
        body_chunks = []

        async def send_wrapper(message):
            nonlocal response_started, response_headers, status_code

            if message["type"] == "http.response.start":
                response_started = True
                status_code = message["status"]
                response_headers = list(message.get("headers", []))
            elif message["type"] == "http.response.body":
                body_chunks.append(message.get("body", b""))
                # Only compress on the final chunk
                if not message.get("more_body", False):
                    full_body = b"".join(body_chunks)
                    if len(full_body) >= self.minimum_size:
                        compressed = brotli.compress(full_body)
                        # Replace content-length with compressed size
                        new_headers = []
                        for k, v in response_headers:
                            if k != b"content-length":
                                new_headers.append((k, v))
                        new_headers.append((b"content-length", str(len(compressed)).encode()))
                        new_headers.append((b"content-encoding", b"br"))
                        await send({
                            "type": "http.response.start",
                            "status": status_code,
                            "headers": new_headers,
                        })
                        await send({
                            "type": "http.response.body",
                            "body": compressed,
                            "more_body": False,
                        })
                    else:
                        # Too small, send uncompressed
                        await send({
                            "type": "http.response.start",
                            "status": status_code,
                            "headers": response_headers,
                        })
                        for i, chunk in enumerate(body_chunks):
                            await send({
                                "type": "http.response.body",
                                "body": chunk,
                                "more_body": i < len(body_chunks) - 1,
                            })
                return

            await send(message)

        await self.app(scope, receive, send_wrapper)
