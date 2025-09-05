pipeline {
    agent any

    environment {
        IMAGE = "vladdocker/cicd-flask"
        TAG = "${env.BUILD_NUMBER}"
    }

    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }

        stage('Unit tests (venv in python:3.11-slim)') {
            steps {
                script {
                    docker.image('python:3.11-slim').inside {
                        sh '''
                            set -e
                            python -m venv .venv
                            . .venv/bin/activate
                            python --version
                            pip install -U pip
                            if [ -f requirements.txt ]; then
                                pip install -r requirements.txt
                            fi
                            pip install pytest
                            [ -d tests ] && pytest -q || echo "No tests/ directory, skipping"
                        '''
                    }
                }
            }
        }

        stage('Docker build') {
            steps {
                sh '''
                    set -e
                    docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .
                '''
            }
        }

        stage('Smoke test (port 9156)') {
            steps {
                sh '''
                    set -e
                    docker rm -f cicd-flask-test || true
                    docker run -d --rm --name cicd-flask-test -p 9156:8000 "$IMAGE:latest"
                    sleep 5
                    curl -fs http://localhost:9156/health
                    docker rm -f cicd-flask-test
                '''
            }
        }

        stage('Docker push') {
            steps {
                withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
                    sh '''
                        echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
                        docker push "$IMAGE:$TAG"
                        docker push "$IMAGE:latest"
                    '''
                }
            }
        }
    }

    post {
        always {
            echo "Build finished with status: ${currentBuild.currentResult}"
        }
    }
}

