import os
from configparser import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser()

    def create_config(self, mode, scheduled_time, time, end_next_day, break_time, comment, project):
        self.config['General'] = {'mode': mode, 'scheduled_time': scheduled_time }
        self.config['Timesheet'] = {
            'start': time[0], 
            'end': time[1], 
            'end_next_day': end_next_day, 
            'break_time': break_time,
            'comment': comment,
            'project': project
        }

        overwrite = False
        if os.path.exists("./config.ini"):
            overwrite = True

        with open('./config.ini', 'w') as configfile:
            self.config.write(configfile)

        if overwrite:
            print('Configuration has been updated')
        else:
            print('Configuration has been created')

    def read_config(self, is_api):
        self.config.read('./config.ini')

        mode = self.config.get('General', 'mode')
        scheduled_time = self.config.get('General', 'scheduled_time')
        start = self.config.get('Timesheet', 'start')
        end = self.config.get('Timesheet', 'end')
        time = [start, end]
        end_next_day = self.config.getboolean('Timesheet', 'end_next_day')
        break_time = self.config.get('Timesheet', 'break_time')
        comment = self.config.get('Timesheet', 'comment')
        project = self.config.get('Timesheet', 'project')

        if is_api:
            return {
                'mode': mode,
                'scheduledTime': scheduled_time,
                'time': time,
                'endNextDay': end_next_day,
                'breakTime': break_time,
                'comment': comment,
                'project': project
            }
        else:
            return mode, scheduled_time, start, end, end_next_day, break_time, comment, project