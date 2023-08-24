import os
import json

# Read environment variables
parameter_store = json.loads(os.environ.get("parameter_store"))

# Jira configuration
jira_config = {
    'server_url': 'https://quext.atlassian.net/',
    'reporter_email':'cs.noreply@onequext.com',
    'token': parameter_store["JIRA_REPORTER_TOKEN"],
}

priorities = {
    1: "1: Lowest / Trivial",
    2: "2: Low / Annoying",
    3: "3: Medium / Problematic",
    4: "4: High / Critical",
    5: "5: Highest / Blocker"
}

whitelist = ["zato", "monitoring"] 