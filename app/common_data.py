import MyWatcher as watcher
import os

dir = os.path.dirname(__file__)

api = None
with open(os.path.join(dir, "../key.txt")) as f:
    api = f.readline().strip()
watcher = watcher.MyWatcher(api)

CHAMPS_BY_ID = watcher.static_get_champion_list(data_by_id=True, champ_data=["all"])