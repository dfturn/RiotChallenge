import MyWatcher as watcher

api = None
with open("key.txt") as f:
    api = f.readline().strip()
watcher = watcher.MyWatcher(api)

CHAMPS_BY_ID = watcher.static_get_champion_list(data_by_id=True, champ_data=["all"])