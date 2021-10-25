pipeline {
    agent {
        docker {
            image 'fedorapython/fedora-python-tox:amd64'
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
