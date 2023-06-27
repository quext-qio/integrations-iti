git_repo_creds = [$class: 'UsernamePasswordMultiBinding', credentialsId: 'quext-github', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_PASSWORD']
List stop_branches_list = ['stage', 'prod']
List envsToBuildAndDeploy = ['dev','qa']
List envs = envsToBuildAndDeploy + stop_branches_list
defaultRegion = "us-east-1"
DEPLOY_ENVIRONMENT = 'none'
shared_services_account_id = '273056594042'
ecr_repository_uri = '273056594042.dkr.ecr.us-east-1.amazonaws.com/integration/api'

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
                    env.ecr_repository = "repository_uri"
                    env.ecr_tag = ${DEPLOY_ENVIRONMENT}-${BRANCH_NAME}
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
                    env.COMMON_CONFIGS = """ aws://${accounts.get(DEPLOY_ENVIRONMENT)}/${defaultRegion} --cloudformation-execution-policies arn:aws:iam::${ACCOUNT_ID}:policy/devops-test-cdk"""//--cloudformation-execution-policies arn:aws:iam::633546161654:role/devops-test-cdk --trust ${shared_services_account_id} --trust-for-lookup ${shared_services_account_id} --cloudformation-execution-policies ${jenkinsRole}"""
                }
            }
        }     
        stage("Build and Publish tagged Docker images") {
            when {
                allOf {
                    anyOf {
                        changeset "Dockerfile"
                        changeset "requirements.txt"
                    }
                    envs.contains(DEPLOY_ENVIRONMENT) 
                }                    
            }
            steps {
                script { 
                    docker_build_and_publish(ecr_tag, ecr_repository)
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
                    sh "env"
                    docker.image("${ecr_repository}:${ecr_tag}").inside() {
                    sh "export STAGE=${DEPLOY_ENVIRONMENT}"
                    sh "cdk deploy --all --require-approval never --toolkit-stack-name quext-${DEPLOY_ENVIRONMENT}-integrationApi-cdk-toolkit --progress bar --trace true"
                    }
                }
            }
        }     
    }
}