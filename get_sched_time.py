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


from datetime import datetime, timedelta
import re

class date_agent: # Handles all the time related functionality
    def __init__(self, msg_sent_on):
        self.timestamp = msg_sent_on
        self.msg_year = self.timestamp.year
        self.msg_month = self.timestamp.month
        self.msg_day = self.timestamp.day
        self.msg_hr = self.timestamp.hour
        self.msg_min = self.timestamp.minute
        self.sched_msg_year = self.timestamp.year
        self.sched_msg_month = self.timestamp.month
        
    def sched_date(self,offset_str):
        
        offset = regex_time_offset(offset_str)
        
        if offset.type == 'Y':
            self.sched_msg_year += offset.length
            sched_time = datetime(self.sched_msg_year, self.msg_month, self.msg_day, self.msg_hr, self.msg_min)
            
        elif offset.type == 'M':
            self.sched_msg_month += offset.length
            if self.sched_msg_month > 12:
                year_offset, new_month = divmod(self.sched_msg_month, 12)
                self.sched_msg_year += year_offset
                self.sched_msg_month = new_month
        
            sched_time = datetime(self.sched_msg_year, self.sched_msg_month, self.msg_day, self.msg_hr, self.msg_min)
            
        
        else: 
            date_ref = dict(W=0,D=0,H=0) # For Month, Week, Day, Hour respectively
            date_ref[offset.type] = offset.length
        
            sched_time = self.timestamp + timedelta(weeks=date_ref['W'], days=date_ref['D'], hours=date_ref['H'])
        
        return sched_time


class regex_time_offset: # Handles all the regex related functionality
    def __init__(self,offset_str):
        self.time_pattern = "(([+-])(\d+)([HWYDM]))+"
        self.offset_str = offset_str
        self.type, self.length = self.parse_offset()
        
    def parse_offset(self):
        match = re.search(self.time_pattern, self.offset_str.upper())
        
        period_offset = int(match[3])
        period_offset_type = match[4]
        
        return period_offset_type, period_offset