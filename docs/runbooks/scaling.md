# Auto-Scaling & Cost Optimization Runbook

This document details the auto-scaling rules, triggers, policies, and cost projections for AWS Fargate compute tasks and RDS database instances.

---

## 1. Fargate Auto-Scaling Rules

The API and worker container services run on AWS Fargate. Autoscaling is managed via AWS Application Auto-Scaling.

### Scaling Target Limits

* **Minimum Tasks:** 2 (High Availability across two Availability Zones)
* **Maximum Tasks:** 20 (Protects downstream databases and services from overload)

### Auto-Scaling Policies & Triggers

#### A. Target Tracking Scaling (CPU)

* **Metric:** `ECSServiceAverageCPUUtilization`
* **Target Value:** 70%
* **Cooldown Period:** Scale-Out: 60s, Scale-In: 300s
* **Behavior:** Scale tasks up rapidly when average CPU exceeds 70%, and slowly scale tasks down when load decreases.

#### B. Target Tracking Scaling (Memory)

* **Metric:** `ECSServiceAverageMemoryUtilization`
* **Target Value:** 80%
* **Cooldown Period:** Scale-Out: 60s, Scale-In: 300s

#### C. Request Count Auto-Scaling (ALB)

* **Metric:** `ALBRequestCountPerTarget`
* **Target Value:** 1000 requests per task per minute

---

## 2. RDS Auto-Scaling & Storage Scaling

Amazon RDS automatically scales storage and computes read replicas based on load.

### Storage Auto-Scaling

* **Trigger:** Available space falls below 10% of allocated storage.
* **Increment:** 10% of current allocated storage or 10 GB (whichever is greater).
* **Max Storage Limit:** Configured to 500 GB to prevent unbounded cost growth.

### RDS Read Replicas (Optional/Scale-out)

If database CPU utilization consistently exceeds 75% due to read queries, deploy an RDS Read Replica via Terraform:

1. Increase the `read_replica_count` variable in `variables.tf` to `1`.
2. Apply the configuration change to direct query traffic to the read replica.

---

## 3. Cost Analysis and Projections

Estimated operational costs based on Fargate and RDS pricing (US East 1 region).

### Compute: AWS Fargate Tasks (0.5 vCPU, 1 GB RAM per Task)

* **Base Load (2 Tasks constantly running):**
  * 0.5 vCPU *2* $0.04048/hour = $0.04048/hour
  * 1 GB RAM *2* $0.004445/hour = $0.00889/hour
  * **Monthly Base Compute Cost:** ~$36.00 / month
* **Peak Load (10 Tasks running 4 hours/day, 2 Tasks otherwise):**
  * **Monthly Peak Compute Cost:** ~$96.00 / month

### Database: Amazon RDS PostgreSQL (db.m6g.large - Multi-AZ)

* **Instance Cost:** $0.152 / hour (Single-AZ) -> $0.304 / hour (Multi-AZ)
  * **Monthly Instance Cost:** ~$220.00 / month
* **Storage (100 GB GP3 Storage):** $0.115 / GB-month
  * **Monthly Storage Cost:** $11.50 / month
* **Backups:** First 100% of storage backup is free, additional snapshots are $0.095 / GB-month.

### Total MVP Infrastructure Cost Run-Rate

* **Fargate Compute:** ~$50 - $100 / month
* **RDS Database:** ~$235 / month
* **Cache (Valkey Serverless / Redis):** ~$30 / month
* **ALB + Networking:** ~$40 / month
* **Total Estimated MVP Cost:** **~$350 - $400 / month**
