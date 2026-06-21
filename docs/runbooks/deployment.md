# Deployment Runbook

This document details the production container update procedure, automated/manual smoke testing, and rollback operations on AWS Elastic Container Service (ECS).

---

## 1. Production Container Updates

Production deployments utilize AWS ECS with rolling updates (or blue/green via AWS CodeDeploy if configured). Below is the rolling update deployment procedure.

### Prerequisites

* AWS CLI installed and configured with appropriate permissions.
* Access to the production AWS account.
* Docker image built and pushed to AWS ECR.

### Step-by-Step Deployment

1. **Retrieve Docker Image Tag:**
    Ensure you have the target image tag from the CI/CD pipeline (e.g., `git-sha-abcdef`).
2. **Register a New ECS Task Definition:**
    Retrieve the current task definition, update the container image tag, and register the new version:

    ```bash
    # Get current task definition JSON (strip metadata)
    aws ecs describe-task-definition --task-definition production-api-task \
      --query 'taskDefinition' > task-def.json

    # Update image tag inside task-def.json (manually or via jq)
    # E.g. using jq:
    # jq '.containerDefinitions[0].image = "123456789012.dkr.ecr.us-east-1.amazonaws.com/restaurant-platform-api:git-sha-abcdef"' task-def.json > new-task-def.json

    # Register the new task definition
    aws ecs register-task-definition --cli-input-json file://new-task-def.json
    ```

3. **Update ECS Service:**
    Deploy the new task definition revision:

    ```bash
    aws ecs update-service \
      --cluster production-cluster \
      --service production-api-service \
      --task-definition production-api-task:REV_NUMBER \
      --force-new-deployment
    ```

    *Replace `REV_NUMBER` with the newly registered revision number.*

---

## 2. Smoke Tests

Once ECS starts spinning up the new tasks, run smoke tests immediately to confirm system stability before old containers are terminated.

### Automated Smoke Tests

Run the health-check suite from the repository or trigger a curl command:

```bash
# 1. Main API Gateway health endpoint
curl -f -i https://api.production.restaurant-platform.com/health

# 2. Verify JSON structure and DB/Cache connectivity status
# The response should return HTTP 200 and:
# {"status":"healthy","database":"connected","cache":"connected"}
```

### Manual Smoke Test Checklist

Perform these checks via the application front-end or Postman:

1. **Authentication:** Sign in and verify JWT token acquisition.
2. **Browsing:** Load the restaurant listing and search for active locations.
3. **Cart & Customization:** Add a customized menu item to the cart.
4. **Checkout:** Create a pending checkout order (using test payment credentials if safe, or checking mock payment gateways in staging).
5. **Tracking:** Query the active order status to verify maps tracking endpoint works.

---

## 3. ECS Rollbacks

If smoke tests fail or alarms are triggered, roll back the deployment immediately.

### Automatic Rollbacks (ECS Service Alarms)

If CloudWatch Alarm threshold is breached during deployment (e.g., Target Group 5XX errors or ECS Task crashes), ECS will automatically roll back to the previous stable task definition revision if "Deployment Circuit Breaker" is enabled.

### Manual Rollback Procedure

If auto-rollback is not triggered but issues are detected:

1. **Identify the Last Known Stable Task Definition Revision:**
    Check AWS ECS Console or run:

    ```bash
    aws ecs list-task-definitions --family-prefix production-api-task --sort DESC
    ```

2. **Force Deployment to the Stable Revision:**

    ```bash
    aws ecs update-service \
      --cluster production-cluster \
      --service production-api-service \
      --task-definition production-api-task:STABLE_REV_NUMBER \
      --force-new-deployment
    ```

3. **Confirm Rollback Completion:**
    Monitor the service deployments until the old deployment is inactive:

    ```bash
    aws ecs describe-services --cluster production-cluster --services production-api-service \
      --query 'services[0].deployments'
    ```

4. **Verify Application Health:**
    Re-run the health-check suite to confirm stability.
