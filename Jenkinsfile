git_repo_creds = [$class: 'UsernamePasswordMultiBinding', credentialsId: 'quext-github', usernameVariable: 'GITHUB_USERNAME', passwordVariable: 'GITHUB_PASSWORD']
List stop_branches_list = ['stage', 'prod']
List envsToBuildAndDeploy = ['dev','qa']
List envs = envsToBuildAndDeploy + stop_branches_list
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
        // ansiColor('xterm')
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
                    env.CDK_ACCOUNT = accounts.get(DEPLOY_ENVIRONMENT)
                    env.CDK_REGION = defaultRegion
                    echo(env.CDK_ACCOUNT)
                    echo(env.CDK_REGION)
                    jenkinsRole = "arn:aws:iam::633546161654:role/quext-dev-zato-serverless-policy"
                    def AWS_KEYS = sh(returnStdout: true, script: """
                        aws sts assume-role --role-arn $jenkinsRole \
                        --role-session-name cdk \
                        --query '[Credentials.AccessKeyId,Credentials.SecretAccessKey,Credentials.SessionToken]' \
                        --output text""")
                    
                    AWS_KEYS = AWS_KEYS.split("\\s+")
                    env.AWS_ACCESS_KEY_ID=AWS_KEYS[0]
                    env.AWS_SECRET_ACCESS_KEY=AWS_KEYS[1]
                    env.AWS_SESSION_TOKEN=AWS_KEYS[2]
                    env.COMMON_CONFIGS = """ aws://${accounts.get(DEPLOY_ENVIRONMENT)}/${defaultRegion} --cloudformation-execution-policies arn:aws:iam::633546161654:policy/devops-test-cdk"""//--cloudformation-execution-policies arn:aws:iam::633546161654:role/devops-test-cdk --trust ${shared_services_account_id} --trust-for-lookup ${shared_services_account_id} --cloudformation-execution-policies ${jenkinsRole}"""
                    env.DEPLOY_SCRIPT = """cdk deploy --require-approval=never """
                    writeFile file: 'AWS', text: "AWS_ACCESS_KEY_ID=${env.AWS_ACCESS_KEY_ID}"+"\n"+"AWS_SECRET_ACCESS_KEY=${env.AWS_SECRET_ACCESS_KEY}"+"\n"+"AWS_SESSION_TOKEN=${env.AWS_SESSION_TOKEN}"
                }
            }
        }
        stage("Build image") {
            when {
                expression { 
                    envs.contains(DEPLOY_ENVIRONMENT) 
                }
            }
            steps {
                script { 
                    sh """
                        echo "Building image for ${DEPLOY_ENVIRONMENT}"
                        echo "docker build -t quext/${DEPLOY_ENVIRONMENT} ."
                        docker build -t quext/${DEPLOY_ENVIRONMENT} .
                    """
                }
            }
        }        
        // stage(('CDK bootstrap')) {
        //     when {
        //         expression { 
        //             envs.contains(DEPLOY_ENVIRONMENT) 
        //         }
        //     }
        //     steps {
        //         script {
        //             docker.image("quext/${DEPLOY_ENVIRONMENT}").inside() {
        //             sh "ls -lha"
        //             sh "cdk bootstrap ${env.COMMON_CONFIGS} --template cdk-zatoserverless-template.yaml --toolkit-stack-name quext-dev-zatoserverless --qualifier zatoapi --tags Project=Quext --tags Environment=${DEPLOY_ENVIRONMENT} --tags Team=Integration --tags Service=ZatoServerless"
        //             }
        //         }
        //     }
        // }
        stage('CDK synth') {
            when {
                expression { 
                    envs.contains(DEPLOY_ENVIRONMENT) 
                }
            }
            steps {
                script {
                    docker.image("quext/${DEPLOY_ENVIRONMENT}").inside() {
                    sh "cdk ls"
                    sh "cdk synth"
                    sh "cdk deploy --app cdk.out --all --require-approval never --toolkit-stack-name quext-dev-zato-serverless --progress bar --trace true"
                    }
                }
            }
        }     
    }
}