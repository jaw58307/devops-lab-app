pipeline {
  agent any
 
  environment {
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKER_IMAGE = "jawad027/devops-lab-app:latest"
  }
 
  stages {
    stage('Code Fetch') {
      steps {
        echo 'Fetching code from GitHub'
        checkout scm
      }
    }
   
    stage('Docker Image Creation') {
      steps {
        echo 'Building Docker Image'
        sh 'docker build -t ${DOCKER_IMAGE}:latest .'
        sh 'docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .'
      }
    }
   
    stage('Docker Push to DockerHub') {
      steps {
        echo 'Pushing Docker Image to DockerHub'
        sh 'echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin'
        sh 'docker push ${DOCKER_IMAGE}:latest'
        sh 'docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}'
      }
    }
   
    stage('Kubernetes Deployment') {
      steps {
        echo 'Deploying to Kubernetes'
        sh 'kubectl apply -f pvc.yaml'
        sh 'kubectl apply -f deployment.yaml'
        sh 'kubectl apply -f service.yaml'
        sh '''
          # Force rollout restart to ensure pods pull latest image
          kubectl rollout restart deployment/devops-lab-app
          kubectl rollout status deployment/devops-lab-app --timeout=300s
        '''
        sh 'kubectl get pods'
        sh 'kubectl get svc'
      
      }
    }
   
    stage('Prometheus/Grafana Deployment') {
      steps {
        echo 'Deploying Prometheus and Grafana using Helm'
        sh '''
          # Install Helm if not installed
          if ! command -v helm &> /dev/null; then
            curl https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
          fi
         
          # Create monitoring namespace
          kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -
         
          # Install or upgrade kube-prometheus-stack
          helm upgrade --install prometheus kube-prometheus-stack \
            --repo https://prometheus-community.github.io/helm-charts \
            --namespace monitoring
         
          kubectl get deployments -n monitoring
          kubectl get svc -n monitoring
        '''
      }
    }
   
    stage('Setup Port Forwarding') {
      steps {
        echo 'Setting up port forwarding for CRUD app and Grafana'
        sh '''#!/bin/bash
          # Kill any existing port-forward processes
          pkill -f "kubectl port-forward.*devops-lab-app" || true
          pkill -f "kubectl port-forward.*grafana" || true
         
          # Wait for pods to be ready
          kubectl wait --for=condition=ready pod -l app=devops-lab-app --timeout=300s || true
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s || true
         
          # Prevent Jenkins from killing these processes
          export JENKINS_NODE_COOKIE=dontKillMe
          export BUILD_ID=dontKillMe
         
          # Start port forwarding in background with nohup and disown
          nohup kubectl port-forward svc/devops-lab-app 8000:80 --address=0.0.0.0 > /tmp/crud-app-portforward.log 2>&1 </dev/null &
          disown
         
          nohup kubectl --namespace monitoring port-forward svc/prometheus-grafana 3000:80 --address=0.0.0.0 > /tmp/grafana-portforward.log 2>&1 </dev/null &
          disown
         
          sleep 5
         
          # Verify processes are running
          ps aux | grep "port-forward" | grep -v grep || echo "Warning: Port forwarding processes may not be running"
         
          echo "Port forwarding started:"
          echo "- App: http://13.60.187.42:8000"
          echo "- Grafana: http://13.60.187.42:3000"
          echo ""
          echo "Grafana admin password:"
          kubectl get secret --namespace monitoring prometheus-grafana -o jsonpath="{.data.admin-password}" | base64 -d
          echo ""
        '''
      }
    }
  }
 
  post {
    always {
      sh 'docker logout || true'
    }
  }
}
