@echo off
echo Getting pod name...
for /f %%i in ('kubectl get pods -n debot -l app=chatbot -o jsonpath="{.items[0].metadata.name}"') do set POD_NAME=%%i
echo Pod name: %POD_NAME%

echo Copying data to pod...
cd data
kubectl cp . debot/%POD_NAME%:/app/data/
cd ..
echo Data copied successfully!