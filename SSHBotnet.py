#!/usr/bin/env python3
import optparse
from pexpect import pxssh
from time import gmtime, strftime, sleep
from threading import Thread

class Client:
    def __init__(self,host,user,password):
        self.host = host
        self.user = user
        self.password = password
        self.session = self.connect()

    def connect(self):
        try:
            s = pxssh.pxssh()
            s.login(self.host,self.user,self.password)
            print(f'\033[32m[+] Connected to {self.host}\033[0m')
            return s
        except Exception as e:
            print(f'\033[31m[-] Error connecting to {self.host}\033[0m')

    def send_command(self, cmd):
        try:
            self.session.sendline(cmd)
            self.session.prompt()
            return self.session.before
        except:
            pass
        return -1

def botnetCommand(command):
    alloutput = []
    for client in botNet:
        output = client.send_command(command)
        if output == -1:
            return
        output = output.decode()
        print(f'[*] Output from {client.host}')
        print(f'[+] {output}')
        alloutput.append([client.host,output])
    return alloutput

def addClient(host,user,password):
    client = Client(host,user,password)
    if client.session:
        botNet.append(client)

botNet = []
threads = []

def connectFromFile(file):
    global botNet
    botNet = []
    try:
        with open(file,'r') as f:
            for line in f:
                (host,user,password) = line.split(':')
                t = Thread(target=addClient, args=(host,user,password))
                t.start()
                threads.append(t)
    except:
        pass

def handleArgs(arguments,cmd):
    if arguments[0].lower() == 'quit':
        exit(0)
    if arguments[0].lower() == 'recon':
        connectFromFile(bnFile)
    output = botnetCommand(cmd)
    if arguments[0].lower() == 'saveoutput':
        with open(arguments[1],'w') as f:
            outputstring = ''
            for i in output:
                outputstring += f'[+] Output from {i[0]}\n'
                outputstring += i[1]
                f.write(outputstring)

def clearThreads():
    while threads:
        for t in threads:
            if not t.is_alive():
                threads.remove(t)

if __name__ == '__main__':
    parser = optparse.OptionParser('-c <command>')
    parser.add_option('-c',dest='cmd',type='string',help='specify command')
    parser.add_option('-f',dest='bnFile',type='string',help='specify command')
    (options,args) = parser.parse_args()
    cmd = options.cmd
    bnFile = options.bnFile
    if not bnFile:
        print(parser.usage())
    connectFromFile(bnFile)
    clearThreads()

    if cmd:
        botnetCommand(cmd)
    else:
        while True:
            clearThreads()
            if not threads:
                cmd = input(f'\n\033[1;36m(Botnet: {strftime("%H:%M:%S",gmtime())}) >\033[00m ')
                args = ''
                try:
                    (cmd,args) = cmd.split('BN ')
                except:
                    pass
                if args:
                    handleArgs(args.split(),cmd)
                else:
                    output = botnetCommand(cmd)
