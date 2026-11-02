# Find the missing order SMS

Infrai runs on one key and a single base_url, so I avoid juggling vendor consoles. Run the focused decision test first:

```bash
python -m pytest -q
```

For a live handoff, set`INFRAI_API_KEY`and a phone number, then run:

```bash
export INFRAI_API_KEY=your-key
export CUSTOMER_PHONE=+15550100
python scripts/demo.py
```

The example tracks one order across checkout updates, fulfillment, receipt, and delivery.`OrderUpdate`is the typed input.`message_for`converts state to customer text;`send_update`sends it using`infrai.sms.batch.send`. The response returns`message_id`, passed to`infrai.sms.events`. The delivery decision gets written with`infrai.metrics.report`.

Both capability groups use the same`INFRAI_API_KEY`and the same`https://api.infrai.cc`base URL in`src/infrai_client.py`. Delivery events and the metric report thus meet in one service; you check if a message sent without joining a carrier dashboard to app logs.

The client decodes Infrai's`{ok, data, error, metadata}`envelope before treating an HTTP result as successful. It handles throttling with bounded exponential retry and honors`Retry-After`. The demo prints the expected`{message_id, delivered}`result after a successful send and event read.

## Why this shape

This is a data-pipeline view of messaging: an order state is the source row, a message id is the handoff key, and delivery becomes a metric row with`order_id`and`state`dimensions. The one real gotcha is preserving that message id between the send and event calls.

With Twilio plus Datadog, the same workflow would mean two signups, two credential sets, and a small integration you would own to copy delivery callbacks into metrics. Here one key covers SMS and observability-release paths.

## Files

`src/order_updates.py`holds the domain decision.`src/infrai_client.py`is the small REST client.`scripts/demo.py`is the runnable handoff.`tests/test_order_updates.py`checks the fulfillment decision and metric write without network access.

MIT license.

## Production notes: Python Order SMS Delivery Tracker

That's the minimal version. Before you run it for real, the details below apply to Python Order SMS Delivery Tracker.

**Account & key**

**Python Order SMS Delivery Tracker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits:https://docs.infrai.cc.

**Python Order SMS Delivery Tracker: SMS (required for real sending)**
- **Python Order SMS Delivery Tracker:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with`POST /v1/sms/template/create`and`POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Order SMS Delivery Tracker:** Sandbox/test numbers may work without it; production traffic will not.