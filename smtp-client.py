from socket import *
import ssl
import argparse
import sys

parser = argparse.ArgumentParser()
parser.add_argument('-f', '--fro', type=str, metavar='', help='sender\'s email address')
parser.add_argument('-t', '--to', type=str, metavar='', help='recipient\'s email address')
parser.add_argument('-m', '--message', type=str, metavar='', help='email message')
parser.add_argument('-s', '--server', type=str, metavar='', help='mail server')
parser.add_argument('-o', '--port', type=int, metavar='', help='server\'s port number')
parser.add_argument('-u', '--username', type=str, metavar='', help='username - encodes into base64')
parser.add_argument('-p', '--password', type=str, metavar='', help='password - encodes into base64')
args = parser.parse_args()

def main():
	message, fromMessage, toMessage, mailServer, port = readArguments()

	# Create socket called clientSocket and establish a TCP connection with mailserver
	clientSocket = socket(AF_INET, SOCK_STREAM)
	clientSocket.connect((mailServer, port))

	# Connect to mail server
	print 'Connecting to mail server ' + mailServer + ' on port ' + str(port)
	recv, code = receiveSmtpMessage(clientSocket)
	checkResponse('220', code, 'connection', recv)

	# Send HELO command and print server response
	print 'Sending HELO message...'
	sendSmtpMessage(clientSocket, 'HELO gmail.com\r\n')
	recv, code = receiveSmtpMessage(clientSocket)
	checkResponse('250', code, 'HELO', recv)

	# Send STARTTLS command and print server response (returns a 220)
	print 'Sending STARTTLS message...'
	sendSmtpMessage(clientSocket, 'STARTTLS\r\n')
	recv, code = receiveSmtpMessage(clientSocket)
	checkResponse('220', code, 'STARTTLS', recv)

	# Wrap our socket such that ssl version 23-1 is applied
	secureSocket = ssl.wrap_socket(clientSocket, None, None, False, ssl.CERT_NONE, ssl.PROTOCOL_SSLv23)

	# Resend the HELO command to start the new secure connection
	print 'Sending secure HELO message...'
	sendSmtpMessage(secureSocket, 'HELO gmail.com\r\n')
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('250', code, 'secure HELO', recv)

	# Initiate an AUTH LOGIN using APP password (returns a 334)
	print 'Sending AUTH LOGIN message...'
	sendSmtpMessage(secureSocket, 'AUTH LOGIN\r\n')
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('334', code, 'AUTH LOGIN', recv)

	print 'Sending base64 encoded username...'
	username = args.username.encode('base64') + '\r\n'
	secureSocket.send(username)
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('334', code, 'username', recv)

	print 'Sending base64 encoded password...'
	password = args.password.encode('base64') + '\r\n'
	secureSocket.send(password)
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('235', code, 'password', recv)
		
	# Send MAIL FROM command and print server response
	print 'Sending mail from message...'
	sendSmtpMessage(secureSocket, fromMessage)
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('250', code, 'mail from', recv)

	# Send RCPT TO command and print server response
	print 'Sending mail to message...'
	sendSmtpMessage(secureSocket, toMessage)
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('250', code, 'mail to', recv)

	# Send DATA command and print server response (returns a 354)
	print 'Sending DATA message...'
	sendSmtpMessage(secureSocket, 'DATA\r\n')
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('354', code, 'DATA', recv)

	# Send message data
	print 'Sending message...'
	sendSmtpMessage(secureSocket, message)

	# Message ends with a single period
	print 'Sending period end message...'
	sendSmtpMessage(secureSocket, '\r\n.\r\n')
	recv, code = receiveSmtpMessage(secureSocket)
	checkResponse('250', code, 'end', recv)

	print 'Sending QUIT message...'
	sendSmtpMessage(secureSocket, 'QUIT')

def readArguments():
	message = '\r\n ' + args.message if args.message != None else '\r\nI love computer networks!'
	fromMessage = 'MAIL FROM: <' + args.fro + '>\r\n' if args.fro != None else 'MAIL FROM: <alice@gmail.com>\r\n'
	toMessage = 'RCPT TO: <' + args.to + '>\r\n' if args.to != None else 'RCPT TO: <bob@yahoo.com>\r\n'
	mailServer = args.server if args.server != None else 'smtp.live.com'
	port = args.port if args.port != None else 587

	if args.username == None:
		print 'Error: requires username -u'
		sys.exit()

	if args.password == None:
		print 'Error: requires password -p'

	return message, fromMessage, toMessage, mailServer, port

def sendSmtpMessage(clientSocket, message):
	clientSocket.send(message.encode())

def receiveSmtpMessage(clientSocket):
	recv = clientSocket.recv(1024).decode()
	return recv, recv[:3]

def checkResponse(expectedCode, receivedCode, message, recv):
	if expectedCode != receivedCode:
		print 'Error: did not receive ' + expectedCode + ' reply for ' + message + ' message\nInstead received: ' + receivedCode
		print recv
		print 'Exiting...'
		sys.exit()
	else:
		print 'Received: ' + recv

if __name__ == '__main__':
	main()
