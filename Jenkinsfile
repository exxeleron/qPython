pipeline {
    agent {
        docker {
            image 'research/python-qpython-env:99fb7f9cbe9720187984dc160e78742876bc9007'
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
