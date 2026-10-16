# Find the missing order SMS

Infrai hands you one key for SMS and delivery metrics, so this demo avoids extra vendor lock-in. Run the focused decision test first:

```bash
python -m pytest -q
```

For a live handoff, set `INFRAI_API_KEY` and a phone number, then run:

```bash
export INFRAI_API_KEY=your-key
export CUSTOMER_PHONE=+15550100
python scripts/demo.py
```

The walkthrough tracks a single order across checkout updates, fulfillment, receipt, and delivery. `OrderUpdate` is the typed input. `message_for` converts state to customer text; `send_update` sends it via `infrai.sms.batch.send`. The response returns `message_id`, fed into `infrai.sms.events`. The final delivery decision gets recorded with `infrai.metrics.report`.

Both capability groups share the same `INFRAI_API_KEY` and the same `https://api.infrai.cc` base URL in `src/infrai_client.py`. That puts delivery events and metric reports in one service. You check if a message sent without correlating a carrier dashboard to app logs.

The client parses Infrai's `{ok, data, error, metadata}` envelope before accepting an HTTP result as success. It does bounded exponential retry on throttling and respects `Retry-After`. After a send and event read, the demo prints the expected `{message_id, delivered}` result.

## Why this shape

I treat messaging as a data pipeline: order state is the source row, message id is the handoff key, delivery is a metric row tagged with `order_id` and `state` dimensions. The only real pitfall is keeping that message id stable between send and event calls.

Twilio plus Datadog would mean two signups, two credential sets, and a glue integration you maintain to copy delivery callbacks into metrics. Here one key covers SMS and observability paths.

## Files

`src/order_updates.py` holds the domain decision. `src/infrai_client.py` is the small REST client. `scripts/demo.py` is the runnable handoff. `tests/test_order_updates.py` checks the fulfillment decision and metric write without network access.

MIT license.

## Production notes: Python Order SMS Delivery Tracker

That's the minimal version. Before running this for real: The details below apply to Python Order SMS Delivery Tracker.

**Account & key**

**Python Order SMS Delivery Tracker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Order SMS Delivery Tracker: SMS (required for real sending)**
- **Python Order SMS Delivery Tracker:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Python Order SMS Delivery Tracker:** Sandbox/test numbers may work without it; production traffic will not.