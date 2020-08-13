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


import ezgmail
import json
from pytodoist import todoist
import get_sched_time
import toml


class gmail_agent: # This agent is responsible for handling all email via gmail
    def __init__(self):
        self.reader = ezgmail
        self.user = ezgmail.EMAIL_ADDRESS
    

    def refresh_unread_threads(self,**kwargs):
        # read all unread threads    
        self.unread = self.reader.unread()
        
        # If the emails should be marked as read:        
        if 'mark_as_read' in kwargs.keys():
            if kwargs['mark_as_read'] is True:
                self.reader.markAsRead(self.unread)
        
        return
    

    def mark_as_read(self):
        # Mark all emails as read
        ezgmail.markAsRead(self.unread)
        print('All unread messages were marked as read')
        
        return                
    # def msg_handler(self):
        
class emails2task: # This agent is responsible for filtering out the tasks from the messages
    def __init__(self,unread_threads):
        self.all_msgs = unread_threads
        self.all_tasks = []
        self.find_new_tasks()
    
    
    def find_new_tasks(self):
        for thread in self.all_msgs:
            msg = thread.messages[0]
            self.msg2task(msg) # Parses the one_task_threadthread into the task
            
            # Email with subject as a JSON task

    def str2task(self,task_str,sent_on):
        # If the string is one task
        if task_str.startswith('{^project^:^') == True:
            # Parse the task
            temp_task = task(task_str = task_str, sent_on = sent_on)
            
            # Add the new task
            self.all_tasks.append(temp_task.from_task_str())

    def msg2task(self,msg):
        # If the msg is one task
        if msg.subject.startswith('{^project^:^') == True:
            task_str = msg.subject
            sent_on = msg.timestamp

            self.str2task(task_str,sent_on)

        # If the msg is a collection of multiple tasks
        elif msg.subject == 'add_all':
            sent_on = msg.timestamp
        
            # Parse the body of the message
            msg_body = msg.body    
            task_list = msg_body.split('\r\n')
            
            # Check each line of the body for tasks            
            for task_str in task_list:
                self.str2task(task_str, sent_on)

        # If the msg is a collection of multiple tasks as TOML
        elif msg.subject == 'add_toml':
            sent_on = msg.timestamp
        
            # Parse the body of the message
            msg_body = msg.body.replace('^','"')    
            toml_data = toml.loads(msg_body)
            
            self.toml2task(toml_data, sent_on, self.all_tasks)
    
    def toml2task(self, toml_data, sent_on, parent_task):
        '''
        Recursive function to convert the given Proj and its subtasks (from TOML) given the template into tasks

        Syntax of the TOML File
        =======================        
        [[proj_list]]
          parent = "Test"
          project = "to_be_created"

          [[proj_list.task]]
            due_in = "+4h"
            priority = "2"
            title = "Send the updated IOWA feeder files to Jose"
        
        and more such proj_list.task and proj_list entries
        # Each proj_list entry creates a new project, and all the subtasks are created within
        '''
        for given_proj in toml_data['proj_list']:
            temp_project = given_proj['project']
            temp_parent = given_proj['parent'].upper()

            # This is a complex task with one/more sub-tasks to be performed under the respective new sub-project that is created as a part
            task_to_do = task(task_str = None, sent_on = sent_on, project = temp_project, task_type = 'template', parent = temp_parent)

            # Travel the complex task for simple sub-tasks            
            for each_task in given_proj['task']:
                # Create a new sub-task
                temp_task = task(task_str=each_task['title'], sent_on=sent_on)
                
                # Update the respective attributes - due_in, project, priority, title
                temp_task.project = temp_project
                temp_task.__dict__.update(each_task)
                
                # Append the simple sub-task declarations to the main task
                task_to_do.sub_tasks.append(temp_task)           
            
            # Append the complex task to the list of tasks
            parent_task.append(task_to_do)
            
            ## Check if there are any sub-projects to be created
            ## TODO: This may not work well - especially with difficulty in finding the parent 
            ## TODO: This is likely if there are more than one sub-projects with the same description (more than one IDs - and unable to distinguish)
            ## TODO: May be best resolved in the respective agent
            if 'proj_list' in given_proj.keys():
                self.toml2task(given_proj['proj_list'], sent_on, task_to_do.sub_tasks)
        
        # Other cases can be added over time
        # return        
        
class generic_task: # This agent handles the task class - parses specific references to the common task object
    def __init__(self):
        # Define the default properties of the given task
        self.parent = None           # Initializes the 'parent' property as None  -- Relevant for create project like tasks
        self.project = None          # Initializes the 'project' property as None 
        self.title = None            # Initializes the 'title' property as None 
        self.description = None      # Initializes the 'description' property as None     
        self.due_in = None           # Initializes the 'due' property as None 
        self.priority = None         # Initializes the 'priority' property as None     
        self.due_date = None         # Initializes the 'due_date' property as None     
        self.sent_on = None          # Initializes the 'sent_on' property as None     
        self.from_toml = False       # Indicates if the task is based on a template - Default is 'False'
        self.task_type = 'task'      # :template, or :task - Indicates the type of a task (complex: template - includes multiple sub-tasks, or task - creation of a simple event)
        self.sub_tasks = []          # Indicates if the task has any sub-tasks (usually associated with a complex task)
        # Default priority values
        # self.NO_priority = 0 # Not an important task
        # self.LOW_priority = 1
        # self.NORMAL_priority = 2
        # self.HIGH_priority = 3
        # self.VERY_HIGH_priority = 4


class task(generic_task): # This agent handles the task class - parses specific references to the common task object
    def __init__(self, task_str, sent_on, **kwargs):        
        # Define the default properties of the given task
        super().__init__()
        # Initializes the properties of the generic_task class
        # self.project = None        # Initializes the 'project' property as None 
        # self.title = None          # Initializes the 'title' property as None 
        # self.description = None    # Initializes the 'description' property as None     
        # self.due_in = None         # Initializes the 'due' property as None 
        # self.priority = None       # Initializes the 'priority' property as None     
        # self.due_date = None       # Initializes the 'due_date' property as None     
        
        # Store the original string in the task class
        self.task_str = task_str
        self.sent_on = get_sched_time.date_agent(sent_on)
        
        # Add additional properties (used for creating new projects, etc)
        self.__dict__.update( kwargs )
            
    
    def from_task_str(self):
        self.task_json = self.str2json(self.task_str)
        self.from_json()
        
        return self
    
    def str2json(self,task_str):
        # Original json string def has ^ as the separators ; to be replaced with " before loading
        temp_dict = json.loads(self.task_str.replace('^','"'))
        
        return temp_dict
    
    def from_json(self):
        for k,v in self.task_json.items():
            setattr(self, k, v)
        
        # Update due date/time given the due_in property
        if self.due_in is not None:
            self.due_date = self.sent_on.sched_date(self.due_in)
            
        return self
    
    
