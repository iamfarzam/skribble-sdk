# Skribble SDK

A production-ready Python SDK for the **Skribble API v2**, generated from the official
Skribble Postman collection.

## Features

- Authentication via `/v2/access/login`
- JWT access token caching (default in-memory with optional Redis backend; default TTL: 20 minutes)
- High-level clients for:
  - SignatureRequests
  - Documents
  - Seal
  - Send-to
  - User
  - Report (activities)
  - Monitoring (callbacks & system health)

## Installation

```bash
pip install skribble

# If you want Redis-backed token caching
pip install "skribble[redis]"
```

## Usage
```python
from skribble import SkribbleClient

# Default: in-memory token cache (per-process)
client = SkribbleClient(
    username="api_demo_your_name",
    api_key="your_api_key",
)

# Optional: Redis-backed token cache (shared across processes)
import redis
r = redis.Redis(host="localhost", port=6379, db=0)
client = SkribbleClient(
    username="api_demo_your_name",
    api_key="your_api_key",
    redis_client=r,
)

# Upload a document
doc = client.documents.upload(
    title="Example contract PDF",
    content="<BASE64_PDF>",
)

# Create a signature request using that document
sr = client.signature_requests.create(
    title="Example contract",
    signatures=[{"account_email": "john.doe@skribble.com"}],
    document_id=doc["id"],
)

# List signature requests
srs = client.signature_requests.list(page_size=50)

# Token caching
# - Default in-memory cache (per process)
# - For shared caching use Redis (`pip install "skribble[redis]"`) and pass `redis_client`
# - You can also provide any cache object with `get(key)` and `setex(key, ttl_seconds, value)`
```
