pipeline {
    agent {
        docker {
            image 'ubuntu:20.04'
            label 'docker'
            args '-u 1001:998 -v /usr/bin/docker:/usr/bin/docker -v /var/run/docker.sock:/var/run/docker.sock -v ${HOME}/.docker:${WORKSPACE}/.docker'
        }
    }

    environment {
        DOCKER_REPOSITORY = 'docker.velovec.pro/btc'
        DOCKER_CONFIG = "${env.WORKSPACE}/.docker"
    }

    options {
        buildDiscarder(logRotator(numToKeepStr: '15', daysToKeepStr: '30'))
    }

    stages {
        stage ('Build :: Build Artifacts') {
            steps {
                sh "docker build -t ${env.DOCKER_REPOSITORY}/supervisor-base:latest ."
            }
        }

        stage ('Promote') {
            when {
                branch 'master'
            }

            steps {
                sh "docker push ${env.DOCKER_REPOSITORY}/supervisor-base:latest"
            }
        }

        stage ('Build Downstream') {
            when {
                branch 'master'
            }

            steps {
                build "../bloomgenerator/master"
                build "../btcaddr_checker/main"
                build "../btcaddrgen/master"
            }
        }
    }

    post {
        always {
            sh 'docker rmi $(docker images -f dangling=true -q) || echo "No dangling images"'

            deleteDir()
        }
    }
}