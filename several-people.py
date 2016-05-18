import time
from slackclient import SlackClient

token = "<token>" # get a token at https://api.slack.com/web#authentication
sc = SlackClient(token)

def rtm_iter(sc):
    sc.rtm_connect()
    while True:
        for m in sc.rtm_read():
            yield m
        time.sleep(0.1)

class Tracker:
    def __init__(self,decay_secs=6):
        self.decay_secs = decay_secs
        self.ct = {}
        
    def rem(self,channel,user):
        if (channel,user) in self.ct:
            del self.ct[(channel,user)]

    def add(self,channel,user):
        self.ct[(channel,user)] = time.time()
        
    def purge(self):
        now = time.time()
        for k,v in list(self.ct.items()):
            if v < now-self.decay_secs:
                self.rem(*k)
    
    def typers(self,channel):
        self.purge()
        return [u for c,u in self.ct.keys() if c==channel]
        
t = Tracker()
tripped = {}

for m in rtm_iter(sc):
    c = m.get('channel')
    if m['type']=='message'and 'user' in m:
        tripped[c] = False
        t.rem(c,m['user'])
    if m['type']=='user_typing':
        t.add(c,m['user'])
        if len(t.typers(c))>=3 and not tripped.get(c,False):
            tripped[c] = True
            sc.api_call(
                "chat.postMessage", channel=m['channel'], text="_several people are typing_",
                username='Several People', icon_emoji=':keyboard:'
            )
