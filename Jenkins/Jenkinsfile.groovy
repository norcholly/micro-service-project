pipeline {
    agent any
    
    environment {
        DOCKER_USER = "norcholly"
        IMAGE_NAME = "mikro-servis"
        TAG = "v${env.BUILD_NUMBER}"
    }
    
    stages {
        
        stage('Checkout') {
            steps {
                echo "GitHub deposundan en güncel kodlar çekiliyor..."
                git branch: 'main', url: 'https://github.com/norcholly/micro-service-project.git'
            }
        }
        
        stage('Docker Build') {
            steps {
                echo "Yeni versiyon imajı (${TAG}) üretiliyor..."

                // github deposundaki (varsa yenilikleri) yeni imaj olarak üretir
                sh 'docker build -t ${DOCKER_USER}/${IMAGE_NAME}:${TAG} .'
            }
        }
        
        stage('Docker Push') {
            steps {
                echo "İmaj Docker Hub'a gönderiliyor..."

                // docker'a yeni versiyon imajını yükler
                withCredentials([string(credentialsId: 'docker-hub-sifrem', variable: 'DOCKER_PASS')]) {
                    sh 'echo $DOCKER_PASS | docker login -u ${DOCKER_USER} --password-stdin'
                    sh 'docker push ${DOCKER_USER}/${IMAGE_NAME}:${TAG}'
                }
            }
        }
        
        stage('Deploy to Kubernetes') {
            steps {
                echo "Kubernetes'e yeni versiyonu sahaya sürme emri veriliyor..."

                // "sudo" gerektirmeden yetkili bir şekilde çalıştırabilecek
                withCredentials([file(credentialsId: 'k3s-gizli-dosya', variable: 'KUBECONFIG')]) {
                    
                    // eğer bu dosyalarda değişiklik varsa, o değişikliği uygular
                    dir('k3s') {
                        sh 'kubectl apply -f redis.yaml'
                        sh 'kubectl apply -f flask.yaml'
                    }

                    // eskileri kaldırırken yenileri ekler
                    sh 'kubectl set image deployment/flask-deployment flask-app=${DOCKER_USER}/${IMAGE_NAME}:${TAG}'
                }
            }
        }
    }
}
