# from fuzzywuzzy import fuzz
#
# res = fuzz.token_set_ratio("fuzzy was a bear", "fuzzy fuzzy was a bear")
#
# print(res)


import threading
import time


class StoppableThread(threading.Thread):
    """Thread class with a stop() method. The thread itself has to check
    regularly for the stopped() condition."""

    def __init__(self):
        super(StoppableThread, self).__init__()
        self.stopped = False

    @property
    def stop(self):
        self.stopped = True
        yield self.stopped


    def run(self):

        i = 0
        while not self.stopped:
            i += 1
            print("Child Thread value ",i)
            time.sleep(1)

            if i > 10:
                self.stop()


import threading

def printit():
  threading.Timer(5.0, printit).start()
  print( "Hello, World!")

printit()