<pre>
___  ____ _              ______ _                        _ _ 
|  \/  (_) |             |  ___(_)                      | | |
| .  . |_| |_ _ __ ___   | |_   _ _ __ _____      ____ _| | |
| |\/| | | __| '_ ` _ \  |  _| | | '__/ _ \ \ /\ / / _` | | |
| |  | | | |_| | | | | | | |   | | | |  __/\ V  V / (_| | | |
\_|  |_/_|\__|_| |_| |_| \_|   |_|_|  \___| \_/\_/ \__,_|_|_|
</pre>

A simple Man in the Middle Firewall that can be used to block access to websites or redirect hostnames, IP addresses to other addresses.

# Installation: (with Aptitude and Y.U.M.)

<pre>
sudo apt install python3 git -y
sudo yum -y install python3 git
cd
rm -rf mitmfirewall
git clone https://github.com/eoksum/mitmfirewall
cd mitmfirewall
chmod 755 app.py
./app.py
</pre>

Then you can also move app.py to /bin/mitmfirewall to access it directly.
Usage is simple, you will know how to use it when you run it.

# DISCLAIMER:
Only use this for educational purposes and do not use this to distrupt anyones access to any content.
I am denying any responsibility for the any damage you can possibly cause with this small script of mine.

Thanks
Emrecan OKSUM
