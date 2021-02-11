# htb-doctor

## Usage

To run commands on the target:

`python3 rce.py -c 'whoami'`

To run with verbose mode use the `-v` flag.

For the script to work you must be connected to your HTB VPN with `doctors.htb` in your `/etc/hosts` file with the corresponding IP address.

# Explanation

The script works by creating an account, logging in and posting a message with the payload. The payload utilises an SSTI exploit which you can read about [here](https://www.onsecurity.io/blog/server-side-template-injection-with-jinja2/).

I also added a function to delete the message with the payload if the payload causes an error. When the command causes the error the archive page returns `500 INTERNAL SERVER ERROR` so the only way to do more commands is to delete the message.
