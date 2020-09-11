//  Archivo Jenkinsfile para proyecto emotional-health-service
//
//  by: Yudy Ramírez

def microservicio = "emotional-health-service"

def PROJECT_ID = "covidpass-desarrollo"
def PROJECT_ID_QA = "covidpass-laboratorio"
def PROJECT_ID_PROD = "covidpass-produccion"

def CLUSTER_DEV = "o3p-covidpassk8spriv-d01"
def CLUSTER_DEV_REGION = "us-central1"

def CLUSTER_QA = "o3p-covidpassk8spriv-l01"
def CLUSTER_QA_REGION = "us-central1"

def CLUSTER_PROD = "o3p-covidpassk8spriv-p01"
def CLUSTER_PROD_REGION = "us-central1"
 
def PROJECT_ID_REF = "dev-qrcovidpass"
def PROJECT_ID_REF_QA = "qa-qrcovidpass"
def PROJECT_ID_REF_PROD = "prod-qrcovidpass"

def imageTag = "gcr.io/${PROJECT_ID}/${JOB_NAME}:${BUILD_NUMBER}"
def imageTag_Ref = "gcr.io/${PROJECT_ID_REF}/${JOB_NAME}:${BUILD_NUMBER}"


pipeline {
  options {
    timeout(time: 20, unit: 'MINUTES')
  }
  agent {
    kubernetes {
      label "${microservicio}-slave"
      defaultContainer 'jnlp'
      yaml """
apiVersion: v1
kind: Pod
metadata:
  labels:
    component: ci
spec:
  resources:
    limits:
      cpu: 3.0
      memory: 7G
      ephemeral-storage: 15360M
    requests:
      cpu: 2.5
      memory: 5G
      epehemeral-storage: 13312M
  serviceAccount: cd-jenkins
  volumes:
  - name: dockersock
    hostPath:
      path: "/var/run/docker.sock"
  - name: docker
    hostPath:
      path: "/usr/bin/docker"
  - name: google-cloud-key
    secret:
      secretName: registry-jenkins
  containers:
  - name: gcloud
    image: gcr.io/cloud-builders/gcloud
    volumeMounts:
    - name: google-cloud-key
      readOnly: true
      mountPath: "/var/secrets/google"
    - name: docker
      mountPath: "/usr/bin/docker"
    - name: dockersock
      mountPath: "/var/run/docker.sock"
    command:
    - cat
    env:
    - name: GOOGLE_APPLICATION_CREDENTIALS
      value: /var/secrets/google/key.json
    tty: true
  - name: node
    image: node:lts-alpine
    env:
    - name: NO_PROXY
      value: "localhost, 0.0.0.0/4201, 0.0.0.0/9876"
    - name: CHROME_BIN
      value: /usr/bin/chromium-browser
    resources:
      requests:
        cpu: 800m
        memory: 1024Mi
      limits:
        cpu: 1
        memory: 2048Mi
    command:
    - cat
    tty: true
  - name: docker
    image: docker:18.09
    volumeMounts:
    - name: google-cloud-key
      readOnly: true
      mountPath: "/var/secrets/google"
    - name: docker
      mountPath: "/usr/bin/docker"
    - name: dockersock
      mountPath: "/var/run/docker.sock"
    command:
    - cat
    env:
    - name: GOOGLE_APPLICATION_CREDENTIALS
      value: /var/secrets/google/key.json
    tty: true
"""
    }
  }
  environment {
    COMMITTER_EMAIL = sh (
      returnStdout: true,
      script: 'git --no-pager show -s --format=\'%ae\''
    ).trim()
    TAG_NAME = sh (
      returnStdout: true,
      script: 'git tag --points-at HEAD | awk NF'
    ).trim()
  }
  stages {

    stage('Initialize') {
      steps {
        container('docker') {
          sh "apk update"
          sh "apk add curl"
          sh "curl -fsSL https://github.com/GoogleCloudPlatform/docker-credential-gcr/releases/download/v2.0.0/docker-credential-gcr_linux_amd64-2.0.0.tar.gz | tar xz --to-stdout ./docker-credential-gcr > /usr/bin/docker-credential-gcr && chmod +x /usr/bin/docker-credential-gcr"
          sh "docker-credential-gcr configure-docker"
          sh 'docker --version'
        }
        container('gcloud') {
          // sh 'gcloud components update'
          sh 'gcloud auth activate-service-account --key-file=$GOOGLE_APPLICATION_CREDENTIALS'
          sh "gcloud config set project ${PROJECT_ID}"
        }
        container('python') {
        //  sh 'pip install coverage'
        //  sh 'pip install -r requirements.txt'
        }
      }
    }

    stage('Test') {
      steps {
        container('python') {
            echo "skiping tests"
        //   sh 'python manage.py test'
        //   sh 'coverage run manage.py test'
        //   sh 'mkdir coverage'
        //   sh 'coverage html -d ./coverage/coverage.html'
        }
      }
    }

    stage('Build') {
     when {
        not {
          anyOf{
            branch 'refactor'
            branch 'refactor_qa'
             branch 'refactor_prod'
          }
        }
      }

      steps {
        container('docker') {
          sh 'docker build --tag=${JOB_NAME}:${BUILD_NUMBER} .'
          sh 'docker images'
          sh "docker tag ${JOB_NAME}:${BUILD_NUMBER} gcr.io/${PROJECT_ID}/${JOB_NAME}:${BUILD_NUMBER}"
          sh "docker push gcr.io/${PROJECT_ID}/${JOB_NAME}:${BUILD_NUMBER}"
        }
      }
    }
    
    
    stage('Build Refactor') {
       when { anyOf{
            branch 'refactor'
            branch 'refactor_qa'
             branch 'refactor_prod'
          }
           }
        steps {
          container('docker') {
            sh 'docker build --tag=${JOB_NAME}:${BUILD_NUMBER} .'
            sh 'docker images'
            sh "docker tag ${JOB_NAME}:${BUILD_NUMBER} gcr.io/${PROJECT_ID_REF}/${JOB_NAME}:${BUILD_NUMBER}"
            sh "docker push gcr.io/${PROJECT_ID_REF}/${JOB_NAME}:${BUILD_NUMBER}"
          }          
      }
    }




    stage('Deploy DEV') {
      when { branch 'develop' }
      steps {
        container('gcloud') {
          sh "gcloud container clusters get-credentials ${CLUSTER_DEV} --region ${CLUSTER_DEV_REGION} --project ${PROJECT_ID}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          sh "sed -i.bak 's#{imageTag}#${imageTag}#' despliegues/desarrollo/${microservicio}/deployment.yaml"
          sh "kubectl apply -f despliegues/desarrollo/${microservicio}/deployment.yaml"
        }
      }
    }

  stage('Deploy refactor') {
      when { branch 'refactor' }
      steps {
        container('gcloud') {
           sh "gcloud container clusters get-credentials dev-qrcovidpass --zone us-central1-a --project ${PROJECT_ID_REF}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          echo '---- VERIFICACION ESTRUCTURA DIRECTORIOS ----'
          sh 'ls'
          echo '---- VERIFICACION DIRECTORIO DE DESPLIEGUE ----'
          sh 'ls despliegues/refactor/${microservicio}/'
          echo '----------------------------------------------'
          sh "sed -i.bak 's#{imageTag}#${imageTag_Ref}#' despliegues/refactor/${microservicio}/deployment.yaml"
          sh 'kubectl apply -f despliegues/refactor/${microservicio}/deployment.yaml'
        }
  

      }
    }

 stage ('Aprobacion Refactor QA') {
      when { branch 'refactor_qa'}
      steps {
        timeout (time:5, unit:'DAYS') {
          input message: 'Aprueba Despliegue Ambiente QA?',
          submitter: 'DevOps'
        }
      }
    }
    
stage('Deploy REFACTOR QA') {
      when { branch 'refactor_qa' }
      steps {
        container('gcloud') {
          sh "gcloud container clusters get-credentials qa-k8s-qrcovid --zone us-east1-b --project ${PROJECT_ID_REF_QA}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          sh "sed -i.bak 's#{imageTag}#${imageTag_Ref}#' despliegues/refactor_qa/${microservicio}/deployment.yaml"
          sh "kubectl apply -f despliegues/refactor_qa/${microservicio}/deployment.yaml"
        }
       }
    }


stage ('Aprobacion Refactor PROD') {
      when { branch 'refactor_prod'}
      steps {
        timeout (time:5, unit:'DAYS') {
          input message: 'Aprueba Despliegue Ambiente PROD?',
          submitter: 'DevOps'
        }
      }
    }
    
stage('Deploy REFACTOR PROD') {
      when { branch 'refactor_prod' }
      steps {
        container('gcloud') {
          sh "gcloud container clusters get-credentials prod-k8s-qrcovid --region us-central1 --project ${PROJECT_ID_REF_PROD}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          sh "sed -i.bak 's#{imageTag}#${imageTag_Ref}#' despliegues/refactor_prod/${microservicio}/deployment.yaml"
          sh "kubectl apply -f despliegues/refactor_prod/${microservicio}/deployment.yaml"
        }
       }
    }

    
    stage ('Aprobacion QA') {
      when { branch 'qa'}
      steps {
        timeout (time:5, unit:'DAYS') {
          input message: 'Aprueba Despliegue Ambiente QA?',
          submitter: 'DevOps'
        }
      }
    }

    stage('Deploy QA') {
      when { branch 'qa' }
      steps {
        container('gcloud') {
          sh "gcloud container clusters get-credentials ${CLUSTER_QA} --region ${CLUSTER_QA_REGION} --project ${PROJECT_ID_QA}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          sh "sed -i.bak 's#{imageTag}#${imageTag}#' despliegues/qa/${microservicio}/deployment.yaml"
          sh "kubectl apply -f despliegues/qa/${microservicio}/deployment.yaml"
        }
      }
    }

    stage ('Aprobacion PROD') {
      when { branch 'master'}
      steps {
        timeout (time:5, unit:'DAYS') {
          input message: 'Aprueba Despliegue Ambiente produccion?',
          submitter: 'DevOps'
        }
      }
    }

    stage('Deploy PROD') {
      when { branch 'master' }
      steps {
        container('gcloud') {
          sh "gcloud container clusters get-credentials ${CLUSTER_PROD} --region ${CLUSTER_PROD_REGION} --project ${PROJECT_ID_PROD}"
          withCredentials([usernamePassword(credentialsId: 'Jenkins-GitLab', passwordVariable: 'password', usernameVariable: 'username')]) {
            sh "git clone https://$username:$password@git.co.davivienda.com/qrcovidpass/servinformacion/devops/despliegues.git"
          }
          sh "sed -i.bak 's#{imageTag}#${imageTag}#' despliegues/produccion/${microservicio}/deployment.yaml"
          sh "kubectl apply -f despliegues/produccion/${microservicio}/deployment.yaml"
        }
      }
    }
  }
  post {
    always {
      echo 'Pipeline Finalizado'
    }
    aborted {
      echo 'Pipeline Cancelado'
    }
    failure {
      echo 'Pipeline Fallido'
    }
    success {
      echo 'Pipeline Exitoso'
    }
  }
}
