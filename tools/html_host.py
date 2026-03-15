import os
import socket
import subprocess
import sys
from pathlib import Path

from pyngrok import conf, ngrok
from agno.tools.toolkit import Toolkit


GENERATED_DIR = Path(__file__).parent.parent / "generated_sites"
GENERATED_DIR.mkdir(exist_ok=True)

# Track state
_server_proc: subprocess.Popen | None = None
_server_port: int | None = None
_ngrok_url: str | None = None


def _find_free_port(start: int = 8080) -> int:
    """Find a free port starting from `start`."""
    port = start
    while port < 9000:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            if s.connect_ex(("localhost", port)) != 0:
                return port
        port += 1
    raise RuntimeError("No free port found in range 8080-9000")


def _ensure_server() -> tuple[int, str]:
    """Ensure the HTTP server and ngrok tunnel are running. Returns (port, public_url)."""
    global _server_proc, _server_port, _ngrok_url

    # Start local server if not running
    if _server_proc is None or _server_proc.poll() is not None:
        _server_port = _find_free_port()
        _server_proc = subprocess.Popen(
            [sys.executable, "-m", "http.server", str(_server_port)],
            cwd=str(GENERATED_DIR),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

    # Start ngrok tunnel if not running
    if _ngrok_url is None:
        auth_token = os.environ.get("NGROK_AUTH_TOKEN")
        if auth_token:
            conf.get_default().auth_token = auth_token
        tunnel = ngrok.connect(_server_port, "http")
        _ngrok_url = tunnel.public_url

    return _server_port, _ngrok_url


class HtmlHostToolkit(Toolkit):
    def __init__(self):
        super().__init__(
            name="html_host",
            tools=[self.save_and_host, self.list_hosted_pages],
        )

    def save_and_host(self, filename: str, html_content: str) -> str:
        """Save an HTML file and host it on a public URL via ngrok.

        Args:
            filename: Name for the HTML file (without .html extension).
            html_content: The complete HTML content to save.

        Returns:
            The public URL where the page is hosted.
        """
        safe_name = filename.strip().replace(" ", "-").lower()
        if not safe_name.endswith(".html"):
            safe_name += ".html"

        filepath = GENERATED_DIR / safe_name
        filepath.write_text(html_content, encoding="utf-8")

        port, public_url = _ensure_server()
        return f"{public_url}/{safe_name}"

    def list_hosted_pages(self) -> str:
        """List all generated HTML pages and their public URLs.

        Returns:
            A formatted list of all hosted pages with URLs.
        """
        files = list(GENERATED_DIR.glob("*.html"))
        if not files:
            return "No pages have been generated yet."

        if _ngrok_url is None:
            return "Pages exist but no server is running. Generate a new page to start the server."

        lines = ["Hosted pages:"]
        for f in sorted(files):
            lines.append(f"  - {_ngrok_url}/{f.name}")
        return "\n".join(lines)
