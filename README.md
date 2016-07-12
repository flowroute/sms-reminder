# Quickstart

### Prerequisites

The following must first be installed before you can use the Appointment Reminder service:

*	Docker
* 	Docker Compose ~ 1.7.1.

### Start the Appointment Reminder servers

1.	Start the Redis server:

	 	redis-server

2.	Start the Celery server:

	 	celery worker -A appointment_reminder.tasks.celery --loglevel=INFO
	 
3.	Start the reminder server:

	 	python -m appointment_reminder.service

##### Create a new appointment reminder request

*	Pass the following to create a reminder request:

		curl -v -X POST -d '{"contact_number":12223334444, "appointment_time": "2016-07-06T15:23-0800",  "notify_window":"1", "location":"West Side Mechanics"}' -H "Content-Type: application/json" http://192.168.99.100:8000/reminder
	
	A successful POST returns the following:
	
    	{"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "successfully created a reminder with id 00795872bc554893bde41f3f9cb807d0"}

##### Retrieve a reminder list:

*	Pass the following to retrieve a list of reminders:

		curl -X GET "http://192.168.99.100:8000/reminder"

	A successful GET returns the following:
	
  		{"reminders": [{"contact_number": "12069928996", "participant": null, "location": "West Side Mechanics", "reminder_id": "00795872bc554893bde41f3f9cb807d0", "appt_user_dt": "2016-11-07 16:15:00", "will_attend": null, "notify_sys_dt": "2016-11-07 22:15:00", "sms_sent": false, "appt_sys_dt": "2016-11-07 23:15:00"}]}

##### Retrieve a single reminder:

*	Pass the following to retrieve a single reminder:

		curl -X GET http://192.168.99.100:8000/reminder/00795872bc554893bde41f3f9cb807d0

	A successful GET returns the following:
	
    	{"contact_number": "12069928996", "participant": null, "location": "West Side Mechanics", "reminder_id": "00795872bc554893bde41f3f9cb807d0", "appt_user_dt": "2016-11-07 16:15:00", "will_attend": null, "notify_sys_dt": "2016-11-07 22:15:00", "sms_sent": false, "appt_sys_dt": "2016-11-07 23:15:00"}

##### Delete a reminder:

*	Pass the following to delete a reminder:

		curl -v -X DELETE http://192.168.99.100:8000/reminder/00795872bc554893bde41f3f9cb807d0
  
	A successful GET returns the following:
	  
	  	{"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "successfully deleted reminder with id 00795872bc554893bde41f3f9cb807d0"}```


>**Appointment Reminder Notes**

>   - `will_attend` displays `null` if the user hasn't responded; otherwise, this will display a `yes` or `no` boolean if the user has responded.
>   - `sms_sent` indicates that the Celery task returned a 200 response from the Flowroute SMS API.
>   - `notify_sys_dt` is the appointment time converted to UTC, minus the time listed for the `notify_window`.
>  - `notify_window` is the time, in hours, before the appointment the user would like to be reminded (in hours).
>  - `appt_user_dt` is the user's local time.
