# 🚀 Microservices Project — Production-Grade Architecture (Docker, Kubernetes, CI/CD)

A fully scalable **Microservices Architecture** built using modern backend + DevOps technology.  

---

## 🏗️ Architecture Overview

```
               ┌───────────────────────────┐
               │        API Gateway        │
               │           NGINX           │
               └──────────────┬────────────┘
                              │
         ┌────────────────────┼────────────────────┐
         │                    │                    │
 ┌──────────────┐    ┌──────────────┐     ┌────────────────┐
 │ User Service │    │ Order Service│     │ Payment Service│
 │  (Flask)     │    │   (Flask)    │     │     (Flask)    │
 │ PostgreSQL   │    │  MongoDB     │     │     Redis      │
 └──────────────┘    └──────────────┘     └────────────────┘
```

---

## 🛠️ Tech Stack

### **Backend**
- Python Flask
- JWT Authentication
- REST Architecture

### **Databases**
- PostgreSQL (User)
- MongoDB (Orders)
- Redis (Payment status)

### **DevOps & Cloud**
- Docker (containers)
- Kubernetes (Deployments, Services, PVC)
- Minikube (local cluster)
- Kubernetes Secrets (secure env vars)

### **Gateway**
- NGINX reverse proxy

### **CI/CD**
- GitHub Actions
- GHCR (GitHub Container Registry)
- Auto Build → Push → Deploy pipeline

---

## 🔌 Microservices Overview

### **User Service**
Handles:
- Register new users  
- Login  
- JWT Token generation  
- Fetch logged-in user's profile (`/users/profile`)  

Endpoints:
```
POST /users/register
POST /users/login
GET  /users/profile 
```

Database: **PostgreSQL**

---

### **Order Service**
Handles:
- Create Order
- Retrieve Orders for a user  

Endpoints:
```
POST /orders/create
GET  /orders
```

Database: **MongoDB**

---

### **Payment Service**
Handles:
- Fake payment
- Store payment status in Redis  

Endpoints:
```
POST /payments/pay
GET  /payments/pay/status/<txn_id>
```

---

### **API Gateway (NGINX)**
Routes:
```
/users/*    → user-service
/orders/*   → order-service
/payments/* → payment-service
```

---

## 🔐 Secure Secrets (No Hard-Coding)

All secrets stored via Kubernetes:

```
kubectl create secret generic micro-secrets \
  --from-literal=MONGO_URL="mongodb://mongo-service:27017/" \
  --from-literal=REDIS_HOST="redis-service" \
  --from-literal=DATABASE_URL="postgresql://postgres:postgres@postgres-service:5432/postgres" \
  --from-literal=JWT_SECRET="supersecretkey"
```

Postgres password:

```
kubectl create secret generic postgres-secret \
  --from-literal=POSTGRES_PASSWORD="postgres"
```

Used inside YAML:

```yaml
env:
  - name: JWT_SECRET
    valueFrom:
      secretKeyRef:
        name: micro-secrets
        key: JWT_SECRET
```

---

## 🤖 CI/CD (GitHub Actions)

Workflows located here:

```
.github/workflows/user-service.yml
.github/workflows/order-service.yml
.github/workflows/payment-service.yml
.github/workflows/api-gateway.yml
```

Pipeline steps:
1. Build Docker image  
2. Login to GHCR  
3. Push image  
4. Update Kubernetes deployment (optional)

---

## 🐳 Run Locally (Minikube)

Start cluster:

```
minikube start
```

Build Docker images inside Minikube:

```
& minikube -p minikube docker-env | Invoke-Expression
docker build -t user-service ./user-service
docker build -t order-service ./order-service
docker build -t payment-service ./payment-service
docker build -t api-gateway ./api-gateway
```

Apply manifests:

```
kubectl apply -f k8s/
```

---

## 📡 API Testing

Set base URL:

```
$BASE="http://localhost:8000"
```

### Register:
```
Invoke-RestMethod -Method POST -Uri "$BASE/users/register" -Body @{
  username="test"; password="1234"
} -ContentType "application/json"
```

### Login:
```
$resp = Invoke-RestMethod -Method POST -Uri "$BASE/users/login" -Body @{
  username="test"; password="1234"
} -ContentType "application/json"

$token = $resp.token
```

### Get Profile (NEW):
```
Invoke-RestMethod -Method GET -Uri "$BASE/users/profile" `
  -Headers @{ Authorization = "Bearer $token" }
```

### Create order:
```
Invoke-RestMethod -Method POST -Uri "$BASE/orders/create" `
 -Headers @{ Authorization = "Bearer $token" } `
 -Body '{"item":"Laptop","price":50000}' `
 -ContentType "application/json"
```

---

## 📂 Folder Structure

```
Microservices_Project/
│
├── api-gateway/
├── user-service/
├── order-service/
├── payment-service/
│
├── k8s/
│
└── .github/workflows/
```

---



