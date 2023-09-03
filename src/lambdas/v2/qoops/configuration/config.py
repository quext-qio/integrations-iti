import os
import json

# Jira configuration
jira_config = {
    'server_url': 'https://quext.atlassian.net/',
    'reporter_email':'cs.noreply@onequext.com',
    'token': os.environ["JIRA_REPORTER_TOKEN"],
}

priorities = {
    1: "1: Lowest / Trivial",
    2: "2: Low / Annoying",
    3: "3: Medium / Problematic",
    4: "4: High / Critical",
    5: "5: Highest / Blocker"
}

whitelist = ["zato", "monitoring"] 