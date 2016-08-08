# Appointment Reminder

Appointment Reminder is a microservice that allows you to send appointment reminders to users. For example, you might manage appointments at a medical clinic. This service can be used to send reminders at a time that you set to patients of upcoming appointments. The patient is them prompted to confirm yes or no to the reminder message.

The service uses a SQL backend and exposes an API endpoint that uses the following methods:

* **POST** to create an appointment reminder.

*  **GET** to retrieve an appointment reminder or a list of reminders.

*  **POST** to delete an appointment reminder.

## Before you begin

You will need the following before running the Appointment Reminder service:

- [Flowroute API credentials](https://manage.flowroute.com/accounts/preferences/api/) 

- A [Flowroute Phone Number](https://manage.flowroute.com/accounts/dids/) enabled for SMS
- The [Flowroute Messaging Python SDK](https://github.com/flowroute/flowroute-messaging-python/) installed

-  Docker

- Docker Compose 1.7.1.

>**NOTE:** This document does not cover installing Docker or Docker Compose.

## Run git clone to import the library and set your API credentials

1. Open a terminal window.
 
2.  If needed, create a directory where you want to deploy Appointment Reminder service.

3.  Change to the directory, and run the following:

        git clone https://github.com/flowroute/sms-reminder.git

 	The `git clone` command clones the Appointment Reminder repository as a sub directory within the parent folder.

3.  Go to the **sms_reminder** directory.

4.  Run the following:

        pip install -r requirements.txt

5. Go to the **appointment_reminder** sub directory, and using a code text editor, open **settings.py**.

 	In this file set your API credentials by replacing the `FLOWROUTE_SECRET_KEY` and `FLOWROUTE_ACCESS_KEY` with your own API credentials, replace `FLOWROUTE_NUMBER` with your own number, and your `ORG_NAME` with the name of your organization or business.

      	FLOWROUTE_SECRET_KEY = os.environ['FLOWROUTE_SECRET_KEY']
      	FLOWROUTE_ACCESS_KEY = os.environ['FLOWROUTE_ACCESS_KEY']
      	FLOWROUTE_NUMBER = os.environ['FLOWROUTE_NUMBER']
    	
      	ORG_NAME = os.environ.get('ORG_NAME', 'Your Org Name')

5.	Do one of the following:
 
 * Save the file, then [start the Appointment Reminder service](#startservice), or 
 
 *  Optionally change the appointment reminder message and DateTime language, and then  [start the Appointment Reminder service](#startservice).

## Change messages and DateTime language

Within **settings.py** you can change appointment reminder messages as well as change the language used for the DateTime in reminder messages.

### Change message text

**settings.py** contains default appointment reminder, confirmation, cancel, and unparsable response message templates. You can accept these default messages or optionally change any or all of the messages. 

###### MSG_TEMPLATE

Change the appointment reminder message sent to recipients.

	MSG_TEMPLATE = ("[{}] You have an appointment on {}{}. "  # company, datetime, additional details 
           "Please reply 'Yes' to confirm, or 'No'" 
           "to cancel.")

 >**Important:** Do not remove or change the brackets (`{}`)within the message template.

###### CONFIRMATION_RESPONSE

Change the response message sent to the recipient upon a successful appointment confirmation received from the recipient.

	CONFIRMATION_RESPONSE = (u"[{}]\nThank you! Your appointment has been marked "
                         "confirmed.").format(ORG_NAME)

###### CANCEL_RESPONSE

Change the cancellation response message sent to the recipient upon a successful appointment cancellation response received from the recipient.

	CANCEL_RESPONSE = (u"[{}]\nThank you! Your appointment has been"
                   u" marked canceled.").format(ORG_NAME)

###### UNPARSABLE_RESPONSE

An unparsable response is a response received from a recipient that cannot be understood. For example, if the `MSG_TEMPLATE` asks the recipient to reply with `Yes` or `No`, but the recipient sends something other than either of those two options, the Appointment Reminder service will be unable to determine the response. The unparsable response message is a return message to the recipient prompting them again to respond with either `Yes` or `No`.

	UNPARSABLE_RESPONSE = (u"[{}]\nSorry, we did not understand your response. "
                       u"Please reply 'Yes' to confirm, or 'No' "
                       u"to cancel.").format(ORG_NAME)

>**Note:** `Yes` or `No` are case-insensitive, so a `yes` or `no` response are parsed as `Yes` or `No`.

##### Change the default DateTime language

In **settings.py** you can set the DateTime of the reminder message to use any language supported by [arrow.locales](https://github.com/crsmithdev/arrow/blob/master/arrow/locales.py). Changing the default DateTime language translates only the DateTime values sent in the message to use those languages, not the content of the message itself.

To change the default language use the `names` identifying the language in **arrow.locales**. For example, to change the default language to French, edit `LANGUAGE_DEFAULT` as follows:

	LANGUAGE_DEFAULT = 'fr'

Some languages in **arrow.locales** also include abbreviated forms for months and days. If the language has abbreviated forms, that abbreviated form will be used in the message. For example, in French, the abbreviated form of **mercredi** (Wednesday) is **mer**, and **juillet** (July) is **juil**. An appointment reminder using a French DateTime will send the abbreviated forms.

>**Important:** If you change the `DEFAULT_LANGUAGE` you should consider also translating your appointment reminder messages. Changing the default language only translates the reminder DateTime into that language, not the message itself. 

>For example, if your language is English your reminder message might say: "You have an appointment on Wednesday, July 21 at 2:00 PM. Please reply Yes to confirm, or No to cancel." If French is set as the default language, the same message appears as follows: "You have an appointment on mer 21 juil à 14:00. Please reply Yes to confirm, or No to cancel."	

## Start the Appointment Reminder service<a name="startservice"></a>

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

*	**400** for an invalid argument
* 	**500** if Redis is unavailable
	
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
	
	{  
  	 "reminders":[  
      {  
         "confirm_sent":false,
         "contact_number":"12062223333",
         "participant":"Joe",
         "location":"West Side Mechanics",
         "reminder_sent":false,
         "reminder_id":"e616e7b6732d4c9787bb5f7f6bc390f0",
         "appt_user_dt":"2016-08-05 13:21:00",
         "will_attend":null,
         "notify_sys_dt":"2016-08-05 19:21:00",
         "appt_sys_dt":"2016-08-05 20:21:00"
      },
      {  
         "confirm_sent":false,
         "contact_number":"12064447777",
         "participant":"Joe",
         "location":"West Side Mechanics",
         "reminder_sent":false,
         "reminder_id":"98dc1efb27ce419caaee94ccf660227c",
         "appt_user_dt":"2016-08-10 13:21:00",
         "will_attend":null,
         "notify_sys_dt":"2016-08-10 19:21:00",
         "appt_sys_dt":"2016-08-10 20:21:00"
  	    }
 	  ]
	}

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
	  
	{"reminder_id": "00795872bc554893bde41f3f9cb807d0", "message": "Successfully deleted reminder with id 00795872bc554893bde41f3f9cb807d0"}```

#### Error response

*	A **500** status code can be returned if there is any internal error.

