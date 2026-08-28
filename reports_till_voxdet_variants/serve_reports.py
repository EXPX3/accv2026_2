#!/usr/bin/env python3
"""Serve this portable report archive on the local host."""

from __future__ import annotations

import argparse
from functools import partial
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
import threading
import webbrowser


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1", help="bind address (default: localhost only)")
    parser.add_argument("--port", type=int, default=8770)
    parser.add_argument("--open", action="store_true", help="open the system browser")
    args = parser.parse_args()

    root = Path(__file__).resolve().parent
    handler = partial(SimpleHTTPRequestHandler, directory=str(root))
    server = ThreadingHTTPServer((args.host, args.port), handler)
    display_host = "127.0.0.1" if args.host in {"0.0.0.0", "::"} else args.host
    url = f"http://{display_host}:{server.server_port}/"
    print(f"Serving {root}")
    print(f"Open {url}")
    print("Press Ctrl-C to stop.")
    if args.open:
        threading.Timer(0.5, webbrowser.open, args=(url,)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nStopped.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
