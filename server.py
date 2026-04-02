import json
import logging
import os
import time
from http.server import HTTPServer, BaseHTTPRequestHandler
from render_sdk import Render

_handler = logging.StreamHandler()
_handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
logging.basicConfig(level=logging.INFO, handlers=[_handler], force=True)
logging.root.handlers[0].stream.reconfigure(line_buffering=True)
logger = logging.getLogger(__name__)

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "job-to-workflow")
POLL_INTERVAL = float(os.environ.get("POLL_INTERVAL", "2"))
render_client = Render()


def to_jsonable(obj):
    if hasattr(obj, "model_dump"):
        return obj.model_dump()
    if hasattr(obj, "__dict__"):
        return vars(obj)
    return str(obj)


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def do_GET(self):
        digits = [int(c) for c in self.path if c.isdigit()]
        logger.info("request path=%s digits=%s", self.path, digits)

        started = render_client.workflows.start_task(
            f"{WORKFLOW_SLUG}/calculate_and_process",
            digits,
        )
        logger.info("task started run_id=%s", started.id)

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        def send_event(event, data):
            # SSE supports multi-line data via repeated "data:" prefixes
            data_lines = "\n".join(f"data: {line}" for line in data.splitlines())
            msg = f"event: {event}\n{data_lines}\n\n"
            encoded = msg.encode()
            self.wfile.write(f"{len(encoded):x}\r\n".encode())
            self.wfile.write(encoded)
            self.wfile.write(b"\r\n")
            self.wfile.flush()

        last_status = None
        while True:
            details = render_client.workflows.get_task_run(started.id)
            status = details.status
            if status != last_status:
                logger.info("poll run_id=%s status=%s", started.id, status)
                last_status = status
                send_event("status", status)
            if status in ("completed", "failed", "canceled"):
                break
            time.sleep(POLL_INTERVAL)

        if details.error:
            logger.info("task error run_id=%s error=%s", started.id, details.error)
            send_event("error", details.error)
        else:
            logger.info("task done run_id=%s results=%s", started.id, details.results)
            send_event("result", json.dumps(to_jsonable(details), indent=2, default=str))

        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


if __name__ == "__main__":
    HTTPServer(("", 8080), Handler).serve_forever()
