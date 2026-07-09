"""Tiny local HTTP server that wraps the classifier loop for the web demo's live box.

AUTHOR / LOCAL USE ONLY. This makes live LLM calls (config from the environment / .env,
exactly like the CLI). It exists so the "Classify" box in web/index.html can classify a
pasted description locally. It is NOT for deployment: a static host such as GitHub Pages
runs no server, so the page there degrades gracefully to the cached examples.

It does two things:
  * Serves the static web/ directory, injecting ``window.__CLASSIFY_ENDPOINT__ = "/classify"``
    into index.html so the page served from here has the live endpoint wired up. Opened any
    other way (file://, Pages) the endpoint stays empty and the live box degrades.
  * POST /classify {"description": "..."} -> runs the maker/checker loop and returns the
    ratified-shape result as JSON, WITH the challenge record and an explicit
    "ratification_required" flag. The browser demo auto-accepts the proposal only to display
    it; it never claims a human ratified it (provenance.approved_by stays null and the page
    shows a ratification banner). The human gate is represented, not dropped.

Usage:
    python scripts/serve_classify.py            # http://localhost:8000  (POST /classify)
    PORT=9000 python scripts/serve_classify.py
"""

from __future__ import annotations

import json
import os
import sys
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from classifier.graph import classify
from classifier.provider import LLMProvider
from classifier.run import build_entry, slugify

ROOT = Path(__file__).resolve().parent.parent
WEB_DIR = ROOT / "web"
ENDPOINT_MARKER = "<!--CLASSIFY_ENDPOINT-->"
ENDPOINT_INJECTION = '<script>window.__CLASSIFY_ENDPOINT__ = "/classify";</script>'
MAX_DESCRIPTION_BYTES = 20_000


def _auto_accept(state: dict) -> dict:
    """Let the graph finish unattended WITHOUT claiming human ratification.

    Returns approve so the loop terminates, but with ``approved_by=None`` — the entry is
    displayed, never finalised as ratified. The page surfaces the human gate as a banner.
    """
    return {"decision": "approve", "approved_by": None}


def classify_to_payload(description: str, provider: LLMProvider) -> dict:
    """Run the real maker/checker loop and shape the result for the browser.

    Pure w.r.t. the injected ``provider`` (a fake in tests), so no network is required to
    exercise it. The returned ``entry`` has the exact shape the registry/hero renders, plus
    ``ratification_required`` and the deterministic notes for the banner.
    """
    state = classify(description, provider, human_gate=_auto_accept)
    entry = build_entry(state, slug=slugify(description), approver=None)
    return {
        "entry": entry,
        "ratification_required": True,
        "deterministic_notes": list(state.get("deterministic_notes", [])),
    }


class ClassifyHandler(SimpleHTTPRequestHandler):
    """Serves web/ statically and answers POST /classify with a live classification."""

    def __init__(self, *args, provider_factory, **kwargs):
        self._provider_factory = provider_factory
        super().__init__(*args, directory=str(WEB_DIR), **kwargs)

    # Keep the demo server quiet-ish but informative.
    def log_message(self, fmt: str, *args) -> None:  # noqa: A003 - stdlib signature
        sys.stderr.write("serve_classify: " + (fmt % args) + "\n")

    def _send_json(self, status: int, payload: dict) -> None:
        body = json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self._cors()
        self.end_headers()
        self.wfile.write(body)

    def _cors(self) -> None:
        # Allow the page opened from file:// (Origin: null) or another port to POST here.
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.send_header("Access-Control-Allow-Methods", "POST, OPTIONS")

    def do_OPTIONS(self) -> None:  # noqa: N802 - stdlib signature
        self.send_response(204)
        self._cors()
        self.end_headers()

    def do_POST(self) -> None:  # noqa: N802 - stdlib signature
        if self.path.split("?", 1)[0] != "/classify":
            self._send_json(404, {"error": "not found"})
            return
        length = int(self.headers.get("Content-Length") or 0)
        if length <= 0 or length > MAX_DESCRIPTION_BYTES:
            self._send_json(400, {"error": "missing or oversized request body"})
            return
        try:
            payload = json.loads(self.rfile.read(length).decode("utf-8"))
            description = str(payload["description"]).strip()
        except (ValueError, KeyError, TypeError):
            self._send_json(400, {"error": 'expected JSON {"description": "..."}'})
            return
        if not description:
            self._send_json(400, {"error": "description must not be empty"})
            return
        try:
            provider = self._provider_factory()
        except Exception as exc:  # provider misconfigured (e.g. no LLM_API_KEY)
            self._send_json(
                503,
                {"error": f"live classification unavailable: {exc}"},
            )
            return
        try:
            result = classify_to_payload(description, provider)
        except Exception as exc:  # a live call failed
            self._send_json(502, {"error": f"classification failed: {exc}"})
            return
        self._send_json(200, result)

    def send_head(self):
        """Serve index.html with the live endpoint injected; everything else verbatim."""
        path = self.path.split("?", 1)[0]
        if path in ("/", "/index.html"):
            return self._send_index()
        return super().send_head()

    def _send_index(self):
        html = (WEB_DIR / "index.html").read_text(encoding="utf-8")
        html = html.replace(ENDPOINT_MARKER, ENDPOINT_INJECTION, 1)
        body = html.encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)
        return None


def _lazy_provider_factory():
    """Build the live provider on first use, caching it. Raises if misconfigured."""
    from dotenv import load_dotenv

    from classifier.provider import provider_from_env

    load_dotenv()  # CLI entry point only — never at import time
    cache: dict[str, LLMProvider] = {}

    def factory() -> LLMProvider:
        if "provider" not in cache:
            cache["provider"] = provider_from_env()
        return cache["provider"]

    return factory


def main(argv: list[str] | None = None) -> int:
    port = int(os.environ.get("PORT", "8000"))
    handler = partial(ClassifyHandler, provider_factory=_lazy_provider_factory())
    server = ThreadingHTTPServer(("127.0.0.1", port), handler)
    print(
        f"serve_classify: serving {WEB_DIR.relative_to(ROOT)}/ and POST /classify at "
        f"http://localhost:{port}/  (Ctrl-C to stop)",
        file=sys.stderr,
    )
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nserve_classify: stopped.", file=sys.stderr)
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
