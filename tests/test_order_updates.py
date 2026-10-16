from src.order_updates import OrderUpdate, message_for, send_update, record_delivery
from src.infrai_client import _Metrics


class FakeSms:
    def __init__(self): self.batch = self; self.calls = []
    def send(self, messages): self.calls.append(messages); return {"message_id": "m-1"}
    def events(self, message_id): return [{"status": "delivered", "message_id": message_id}]


class FakeMetrics:
    def __init__(self): self.calls = []
    def report(self, *args): self.calls.append(args); return {"accepted": True}


class FakeApi:
    def __init__(self): self.sms, self.metrics = FakeSms(), FakeMetrics()


def test_fulfillment_is_delivered_and_recorded():
    api = FakeApi()
    update = OrderUpdate("o-7", "+15550100", "fulfilled")
    assert message_for(update) == "Order o-7 has shipped."
    sent = send_update(update, api)
    assert sent["message_id"] == "m-1"
    assert record_delivery(update, sent["message_id"], api) is True
    assert api.metrics.calls[0][0] == "order_sms_delivered"
    assert api.metrics.calls[0][2] == "counter"


def test_metrics_report_uses_contract_fields():
    class Client:
        def request(self, method, path, payload):
            assert (method, path) == ("POST", "/v1/metrics/report")
            assert payload == {"name": "order_sms_delivered", "value": 1, "type": "counter", "tags": {"state": "fulfilled"}}

    _Metrics(Client()).report("order_sms_delivered", 1, "counter", {"state": "fulfilled"})
