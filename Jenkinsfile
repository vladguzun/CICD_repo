pipeline {
  agent any
  options {
    timestamps()
    ansiColor('xterm')
  }
  environment {
    IMAGE = 'vladdocker/cicd-flask'
    TAG   = '2'
  }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Unit tests (venv in python:3.11-slim)') {
      agent {
        docker {
          image 'python:3.11-slim'
          // run as jenkins user, set HOME to writable place, reuse workspace
          args  '-u 1000:1000 -e HOME=/tmp'
          reuseNode true
        }
      }
      steps {
        sh '''
          set -e
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

    stage('Docker build') {
      steps {
        sh '''
          set -e
          docker build -t "$IMAGE:$TAG" -t "$IMAGE:latest" .
        '''
      }
    }

    stage('Smoke test (random free port)') {
      steps {
        script {
          // pick an unused high port to avoid conflicts
          env.SMOKE_PORT = sh(script: 'shuf -i 20000-65000 -n1', returnStdout: true).trim()
        }
        sh '''
          set -e -x
          docker rm -f cicd-flask-test >/dev/null 2>&1 || true
          docker run -d --rm --name cicd-flask-test -p ${SMOKE_PORT}:8000 "$IMAGE:latest"

          # wait up to ~25s for health endpoint
          ok=
          for i in $(seq 1 25); do
            if curl -fsS "http://localhost:${SMOKE_PORT}/health" >/dev/null; then
              echo "Healthcheck OK on port ${SMOKE_PORT}"
              ok=1
              break
            fi
            sleep 1
          done

          if [ -z "$ok" ]; then
            echo "Healthcheck FAILED on port ${SMOKE_PORT}"
            docker logs cicd-flask-test || true
            exit 1
          fi
        '''
      }
    }

    stage('Docker push') {
      when {
        expression { return env.DH_USER?.trim() && env.DH_PASS?.trim() }
      }
      steps {
        sh '''
          set -e
          echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin docker.io
          docker push "$IMAGE:$TAG"
          docker push "$IMAGE:latest"
        '''
      }
    }
  }

  post {
    always {
      sh 'docker rm -f cicd-flask-test >/dev/null 2>&1 || true'
      echo "Build finished with status: ${currentBuild.currentResult}"
    }
  }
}
