from jira import JIRA
from datetime import date, datetime, timedelta
from configuration.config import priorities
from configuration.config import whitelist

class JiraAutomation():

    #---------------------------------------------------------------------------
    # Constructor method
    def __init__(self, project_name, server_url, reporter_email, token):
        """
        Initializes a new instance of the JiraAutomation class.
        :param project_name: The name of the Jira project to interact with.
        :param server_url: The URL of the Jira server.
        :param reporter_email: The email of the Jira reporter.
        :param token: The access token of the Jira reporter.
        """
        self.project_name = project_name
        self.server_url = server_url
        self.reporter_email = reporter_email
        self.token = token
        self.jira = JIRA(
            basic_auth=(reporter_email, token),
            server=server_url,
        )
        self.issues = []

    #---------------------------------------------------------------------------
    # Retrieves all Jira issues for the configured project
    def load_all_issues(self, summary, issue_type):
        self.issues = []
        i = 0
        chunk_size = 100
        while True:
            #chunk = self.jira.search_issues(f'project={self.project_name} and statusCategory!=Done and (labels in (Qoops) or reporter=63e683c682eeee78a4d3b20a)',  startAt=i, maxResults=chunk_size, fields=["id", "status", "summary", "description", "comment", "reporter", "assignee", "labels", "creator", "priority"])
            chunk = self.jira.search_issues(f'project={self.project_name} and summary ~ "{summary}" and issueType = {issue_type} and statusCategory!=Done',  startAt=i, maxResults=chunk_size, fields=["id", "status", "summary", "description", "comment", "reporter", "assignee", "labels", "creator", "priority"])
            i += chunk_size
            self.issues += chunk.iterable
            if i >= chunk.total:
                break
        return self.issues

    #---------------------------------------------------------------------------
    # Search for an issue by summary and status not "Done"
    def search_issue(self, summary, tickets, status="Done"):
        """
        Searches for a Jira issue with the given summary and status.
        :param summary: The summary of the issue to search for.
        :param tickets: The list of tickets to search.
        :param status: The status of the issue to search for (defaults to "Done").
        :return: The matching issue, if found; otherwise, None.
        """
        search_issue = None
        for i in tickets:
            if f"{i.fields.summary}" == summary and f"{i.fields.status}" != status:
                search_issue = i
                break
        return search_issue
    
    #---------------------------------------------------------------------------    
    def clean_strings(self, strings_list):
        """
        Clean a list of strings by removing special characters and replacing
        spaces with hyphens.
    
        Args:
            strings_list (list): A list of strings.
    
        Returns:
            list: A list of cleaned strings.
        """
    
        # Create a list to store the cleaned strings
        cleaned_list = []
    
        # Loop through each string in the input list
        for string in strings_list:
    
            # Remove special characters using the string method "isalnum()"
            # which returns "True" for alphanumeric characters and "False" for
            # all others.
            cleaned_string = ''.join(c for c in string if c.isalnum() or c == ' ')
    
            # Replace spaces with hyphens using the string method "replace()".
            cleaned_string = cleaned_string.replace(' ', '-')
    
            # Append the cleaned string to the output list
            cleaned_list.append(cleaned_string)
    
        # Return the list of cleaned strings
        if "Qoops" not in cleaned_list:
            cleaned_list.insert(0, "Qoops")
        return cleaned_list

    #---------------------------------------------------------------------------
    # Generates a new Jira issue if one does not exist
    def generate_ticket(self, summary, description, list_issues, priority, labels=["Qoops"],issue_type='Bug', testing=False):
        """
        Generates a new Jira issue if one with the same summary and status "Done" does not already exist.
        :param summary: The summary of the issue to generate.
        :param description: The description of the issue to generate.
        :param list_issues: A list of errors to add to the issue comments.
        :param priority: The priority of the issue to generate.
        :param labels: The labels to apply to the issue (defaults to ["Qoops"]).
        :param issue_type: The type of issue to generate (defaults to 'Bug').
        :return: A tuple containing the generated issue and a flag indicating whether or not it was generated.
        """
        
        for summary_to_skip in whitelist:
            if summary_to_skip.lower() in summary.lower():
                return "Service skipped", False
        
        tickets = self.load_all_issues(summary, issue_type)                                 # Load all issues
        search_issue = self.search_issue(summary, tickets)                      # Search issue by summary
        now = datetime.now()                                                    # datetime object containing current date and time
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")                           # dd/mm/YY H:M:S
        errors_for_description ="\n" + "\n".join(list_issues)
 
        necesary_notify = not testing
        if search_issue == None:                                                # If not exist an issue in Jira, will be created 
            today = date.today()
            future_date = today + timedelta(days=30)
            myself = self.jira.myself()
            issue_dict = {
                'project': {'key': self.project_name},
                'summary': summary,
                'description': f'{description} {errors_for_description}',
                'issuetype': {'name': issue_type}, 
                # 'duedate' : f"{future_date}",
                'labels': self.clean_strings(labels),
                'assignee': myself,
                'priority': {"name": priorities[priority]}
            }
            # TODO: Notify false if is testing purposes
            
            
            new_issue = self.jira.create_issue(fields=issue_dict, notify=necesary_notify)               # Create new issue
            for new_issue_reported in list_issues:                              # Add errors in comment section
                self.jira.add_comment(new_issue, body=f"{new_issue_reported} \n{dt_string}")
            return new_issue, True 
        
        data_priorit_by_name = dict((value,key) for key,value in priorities.items())
        actual_priority = data_priorit_by_name.get(f"{search_issue.fields.priority}", -1)
        print(f"actual_priority: {actual_priority}")
        
        new_priority = priority
        print(f"new_priority: {new_priority}")
        
        if new_priority > actual_priority:                                      # If user send priority with more high level will be update it
            search_issue.update(priority = {"name": priorities[priority]})
    
        for new_issue in list_issues:
            is_error_in_comment = False                                         # Flag to check if exist an comment with same error
            for comment in search_issue.fields.comment.comments:

                if new_issue in comment.body:                                   # Validate if new error already exist into the comments
                    is_error_in_comment = True                                  # Update flag to don't comment this error because already exist
                   
                    old_comment = comment.body                              # Save old comment for add new date and time reported
                    new_comment = f"{old_comment}, {dt_string}"
                    comment.update(body=new_comment, notify=False)          # Add new date in comment area
                    comment_dates = new_comment.split("\n")                 # Get dates from string
                    times_reported = len(comment_dates[1].split(","))       # Read times already reported
                    if times_reported % 5 == 0:                             # If times are mod 5 ?
                        # TODO: Call slack webhook every x times (Needs more info)
                        pass
            
            if not is_error_in_comment:                                         # If not exist a comment with issue information, add new comment
                self.jira.add_comment(search_issue, body=f"{new_issue}  \n{dt_string}")
        return search_issue, False
