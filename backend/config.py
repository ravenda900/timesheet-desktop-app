import os
from configparser import ConfigParser

class Config:
    def __init__(self):
        self.config = ConfigParser()
        self.config_file = './config.ini'

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
        if os.path.exists(self.config_file):
            overwrite = True

        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

        if overwrite:
            print('Configuration has been overwritten')
        else:
            print('Configuration has been created')

    def read(self):
        self.config.read(self.config_file)

    def update_config(self, section, option, value):
        self.read()

        # Check if the section exists
        if not self.config.has_section(section):
            raise KeyError(f"Section '{section}' does not exist in the configuration file.")

        # Check if the option exists
        if not self.config.has_option(section, option):
            raise KeyError(f"Option '{option}' does not exist in the configuration file.")

        # Update the key-value pair
        self.config.set(section, option, value)

        # Write the updated configuration back to the file
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)

        print('Configuration has been updated')

    def get_config(self, section, option):
        self.read()
        
        return self.config.get(section, option)

    def read_config(self, is_api):
        self.read()

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