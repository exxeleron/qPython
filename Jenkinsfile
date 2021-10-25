pipeline {
    agent {
        docker {
            image 'python:3.9.7-buster'
        }
    }
    stages {
        stage('Build') {
            steps {
                echo ">> Building..."
            }
        }
        stage('Test') {
            steps {
                sh 'tox'
            }
            post {
                always {
                    junit 'test-reports/results.xml'
                }
            }
        }
        stage('Publish') {
            steps {
                echo ">> Publishing..."
            }
        }
    }
}
