# RAGFlow Deployment Guide

**Guide for deploying RAGFlow using Helm on Kubernetes**

## Overview

This guide covers the essential steps to deploy RAGFlow on Kubernetes using Helm charts. The deployment includes:
- External MySQL database configuration
- Service credentials and password management  
- Admin panel setup
- OpenID Connect (OIDC) authentication
- Production-ready security configurations

**Prerequisites**:
- Kubernetes cluster (1.24+)
- Helm 3.0+
- External MySQL database (Cloud SQL, managed service, or self-hosted)
- Valid domain name for ingress
- OIDC provider (Keycloak, Auth0, etc.) for SSO

## Table of Contents

1. [Prepare External MySQL](#prepare-external-mysql)
2. [Generate Passwords & Update values.yaml](#generate-passwords--update-valuesyaml)
3. [Admin Panel Configuration](#admin-panel-configuration)
4. [OIDC Configuration](#oidc-configuration)
5. [Default Models Configuration](#default-models-configuration)
6. [Verification](#verification)
7. [Configuration Reference](#configuration-reference)
8. [Further Improvements & Production Considerations](#further-improvements--production-considerations)

---

## Prepare External MySQL

RAGFlow requires an external MySQL database. Create the database and user using the Cloud SQL console or the following SQL commands:

```sql
CREATE DATABASE rag_flow CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'ragflow'@'%' IDENTIFIED BY '<YOUR_SECURE_PASSWORD>';
GRANT ALL ON rag_flow.* TO 'ragflow'@'%';
FLUSH PRIVILEGES;
```

---

## Generate Passwords & Update values.yaml

Replace placeholders in `values.yaml` for non-sensitive configuration. For sensitive data, create Kubernetes Secrets separately:

**1. Update values.yaml with non-sensitive configuration:**
```yaml
env:
  # External MySQL (non-sensitive)
  MYSQL_HOST: "<cloud-sql-ip-or-hostname>"                   
  MYSQL_USER: "ragflow"
  MYSQL_PORT: "3306"
  # Sensitive values will be loaded from secrets

# MySQL disabled (using external Cloud SQL)
mysql:
  enabled: false

# Enable ingress for external access
ingress:
  enabled: true
  host: "<your-domain.com>"
  tls:
    enabled: true
    certIssuer: "letsencrypt-prod"  # Or your certificate issuer
```

**2. Create Kubernetes Secrets for sensitive data:**
```bash
# Generate strong passwords
MYSQL_PASSWORD=$(openssl rand -base64 32)
ELASTIC_PASSWORD=$(openssl rand -base64 32)
REDIS_PASSWORD=$(openssl rand -base64 32)
MINIO_PASSWORD=$(openssl rand -base64 32)
RAGFLOW_SECRET_KEY=$(openssl rand -base64 48)

# Create separate secrets for better security isolation
kubectl create secret generic ragflow-mysql \
  --from-literal=MYSQL_PASSWORD="$MYSQL_PASSWORD" \
  -n ragflow

kubectl create secret generic ragflow-elastic \
  --from-literal=ELASTIC_PASSWORD="$ELASTIC_PASSWORD" \
  -n ragflow

kubectl create secret generic ragflow-redis \
  --from-literal=REDIS_PASSWORD="$REDIS_PASSWORD" \
  -n ragflow

kubectl create secret generic ragflow-minio \
  --from-literal=MINIO_PASSWORD="$MINIO_PASSWORD" \
  -n ragflow

kubectl create secret generic ragflow-app \
  --from-literal=RAGFLOW_SECRET_KEY="$RAGFLOW_SECRET_KEY" \
  -n ragflow

# Alternative: For enhanced security in production environments, consider:
# - External Secrets Operator (ESO) with cloud secret managers
# - Sealed Secrets for GitOps workflows
# - HashiCorp Vault with Vault Secrets Operator
```

**3. Reference secrets in workloads**
```yaml
env:
  - name: MYSQL_PASSWORD
    valueFrom:
      secretKeyRef:
        name: ragflow-mysql
        key: MYSQL_PASSWORD
  - name: ELASTIC_PASSWORD
    valueFrom:
      secretKeyRef:
        name: ragflow-elastic
        key: ELASTIC_PASSWORD
  - name: REDIS_PASSWORD
    valueFrom:
      secretKeyRef:
        name: ragflow-redis
        key: REDIS_PASSWORD
  - name: MINIO_PASSWORD
    valueFrom:
      secretKeyRef:
        name: ragflow-minio
        key: MINIO_PASSWORD
  - name: RAGFLOW_SECRET_KEY
    valueFrom:
      secretKeyRef:
        name: ragflow-app
        key: RAGFLOW_SECRET_KEY
```

---

## Admin Panel Configuration

To enable the admin panel, add arguments to the RAGFlow deployment:

**References**:
- [Admin UI Documentation](https://ragflow.io/docs/admin_ui)

**Admin Password Setup**:
1. Access the admin panel at `https://<production server URL>/admin`
2. Navigate to **User Management**
3. Click the user icon next to the admin account
4. Change the password

> **Note**: Do NOT use the `--init-superuser` argument during deployment, as it may cause instability.

---

## Verification

**Check deployment status**:
```bash
kubectl get pods -n ragflow
kubectl get ingress -n ragflow
```

**Verify services & functionality**:
- Access main interface: https://<production server URL>
- Admin panel: https://<production server URL>/admin
- MinIO login to a console (via port-forward)
- Users login using OIDC SSO
- Document ingestion and retrieval
- Default models setup

**Check for errors**:
```bash
kubectl logs <pod-name> -n ragflow
kubectl describe pod <pod-name> -n ragflow
```

---

## OIDC Configuration

To enable OpenID Connect (OIDC) authentication, configure the OAuth settings in `values.yaml`:
Check RAGFlow OIDC Documentation: https://ragflow.io/docs/configurations#oauth

```yaml
ragflow:
  service_conf:
    oauth:
      oidc:
        display_name: "Keycloak SSO"
        client_id: "<YOUR_CLIENT_ID>"
        client_secret: "<YOUR_CLIENT_SECRET>"
        issuer: "https://<YOUR_OIDC_PROVIDER>/realms/<REALM_NAME>"
        scope: "openid email profile"
        redirect_uri: "https://<YOUR_RAGFLOW_DOMAIN>/v1/user/oauth/callback/oidc"
```


**Store sensitive values in Kubernetes Secrets**: Do not hardcode `client_id` and `client_secret` in `values.yaml`
To securely manage sensitive configurations like OAuth credentials, create a Kubernetes Secret containing the `local.service_conf.yaml` file and mount it to the RAGFlow deployment. This avoids hardcoding secrets in `values.yaml`.

1. Create the `local.service_conf.yaml` file with your OIDC and other service configurations:

  ```yaml
  oauth:
    oidc:
     display_name: "SSO_NAME"
     client_id: "<YOUR_CLIENT_ID>"
     client_secret: "<YOUR_CLIENT_SECRET>"
     issuer: "https://<YOUR_OIDC_PROVIDER>/realms/<REALM_NAME>"
     scope: "openid email profile"
     redirect_uri: "https://<YOUR_RAGFLOW_DOMAIN>/v1/user/oauth/callback/oidc"
  # Add other service configurations as needed
  ```

2. Create a Secret from the file:

  ```bash
  kubectl create secret generic ragflow-service-conf \
    --from-file=local.service_conf.yaml \
    -n ragflow
  ```

3. Mount the Secret to the deployment by updating your Helm `values.yaml`:

  ```yaml
  ragflow:
    extraVolumes:
    - name: service-conf
     secret:
      secretName: ragflow-service-conf
    extraVolumeMounts:
    - name: service-conf
     mountPath: /app/conf/local.service_conf.yaml
     subPath: local.service_conf.yaml
  ```

  Adjust the `mountPath` based on your container's expected configuration file location.

Use environment-specific domain names for `issuer` and `redirect_uri`.

**Configuration Fields**:
- `display_name`: Label shown on login page
- `client_id`: OAuth client identifier from your OIDC provider
- `client_secret`: OAuth client secret (store in Kubernetes Secret)
- `issuer`: OIDC provider issuer URL
- `scope`: OpenID Connect scopes to request
- `redirect_uri`: Callback URL after authentication (must match provider configuration)

---

## Default Models Configuration

RAGFlow can be configured with default AI models for various tasks. This eliminates the need for users to manually configure models and provides a seamless out-of-the-box experience.

**Add the following to your `local.service_conf.yaml` file**:

```yaml
# service_conf secret content
user_default_llm:
  factory: 'OpenAI'             
  api_key: '<OPENAI_API_KEY>'
  base_url: 'https://api.openai.com/v1'
  default_models:
    chat_model:
      name: "claude-sonnet-4-5-20250929"
      factory: "Anthropic"
      api_key: "<ANTHROPIC_API_KEY>"
      base_url: "https://api.anthropic.com/v1"
    embedding_model:
      name: "embedding-001"
      factory: "Gemini"
      api_key: "<GOOGLE_API_KEY>"
    image2text_model:
      name: "gemini-3-pro-preview" 
      factory: "Gemini"
      api_key: "<GOOGLE_API_KEY>"
    rerank_model:
      name: "rerank-english-v3.0"
      api_key: "<COHERE_API_KEY>"
      factory: "Cohere"
    asr_model:
      name: "whisper-1"
      factory: "OpenAI"
      # ASR inherits api_key and base_url from main OpenAI config
```

**Model Types Supported**:
- **Chat Model**: Primary conversational LLM
- **Embedding Model**: Text vectorization for document indexing
- **Image2Text Model**: OCR and image analysis capabilities
- **Rerank Model**: Improves search result relevance
- **ASR Model**: Automatic Speech Recognition for audio files

---

## Configuration Reference

**Main config changes:**

| Section | Purpose |
|---------|---------|
| `env.MYSQL_HOST` | Cloud SQL IP address |
| `env.*_PASSWORD` | All service passwords (must change) |
| `mysql.enabled: false` | Disable internal MySQL |
| `ragflow.admin.service.enabled` | Enable admin panel |
| `ingress.enabled: true` | Enable external access |
| `ragflow.service_conf.oauth.oidc.*` | OIDC authentication configuration |
| `ragflow.service_conf.user_default_llm.*` | Default AI models configuration |
| `env.RAGFLOW_SECRET_KEY` | Secure session/crypto key (must be persistent) |

**Additional Resources**:
- [RAGFlow Configuration Guide](https://ragflow.io/docs/configurations)
- [Admin UI Documentation](https://ragflow.io/docs/admin_ui)

---

## Further Improvements & Production Considerations

Once your basic RAGFlow deployment is running, consider implementing these enhancements for production use:

- [ ] **Secret Management**: Migrate all credentials to external secret management
- [ ] **RBAC**: Configure Role-Based Access Control with least privilege principles
- [ ] **Pod Security**: Enable Pod Security Standards (restricted profile) and security contexts
- [ ] **Resource Limits**: Configure CPU/memory requests and limits for all containers
- [ ] **Health Probes**: Verify liveness and readiness probes are configured
- [ ] **TLS/HTTPS**: Enable HTTPS for all ingress endpoints with valid certificates
- [ ] **OIDC**: Configure OpenID Connect for secure authentication (see OIDC Configuration section)
- [ ] **Database Hardening**: Update MySQL plugin to `caching_sha2_password` (deprecation warning for `mysql_native_password`), enable SSL, restrict access
- [ ] **Logging & Monitoring**: Set up log aggregation and application monitoring
- [ ] **Backups**: Configure automated database backups and disaster recovery
- [ ] **Cloud Storage**: Integrate cloud storage (MinIO or cloud provider) for document storage
- [ ] **Network Policies**: Restrict traffic between pods and namespaces
