pipeline {
  agent { docker { image 'python:3.12-slim' } }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r requirements/tests.txt'
      }
    }
    stage('test') {
      steps {
        sh 'pytest tests/all'
      }
    }
    stage('audit') {
      steps {
        sh 'pip install pip-audit && pip-audit -r requirements.txt'
      }
    }
  }
}
