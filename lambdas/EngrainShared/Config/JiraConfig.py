import os

jira_config = {
    'project_name':'QINT',
    'server_url': 'https://quext.atlassian.net/',
    'reporter_email':'randald.villegas@oktara.com',
    'token': os.environ['ENGRAIN_JIRA_REPORTER_TOKEN'],
    'ticket_summary':'Automatic Issue from Engrain',
    'ticket_description':'This ticket is automatically generated for issues found in Engrain, see details in the comments.',
}