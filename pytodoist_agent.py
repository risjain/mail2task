#/*
#* This file is part of mail2task.
#*
#* Copyright (C) 2020 Rishabh Jain
#*
#* mail2task is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* mail2task is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with mail2task.  If not, see <https://www.gnu.org/licenses/>.
#*/


from pytodoist import todoist
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

        #Update Todoist Task Project and Title    
        self.project, self.title = self.set_task_project_and_title(given_task, proj_list)

        #Update Todoist Task Due date    
        self.due_date = given_task.due_date.strftime('%d-%b-%Y %H:%M:%S')

        #Update Todoist Task priority        
        self.priority = self.set_task_priority(given_task)


    def set_task_priority(self,given_task):
        
        if given_task.priority == '0':
            task_priority = todoist.Priority.NO # Not an important task
        elif given_task.priority == '1':
            task_priority = todoist.Priority.LOW
        elif given_task.priority == '2':
            task_priority = todoist.Priority.NORMAL
        elif given_task.priority == '3':
            task_priority = todoist.Priority.HIGH
        elif given_task.priority == '4':
            task_priority = todoist.Priority.VERY_HIGH

        else: # Default priority - If no priority is specified
            task_priority = todoist.Priority.NORMAL
            print('Specified priority not supported - changed to Normal')
        
        return task_priority

    def set_task_project_and_title(self,given_task,proj_list):
        temp_project = None
        temp_title = None
        
        # Update Todoist Task and Project
        if given_task.project.upper() not in proj_list:
            temp_title = 'Proj_not_found : ' + given_task.title
            temp_project = 'Inbox'

        else:
            temp_project = given_task.project.upper()
            temp_title = given_task.title

        return temp_project, temp_title


class todoistAgent(): # This agent is responsible for interacting with Todoist API
    def __init__(self,todoist_token):
        self.user = todoist.login_with_api_token(todoist_token)
        self.projects = self.user.get_projects()
        
        # I'm maintaining all the project names in CAPS - but there should be a better way to map projects to tasks
        # TODO: Mapping the tasks to projects Using user.projects object
        self.proj_list = self.gen_proj_list()
    
    def gen_proj_list(self): # Generate a list of projects available from Todoist
        proj_list = []
        for project in self.projects:
            proj_list.append(project.name)
        
        return proj_list
        
    # Todoist agent to add the task
    def send_task_to_todoist(self, given_task):
        # If Project_name for the given task is not in self.projects - Add an "Proj_not_found" string to the task title
        # and set the project name to None
        todoist_task = TodoistTask(given_task, self.proj_list)
        temp_project = self.user.get_project(todoist_task.project)
        _ = temp_project.add_task(todoist_task.title, date=todoist_task.due_date, priority=todoist_task.priority)
        