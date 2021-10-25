pipeline {
    agent {
        docker {
            image 'research/python-env:bf9b6284fbc13ce83e2a874f04506a02943c85cc'
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
