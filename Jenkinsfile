pipeline {
  agent any

  environment {
    IMAGE = "vladdockerr/cicd-flask"
    TAG   = "${env.BUILD_NUMBER}"
  }

  stages {

    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit tests (venv in python:3.11)') {
      steps {
        sh '''
          set -euxo pipefail
          docker run --rm \
            -u $(id -u):$(id -g) \
            -v "$PWD:/src" -w /src \
            -e HOME=/tmp \
            python:3.11-slim bash -lc '
              python -m venv .venv
              . .venv/bin/activate
              pip install -U pip
              [ -f requirements.txt ] && pip install -r requirements.txt
              pip install -q pytest
              pytest -q
            '
        '''
      }
    }

    stage('Docker build') {
      steps {
        sh '''
          set -eux
          docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .
        '''
      }
    }

    stage('Smoke test') {
      steps {
        sh '''
          set -eux
          docker rm -f cicd-flask-test || true
          PORT=$(shuf -i 20000-65000 -n 1)
          docker run -d --rm --name cicd-flask-test -p ${PORT}:8000 "$IMAGE:latest"
          # așteaptă până pornește aplicația
          for i in $(seq 1 30); do
            if curl -fsS "http://localhost:${PORT}/health" | grep -q '"ok": *true'; then
              echo "Healthcheck OK on ${PORT}"
              break
            fi
            sleep 1
            [ $i -eq 30 ] && { echo "Healthcheck FAILED on ${PORT}"; docker logs cicd-flask-test; exit 1; }
          done
          docker rm -f cicd-flask-test
        '''
      }
    }

    stage('Docker push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -eux
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
      sh 'docker rm -f cicd-flask-test || true'
      echo "Build finished with status: ${currentBuild.currentResult}"
    }
  }
}

