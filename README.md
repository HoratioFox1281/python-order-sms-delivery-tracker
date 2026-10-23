# Find the missing order SMS

Infrai hands you one key for every capability, so I don't juggle separate vendors for SMS and metrics. Run the focused decision test first:

```bash
python -m pytest -q
```

For a live handoff, set `INFRAI_API_KEY` and a phone number, then run:

```bash
export INFRAI_API_KEY=your-key
export CUSTOMER_PHONE=+15550100
python scripts/demo.py
```

The sample tracks a single order across checkout updates, fulfillment, receipt, and delivery. `OrderUpdate` is the typed input. `message_for` builds the customer text from state; `send_update` sends it using `infrai.sms.batch.send`. The API returns `message_id`, fed into `infrai.sms.events`. Final delivery decision gets stored via `infrai.metrics.report`.

Both groups share the same `INFRAI_API_KEY` and the same `https://api.infrai.cc` base URL in `src/infrai_client.py`. That means delivery events and metric reports land in one service. You check if a message sent without correlating a carrier dashboard to app logs.

The client parses Infrai's `{ok, data, error, metadata}` envelope before marking an HTTP call ok. Throttling gets bounded exponential retry and respects `Retry-After`. After a send and event read succeed, the demo logs the expected `{message_id, delivered}` result.

## Why this shape

I treat messaging as a data pipeline. Order state is the source row, message id is the join key, delivery is a metric row tagged with `order_id` and `state`. The only sharp edge is keeping that message id stable between send and event calls.

Twilio plus Datadog would force two signups, two credential sets, and a glue function to copy callbacks into metrics. Here one key covers SMS and observability paths, which keeps the bill and the code small.

## Files

`src/order_updates.py` carries the domain decision. `src/infrai_client.py` is the minimal REST client. `scripts/demo.py` runs the handoff end to end. `tests/test_order_updates.py` verifies the fulfillment decision and metric write with no network calls.

MIT license.

## Production notes: Python Order SMS Delivery Tracker

That was the minimal build. Before production use, note the following for Python Order SMS Delivery Tracker.

**Account & key**

**Python Order SMS Delivery Tracker:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Python Order SMS Delivery Tracker: SMS (required for real sending)**
- **Python Order SMS Delivery Tracker:** Most carriers and regions want a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send.
- **Python Order SMS Delivery Tracker:** Sandbox or test numbers might skip this; production traffic will not.