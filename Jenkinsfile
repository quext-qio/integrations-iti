@Library('quext-shared-library') _

git_repo_creds = [$class: 'UsernamePasswordMultiBinding', credentialsId: 'quext-github', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_PASSWORD']
List stop_branches_list = ['stage', 'prod']
List envsToBuildAndDeploy = ['dev', 'qa', 'rc', 'stage', 'prod']
List envs = envsToBuildAndDeploy + stop_branches_list
ecr_repository_uri = '273056594042.dkr.ecr.us-east-1.amazonaws.com/integration/api'
defaultRegion = "us-east-1"
DEPLOY_ENVIRONMENT = 'none'
shared_services_account_id = '273056594042'

branch_env = [
        "dev"   : 'dev',
        "stage" : 'stage',
        "rc"    : 'rc',
        "qa"    : 'qa',
        "prod"  : 'prod',
    ]

accounts = [
            "dev"  : "633546161654",
            "stage": "323546893515",
            "qa"   : "633546161654",
            "rc"   : "323546893515",
            "prod" : "283107020475",
    ]

shared_stack = [
            "dev"    : 'dev',
            "qa"     : "dev",
            "rc"     : "stage",
            "stage"  : 'stage',
            "prod"   : 'prod',
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
          choices:  ['none'] + envsToBuildAndDeploy,
          description: 'Environment to deploy',
        )
        booleanParam(
          name: 'CDK destroy',
          defaultValue: false,
          description: 'CDK destroy command before deployment process',
        )           
        booleanParam(
          name: 'Rebuild image',
          defaultValue: false,
          description: 'Rebuild the base docker image to install the latest requirements and dependencies',
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
                        if (branch_env.containsKey('qa') || branch_env.containsKey('rc')){
                            DEPLOY_ENVIRONMENT = branch_env.get(env.BRANCH_NAME, 'NONE')
                            STACK = shared_stack.get(env.BRANCH_NAME, 'NONE')
                        }
                    }                
                    else {
                        if (params.ENVIRONMENT.equals('qa') || params.ENVIRONMENT.equals('rc')){
                            DEPLOY_ENVIRONMENT = params.ENVIRONMENT
                            STACK = shared_stack.get(params.ENVIRONMENT, 'NONE')
                        }
                        else {
                            DEPLOY_ENVIRONMENT = params.ENVIRONMENT
                            STACK = params.ENVIRONMENT
                        }                   
                    }
                    currentBuild.displayName = "#${BUILD_NUMBER} Environment: ${DEPLOY_ENVIRONMENT}"
                    env.ACCOUNT_ID = accounts.get(DEPLOY_ENVIRONMENT)
                    env.REGION = defaultRegion
                    env.imageTag = "latest"
                    env.STAGE = "${DEPLOY_ENVIRONMENT}"
                    env.ROLE_ARN = "arn:aws:iam::273056594042:role/cdk-integrationApi-get-ssm-parameters"
                    sh "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin 273056594042.dkr.ecr.us-east-1.amazonaws.com"
                }
            }
        }
        stage("Build image") {
            when {
                expression { params."Rebuild image" }
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
        stage('CDK destroy') {
            when {
                expression { params."CDK destroy" }
            }
            steps {
                script {
                    sh "echo ENVIRONMENT: $DEPLOY_ENVIRONMENT"
                    sh "echo STACK: $STACK"                    
                    docker.image("${ecr_repository_uri}:${imageTag}").inside() {
                        jenkinsRole = "arn:aws:iam::${ACCOUNT_ID}:role/quext-${STACK}-integrationApi-assume-role"
                        def AWS_KEYS = sh(returnStdout: true, script: """
                            aws sts assume-role --role-arn $jenkinsRole \
                            --role-session-name cdk \
                            --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]' \
                            --output text""")
                        AWS_KEYS = AWS_KEYS.split("\\s+")
                        env.AWS_ACCESS_KEY_ID=AWS_KEYS[0]
                        env.AWS_SECRET_ACCESS_KEY=AWS_KEYS[1]
                        env.AWS_SESSION_TOKEN=AWS_KEYS[2]
                        sh "cdk destroy --all --force --toolkit-stack-name quext-${STACK}-integrationApi-cdk-toolkit --progress bar --trace true -vvv"
                    }
                }
            }  
        }    
        stage('CDK deploy') {
            when {
                expression { 
                    envs.contains(DEPLOY_ENVIRONMENT) 
                }
            }
            stages {
                stage('Deploy approval'){
                    when {
                        expression { 
                            stop_branches_list.contains(DEPLOY_ENVIRONMENT)
                        }
                    }
                    steps {
                        input "Deploy to ${DEPLOY_ENVIRONMENT}?"
                    }
                }
                stage('deploy'){
                    steps {
                        script {
                            sh "echo ENVIRONMENT: $DEPLOY_ENVIRONMENT"
                            sh "echo STACK: $STACK"
                            withEnv(["STAGE=${DEPLOY_ENVIRONMENT}"]) {
                                docker.image("${ecr_repository_uri}:${imageTag}").inside() {
                                    if (params."CDK destroy" != true) {
                                        jenkinsRole = "arn:aws:iam::${ACCOUNT_ID}:role/quext-${STACK}-integrationApi-assume-role"
                                        def AWS_KEYS = sh(returnStdout: true, script: """
                                            aws sts assume-role --role-arn $jenkinsRole \
                                            --role-session-name cdk \
                                            --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]' \
                                            --output text""")
                                        AWS_KEYS = AWS_KEYS.split("\\s+")
                                        env.AWS_ACCESS_KEY_ID=AWS_KEYS[0]
                                        env.AWS_SECRET_ACCESS_KEY=AWS_KEYS[1]
                                        env.AWS_SESSION_TOKEN=AWS_KEYS[2]
                                    }
                                    sh "cdk deploy --all --verbose --require-approval never --toolkit-stack-name quext-${STACK}-integrationApi-cdk-toolkit --progress bar --trace true -vv"
                                }
                            }
                        }
                    }
                }
            }
        }
    }
    post{
        always {
            cleanWs()
        }
    }

}