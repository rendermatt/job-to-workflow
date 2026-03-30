import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from render_sdk import Render

WORKFLOW_SLUG = os.environ.get("WORKFLOW_SLUG", "job-to-workflow")
render_client = Render()


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        digits = [int(c) for c in self.path if c.isdigit()]

        started = render_client.workflows.start_task(
            f"{WORKFLOW_SLUG}/calculate_and_process",
            digits,
        )

        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.send_header("Transfer-Encoding", "chunked")
        self.end_headers()

        def write_chunk(text):
            encoded = text.encode()
            self.wfile.write(f"{len(encoded):x}\r\n".encode())
            self.wfile.write(encoded)
            self.wfile.write(b"\r\n")
            self.wfile.flush()

        for event in render_client.workflows.task_run_events([started.id]):
            write_chunk(f"status: {event.status}\n")
            if event.status in ("completed", "failed", "canceled"):
                break

        details = render_client.workflows.get_task_run(started.id)
        if details.error:
            write_chunk(f"error: {details.error}\n")
        else:
            write_chunk(str(details.results) + "\n")

        self.wfile.write(b"0\r\n\r\n")
        self.wfile.flush()


if __name__ == "__main__":
    HTTPServer(("", 8080), Handler).serve_forever()
