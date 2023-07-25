from jira import JIRA
from datetime import date, datetime, timedelta

class JiraAutomation():

    #-----------------------------------------------------------------------------
    # Init method
    def __init__(self, project_name, server_url, reporter_email, token):
        self.project_name = project_name
        self.server_url = server_url
        self.reporter_email = reporter_email
        self.token = token
        self.jira = JIRA(
            basic_auth=(reporter_email, token),
            server=server_url,
        )
        self.issues = []

    #-----------------------------------------------------------------------------
    # Get all Jira issues
    def load_all_issues(self):
        self.issues = []
        i = 0
        chunk_size = 100
        while True:
            chunk = self.jira.search_issues(f'project={self.project_name}', startAt=i, maxResults=chunk_size, fields=["id", "status", "summary", "description", "comment", "reporter", "assignee", "labels", "creator"])
            i += chunk_size
            self.issues += chunk.iterable
            if i >= chunk.total:
                break
        return self.issues

    #-----------------------------------------------------------------------------
    # Search if exists an issue with same summary and status not Done by default
    def search_issue(self, summary, tickets, status="Done"):
        search_issue = None
        for i in tickets:
            if f"{i.fields.summary}" == summary and i.fields.status != status:
                search_issue = i
                break
        return search_issue

    #-----------------------------------------------------------------------------
    # Generate ticket if exist only will add commets of errors which aren't reported yet
    def generate_ticket(self, summary, description, comment_body, labels=[], issue_type='Bug'):
        tickets = self.load_all_issues() # Load all issues
        search_issue = self.search_issue(summary, tickets) # Search issue by summary
        # If find an issue in Jira
        if search_issue != None:
            array_engrain_issues = comment_body.split("\n") #Convert all issues in array by '\n'
            for engrain_issue in array_engrain_issues:
                # Flag to check if exist an comment with same error
                is_error_in_comment = False
                for comment in search_issue.fields.comment.comments:

                    # Validate if new error already exist into the comments
                    if engrain_issue in comment.body:
                        is_error_in_comment = True
                        break

                # If not exist a comment with issue information, add new comment
                if not is_error_in_comment:
                    self.jira.add_comment(search_issue, body=engrain_issue)

            return search_issue, False

        else:
            # Create a new issue
            today = date.today()
            future_date = today + timedelta(days=15)
            myself = self.jira.myself()
            issue_dict = {
                'project': {'key': self.project_name},
                'summary': summary,
                'description': description,
                'issuetype': {'name': issue_type}, 
                'duedate' : f"{future_date}",
                'labels': labels,
                'assignee': myself,
            }
            new_issue = self.jira.create_issue(fields=issue_dict, priority='Low')
            self.jira.add_comment(new_issue, body=comment_body)
            return new_issue, True