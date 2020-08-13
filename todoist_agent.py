import todoist
from email2do import generic_task

class TodoistTask(generic_task):
    def __init__(self,given_task, proj_list):
        # Import the generic_task 
        super().__init__()

        
        # Initializes the properties of the generic_task class
        # self.project = None        # Initializes the 'project' property as None 
        # self.title = None          # Initializes the 'title' property as None 
        # self.description = None    # Initializes the 'description' property as None     
        # self.due_in = None         # Initializes the 'due' property as None 
        # self.priority = None       # Initializes the 'priority' property as None     
        # self.due_date = None       # Initializes the 'due_date' property as None     
        
        # Set due date of the task
        self.due_date = given_task.due_date.strftime('%d-%b-%Y %H:%M:%S')
        
        # If the task is a complex task - with subtasks, etc
        if given_task.create_project is True:
            self.create_project = given_task.create_project

        # Routine for regular tasks
        if given_task.from_toml is False:
            #Update Todoist Task Project and Title    
            self.project, self.title = self.set_task_project_and_title(given_task, proj_list)

            #Update Todoist Task Due date    

            #Update Todoist Task priority        
            self.priority = self.set_task_priority(given_task)

        # Routine for regular tasks
        else:
            self.create_project = True
            
            #Update Todoist Task Project and Title    
            self.project, self.parent = self.set_task_project_and_title(given_task, proj_list)

            #Update Todoist Task Due date    
            self.due_date = given_task.due_date.strftime('%d-%b-%Y %H:%M:%S')


            #Update Todoist Task priority        
            self.priority = self.set_task_priority(given_task)

        # Default priority values
        self.NO_priority = 0 # Not an important task
        self.LOW_priority = 1
        self.NORMAL_priority = 2
        self.HIGH_priority = 3
        self.VERY_HIGH_priority = 4

    def set_task_priority(self,given_task):
        
        if given_task.priority == '0':
            task_priority = self.NO_priority # Not an important task
        elif given_task.priority == '1':
            task_priority = self.LOW_priority
        elif given_task.priority == '2':
            task_priority = self.NORMAL_priority
        elif given_task.priority == '3':
            task_priority = self.HIGH_priority
        elif given_task.priority == '4':
            task_priority = self.VERY_HIGH_priority

        else: # Default priority - If no priority is specified
            task_priority = self.NORMAL_priority
            print('Specified priority not supported - changed to Normal')
        
        return task_priority


    def set_task_project_and_title(self,given_task,proj_list):
        temp_project_id = None
        temp_title = None
        
        # Update Todoist Task and Project
        if given_task.project.upper() not in proj_list:
            temp_title = 'Proj_not_found : ' + given_task.title
            temp_project_id = proj_list['Inbox']

        else:
            temp_title = given_task.title
            temp_project_id = proj_list[given_task.project.upper()]

        return temp_project, temp_title


class todoistAgent: # This agent is responsible for interacting with Todoist API
    def __init__(self,todoist_token):
        self.user = todoist.TodoistAPI(todoist_token)

        # Define the tasker (todoist agent to interact with todoist states)
        self.tasker = self.user.state

        # Defining the agent attributes 
        # (All these attributes should be updated in the sync routine)
        self.root_projects = None
        # TODO: should be a master list of all the projects - including children
        self.proj_refs = None # WIP
        
        
        # Update the api record to the latest
        self.sync() 

    def sync(self): # Sync the API with the server
        _ = self.user.sync() # Update the api record to the latest
        
        #Update the project references
        self.root_projects = self.get_all_root_projs()        
        
        
    def get_all_root_projs(self): # Generate a list of projects (with their mapped IDs) available from Todoist
        projects = {}
        
        for project in self.tasker['projects']:
            if project['parent_id'] == None:
                projects[project['name']] = project['id']
                    
        return projects
        
        
    # Todoist agent to initialize the root_parent
    def process_tasker(self, given_task):
        if given_task.task_type == 'template': # The current tasks creates a sub-folder
            given_task.parent_id = self.root_projects[given_task.parent]
        elif given_task.task_type == 'task':
            if given_task.project == '':
                given_task.parent_id = self.root_projects['Inbox']
            else:
                given_task.parent_id = self.root_projects[given_task.project]

        # Process the todoist tasks
        self.process_tasks(given_task, given_task.parent_id)


    # Todoist agent to add the task
    def process_tasks(self, given_task, parent_id):
        if given_task.task_type == 'template': # The current tasks creates a sub-folder
            new_proj_id = self.create_new_proj(given_task.project, parent_id = parent_id)
            
            for task in given_task.sub_tasks:
                self.process_tasks(task, new_proj_id)
        
        elif given_task.task_type == 'task':
            given_task.parent_id = parent_id
            self.send_task_to_todoist(given_task)

        else:
            print('Incompatible Task Type - Cannot Process')
            

    # Todoist agent to add the task
    def send_task_to_todoist(self, given_task):
        # If Project_name for the given task is not in self.projects - Add an "Proj_not_found" string to the task title
        # and set the project name to None
        
        # todoist_task = TodoistTask(given_task, self.root_projects.keys())        
        temp_item = self.user.items.add(content = given_task.title, 
                                  due = {"string": given_task.due_date}, 
                                  priority = given_task.priority,
                                  project_id = given_task.parent_id)
        
        self.user.commit()
        self.sync()


    # Create a new project within another or at the root
    def create_new_proj(self, new_proj_name, **kwargs):
        
        # Using Main project title (recommended only for unique project names - also case sensitive)
        if 'parent' in kwargs.keys():
            parent_id = self.root_projects[kwargs['parent']]
            temp_project = self.user.projects.add(new_proj_name, parent_id = parent_id)
            
        # Using Main project title (recommended only for unique project IDs - also case sensitive)
        elif 'parent_id' in kwargs.keys():
            temp_project = self.user.projects.add(new_proj_name, parent_id = kwargs['parent_id'])
            
        # New project in the root folder
        else:
            temp_project = self.user.projects.add(new_proj_name)
        
        # Update the changes to the online server
        response = self.user.commit()
        self.user.sync()

        return response['projects'][0]['id']
    
    
    def get_proj_refs(self): # Generate a list of projects (with their mapped IDs) available from Todoist
        projects = {}
        
        for project in self.tasker['projects']:
            self.proj_refs[project['id']] = todoist_proj(project)
                    
        return projects
    
        
# TODO: Develop the todoist_proj class : should allow accessing any project with its children iteratively
# TODO: Is this a relevant feature?
class todoist_proj:
    def __init__(self, project):
        self.id = project.id
        self.name = project.name
        self.parent_id = project.parent_id
        self.children = []
        