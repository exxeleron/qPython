pipeline {
    agent {
        docker {
            image 'research/python-env:bf9b6284fbc13ce83e2a874f04506a02943c85cc'
        }
    }
    stages {
        stage('Build') {
            steps {
                echo ">> Bulding"
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
