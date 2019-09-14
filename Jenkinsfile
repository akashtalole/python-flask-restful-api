pipeline {
  agent { docker { image 'python:3.6-alpine' } }
  stages {
    stage('build') {
      steps {
        sh 'pip install -r requirements.txt'
      }
    }
    stage('test') {
      steps {
        sh 'python manage.py'
      }   
    }
  }
}