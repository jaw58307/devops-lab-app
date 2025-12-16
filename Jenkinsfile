pipeline {
  agent any

  environment {
    KUBECONFIG = '/var/lib/jenkins/.kube/config'
    DOCKERHUB_CREDENTIALS = credentials('dockerhub-creds')
    DOCKER_IMAGE = "jawad027/devops-lab-app"
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
        sh '''
          docker build -t ${DOCKER_IMAGE}:latest .
          docker build -t ${DOCKER_IMAGE}:${BUILD_NUMBER} .
        '''
      }
    }

    stage('Docker Push to DockerHub') {
      steps {
        echo 'Pushing Docker Image to DockerHub'
        sh '''
          echo ${DOCKERHUB_CREDENTIALS_PSW} | docker login -u ${DOCKERHUB_CREDENTIALS_USR} --password-stdin
          docker push ${DOCKER_IMAGE}:latest
          docker push ${DOCKER_IMAGE}:${BUILD_NUMBER}
        '''
      }
    }

    stage('Kubernetes Deployment') {
      steps {
        echo 'Deploying application to Kubernetes'
        sh '''
          kubectl apply -f pvc.yaml
          kubectl apply -f deployment.yaml
          kubectl apply -f service.yaml
          kubectl apply -f hpa.yaml

          kubectl rollout restart deployment/devops-app
          kubectl rollout status deployment/devops-app --timeout=300s

          kubectl get pods
          kubectl get svc
          kubectl get hpa
        '''
      }
    }

    stage('Prometheus & Grafana Deployment') {
      steps {
        echo 'Deploying Prometheus and Grafana using Helm'
        sh '''
          # Install Helm if not present
          if ! command -v helm &> /dev/null; then
            curl -fsSL https://raw.githubusercontent.com/helm/helm/main/scripts/get-helm-3 | bash
          fi

          # Add Helm repo
          helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
          helm repo update

          # Create monitoring namespace
          kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

          # Install kube-prometheus-stack
          helm upgrade --install prometheus prometheus-community/kube-prometheus-stack \
            --namespace monitoring \
            --create-namespace

          kubectl get pods -n monitoring
          kubectl get svc -n monitoring
        '''
      }
    }

    stage('Setup Port Forwarding') {
      steps {
        echo 'Setting up port forwarding'
        sh '''#!/bin/bash
          set -e

          pkill -f "kubectl port-forward.*devops-app" || true
          pkill -f "kubectl port-forward.*grafana" || true

          kubectl wait --for=condition=ready pod -l app=devops-app --timeout=300s || true
          kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=grafana -n monitoring --timeout=300s || true

          export JENKINS_NODE_COOKIE=dontKillMe
          export BUILD_ID=dontKillMe

          nohup kubectl port-forward svc/devops-app 8000:80 --address=0.0.0.0 \
            > /tmp/devops-app.log 2>&1 &

          nohup kubectl -n monitoring port-forward svc/prometheus-grafana 3000:80 --address=0.0.0.0 \
            > /tmp/grafana.log 2>&1 &

          sleep 5

          echo "--------------------------------------------------"
          echo "🚀 Application URL: http://13.60.187.42:8000"
          echo "📊 Grafana URL:     http://13.60.187.42:3000"
          echo "--------------------------------------------------"

          echo "Grafana admin password:"
          kubectl get secret -n monitoring prometheus-grafana \
            -o jsonpath="{.data.admin-password}" | base64 -d
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
