# SMTP TLS Client

## Description
The mail client I implemented utilizes TLS by doing the connection upgrade method. Such that we start with an insecure connection with our HELO message, then tell the server to use TLS with STARTTLS and then login with our credentials. This email client uses the SSLv23 protocol to communicate with the mail server.

## How To Use
To run the program you must have an mail server in mind you want to use to send your email. You will also need to have your own user and password setup with that mail server.
Some examples:
```
hotmail: 'smtp.live.com'
gmail: 'smtp.gmail.com'
```

### Start the server:
```
python smtp-client.py -f <from address> -t <to address> -m <message> -s <server> -o <port> -u <user> -p <password>
```
I've included some arguments you can pass the program in order to setup your connection with the mail server:
```
-f <from address> the email address in the from portion of the email (should usually match your user login)
-t <to address> the email address in the to portion of the email
-m <message> this is the message you are sending
-s <server> this is the mail server you are using (default is smtp.live.com)
-p <port> the port to connect to on the mail server
-u <user> the username used for authentication
-p <password> the password used for authentication
```
