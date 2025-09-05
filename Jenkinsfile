pipeline {
  agent any

  environment {
    // !!! Use your real Docker Hub namespace (two 'r' as in your screenshot)
    IMAGE = 'vladdockerr/cicd-flask'
    TAG   = "${env.BUILD_NUMBER}"
  }

  options { ansiColor('xterm') }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit tests (venv + PYTHONPATH)') {
      steps {
        script {
          sh 'docker inspect -f . python:3.11-slim >/dev/null 2>&1 || docker pull python:3.11-slim'
          docker.image('python:3.11-slim').inside('-u 1000:1000 -e HOME=/tmp -w $PWD') {
            sh '''
              set -e
              APP_DIR=.
              [ -f app.py ] && echo "Using APP_DIR=${APP_DIR}"
              python -m venv .venv
              . .venv/bin/activate
              python --version
              pip install -U pip
              [ -f requirements.txt ] && pip install -r requirements.txt
              pip install pytest
              export PYTHONPATH="${PWD}"
              if [ -d tests ]; then
                pytest -q
              else
                echo "No tests/ directory, skipping"
              fi
            '''
          }
        }
      }
    }

    stage('Docker build') {
      steps {
        sh '''
          set -e
          docker build -t ${IMAGE}:${TAG} -t ${IMAGE}:latest .
        '''
      }
    }

    stage('Smoke test (container IP, no host publish)') {
      steps {
        sh '''
          set -e
          docker rm -f cicd-flask-test || true
          docker run -d --rm --name cicd-flask-test ${IMAGE}:latest
          APP_IP=$(docker inspect -f '{{ .NetworkSettings.IPAddress }}' cicd-flask-test)
          echo "Container IP: $APP_IP"

          ok=""
          for i in $(seq 1 25); do
            if curl -fsS "http://$APP_IP:8000/health" > /dev/null; then
              echo "Healthcheck OK at http://$APP_IP:8000/health"
              ok=1
              break
            fi
            sleep 1
          done
          if [ -z "$ok" ]; then
            echo "Healthcheck FAILED"
            docker logs cicd-flask-test || true
            exit 1
          fi

          docker rm -f cicd-flask-test || true
        '''
      }
    }

    stage('Docker push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -e
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE}:${TAG}
            docker push ${IMAGE}:latest
            docker logout
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

