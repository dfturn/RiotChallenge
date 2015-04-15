import os
import sys
import inspect
import calendar
import datetime
import time

# Add the submodules to our path since they don't include __init__.py files in their root folders
submodules = ["../submodules/riotwatcher"]
for s in submodules:
    cmd_subfolder = os.path.realpath(os.path.abspath(os.path.join(os.path.split(inspect.getfile( inspect.currentframe() ))[0],s)))
    if cmd_subfolder not in sys.path:
        sys.path.insert(0, cmd_subfolder)
        
        
import riotwatcher as rw

class MyWatcher(rw.RiotWatcher):
    def __init__(self, key):
        rw.RiotWatcher.__init__(self, key)
        
    #Throttle our requests so we don't exceed our limits (or at least not too often)
    def base_request(self, url, region, static=False, **kwargs):
        if not static:
            while not self.can_make_request():
                time.sleep(1)
            
        while True:
            try:
                data = rw.RiotWatcher.base_request(self, url, region, static, **kwargs)
            except Exception as e:
                if e == rw.error_429:
                    time.sleep(5)
                else:
                    raise
            else:
                return data
        
    # api-challenge v4.1
    # This is a temporary endpoint so create our own temporary class to handle it
    def _api_challenge_request(self, end_url, region, **kwargs):
        return self.base_request(
            'v{version}/game/{end_url}'.format(
                version=4.1,
                end_url=end_url
            ),
            region,
            **kwargs
        )
        
    def get_game_ids(self, begin_date=None, region=None):
        if not begin_date:
            # If they didn't pass anything in, just set it to ~ an hour ago
            begin_date = (calendar.timegm(datetime.datetime.today().timetuple())-3600)
            begin_date -= begin_date % 300
    
        return self._api_challenge_request('ids', beginDate=begin_date, region=region)
