pipeline {
    agent {
        label 'odoo19-demo'
    }

    environment {
        DEPLOY_DIR = '/opt/odoo19/custom_addons/odoo19-invisible-bed-demo'
    }

    stages {

        stage('Checkout') {
            steps {
                git branch: 'main',
                    url: 'https://github.com/satheeshkumar22/odoo19-invisible-bed.git'
            }
        }

        stage('Deploy') {
            steps {
                sh '''
                    echo "Deploying module..."

                    mkdir -p ${DEPLOY_DIR}

                    rsync -av --delete \
                    ${WORKSPACE}/ \
                    ${DEPLOY_DIR}/
                '''
            }
        }

        stage('Restart Odoo') {
            steps {
                sh '''
                    sudo systemctl restart odoo19
                '''
            }
        }

    }

    post {
        success {
            echo 'Deployment Successful'
        }

        failure {
            echo 'Deployment Failed'
        }
    }
}
