import logging
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from render_sdk import Render

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "job-to-workflow")
render_client = Render()


class Handler(BaseHTTPRequestHandler):
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

        def send_event(data):
            msg = f"data: {data}\n\n"
            encoded = msg.encode()
            self.wfile.write(f"{len(encoded):x}\r\n".encode())
            self.wfile.write(encoded)
            self.wfile.write(b"\r\n")
            self.wfile.flush()

        for event in render_client.workflows.task_run_events([started.id]):
            logger.info("sse event run_id=%s status=%s", event.id, event.status)
            send_event(f"status: {event.status}")
            if event.status in ("completed", "failed", "canceled"):
                break

        details = render_client.workflows.get_task_run(started.id)
        logger.info("task done run_id=%s error=%s results=%s", started.id, details.error, details.results)
        if details.error:
            send_event(f"error: {details.error}")
        else:
            send_event(str(details.results))

        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


if __name__ == "__main__":
    HTTPServer(("", 8080), Handler).serve_forever()
