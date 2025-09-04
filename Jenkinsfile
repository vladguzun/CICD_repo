pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') } // cere pluginul AnsiColor (altfel scoate linia)

  environment {
    IMAGE_NAME   = 'vladdocker/cicd-flask' // schimbă dacă vrei alt nume
  }

  stages {
    // Checkout e făcut de "Pipeline script from SCM" / Multibranch automat.

    stage('Unit tests') {
      agent { docker { image 'python:3.11-slim' } }  // mediu curat de test
      steps {
        sh '''
          set -e
          export PYTHONPATH="$PWD"      # ca 'app.py' să fie importabil
          python --version
          pip install -U pip
          [ -f requirements.txt ] && pip install -r requirements.txt
          pip install pytest
          pytest -q
        '''
      }
    }

    stage('Docker build') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker build -t ${IMAGE_NAME}:${BUILD_NUMBER} -t ${IMAGE_NAME}:latest .
        '''
      }
    }

    stage('Smoke test (port 8000)') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker rm -f cicd-flask-test 2>/dev/null || true
          docker run -d --rm --name cicd-flask-test -p 8000:8000 ${IMAGE_NAME}:latest
          for i in $(seq 1 20); do
            curl -fsS http://localhost:8000/health && ok=1 && break || sleep 1
          done
          [ "${ok:-0}" = "1" ] || (echo "Healthcheck failed"; docker logs cicd-flask-test; exit 1)
          docker rm -f cicd-flask-test
        '''
      }
    }

    stage('Docker push') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DH_USER', passwordVariable: 'DH_PASS')]) {
          sh '''
            set -e
            echo "$DH_PASS" | docker login -u "$DH_USER" --password-stdin
            docker push ${IMAGE_NAME}:${BUILD_NUMBER}
            docker push ${IMAGE_NAME}:latest
            docker logout
          '''
        }
      }
    }
  }
}
