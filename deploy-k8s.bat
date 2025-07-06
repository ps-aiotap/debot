@echo off
echo Building Docker image...
docker build -t debot:latest .

echo Applying K8s manifests...
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/redis.yaml
kubectl apply -f k8s/chromadb.yaml
kubectl apply -f k8s/chatbot.yaml
REM Skipping postgres.yaml - not needed

echo Waiting for pods to be ready...
kubectl wait --for=condition=ready pod -l app=chatbot -n debot --timeout=300s

echo Copying data to pods...
cd data
for /f %%i in ('kubectl get pods -n debot -l app=chatbot -o jsonpath^="{.items[*].metadata.name}"') do (
    echo Copying to pod: %%i
    kubectl cp . %%i:/app/data/ -n debot
)
cd ..

echo Deployment complete!
echo Run: kubectl port-forward svc/chatbot-service 8501:8501 -n debot
echo Then open: http://localhost:8501
pause