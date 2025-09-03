pipeline {
  agent any
  environment {
    REGISTRY = 'docker.io'
    DOCKERHUB_USER = 'YOUR_DOCKERHUB_USER'
    APP = 'mini-flask-ci'
    COMMIT = "${env.GIT_COMMIT?.take(7) ?: 'dev'}"
    IMAGE = "${env.DOCKERHUB_USER}/${env.APP}"
  }
  options { timestamps(); ansiColor('xterm') }

  stages {
    stage('Checkout') {
      steps { checkout scm }
    }

    stage('Unit tests') {
      steps {
        sh '''
          python3 -m venv .venv
          . .venv/bin/activate
          pip install -r requirements.txt
          pytest -q
        '''
      }
    }

    stage('Docker Build') {
      steps {
        sh '''
          docker build -t ${IMAGE}:${COMMIT} -t ${IMAGE}:latest .
        '''
      }
    }

    stage('Docker Push') {
      steps {
        withCredentials([usernamePassword(credentialsId: 'dockerhub-creds', usernameVariable: 'DU', passwordVariable: 'DP')]) {
          sh '''
            echo "$DP" | docker login -u "$DU" --password-stdin ${REGISTRY}
            docker push ${IMAGE}:${COMMIT}
            docker push ${IMAGE}:latest
            docker logout ${REGISTRY}
          '''
        }
      }
    }
  }

  post {
    success { echo "✅ Pushed ${IMAGE}:${COMMIT} și :latest" }
    failure { echo "❌ Pipeline failed" }
    always  { cleanWs() }
  }
}

