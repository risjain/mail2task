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
        
class msg2task: # This agent is responsible for filtering out the tasks from the messages
    def __init__(self,unread_threads):
        self.all_msgs = unread_threads
        self.all_tasks = []
        self.find_new_tasks()
    
    
    def find_new_tasks(self):
        for thread in self.all_msgs:
            
            # Email with subject as a JSON task
            if thread.messages[0].subject.startswith('{^project^:^') == True:
                temp_task = task(msg = thread.messages[0])
                
                # Add the new task
                self.all_tasks.append(temp_task.from_json())
            
            # Other cases can be added over time
            
        return

class generic_task: # This agent handles the task class - parses specific references to the common task object
    def __init__(self):
        # Define the default properties of the given task
        self.project = None        # Initializes the 'project' property as None 
        self.title = None          # Initializes the 'title' property as None 
        self.description = None    # Initializes the 'description' property as None     
        self.due_in = None         # Initializes the 'due' property as None 
        self.priority = None       # Initializes the 'priority' property as None     
        self.due_date = None       # Initializes the 'due_date' property as None     
        self.sent_on = None       # Initializes the 'sent_on' property as None     


class task(generic_task): # This agent handles the task class - parses specific references to the common task object
    def __init__(self, msg):        
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
        self.task_str = msg.subject
        self.sent_on = get_sched_time.date_agent(msg.timestamp)
    
    def from_json(self):
        # Original json string def has ^ as the separators ; to be replaced with " before loading
        temp_dict = json.loads(self.task_str.replace('^','"'))
        for k,v in temp_dict.items():
            setattr(self, k, v)
        
        # Update due date/time given the due_in property
        if self.due_in is not None:
            self.due_date = self.sent_on.sched_date(self.due_in)
            
        return self