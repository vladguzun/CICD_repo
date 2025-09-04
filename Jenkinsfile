pipeline {
  agent any
  options { timestamps(); ansiColor('xterm') }  // keep if AnsiColor plugin installed

  stages {
    // Multibranch/Pipeline-from-SCM already does checkout before this pipeline runs.

    stage('Unit tests') {
      agent { docker { image 'python:3.11-slim' } }   // clean Python env
      steps {
        sh '''
          set -e
          export PYTHONPATH="$PWD"     # make app.py importable in tests
          python --version
          pip install -U pip
          [ -f requirements.txt ] && pip install -r requirements.txt
          pip install pytest
          [ -d tests ] && pytest -q || echo "No tests/, skipping."
        '''
      }
    }

    stage('Docker build') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker build -t vladdocker/cicd-flask:${BUILD_NUMBER} \
                       -t vladdocker/cicd-flask:latest .
        '''
      }
    }

    stage('Smoke test') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        sh '''
          set -e
          docker rm -f cicd-flask-test 2>/dev/null || true
          docker run -d --rm --name cicd-flask-test -p 5000:5000 vladdocker/cicd-flask:latest
          for i in $(seq 1 20); do
            if command -v curl >/dev/null; then
              curl -fsS http://localhost:5000/health && ok=1 && break || true
            else
              wget -qO- http://localhost:5000/health >/dev/null && ok=1 && break || true
            fi
            sleep 1
          done
          [ "${ok:-0}" = "1" ] || (echo "Healthcheck failed"; docker logs cicd-flask-test; exit 1)
          docker rm -f cicd-flask-test
        '''
      }
    }

    stage('Docker push') {
      when { expression { fileExists('Dockerfile') } }
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DOCKER_USER', passwordVariable: 'DOCKER_PASS')]) {
          sh '''
            set -e
            echo "$DOCKER_PASS" | docker login -u "$DOCKER_USER" --password-stdin
            docker push vladdocker/cicd-flask:${BUILD_NUMBER}
            docker push vladdocker/cicd-flask:latest
            docker logout
          '''
        }
      }
    }
  }
}
