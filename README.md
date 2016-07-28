# Appointment Reminder

Appointment Reminder is a microservice that allows you to send appointment reminders to users. For example, you might manage appointments at a medical clinic. This service can be used to send reminders at a time that you set to patients of upcoming appointments. The patient is them prompted to confirm yes or no to the reminder message.

The service uses a SQL backend and exposes an API endpoint that uses the following methods:

* **POST** to create an appointment reminder.

*  **GET** to retrieve an appointment reminder or a list of reminders.

*  **POST** to delete an appointment reminder.

## Before you begin

You will need the following before running the Appointment Reminder service:

- [Flowroute API credentials](https://manage.flowroute.com/accounts/preferences/api/) 

- A [Flowroute Phone Number](https://manage.flowroute.com/accounts/dids/) enabled for SMS</a> 

-  Docker

- Docker Compose 1.7.1.

>**NOTE:** This document does not cover installing Docker or Docker Compose.

## Run git clone to import the library and set your API credentials

1.	If needed, in a terminal window create a parent directory where you want to deploy Appointment Reminder service.

2.	Change to the parent directory, and run the following:

		git clone git@gitlab.internal:l-pod/appointment-reminder.git

	The git clone command clones the Appointment Reminder repository as a sub directory within the parent folder.
	
3.  Go to **.\apppointment_reminder\appointment_reminder**.

4. Using a code text editor, open **settings.py.** In this file set your API credentials by replacing the FLOWROUTE_SECRET_KEY and FLOWROUTE_ACCESS_KEY with your own API credentials, and replace FLOWROUTE_NUMBER with your own number.

       	FLOWROUTE_SECRET_KEY = os.environ['FLOWROUTE_SECRET_KEY']
       	FLOWROUTE_ACCESS_KEY = os.environ['FLOWROUTE_ACCESS_KEY']
       	FLOWROUTE_NUMBER = os.environ['FLOWROUTE_NUMBER']

5. Start the Appointment Reminder service.

## Start the Appointment Reminder service

1.	Start the Redis server:

	 	redis-server

2.	Start the Celery server:

	 	celery worker -A appointment_reminder.tasks.celery --loglevel=INFO
	 
3.	Start the reminder service:

	 	python -m appointment_reminder.service

## Create, retrieve, and delete appointment reminders

The Appointment Reminder service allows you to perform the following operations for creating and managing appointment reminders:

*	[Create a new appointment reminder](#createrem)
* 	[Retrieve a single reminder](#getsingle)
*	[Retrieve a reminder list](#getlist)
* 	[Delete a reminder](#deleterem)

### Create a new appointment reminder<a name=createrem></a>

Use the POST method to send an appointment reminder.

#### Usage

	curl -v -X POST -d '{"contact_number":<contact number>, "appointment_time": "<appointment_time>",  "notify_window":"<notify_window>", "location":"<location>"}' -H "Content-Type: application/json" http://<Docker Daemon>:<port>/reminder 

##### Example usage

	curl -v -X POST -d '{"contact_number":12223334444, "appointment_time": "2016-07-06T15:23-0800",  "notify_window":"1", "location":"West Side Mechanics"}' -H "Content-Type: application/json" http://192.168.99.100:8000/reminder

| Parameter | Required | Type |Description   |                                                                             
|-----------|----------|-------|--------------------------------------------------------|
| `contact_number`  | True     | string| The contact's phone number. Must use an 11-digit, 1XXXXXXXXXX format.|                                                                     |
| `appointment_time `   | True     | string |The scheduled appointment time, using an ISO 8601 `"YYYY-MM-DDTHH:mmZ"` format.| 
| `notify_window`| True   |integer | The length of time, in hours, before the scheduled appointment to send a reminder. For example, `1` indicates that a reminder is sent one hour before the `appointment_time`.| 
|`location`| False | string | The appointment location. Limited to 128 characters. The following SQL characters are disallowed: `|`,`-`,`*`,`/`,`<>`,`<`, >, `,`(comma),`=`,`<=`,`>=`,`~=`,`!=`, ^`=`,`(`,`)`|
| `participant`|False|string| Provides more information about the appointment. For example, this might be a particular person or department at the `location`. Limited to 256 characters. |

##### Example response

A successful POST returns a `reminder_id`, as shown in the following:
	
    {"reminder_id": "2a00aadba83b40aa8a3a6e99a1bd88b9", "message": "successfully created a reminder with id 2a00aadba83b40aa8a3a6e99a1bd88b9"}

>**NOTE:** Note down the `reminder_id` if you want to later look up information about the appointment reminder.

#### Error response

The following error responses can be returned:

*	400 for an invalid argument
* 	500 if Redis is unavailable
	
### Retrieve a single reminder<a name=getsingle></a>

Retrieving information about a sent reminder uses the GET method and passes the `reminder_id` from a previously sent appointment reminder.

#### Usage

	curl -X GET http://<Docker Daemon>:<port>/reminder/reminder_id

##### Example usage

	curl -X GET http://192.168.99.100:8000/reminder/2a00aadba83b40aa8a3a6e99a1bd88b9

##### Example response

A successful GET returns the following:
	
```
{"confirm_sent": true, "contact_number": "12069928996", "participant": "Joe", "location": "West Side Mechanics", "reminder_id": "2a00aadba83b40aa8a3a6e99a1bd88b9", "appt_user_dt": "2016-07-15 11:40:00", "will_attend": true, "notify_sys_dt": "2016-07-15 17:40:00", "reminder_sent": true, "appt_sys_dt": "2016-07-15 18:40:00"}
```	

### Retrieve a reminder list<a name=getlist></a>

Use the GET method to retrieve a list of reminders.

#### Usage

	curl -X GET "http://<Docker Daemon>:<port>/reminder"

##### Example usage

	curl -X GET "http:/192.168.99.100:8000/reminder"

##### Example response

A successful GET returns the following:
	
	{"reminders": [{"confirm_sent": true, "contact_number": "12069928996", "participant": "Joe", "location": "West Side Mechanics", "reminder_id": "2a00aadba83b40aa8a3a6e99a1bd88b9", "appt_user_dt": "2016-07-15 11:40:00", "will_attend": true, "notify_sys_dt": "2016-07-15 17:40:00", "reminder_sent": true, "appt_sys_dt": "2016-07-15 18:40:00"}]}

#### Response field descriptions

The following information is returned in the response for both a single reminder and for a list of reminders:
 
| Parameter |  Nullable| Description   |                                                                             
|-----------|---------------------|---------------------------------------|
|`confirm_sent`|False | Confirmation that the reminder was received. This will be `true` for received or `false` that the confirmation was not received.|
| `contact_number`  | False   |The number to which the appointment reminder was sent. |  
| `participant`|False|Any additional context for the appointment; this might be the name of a particular person or department at the `location`. | 
| `location`| True| The location for the appointment. This might be the name of a business.|
|`reminder_id`| False| The appointment's `reminder_id`. |                                                                 
|`appt_user_dt`|False| The user's appointment time, based on the time zone passed in the original reminder.|
|`notify_sys_dt`|False| The user's appointment time, in UTC, minus the time set for the `notify_window`.|
|`appt_sys_dt`|False | The user's appointment time, in UTC, based on the time zone passed in the original reminder.|
|`reminder_sent`| False |A **200** response was received from the Flowroute SMS API. This field will be either `true` or `false`. |
|`will_attend`| True   | Displays `null` if the user hasn't responded; otherwise, this will display a `yes` or `no` boolean if the user has responded.| 

#### Error response

The following error response can be returned for both retrieving an appointment reminder and for retrieving a list of appointment reminders.

*	A **500** status code can be returned if there is any internal error.

### Delete a reminder<a name=deleterem></a>

Use the DELETE method and pass an existing `reminder_id` to delete an appointment reminder.

#### Usage

	curl -v -X DELETE http://<Docker Daemon>:<port>reminder/reminder_id

##### Example usage

	curl -v -X DELETE http://192.168.99.100:8000/reminder/00795872bc554893bde41f3f9cb807d0

##### Example Response
A successful DELETE returns the following:
	  
	 {"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "successfully deleted reminder with id 00795872bc554893bde41f3f9cb807d0"}```

#### Error response

*	A **500** status code can be returned if there is any internal error.

