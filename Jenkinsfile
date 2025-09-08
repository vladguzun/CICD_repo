pipeline {
  agent any

  environment {
    APP_PORT   = '8000'
    IMAGE_NAME = 'vladdocker/cicd-flask'
  }

  options {
    timestamps()
    ansiColor('xterm')
  }

  stages {
    stage('Checkout') {
      steps {
        checkout scm
      }
    }

    stage('Unit tests (venv)') {
      steps {
        script {
          sh '''
            set -e
            python3 -V
            python3 -m venv .venv
            . .venv/bin/activate
            python -V
            pip install -U pip
            [ -f requirements.txt ] && pip install -r requirements.txt
            pip install pytest
            export PYTHONPATH="$PWD"
            [ -d tests ] && pytest -q
          '''
        }
      }
    }

    stage('Docker build') {
      steps {
        script {
          sh '''
            set -e
            TAG="$(echo ${GIT_COMMIT:-latest} | cut -c1-7)"
            docker build -t ${IMAGE_NAME}:${TAG} -t ${IMAGE_NAME}:latest .
            echo "${TAG}" > .imgtag
          '''
        }
      }
    }

    stage('Smoke test') {
      steps {
        script {
          sh '''
            set -e
            TAG=$(cat .imgtag || echo latest)

            # pornesc containerul fara publish pe host (evit conflictele de port)
            docker rm -f cicd-flask-test >/dev/null 2>&1 || true
            docker run -d --rm --name cicd-flask-test ${IMAGE_NAME}:${TAG}

            # iau IP-ul containerului pe bridge-ul docker0
            APP_IP=$(docker inspect -f '{{ .NetworkSettings.IPAddress }}' cicd-flask-test)
            echo "Container IP: ${APP_IP}"

            # astept sa porneasca si verific /health
            ok=""
            for i in $(seq 1 25); do
              if curl -fsS "http://${APP_IP}:${APP_PORT}/health" >/dev/null; then
                echo "Smoke OK: http://${APP_IP}:${APP_PORT}/health"
                ok=1; break
              fi
              sleep 1
            done

            if [ -z "$ok" ]; then
              echo "Smoke FAILED"
              echo "==== Container logs ===="
              docker logs cicd-flask-test || true
              exit 1
            fi
          '''
        }
      }
      post {
        always {
          sh 'docker rm -f cicd-flask-test >/dev/null 2>&1 || true'
        }
      }
    }

    stage('Docker push') {
      steps {
        script {
          sh '''
            set -e
            TAG=$(cat .imgtag || echo latest)
          '''
          withCredentials([usernamePassword(credentialsId: 'dockerhub', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
            sh '''
              echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
              docker push ${IMAGE_NAME}:${TAG}
              docker push ${IMAGE_NAME}:latest
              docker logout || true
            '''
          }
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

