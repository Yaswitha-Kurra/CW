import time
import importlib

def run_continuously():
    while True:
        print("Running module one (fetching courses)...")
        importlib.reload(importlib.import_module('test1'))

        print("Running module two (updating course links)...")
        importlib.reload(importlib.import_module('test2'))

        print("Running module three (scraping UI segment links)...")
        importlib.reload(importlib.import_module('CW3'))

        #print("Running module four (filtering non-English courses)...")
        #importlib.reload(importlib.import_module('four'))

        #print("Running module five (checking new courses)...")
        #importlib.reload(importlib.import_module('five'))

        print("Completed one cycle. Waiting for next cycle...")
        time.sleep(1800)  # 5 minutes
        
        #print("Running module four (cleaning expired courses)...")
        #importlib.reload(importlib.import_module('clean_expired'))

        #print("✅ Completed one cleaning. Waiting for next cycle...")
        #time.sleep(3600)  # 5 minutes


run_continuously()
