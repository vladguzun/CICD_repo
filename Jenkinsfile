pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }

  environment {
    IMAGE = 'vladdocker/cicd-flask'   // <- your Docker Hub repo
    TAG   = "${env.BUILD_NUMBER}"
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Unit tests (venv in python:3.11-slim)') {
      steps {
        script {
          // make sure the image is available
          sh 'docker inspect -f . python:3.11-slim || docker pull python:3.11-slim'

          // run tests in a disposable python container with a local venv
          docker.image('python:3.11-slim').inside('-u 1000:1000 -e HOME=/tmp') {
            sh '''
              set -e
              python -m venv .venv
              . .venv/bin/activate
              python --version
              pip install -U pip
              [ -f requirements.txt ] && pip install -r requirements.txt
              pip install pytest
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
          docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .
        '''
      }
    }

    stage('Smoke test (container IP, no host publish)') {
      steps {
        sh '''
          set -e

          # Clean any previous test container
          docker rm -f cicd-flask-test >/dev/null 2>&1 || true

          # Start the app container WITHOUT -p; we’ll curl it via its bridge IP
          docker run -d --rm --name cicd-flask-test "$IMAGE:latest"

          # Get bridge IP of the test container
          APP_IP="$(docker inspect -f '{{ .NetworkSettings.IPAddress }}' cicd-flask-test)"
          echo "Container IP: ${APP_IP}"

          ok=
          for i in $(seq 1 25); do
            if curl -fsS "http://${APP_IP}:8000/health" >/dev/null; then
              echo "Healthcheck OK at http://${APP_IP}:8000/health"
              ok=1
              break
            fi
            sleep 1
          done

          if [ -z "$ok" ]; then
            echo "Healthcheck FAILED"
            echo "--- docker logs cicd-flask-test ---"
            docker logs cicd-flask-test || true
            exit 1
          fi

          # Stop the test container (it was started with --rm)
          docker rm -f cicd-flask-test >/dev/null 2>&1 || true
        '''
      }
    }

    stage('Docker push') {
      when { branch 'main' }
      steps {
        withCredentials([usernamePassword(
          credentialsId: 'dockerhub',        // <- your Jenkins creds ID
          usernameVariable: 'DH_USER',
          passwordVariable: 'DH_PASS'
        )]) {
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

