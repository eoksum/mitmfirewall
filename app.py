#!/usr/bin/python3

import os
import sys
import json
import socket

banner = '''
___  ____ _              ______ _                        _ _ 
|  \/  (_) |             |  ___(_)                      | | |
| .  . |_| |_ _ __ ___   | |_   _ _ __ _____      ____ _| | |
| |\/| | | __| '_ ` _ \  |  _| | | '__/ _ \ \ /\ / / _` | | |
| |  | | | |_| | | | | | | |   | | | |  __/\ V  V / (_| | | |
\_|  |_/_|\__|_| |_| |_| \_|   |_|_|  \___| \_/\_/ \__,_|_|_|
'''
ver = "1.0"
path = "/usr/local/mitmfw"
ignore = " >/dev/null 2>&1"
debugging = False # Set this to True if you want to see debugging messages or set it to False if you don't want to see them.

if debugging == True:
    ignore = " 2>&1"

def chkIp(ip):
    try:
        socket.inet_aton(ip)
    except:
        return False
    return True

def dbgMsg(msg):
    
    if debugging == True:
        print("[DEBUG] " + msg)    

def dbManagement(action, extra):
    
    if action == "CREATE":
        hd = open(path + "/mitmfw.db", "w")
        hd.write("[]")
        hd.close()
        return True
    elif action == "GET":
        
        hd = open(path + "/mitmfw.db", "r")
        dbc = hd.read()
        hd.close()
        
        dbc = dbc.replace("\r\n","")
        dbc = dbc.replace("\n","")
        dbc = dbc.replace("\r","")
        
        try:
            dbc = json.loads(dbc)
        except:
            dbc = []
        
        get = ""
        if extra[0] == "GetDomains":
            get = "d"
        elif extra[0] == "GetRedirectedPorts":
            # Coming soon...
            get = "rp"
        elif extra[0] == "GetRedirectedAddresses":
            get = "ra"
        
        ret = []
        for rec in dbc:
            if get == "d" and rec["hostname"] and rec["hostname"] not in ret:
                ret.append(rec["hostname"])
        return ret
    elif action == "UPDATE":
        hd = open(path + "/mitmfw.db", "r")
        dbc = hd.read()
        hd.close()
        
        dbc = dbc.replace("\r\n","")
        dbc = dbc.replace("\n","")
        dbc = dbc.replace("\r","")
        
        try:
            dbc = json.loads(dbc)
        except:
            dbc = []
        
        if extra[0] == "ADD":
            
            dbc.append({"ip":extra[1],"hostname":extra[2]})
            hd = open(path + "/mitmfw.db", "w")
            dbc = json.dumps(dbc)
            hd.write(dbc)
            hd.close()
        elif extra[0] == "DEL":
            
            ndbc = dbc.copy()
            for ind, rec in enumerate(dbc):
                
                if rec["ip"] == extra[1]:
                    del ndbc[ind]
                    
            hd = open(path + "/mitmfw.db", "w")
            ndbc = json.dumps(ndbc)
            hd.write(ndbc)
            hd.close()
    elif action == "DELETE":
        # Only this works in reverse order instead of others.
        hd = open(path + "/mitmfw.db", "r")
        dbc = hd.read()
        hd.close()
        
        dbc = dbc.replace("\r\n","")
        dbc = dbc.replace("\n","")
        dbc = dbc.replace("\r","")
        
        try:
            dbc = json.loads(dbc)
        except:
            dbc = []
        
        ndbc = dbc.copy()
        for ind, rec in enumerate(dbc):
            
            iptablesManagement("UNBAN", rec["ip"], "DELETE", "")
            del ndbc[ind]
        
        hd = open(path + "/mitmfw.db", "w")
        ndbc = json.dumps(ndbc)
        hd.write(ndbc)
        hd.close()
    else:
        dbgMsg("Unexpected action?!")
        return False
    return True

def iptablesManagement(action, hostname, ip, bm):
    # Manage IPtables, get managed by dbManagement func if this is a DELETE action (check function cleanexit) request to our local DB.
    if action == "BAN":
        if bm == "DROP" or bm == "REJECT":
            hd = os.popen("sudo iptables -I FORWARD -s " + ip + " -j " + bm + ignore)
            hd.read()
            dbManagement("UPDATE", ["ADD",ip, hostname])
    elif action == "UNBAN":
        hd = os.popen("sudo iptables -D FORWARD -s " + ip + " -j DROP" + ignore)
        hd.read()
        hd = os.popen("sudo iptables -D FORWARD -s " + ip + " -j REJECT" + ignore)
        hd.read()
        if bm != "DELETE":    
            dbManagement("UPDATE", ["DEL",ip, hostname])
    hd = os.popen("sudo service iptables save")
    hd.read()

def hostnameManagement(action, hostname, bm):
    
    try:
        iplist = socket.gethostbyname_ex(hostname)[2]
    except:
        return False
    dbgMsg(hostname + " has " + " ".join(iplist))
    if action == "BAN" or action == "UNBAN":
        for ip in iplist:
            iptablesManagement(action, hostname, ip, bm)
            dbgMsg(action + " IP address " + ip + " for hostname " + hostname)
    return True

def blockIpManagement():
    
    hn = input("Please type in a FQDN-valid hostname for blocking: ")
    bm = input("Please choose a blocking mode. Available options:\n\n1-) REJECT (This blocking mode returns CONNECTION REFUSED error by rejecting TCP connections to blocked websites.)\n2-) DROP (This blocking mode drops connection requests and eventually they time out and returns CONNECTION TIMEOUT error. This is good if you want to slow client down.)\n\nYour choice: ")
    if bm == "1":
        bm = "REJECT"
    elif bm == "2":
        bm = "DROP"
    else:
        print("Invalid option provided! Using REJECT mode as default...")
        bm = "REJECT"
    print("Please wait trying to block " + hn + " with mode " + bm + "...")
    r = hostnameManagement("BAN", hn, bm)
    if r == False:
        print("Oops! Something went wrong. Perhaps you typed a invalid hostname? try again if so or maybe DNS query failed for some reason. If you believe you typed a correct FQDN-valid hostname check your DNS resolver settings and try again.")
        sys.exit()
    print("Successfully blocked " + hn + "! sending you back to main menu...")
    return startup()

def unblockIpManagement():
    
    ba = dbManagement("GET", ["GetDomains"])
    print("Please choose a website domain to unblock in the entire network from below:\n\n")
    for ind, dom in enumerate(ba):
        print(str(ind + 1) + "-) " + dom)
    bid = input("Your choice: ")
    bid = int(bid) - 1
    hostname = ba[bid]
    print("Please wait trying to unblock " + hostname + "...")
    r = hostnameManagement("UNBAN", hostname, "")
    if r == False:
        print("Oops! Something went wrong. Perhaps you typed a invalid hostname? try again if so or maybe DNS query failed for some reason. If you believe you typed a correct FQDN-valid hostname check your DNS resolver settings and try again.")
        sys.exit()
    print("Successfully unblocked " + hostname + "! sending you back to main menu...")
    return startup()

def cleanexit():
    print("Unblocking all the blocked websites before quitting please wait...")
    dbManagement("DELETE","")
    print("Successful! See you later ^_^")
    sys.exit()

def preStartup():
    
    print("Mitm-Firewall " + ver + " is starting...")
    
    if not os.path.exists(path):
        print("Mitm-Firewall not installed yet! Creating directory and database...")
        try:    
            os.mkdir(path, 0o755)
        except:
            print("Couldn't create required directory for database! Check if you have superuser permissions (root) or write permission to " + path)
            sys.exit()
        print("Creating database file...")
        hd = open(path + "/mitmfw.db", "w")
        hd.write("[]")
        hd.close()
    
    print("Mitm-Firewall needs ARPSpoof or Mitmf or Ettercap to be running at the same time. Do you have any of these running now? (y/N)")
    p = input()
    if p == "N":
        print("Please start any of these third party applications on ARP spoofing mode and try running Mitm-Firewall again.")
        sys.exit()
    os.system("cls")
    os.system("clear")
    return startup()

def startup():
    
    print(banner)
    print("Welcome to Mitm-Firewall. You are currently running version " + ver + ".\nMitm-Firewall is developed and maintainted by me, Emrecan OKSUM. Only use this for educational purposes and do not use this to distrupt communication.\nI deny any responsibility for any damages caused by use of this application.")
    print("=" * 40)
    print("Please choose a action from the menu below: \n\n1-) Block a website on entire network\n2-) Unblock a website on entire network\n3-) Redirect web traffic to another address [Coming Soon]\n4-) Remove redirection of web traffic to another address [Coming Soon]\n5-) Exit the application without unblocking the blocked content\n6-) Exit the application with unblocking the blocked content.")
    print("=" * 40)
    while True:
        p = input("Your choice: ")
        if p == "1":
            return blockIpManagement()
        elif p == "2":
            return unblockIpManagement()
        elif p == "3":
            print("Im not ready yet -_- please check back later or try again with other functions.")
            #return redirectIpManagement()
        elif p == "4":
            print("Im not ready yet -_- please check back later or try again with other functions.")
            #return redirectIpManagement()
        elif p == "5":
            print("OK then, see you later ^_^")
            sys.exit()
        elif p == "6":
            return cleanexit()
        else:
            print("That wasn't a valid choice! Please try again...")
preStartup()
