from extensions import timer
import time

@timer.monitor()
@timer.track(time_saved=10)
def do_the_work():

    time.sleep(10)
    print('jai attendu 10 secondes')

def test_run():
    do_the_work()