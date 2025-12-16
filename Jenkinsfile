pipeline {
    agent any

    environment {
        DOCKER_IMAGE = "jawad027/devops-lab-app"
        KUBECONFIG_PATH = "/home/ubuntu/.minikube/profiles/minikube/config"
    }

    stages {

        stage('Code Fetch') {
            steps {
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                script {
                    docker.build("${DOCKER_IMAGE}:latest")
                }
            }
        }

        stage('Push Docker Image') {
            steps {
                script {
                    docker.withRegistry('', 'dockerhub-credentials') {
                        docker.image("${DOCKER_IMAGE}:latest").push()
                    }
                }
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                dir('app') { // ensure we are in the folder containing deployment.yaml
                    withEnv(["KUBECONFIG=${KUBECONFIG_PATH}"]) {
                        sh '''
                        kubectl apply -f deployment.yaml
                        kubectl apply -f service.yaml
                        kubectl apply -f pvc.yaml
                        kubectl get pods -o wide
                        '''
                    }
                }
            }
        }
    }
}
