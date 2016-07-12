Quickstart:

Install docker, and docker-compose ~ 1.7.1

Start the redis server with ```redis-server```
Start the celery server with ```celery worker -A appointment_reminder.tasks.celery --loglevel=INFO```
Start the reminder server with ```python -m appointment_reminder.service```

Make a new appointment reminder request:
    ```curl -v -X POST -d '{"contact_number":12223334444, "appointment_time": "2016-07-06T15:23-0800",  "notify_window":"1", "location":"West Side Mechanics"}' -H "Content-Type: application/json" http://192.168.99.100:8000/reminder```
    Response:
    ```{"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "successfully created a reminder with id 00795872bc554893bde41f3f9cb807d0"}```

Retrieve a reminder list:
    ```curl -X GET "http://192.168.99.100:8000/reminder"```
    Response:
    ```{"reminders": [{"contact_number": "12069928996", "participant": null, "location": "West Side Mechanics", "reminder_id": "00795872bc554893bde41f3f9cb807d0", "appt_user_dt": "2016-11-07 16:15:00", "will_attend": null, "notify_sys_dt": "2016-11-07 22:15:00", "sms_sent": false, "appt_sys_dt": "2016-11-07 23:15:00"}]}```

Or a single reminder:
    ```curl -X GET http://192.168.99.100:8000/reminder/00795872bc554893bde41f3f9cb807d0```
    Response:
    ```{"contact_number": "12069928996", "participant": null, "location": "West Side Mechanics", "reminder_id": "00795872bc554893bde41f3f9cb807d0", "appt_user_dt": "2016-11-07 16:15:00", "will_attend": null, "notify_sys_dt": "2016-11-07 22:15:00", "sms_sent": false, "appt_sys_dt": "2016-11-07 23:15:00"}

Delete a reminder:
    ```curl -v -X DELETE http://192.168.99.100:8000/reminder/00795872bc554893bde41f3f9cb807d0```
    Response:
    ```{"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "successfully deleted reminder with id 00795872bc554893bde41f3f9cb807d0"}```


Reminder
    - the will_attend attribute is either null if the user hasn't responded, otherwise boolean indicating there response 'yes', or 'no'
    - the sms_sent flag indicates that the celery task got a 200 response from Flowroute's SMS api
    - the notify_sys_dt is the appointment time converted to utc less the notify_window
    - the notify_window is the time before the appointment the user would like to be reminded (in hours)
    - appt_user_dt is the user's local time
