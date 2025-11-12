# Week 7 Assignment – Kubernetes Autoscaling and Stress Testing (IRIS API)

## Overview
This week’s assignment builds upon the previous **CI/CD pipeline** for the IRIS Classification API.  
The main objective is to **scale the deployed service on Kubernetes** and perform **stress testing** to observe system performance and bottlenecks.

---

## Objectives
- Extend the existing CI/CD workflow to include **stress testing**.
- Use **`wrk`** to simulate a high number of concurrent requests (>1000).
- Demonstrate **Kubernetes Horizontal Pod Autoscaling (HPA)** with:
  - **Default pods:** 1  
  - **Maximum pods:** 3
- Observe **bottlenecks** when autoscaling is restricted to 1 pod while concurrency increases from 1000 to 2000.

---

## Project Structure
```
week7-logging/
│
├── app/
│ ├── log.py
│ └── models
|     └── model.joblib
├── k8s/
|   ├── deployment.yaml
|   ├── service.yaml
│   └── hpa.yaml
├── requirements.txt
├── Dockerfile
├── README.md
├── post.lua
└── .github/workflows/cd.yml
```

---

## Deployment Steps
### 1. Apply all manifests
```bash
kubectl apply -f k8s/deployment.yaml
kubectl apply -f k8s/service.yaml
kubectl apply -f k8s/hpa.yaml
```

### 2. Verify resources
```bash
kubectl get all
kubectl get hpa
```

### 3. Expose the service
Once deployed, note the External IP of the service:
```bash
kubectl get svc
```
Access the API at:
```cpp
http://<EXTERNAL_IP>/
```

---

## Stress Testing with wrk
### 1. Install wrk
```bash
sudo apt-get install wrk -y
```

### 2. Run Load Test
Moderate Load (1000 concurrent requests)
```bash
wrk -t4 -c1000 -d30s --latency -s post.lua http://34.57.156.15:8200/predict
```

Heavy Load (2000 concurrent requests)
```bash
wrk -t4 -c2000 -d30s --latency -s post.lua http://34.57.156.15:8200/predict
```

---

## Observing Metrics and Scaling Behavior
### 1. Monitor CPU usage
```bash
kubectl top pods
kubectl top nodes
```

### 2. Watch pods scale up
```bash
kubectl get pods -w
```

---

## Bottleneck Demonstration (Without Autoscaling)
Disable HPA:
```bash
kubectl delete hpa iris-hpa
kubectl scale deployment iris-api --replicas=1
```
Re-run the 2000-concurrent load test and observe:
- Increased latency
- Decreased throughput
- Higher timeout rate
