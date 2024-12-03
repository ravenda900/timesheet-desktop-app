import datetime
import requests
from requests.auth import HTTPBasicAuth
import json
from logging.handlers import RotatingFileHandler
import logging
import calendar
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import schedule
import time

# Set up rotating log file
handler = RotatingFileHandler("logs/timesheet_entry.log", maxBytes=100000000,
                              backupCount=5)  # maxBytes is the size threshold, backupCount is the number of backup files
logging.basicConfig(
    handlers=[handler],
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
)

class Timesheet:
    def __init__(self, email, password, api):
        self.email = email
        self.password = password
        self.api = api
        
        self.user_key = self.get_myself()["key"]
        self.holidays = self.get_holidays()
        self.leaves = self.get_leaves()
        self.projects = self.get_projects()

    def scheduled_run(self):
        while True:
            print(self.api.has_configuration)
            if self.api.has_configuration():
                break

            time.sleep(1)

        self.mode, self.scheduled_time, self.start, self.end, self.end_next_day, self.break_time, self.comment, self.project = self.api.get_configuration(False)

        if self.mode == "Automatic":
            schedule.every().day.at(self.scheduled_time).do(self.init)

        while True:
            schedule.run_pending()
            time.sleep(1)

    def init(self):
        now = datetime.datetime.now()
        date = now.strftime("%Y-%m-%d")
        self.create_timesheet_entry(date)
        # self.show_missing_timesheet_entries(date)


    def get_working_days(self, user_key):
        contract_days = self.get_contract_days(user_key)

        return [x for x in contract_days if x["isWorkingDay"]]


    def show_missing_timesheet_entries(self, date):
        timesheet_entries = self.get_timesheet_entries(self.user_key)
        working_days = self.get_working_days(self.user_key)

        past_working_days = []
        for working_day in working_days:
            working_day_date = working_day["date"]
            working_date = datetime.datetime.strptime(working_day_date, "%Y-%m-%d")

            # Convert date to datetime
            check_date = datetime.datetime.strptime(date, "%Y-%m-%d")

            # Check if the date is in the past and not a holiday nor a leave
            if working_date <= check_date and not self.is_holiday(working_day_date, self.holidays) and not self.is_on_leave(
                    working_day_date, self.leaves):
                past_working_days.append(working_day_date)

        missing_timesheet_entries = []
        for past_working_day in past_working_days:
            # Check if a timesheet entry exists for this working day
            for timesheet_entry in timesheet_entries:
                timesheet_entry_date_timestamp = timesheet_entry["date"] / 1000
                timesheet_entry_date_obj = datetime.datetime.fromtimestamp(timesheet_entry_date_timestamp)
                timesheet_entry_date = timesheet_entry_date_obj.strftime("%Y-%m-%d")
                if timesheet_entry_date == past_working_day:
                    # Remove the found entry to optimize subsequent searches
                    timesheet_entries.remove(timesheet_entry)
                    break
            else:
                # If no matching entry was found, add to missing list
                missing_timesheet_entries.append(past_working_day)

        # we will not show the dialog if there are no missing entries
        if len(missing_timesheet_entries) == 0:
            return

        title = "Missing Timesheet Entries"
        text = f"You have {len(missing_timesheet_entries)} missing timesheet entries..."
        details = "\n".join([f"No timesheet entry found in {x}" for x in missing_timesheet_entries])

        self.send_email(title, text, details)


    def create_timesheet_entry(self, date):
        # do not create a timesheet entry if the current day is a holiday
        if self.is_holiday(date, self.holidays) or self.is_on_leave(date, self.leaves):
            return

        api_url = "https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/workspace"
        hours, minutes = map(int, self.break_time.split(":"))
        total_minutes = hours * 60 + minutes

        # Define the format for the time strings
        time_format = "%H:%M"
        # Parse the input times
        start = datetime.strptime(self.start, time_format)
        end = datetime.strptime(self.end, time_format)
        # Calculate the difference in minutes
        minutes = int((end - start).total_seconds() / 60)
        payload = {
            "wsId": None,
            "date": date,
            "workStart": self.start,
            "workEnd": self.end,
            "workPause": total_minutes,
            "comment": self.comment,
            "endIsNextDay": self.end_next_day,
            "submitStatus": 0,
            "items": [{
                "issueId": self.project,
                "workingTime": minutes,
                "comment": ""
            }],
            "userKey": self.user_key
        }
        headers = {"Content-Type": "application/json"}

        response = requests.post(api_url, data=json.dumps(payload), headers=headers, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully created a timesheet entry for {date}...")
        else:
            logging.error(f"Failed to create a timesheet entry for {date}...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")


    def is_holiday(self, date, holidays):
        found = False
        for holiday in holidays:
            if holiday["date"] == date:
                found = holiday
                break

        if found:
            logging.info(f"Holiday found in {date}: {found['name']}. Skipping creation of timesheet entry...")

        return found


    def is_on_leave(self, date, leaves):
        found = False
        for leave in leaves:
            if leave["status"]["name"] != "Approved" or leave["status"]["id"] != 1:
                continue

            start_timestamp = leave["startDate"] / 1000
            end_timestamp = leave["endDate"] / 1000

            # Convert timestamps to datetime
            start_date = datetime.datetime.fromtimestamp(start_timestamp)
            end_date = datetime.datetime.fromtimestamp(end_timestamp)

            # Convert date to datetime
            check_date = datetime.datetime.strptime(date, "%Y-%m-%d") + datetime.timedelta(hours=8)

            # Check if the date is within the range
            if start_date <= check_date <= end_date:
                found = leave

        if found:
            logging.info(f"Leave found in {date}: {found['leaveType']['name']}. Skipping creation of timesheet entry...")

        return found


    def get_first_and_last_day_of_the_month(self):
        # Get the current date
        today = datetime.date.today()

        # Get the first day of the current month
        first_day_of_month = today.replace(day=1)

        # Get the last day of the current month
        last_day_of_month = today.replace(day=calendar.monthrange(today.year, today.month)[1])

        return first_day_of_month, last_day_of_month


    def get_myself(self):
        api_url = f"https://issues.mycollab.co/rest/api/2/myself"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved current user info...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve current user info...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")


    def get_holidays(self):
        (first_day, last_day) = self.get_first_and_last_day_of_the_month()
        logging.info(f"Retrieving list of holidays for {first_day} - {last_day} date range")
        api_url = f"https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/holidays" \
                f"/{self.user_key}/{first_day}/{last_day}"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved holidays for {first_day} - {last_day} date range...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve holidays for {first_day} - {last_day} date range...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")


    def get_leaves(self):
        (first_day, last_day) = self.get_first_and_last_day_of_the_month()
        logging.info(f"Retrieving list of leaves for {first_day} - {last_day} date range")
        api_url = f"https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/leaves" \
                f"/{self.user_key}/{first_day}/{last_day}"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved leaves for {first_day} - {last_day} date range...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve leaves for {first_day} - {last_day} date range...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")


    def get_contract_days(self, user_key):
        (first_day, last_day) = self.get_first_and_last_day_of_the_month()
        logging.info(f"Retrieving list of contract days for {first_day} - {last_day} date range")
        api_url = f"https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/contract/days" \
                f"/{user_key}/{first_day}/{last_day}"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved contract days for {first_day} - {last_day} date range...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve contract days for {first_day} - {last_day} date range...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")


    def get_timesheet_entries(self, user_key):
        (first_day, last_day) = self.get_first_and_last_day_of_the_month()
        logging.info(f"Retrieving list of timesheet entries for {first_day} - {last_day} date range")
        api_url = f"https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/workspaces" \
                f"/{user_key}/{first_day}/{last_day}"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved timesheet entries for {first_day} - {last_day} date range...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve timesheet entries for {first_day} - {last_day} date range...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")

    def get_projects(self):
        current_date = datetime.datetime.now().strftime("%Y-%m-%d")
        current_timestamp = int(datetime.datetime.now().timestamp() * 1000)

        logging.info(f"Retrieving list of project issues for {current_date}")
        api_url = f"https://issues.mycollab.co/rest/com.easesolutions.jira.plugins.timesheet/latest/timesheet/bookableissues" \
                f"?userkey=petter.amaleona%40easesolutions.com&date={current_timestamp}"
        response = requests.get(api_url, auth=HTTPBasicAuth(self.email, self.password))

        # Check if the request was successful
        if response.status_code == 200:
            logging.info(f"Successfully retrieved project issues for {current_date}...")
            return response.json()
        else:
            logging.info(f"Failed to retrieve project issues for {current_date}...")
            logging.debug(f"Status code: {response.status_code}")
            logging.debug(f"Response: {response.text}")

    def send_email(self, title, text, details):
        # Create the message
        msg = MIMEMultipart()
        msg["From"] = self.email
        msg["To"] = self.email
        msg["Subject"] = title

        # Add the body of the email
        body = f"{text}\n\n" + details
        msg.attach(MIMEText(body, "plain"))

        server = smtplib.SMTP("smtp.office365.com", 587)  # Outlook SMTP server
        try:
            # Setup the server for Outlook
            server.starttls()  # Start TLS encryption
            server.login(self.email, self.password)  # Login to the email account

            # Send the email
            text = msg.as_string()
            server.sendmail(self.email, self.password, text)

            logging.info("Email sent successfully!")

        except Exception as e:
            logging.error(f"Failed to send email: {e}")

        finally:
            server.quit()