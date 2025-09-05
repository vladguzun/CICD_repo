pipeline {
  agent any

  options {
    ansiColor('xterm')
    timestamps()
  }

  environment {
    IMAGE = 'vladdocker/cicd-flask'       // change if you want a different repo
    TAG   = "${env.BUILD_NUMBER}"         // numeric build tag
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
          // Run a temporary python container, create a venv, install deps, run pytest
          docker.image('python:3.11-slim').inside('-e HOME=/tmp') {
            sh '''
              set -e
              export PYTHONPATH=$PWD
              python -m venv .venv
              . .venv/bin/activate
              python --version
              pip install -U pip
              [ -f requirements.txt ] && pip install -r requirements.txt
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

    stage('Smoke test (port 8000)') {
      steps {
        sh '''
          set -e
          # Start container on 8000:8000
          docker rm -f cicd-flask-test >/dev/null 2>&1 || true
          docker run -d --rm --name cicd-flask-test -p 8000:8000 "$IMAGE:latest"

          # Wait for /health to respond
          ok=0
          for i in $(seq 1 30); do
            if command -v curl >/dev/null 2>&1; then
              curl -fsS http://localhost:8000/health && ok=1 && break || true
            else
              wget -qO- http://localhost:8000/health && ok=1 && break || true
            fi
            sleep 1
          done

          if [ "$ok" != "1" ]; then
            echo "Healthcheck failed"
            docker logs cicd-flask-test || true
            exit 1
          fi
        '''
      }
      post {
        always {
          sh 'docker rm -f cicd-flask-test >/dev/null 2>&1 || true'
        }
      }
    }

    stage('Docker push') {
      when { expression { return true } } // set to false to disable pushing
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -e
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
