import threading
import time

def cpu_bound_work():
    count = 0
    print(time.time())
    for i in range(50_000_000):
        count += i

    print("completed at: ", time.time())

    return count

start = time.perf_counter()

t1 = threading.Thread(target=cpu_bound_work)
t2 = threading.Thread(target=cpu_bound_work)

t1.start()
t2.start()

# shared lock
# t1.join()
# t2.join()

end = time.perf_counter()

print("main thread time: ", end-start)