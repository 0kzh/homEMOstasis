import queue

q = queue.Queue()   # All threads access this, including main thread.

def runOnMain(threadfunc):
    q.put(threadfunc)

def execFromMain(noBlock=True):
    # Execute all queued tasks from main:
    while noBlock:
        try:
            callback = q.get(False) #doesn't block
        except queue.Empty: #raised when queue is empty
            break
        callback()
