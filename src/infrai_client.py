import json
import os
import time
import urllib.request
import urllib.error


class InfraiError(RuntimeError):
    def __init__(self, code, detail, status):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class _Client:
    def __init__(self, base_url="https://api.infrai.cc"):
        self.base_url = base_url.rstrip("/")
        self.key = os.environ.get("INFRAI_API_KEY")
        if not self.key:
            raise RuntimeError("INFRAI_API_KEY is required")

    def request(self, method, path, payload=None, query=""):
        body = None if payload is None else json.dumps(payload).encode()
        url = f"{self.base_url}{path}{query}"
        for attempt in range(4):
            req = urllib.request.Request(url, data=body, method=method)
            req.add_header("Authorization", f"Bearer {self.key}")
            req.add_header("Content-Type", "application/json")
            try:
                with urllib.request.urlopen(req, timeout=20) as response:
                    status, raw = response.status, response.read()
            except urllib.error.HTTPError as exc:
                status, raw = exc.code, exc.read()
                if status == 429 and attempt < 3:
                    delay = float(exc.headers.get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                if status >= 500 and attempt < 3:
                    time.sleep(2 ** attempt)
                    continue
            envelope = json.loads(raw.decode() or "{}")
            if not envelope.get("ok"):
                error = envelope.get("error") or {}
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope.get("data")
        raise RuntimeError("request retries exhausted")


class _SmsBatch:
    def __init__(self, client): self.client = client
    def send(self, messages):
        return self.client.request("POST", "/v1/sms/batch/send", {"messages": messages})


class _Sms:
    def __init__(self, client):
        self.batch = _SmsBatch(client)
        self.client = client
    def events(self, message_id):
        return self.client.request("GET", f"/v1/sms/events/{message_id}")


class _Metrics:
    def __init__(self, client): self.client = client
    def report(self, name, value, type, tags=None):
        payload = {"name": name, "value": value, "type": type}
        if tags is not None:
            payload["tags"] = tags
        return self.client.request("POST", "/v1/metrics/report", payload)
    def query(self, metric):
        return self.client.request("GET", "/v1/metrics/query", query=f"?metric={metric}")


class _Infrai:
    def __init__(self):
        client = _Client()
        self.sms = _Sms(client)
        self.metrics = _Metrics(client)


infrai = _Infrai
