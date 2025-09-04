pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }   // keep if AnsiColor plugin is installed

  environment {
    DOCKERHUB_USER = 'vladdockerr'    // change if needed
    IMAGE_NAME     = 'cicd-flask'   // change if needed
  }

  stages {
    // No Checkout stage — Multibranch/Pipeline-from-SCM already checked out the code.

    stage('Unit tests') {
      agent { docker { image 'python:3.11-slim' } }   // clean Python env
      steps {
        sh '''
          set -e
          python --version
          pip install -U pip
          [ -f requirements.txt ] && pip install -r requirements.txt
          pip install pytest
          if [ -d tests ]; then
            pytest -q
          else
            echo "No tests/ directory, skipping."
          fi
        '''
      }
    }

    stage('Docker build') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:$BUILD_NUMBER \
                       -t ${DOCKERHUB_USER}/${IMAGE_NAME}:latest .
        '''
      }
    }

    stage('Smoke test') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker rm -f cicd-flask-test 2>/dev/null || true
          docker run -d --rm --name cicd-flask-test -p 5000:5000 ${DOCKERHUB_USER}/${IMAGE_NAME}:latest
          for i in $(seq 1 20); do
            curl -fsS http://localhost:5000/health && ok=1 && break || sleep 1
          done
          [ "${ok:-0}" = "1" ] || (echo "Healthcheck failed"; docker logs cicd-flask-test; exit 1)
          docker rm -f cicd-flask-test
        '''
      }
    }

    stage('Docker push') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -e
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:$BUILD_NUMBER
            docker push ${DOCKERHUB_USER}/${IMAGE_NAME}:latest
            docker logout
          '''
        }
      }
    }
  }
}

