Install dependencies
Start the redis server with ```redis-server```
Start the celery server with ```celery worker -A appointment_reminder.tasks.celery --loglevel=INFO```
Start the reminder server with ```python -m appointment_reminder.service```

Make a new appointment reminder request:
    ```curl -v -X POST -d '{"contact_number":12069928996, "appointment_time": "2016-07-27 14:45",  "notify_window":"1", "location":"West Side Mechanics"}' -H "Content-Type: application/json" http://127.0.0.1:5000/reminder```

Retrieve a reminder list:
    ```curl -X GET "http://127.0.0.1:5000/reminder"```
