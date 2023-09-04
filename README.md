# Onetime-secret project

***
API app for creating messages with secret phrase to access and expiration time,
which can be read only once during set time using secret phrase.
***

App doesn't store original message or secret phrase. Internal algorithm to save information:

- app hashes a secret phrase to use it as a key to encrypt a message
- app encrypts the message and save it
- app hashes the key second time and save it
- app create the one-off periodic task with name of related database instance to delete the database instance
after a certain amount of time (which you can set using format DD:HH:MM or 7 days will be set automatically)

Internal algorithm to get the message:
- app hashes got the secret phrase to use it as the key to decrypt the message, if the message still exists
- app hashes the key second time and find the instance
- app decrypts the message out of found instance
- app deletes the instance and related periodic task

If expiration time is reached and the message wasn't gotten from the database, the instance will be deleted
as well as related periodic task.

You can run app by docker using one command:

    docker-compose up

Two addresses are available. The first one:

    /generate/

Send POST request to create a secret message. An example of data for request:

    {
    "secret_phrase": "Time is over",
    "message": "Hello! Come to my place for a party!",
    "expiration_time": "15:0:0"
    }
Response in case of success:

    {
    "secret_phrase": "Time is over"
    }

The second address:

    /secrets/{secret phrase}/

Send DELETE request to get a secret message and delete it from database. An example of request:

    /secrets/Time is over/

Response in case of success:

    {
    "message": "Hello! Come to my place for a party!"
    }

***
Documentation is available on /docs/ or /redoc/

Current test coverage 90%
***