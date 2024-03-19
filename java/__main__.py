#!/usr/bin/env python3

# import optioner for argument catching
from optioner import options
# import sys.argv as gotargs for actual args
from sys import argv as gotargs
# import chdir and mkdir and popen and system
from os import chdir, mkdir, popen as getOutputOf, system as run, geteuid as root
# from os.path import abspath and join
from os.path import abspath, join
# from colorama import init as color and Fore as _
from colorama import init as color, Fore as _
# import subprocess
import subprocess


def catch_args():
    """catch the arguments
    NOTE: define global vars -> ['actualargs', 'argcheck', 'argerror', 'falseargs', 'shortargs', 'longargs']
    """
    # global variables
    global actualargs, argcheck, argerror, falseargs, shortargs, longargs

    # catch options
    optionCTRL = options(shortargs, longargs, gotargs[1:])
    
    # parse options and set global variables
    actualargs, argcheck, argerror,falseargs = optionCTRL._argparse()
    
def helper():
    print(_.GREEN, " -> java setup module")
    with open("java/version", 'r') as vfile:
        print(_.BLUE, f" -> v{vfile.read()}")
    print("   ?help")
    print(_.BLACK, "-h | --help         : show this help module.")
    print(_.BLACK, "-j | --java-file    : java file path (java file must be .tar.gz)")
    print(_.BLACK, "-c | --config       : change java version")
    exit(0)

def status(color: str, _status: str):
    print(f'{color}', 'status', _.RESET, f' : {_status}')

def setup():
    # get global variable javapath
    global javapath
    
    # change directory to /usr/lib/jvm
    status(_.YELLOW, 'checking [/usr/lib/jvm]')
    try:
        chdir('/usr/lib/jvm')
        status(_.GREEN, "Checked [/usr/lib/jvm]")
    except FileNotFoundError:
        status(_.RED, "No Directory [/usr/lib/jvm]")
        mkdir('/usr/lib/jvm')
        chdir('/usr/lib/jvm')
        status(_.GREEN, "Created [/usr/lib/jvm]")
    
    # get filenames present there
    files = getOutputOf('ls').readlines()
    for i in range(len(files)):
        files[i] = files[i].replace('\n', '')
    
    status(_.YELLOW, f'attempting to extract {javapath}')
    # extract the file
    run(f"sudo tar -xzf {javapath}")
    status(_.GREEN, 'extracted')
    
    # get extracted filename
    newfiles = getOutputOf('ls').readlines()
    extracted_filename: str
    
    for file in newfiles:
        file = file.replace('\n', '')
        if file not in files:
            extracted_filename = abspath(file)
    
    status(_.GREEN, f'resolved extracted directory -> [{extracted_filename}]')
    
    status(_.YELLOW, 'editing /etc/environment')
    # echo the filenames in the /etc/environment file
    entries = [
        f"{join(extracted_filename, 'bin')}",
        f"{join(extracted_filename, 'db', 'bin')}",
        f"{join(extracted_filename, 'jre', 'bin')}"
    ]
    
    with open('/etc/environment', 'r') as envfile:
        envtexts = envfile.readlines()
    
    newpath:str
    
    for i in range(len(envtexts)):
        if envtexts[i].split('=')[0] == 'PATH':
            newpath = envtexts[i].replace('\n', '')
            for entry in entries:
                newpath +=  ':' + entry
                status(_.GREEN, f'added \'{entry}\' to PATH')
            
            newpath += '\n'
            
            envtexts[i] = newpath
    
    with open('/etc/environment', 'w') as envfile:
        for entry in envtexts:
            envfile.write(entry)
    
    status(_.GREEN, 'finished editing /etc/environment')
    
    run(f"sudo update-alternatives --install \"/usr/bin/java\" \"java\" {join(extracted_filename, 'bin', 'java')} 0")
    run(f"sudo update-alternatives --install \"/usr/bin/java\" \"java\" {join(extracted_filename, 'bin', 'javac')} 0")
    
    status(_.GREEN, 'installed update alternatives')
    
    run(f"sudo update-alternatives --set java {join(extracted_filename, 'bin', 'java')}")
    run(f"sudo update-alternatives --set java {join(extracted_filename, 'bin', 'javac')}")
    
    status(_.GREEN, 'setting update alternatives complete')
    
    codechoke: str
    
    codechoke = input('Press Enter to Continue')
    
    run('clear')    
    run('sudo update-alternatives --config java')

def config():
    subprocess.Popen(['clear']).wait()
    # run('clear')
    # run('sudo update-alternatives --config java')
    subprocess.Popen(['sudo', 'update-alternatives', '--config', 'java']).wait()
    subprocess.Popen(['clear']).wait()
    exit(0)

if __name__=="__main__":
    try:
        # check root
        if root() != 0:
            raise PermissionError
        
        # initialise color 
        color(autoreset=True)

        # define global variables #

        # actualargs is a list of all defined arguments that is passed.
        actualargs:list

        # argcheck is a bool type variable; it is true if all arguments are within the scope, false if wrong args are passed.
        argcheck:bool

        # argument errors if any
        argerror:str

        # all the false args if any
        falseargs:list

        # define short and long arguments
        shortargs = ['j', 'h', 'c']
        longargs = ['java-file', 'help', 'config']

        # define java-file path
        javapath:str

        # global variable definition END #

        # catch and parse the given arguments:
        catch_args()

        # if there is any error in arguments print them
        if not argcheck:
            print(_.RED, "INFO", f" : {argerror}")
        # else
        else:
            # get argument values
            for i in range(len(gotargs)):
                if gotargs[i]=='-j' or gotargs[i]=='--java-file':
                    # set javafile path
                    javapath = gotargs[i+1]
                elif gotargs[i]=='-h' or gotargs=="--help":
                    # show help and exit
                    helper()
                elif gotargs[i]=='-c' or gotargs=='--config':
                    config()

        # setup and install java
        setup()
    except PermissionError:
        lastarg = gotargs[0]
        for arg in gotargs[1:]:
            lastarg += " " + arg
        print(lastarg)
        run(f'sudo python3 {lastarg}')