import os
from django.contrib.auth.models import User

direc = '/home/maninder/vesta/media'
local = 'D:\\vesta\\vesta\\our_static\\media_root'

os.chdir(local)

for x in os.listdir(os.getcwd()):
    try:
        # print x
        user=User.objects.get(username=x)
        os.rename(x, user.email)
        print "renamed " + x + " -> " + user.username
    except Exception as e:
        print str(e)

