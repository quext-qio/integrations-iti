@Library('quext-shared-library') _

git_repo_creds = [$class: 'UsernamePasswordMultiBinding', credentialsId: 'quext-github', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_PASSWORD']
List stop_branches_list = ['stage', 'prod']
List envsToBuildAndDeploy = ['dev','qa']
List envs = envsToBuildAndDeploy + stop_branches_list
ecr_repository_uri = '273056594042.dkr.ecr.us-east-1.amazonaws.com/integration/api'
defaultRegion = "us-east-1"
DEPLOY_ENVIRONMENT = 'none'
shared_services_account_id = '273056594042'

branch_env = [
        "dev"   : 'dev'
    ]
accounts = [
            "dev"  : "633546161654"
    ]

pipeline {
    agent { label 'jenkins-spot-fleet'}
    options {
        buildDiscarder(logRotator(numToKeepStr: '100'))
        timeout(time: 20, unit: 'MINUTES')
        ansiColor('xterm')
        timestamps()
        disableConcurrentBuilds()
    }
    parameters {
        choice(
          name: 'ENVIRONMENT',
          choices:  ['dev'],
          description: 'Environment to deploy',
        )
    }
    stages {
        stage('Initialization') {
            when {
                beforeAgent true
                expression{
                    return !params.ENVIRONMENT.equals('none') || branch_env.containsKey(env.BRANCH_NAME)
                }
            }
            steps {
                script {
                    if (params.ENVIRONMENT.equals('none')){
                        DEPLOY_ENVIRONMENT = branch_env.get(env.BRANCH_NAME, 'NONE')
                    }
                    else {
                        DEPLOY_ENVIRONMENT = params.ENVIRONMENT
                    }
                    currentBuild.displayName = "#${BUILD_NUMBER} Environment: ${DEPLOY_ENVIRONMENT}"
                    env.ACCOUNT_ID = accounts.get(DEPLOY_ENVIRONMENT)
                    env.REGION = defaultRegion
                    env.imageTag = "${DEPLOY_ENVIRONMENT}-${BRANCH_NAME}"
                    // jenkinsRole = "arn:aws:iam::${ACCOUNT_ID}:role/devops-test-cdk"
                    // def AWS_KEYS = sh(returnStdout: true, script: """
                    //     aws sts assume-role --role-arn $jenkinsRole \
                    //     --role-session-name cdk \
                    //     --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]' \
                    //     --output text""")
                    
                    // AWS_KEYS = AWS_KEYS.split("\\s+")
                    // env.AWS_ACCESS_KEY_ID=AWS_KEYS[0]
                    // env.AWS_SECRET_ACCESS_KEY=AWS_KEYS[1]
                    // env.AWS_SESSION_TOKEN=AWS_KEYS[2]
                }
            }
        }
        stage("Build image") {
            when {
                allOf {
                    expression { 
                        envs.contains(DEPLOY_ENVIRONMENT) 
                    }
                    anyOf {
                        changeset "Dockerfile"
                        changeset "requirements.txt"
                    }
                }
            }
            steps {
                script { 
                    sh """
                        aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 273056594042.dkr.ecr.us-east-1.amazonaws.com
                        docker build -t ${ecr_repository_uri}:${imageTag} .
                        docker push ${ecr_repository_uri}:${imageTag}
                    """
                }
            }
        }        
        stage('CDK deploy') {
            when {
                expression { 
                    envs.contains(DEPLOY_ENVIRONMENT) 
                }
            }
            steps {
                script {
                    sh "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 273056594042.dkr.ecr.us-east-1.amazonaws.com"
                    docker.image("${ecr_repository_uri}:${imageTag}").inside() {
                    jenkinsRole = "arn:aws:iam::${ACCOUNT_ID}:role/devops-test-cdk"
                    def AWS_KEYS = sh(returnStdout: true, script: """
                        aws sts assume-role --role-arn $jenkinsRole \
                        --role-session-name cdk \
                        --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]' \
                        --output text""")
                    AWS_KEYS = AWS_KEYS.split("\\s+")
                    env.AWS_ACCESS_KEY_ID=AWS_KEYS[0]
                    env.AWS_SECRET_ACCESS_KEY=AWS_KEYS[1]
                    env.AWS_SESSION_TOKEN=AWS_KEYS[2]
                    sh "ROLE_ARN=arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters"
                    sh "export STAGE=${DEPLOY_ENVIRONMENT}"
                    //sh "cdk synth"
                    sh "cdk deploy --all --require-approval never --toolkit-stack-name quext-${DEPLOY_ENVIRONMENT}-integrationApi-cdk-toolkit --progress bar --trace true -vv"
                    }
                }
            }
        }     
    }
}