pipeline {
    agent any

    stages {
        stage('Checkout Code') {
            steps {
                // Jenkins automatically pulls the code if connected to your Git repo
                checkout scm
            }
        }

        stage('Build Docker Image') {
            steps {
                sh "docker build -t cicd-k8s-demo:latest ."
            }
        }

        stage('Deploy to Kubernetes') {
            steps {
                sh "kubectl apply -f k8s-deployment.yaml"
                sh "kubectl rollout restart deployment/cicd-k8s-demo"
                sh "kubectl rollout status deployment/cicd-k8s-demo"
            }
        }
    }
}