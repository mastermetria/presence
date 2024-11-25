from automations.decorator.logs import logs_history_factory
import time

@logs_history_factory(2)
def run():
    print("cette fonction est un test et fait patienter 3 secondes")
    time.sleep(3)