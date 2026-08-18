# 🛠️ Infrastructure as Code (IaC) — EduPathway AI

This directory contains production Terraform definitions to provision all Google Cloud resources required by **EduPathway AI**:

- **Google Cloud Vertex AI** (Gemini 2.5 Flash / Pro model APIs)
- **Google Cloud Sensitive Data Protection (DLP v2)** (PII Inspection & De-identification)
- **Cloud Storage** (Artifact buckets for lesson plans and student profile backups)
- **Cloud Trace & Logging** (Distributed OpenTelemetry telemetry & JSON trace sink)
- **IAM & Service Accounts** (Least-privilege agent runtime execution identity)

---

## 🚀 How to Provision Infrastructure

### 1. Initialize Terraform
```bash
cd terraform
terraform init
```

### 2. Plan Infrastructure
```bash
terraform plan -var="project_id=ai-in-5-days-dyl-temp" -var="region=us-central1"
```

### 3. Apply Infrastructure
```bash
terraform apply -var="project_id=ai-in-5-days-dyl-temp" -var="region=us-central1" -auto-approve
```
