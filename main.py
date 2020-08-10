#/*
#* This file is part of mail2task.
#*
#* Copyright (C) 2020 Rishabh Jain
#*
#* espanso is free software: you can redistribute it and/or modify
#* it under the terms of the GNU General Public License as published by
#* the Free Software Foundation, either version 3 of the License, or
#* (at your option) any later version.
#*
#* espanso is distributed in the hope that it will be useful,
#* but WITHOUT ANY WARRANTY; without even the implied warranty of
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#* GNU General Public License for more details.
#*
#* You should have received a copy of the GNU General Public License
#* along with espanso.  If not, see <https://www.gnu.org/licenses/>.
#*/


import email2do
from pytodoist_agent import todoistAgent
from init_file import *
from datetime import datetime

my_gmail = email2do.gmail_agent()
my_gmail.refresh_unread_threads()
# my_gmail.mark_as_read()

# Filter all the taks along with their due dates
tasker = email2do.emails2task(my_gmail.unread)

# Agent to use the Tasker to create tasks in specific applications
todoist_agent = todoistAgent(todoist_token)

# Send all the taks to Todoist
for given_task in tasker.all_tasks:
    todoist_agent.send_task_to_todoist(given_task)

# Mark all the emails analyzed as read
my_gmail.mark_as_read()

print('Tasks added to Todoist at: {}'.format(datetime.now().strftime('%d-%b-%Y %H:%M:%S')))