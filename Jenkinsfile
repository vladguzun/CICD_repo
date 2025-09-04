pipeline {
  agent any

  options {
    timestamps()
    ansiColor('xterm')  // păstrează dacă ai pluginul AnsiColor
  }

  environment {
    DOCKERHUB_USER = 'vladdockerr'         // schimbă dacă e altul
    IMAGE_NAME     = 'cicd-flask'        // numele imaginii
  }

  stages {
    stage('Checkout') {
      steps {
        checkout([
          $class: 'GitSCM',
          branches: [[name: '*/main']],
          userRemoteConfigs: [[url: 'git@github.com:vladguzun/CICD_repo.git']]
        ])
      }
    }

    stage('Unit tests (Python 3.11 in Docker)') {
      agent { docker { image 'python:3.11-slim' } }
      steps {
        sh '''
          python --version
          pip install --upgrade pip
          if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
          if [ -d tests ]; then python -m pytest -q; else echo "No tests/ directory, skipping."; fi
        '''
      }
    }

    stage('Docker Build') {
      steps {
        sh '''
          docker build -t ${DOCKERHUB_USER}/${IMAGE_NAME}:$BUILD_NUMBER -t ${DOCKERHUB_USER}/${IMAGE_NAME}:latest .
        '''
      }
    }

    stage('Docker Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub_creds', passwordVariable: 'DH_PASS', usernameVariable: 'DH_USER')]) {
          sh '''
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

