# Database Operations Runbook

This document details database administration tasks for the Postgres/RDS instance, including database migrations, failovers, backups, and restores.

---

## 1. Alembic Migrations

The application uses Alembic (via SQLAlchemy) to manage database migrations.

### Applying Migrations (Deploy/Upgrade)

Migrations are run automatically during the CD pipeline or manually on the app server:

1. **Locate Migration Configuration:**
    Verify the `alembic.ini` file is configured with the correct connection string (or via environmental variables such as `DATABASE_URL`).
2. **Run Upgrade to Latest:**

    ```bash
    # Run from the backend directory
    poetry run alembic upgrade head
    ```

3. **Verify Migration Status:**
    Confirm that the database is at the current version:

    ```bash
    poetry run alembic current
    ```

### Rolling Back a Migration (Downgrade)

If a migration fails or introduces performance bottlenecks:

1. **Revert to the Previous Version:**

    ```bash
    # Downgrade by 1 step
    poetry run alembic downgrade -1
    ```

    *Or target a specific revision hash:*

    ```bash
    poetry run alembic downgrade <revision_hash>
    ```

---

## 2. Database Failovers

AWS RDS Multi-AZ deployments handle database failures automatically. However, manual failovers can be triggered for maintenance or testing.

### Automated RDS Failover (Multi-AZ)

When the primary DB instance goes offline, RDS automatically switches to the standby replica in another Availability Zone. This typically takes 60–120 seconds. The DB endpoint CNAME automatically updates to point to the new primary.

### Manual RDS Failover

To initiate a manual failover to test high availability:

1. **Trigger Failover via AWS CLI:**

    ```bash
    aws rds reboot-db-instance \
      --db-instance-identifier production-postgres-db \
      --force-failover
    ```

2. **Monitor the Failover:**
    Check RDS status during reboot:

    ```bash
    aws rds describe-db-instances \
      --db-instance-identifier production-postgres-db \
      --query 'DBInstances[0].DBInstanceStatus'
    ```

    *Status will transition to `rebooting` then back to `available` once the standby has assumed the primary role.*

---

## 3. Backups and Restores

### Backup Strategy

* **Automated Backups:** Enabled on RDS with a 30-day retention period. Daily snapshots are taken automatically.
* **Transaction Logs:** Uploaded to Amazon S3 every 5 minutes, allowing Point-In-Time Restore (PITR).
* **Manual Snapshots:** Taken before major deployments or database upgrades.

### Creating a Manual Snapshot

Before running risk-prone migrations or structural DB changes:

```bash
aws rds create-db-snapshot \
  --db-instance-identifier production-postgres-db \
  --db-snapshot-identifier pre-deployment-snapshot-$(date +%F-%H%M)
```

### Database Restore Procedures

#### Option A: Point-in-Time Restore (PITR)

Restores the database to a specific second within the retention period (creates a *new* DB instance):

```bash
aws rds restore-db-instance-to-point-in-time \
  --source-db-instance-identifier production-postgres-db \
  --target-db-instance-identifier production-postgres-db-restored \
  --restore-time 2026-06-19T10:15:00Z
```

#### Option B: Restore from Snapshot

Creates a new DB instance from an existing snapshot:

```bash
aws rds restore-db-instance-from-db-snapshot \
  --db-instance-identifier production-postgres-db-restored \
  --db-snapshot-identifier pre-deployment-snapshot-2026-06-19-1100
```

#### Option C: Local/Manual pg_dump & pg_restore (Emergency/Development)

Export database schema and data:

```bash
pg_dump -H production-db-endpoint -U dbuser -d dbname -F c -b -v -f backup.dump
```

Restore the database schema and data:

```bash
pg_restore -H production-db-endpoint -U dbuser -d dbname -v backup.dump
```
