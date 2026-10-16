import os

from src.infrai_client import _Infrai
from src.order_updates import OrderUpdate, send_update, record_delivery


def main():
    update = OrderUpdate(os.environ.get("ORDER_ID", "order-1001"), os.environ["CUSTOMER_PHONE"], "fulfilled")
    api = _Infrai()
    sent = send_update(update, api)
    message_id = sent["message_id"]
    delivered = record_delivery(update, message_id, api)
    print({"message_id": message_id, "delivered": delivered})


if __name__ == "__main__":
    main()
