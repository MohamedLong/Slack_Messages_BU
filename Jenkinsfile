pipeline {
    agent {
        label 'spring'
    }

    environment {
        SLACK_TOKEN = credentials('slack-token') // Use the credential ID for your Slack token
        NOTIFY_EMAIL = credentials('email') // Use the credential ID for your notification email
    }

    stages {
        stage('Checkout Repository') {
            steps {
                // Clone the GitHub repository containing the backup script
                git branch: 'main', credentialsId: 'long_jenkins', url: 'https://github.com/MohamedLong/Slack_Messages_BU.git'
            }
        }

        stage('Install Dependencies') {
            steps {
                script {
                    // Install any required dependencies (e.g., using pip for Python)
                    sh 'pip install -r requirements.txt'
                }
            }
        }

        stage('Run Backup Script') {
            steps {
                script {
                    // Set the environment variable for the Slack token and run the backup script
                    sh '''
                    export SLACK_TOKEN=${SLACK_TOKEN}
                    python3 main.py
                    '''
                }
            }
        }
    }

    post {
        always {
            // Archive backup files or perform any cleanup if necessary
            archiveArtifacts artifacts: '**/*.json', allowEmptyArchive: true
            emailext subject: 'Jenkins Build: ${currentBuild.fullDisplayName}',
                    attachLog: true,
                    body: 'Build finished with status: ${currentBuild.currentResult}\nCheck details at: ${env.BUILD_URL}',
                    recipientProviders: [
                        [$class: 'CulpritsRecipientProvider'],
                        [$class: 'DevelopersRecipientProvider'],
                        [$class: 'RequesterRecipientProvider']
                    ],
                    to: '${NOTIFY_EMAIL}'
        }
    }
}
