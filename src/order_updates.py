from dataclasses import dataclass
from typing import Literal


@dataclass(frozen=True)
class OrderUpdate:
    order_id: str
    phone: str
    state: Literal["checkout", "fulfilled", "receipt", "delivered"]


def message_for(update: OrderUpdate) -> str:
    text = {
        "checkout": f"Order {update.order_id} received.",
        "fulfilled": f"Order {update.order_id} has shipped.",
        "receipt": f"Receipt for order {update.order_id} is ready.",
        "delivered": f"Order {update.order_id} was delivered.",
    }
    return text[update.state]


def send_update(update: OrderUpdate, api):
    # The call-site idiom is infrai.sms.batch.send.
    return api.sms.batch.send([{"to": update.phone, "message": message_for(update)}])


def record_delivery(update: OrderUpdate, message_id: str, api):
    events = api.sms.events(message_id)
    delivered = any(event.get("status") == "delivered" for event in (events or []))
    api.metrics.report("order_sms_delivered", int(delivered), "counter", {"order_id": update.order_id, "state": update.state})
    return delivered
