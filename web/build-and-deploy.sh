#!/bin/bash
# Build and Deploy Script for OpenShift (Linux/Mac)
# Offline Voice Translator

# Configuration
IMAGE_NAME="voice-translator-offline"
IMAGE_TAG="1.0"
REGISTRY="quay.io/your-org"  # Change this to your registry
NAMESPACE="translation-services"

echo ""
echo "========================================"
echo "  Offline Voice Translator - Build & Deploy"
echo "========================================"
echo ""

# Step 1: Build Docker image
echo "[1/6] Building Docker image..."
docker build -t ${IMAGE_NAME}:${IMAGE_TAG} .

if [ $? -ne 0 ]; then
    echo "✗ Docker build failed!"
    exit 1
fi

echo "✓ Docker image built successfully"
echo ""

# Step 2: Test image locally
echo "[2/6] Testing image locally..."
docker run -d -p 8081:8081 --name translator-test ${IMAGE_NAME}:${IMAGE_TAG}

sleep 15

HEALTH=$(curl -s http://localhost:8081/health 2>/dev/null | grep -o '"status":"healthy"')

docker stop translator-test > /dev/null 2>&1
docker rm translator-test > /dev/null 2>&1

if [ -n "$HEALTH" ]; then
    echo "✓ Image test passed"
else
    echo "⚠ Warning: Health check failed, but continuing..."
fi
echo ""

# Step 3: Tag for registry
echo "[3/6] Tagging image for registry..."
docker tag ${IMAGE_NAME}:${IMAGE_TAG} ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}
echo "✓ Image tagged: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}"
echo ""

# Step 4: Push to registry
echo "[4/6] Pushing image to registry..."
echo "  (You may need to login: docker login ${REGISTRY})"
echo ""

docker push ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}

if [ $? -ne 0 ]; then
    echo "✗ Docker push failed! Did you login to the registry?"
    echo "  Run: docker login ${REGISTRY}"
    exit 1
fi

echo "✓ Image pushed to registry"
echo ""

# Step 5: Update deployment YAML
echo "[5/6] Updating deployment configuration..."

sed -i.bak "s|image: your-registry.io/voice-translator-offline:1.0|image: ${REGISTRY}/${IMAGE_NAME}:${IMAGE_TAG}|g" openshift-deployment.yaml

echo "✓ Deployment file updated"
echo ""

# Step 6: Deploy to OpenShift
echo "[6/6] Deploying to OpenShift..."
echo "  (Make sure you're logged in: oc login)"
echo ""

# Check if logged in
OC_USER=$(oc whoami 2>&1)

if [ $? -ne 0 ]; then
    echo "✗ Not logged in to OpenShift!"
    echo "  Run: oc login https://your-cluster.com"
    exit 1
fi

echo "  Logged in as: $OC_USER"

# Apply deployment
oc apply -f openshift-deployment.yaml

if [ $? -eq 0 ]; then
    echo ""
    echo "✓ Deployment applied successfully!"
    echo ""
    
    # Wait for rollout
    echo "Waiting for rollout to complete..."
    oc rollout status deployment/voice-translator-offline -n $NAMESPACE --timeout=5m
    
    # Get route
    ROUTE=$(oc get route voice-translator-route -n $NAMESPACE -o jsonpath='{.spec.host}' 2>/dev/null)
    
    if [ -n "$ROUTE" ]; then
        echo ""
        echo "========================================"
        echo "  Deployment Complete!"
        echo "========================================"
        echo ""
        echo "  Application URL: https://$ROUTE"
        echo ""
        echo "  Check status:"
        echo "    oc get pods -n $NAMESPACE"
        echo ""
        echo "  View logs:"
        echo "    oc logs -f deployment/voice-translator-offline -n $NAMESPACE"
        echo ""
    fi
else
    echo ""
    echo "✗ Deployment failed!"
    echo "  Check the error messages above"
    exit 1
fi
