import sys
import subprocess

data = sys.stdin.read().splitlines()

if len(data) == 1:
    bash = '/home/pi/chamosbot/startbot'
    print('RESTARTING BOT')
    subprocess.run([bash])
else:
    print('NOT RESTARTING BOT')
