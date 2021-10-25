pipeline {
    agent {
        docker {
            image 'python:2-alpine'
        }
    }
    stages {
        stage('Build') {
            steps {
              sh 'ls'
            }
        }
        stage('Test') {
            steps {
                sh 'py.test --junit-xml test-reports/results.xml tests'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
    }
}
