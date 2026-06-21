# Common Issues & Troubleshooting Runbook

This document outlines standard diagnostic procedures and remediation steps for Valkey cache outages, database connection pool exhaustion, and payment checkout timeouts.

---

## 1. Valkey Cache Outages

### Symptoms

* API logs showing `ConnectionError` or `TimeoutError` connecting to Valkey/Redis.
* Increased response times (latency spikes) on endpoints that rely heavily on caching.
* Increased CPU utilization on the RDS primary database due to cache-miss traffic.

### Diagnostics

1. **Check Valkey Cluster Status:**

    ```bash
    aws elasticache describe-cache-clusters --cache-cluster-id production-valkey-cache
    ```

2. **Verify Network Connectivity (from API/Worker tasks):**
    Ensure the security groups allow traffic on port `6379`.
3. **Inspect Memory/Eviction Metrics:**
    Check if the cache is full and evicting active keys (look for `Evictions` metric in CloudWatch).

### Fixes & Mitigation

* **Reboot Valkey Instance:**
    If the cluster is unresponsive, reboot via CLI:

    ```bash
    aws elasticache reboot-cache-cluster \
      --cache-cluster-id production-valkey-cache \
      --nodes-to-reboot "0001"
    ```

* **Increase Cache Size (Scale-up):**
    If the cache is running out of memory, change the node type in `variables.tf` and apply Terraform:

    ```hcl
    cache_node_type = "cache.t4g.medium" # Upgraded from cache.t4g.micro
    ```

* **Bypass Valkey (Emergency Rollout):**
    If Valkey is dead and cannot be recovered immediately, set the environment variable `DISABLE_CACHE=true` in the ECS task definition to route all traffic directly to PostgreSQL.

---

## 2. Database Connection Pool Exhaustion

### Symptoms

* API returns HTTP 500 errors.
* Backend logs contain `QueuePool limit of size <N> overflow <M> reached, connection timed out`.
* Application tasks crash due to DB connection acquisition timeouts.

### Diagnostics

1. **Check Active PostgreSQL Connections:**
    Connect to PostgreSQL and query active backends:

    ```sql
    SELECT count(*), state FROM pg_stat_activity GROUP BY state;
    ```

2. **Check Max Connections Limit:**

    ```sql
    SHOW max_connections;
    ```

### Fixes & Mitigation

* **Tune SQLAlchemy Pool Settings:**
    Increase the connection pool size and overflow limits in the application's environment configuration:

    ```ini
    DB_POOL_SIZE=20          # Increase from default (e.g. 5 or 10)
    DB_MAX_OVERFLOW=10      # Increase allowed transient connections
    DB_POOL_TIMEOUT=30      # Timeout (seconds) to wait for a connection
    ```

* **Deploy pgBouncer (Connection Pooler):**
    If connection counts scale linearly with ECS tasks and exceed database capacity, verify that RDS Proxy is enabled or deploy pgBouncer to pool client connections.
* **Terminate Idle Connections:**
    Kill long-running idle transactions to free up slots:

    ```sql
    SELECT pg_terminate_backend(pid) 
    FROM pg_stat_activity 
    WHERE state = 'idle in transaction' 
      AND state_change < current_timestamp - INTERVAL '5 minutes';
    ```

---

## 3. Payment Checkout Timeouts

### Symptoms

* Users report checkout transactions failing mid-process.
* API logs indicate connection/read timeouts when communicating with external payment gateways (Stripe, Adyen, etc.).
* Webhook deliveries from payment processors are missing or delayed.

### Diagnostics

1. **Check Payment Provider Status:**
    Verify if the external payment provider (e.g., Stripe Status Page) is experiencing an outage.
2. **Verify Network Outbound Config:**
    Ensure ECS tasks running in private subnets have internet routing via active NAT Gateways.
3. **Inspect Webhook Endpoint Health:**
    Verify HTTP logs for POST requests to `/api/v1/payments/webhook`. Look for 502/504 errors.

### Fixes & Mitigation

* **Implement Retry with Exponential Backoff:**
    Ensure the payment service wraps API requests in idempotent retry blocks.
* **Process Payments Asynchronously:**
    If synchronous checkout times out, switch to an asynchronous flow:
    1. Mark order as `pending_payment`.
    2. Return control to the user.
    3. Process the payment in a Celery/Huey worker.
    4. Update order status once the payment processor webhook returns success/failure.
* **Disable/Enable Idempotency Keys:**
    Verify that every payment request sends a unique `Idempotency-Key` header. This prevents double-charging users during retry loops.
