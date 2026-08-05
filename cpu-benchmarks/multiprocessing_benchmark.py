import multiprocessing
import time

def cpu_bound_work():
    count = 0
    print(time.time())
    for i in range(50_000_000):
        count += i

    print("completed at: ", time.time())

    return count

if __name__ == "__main__":
    start = time.perf_counter()
    p1 = multiprocessing.Process(target=cpu_bound_work)
    p2 = multiprocessing.Process(target=cpu_bound_work)

    p1.start()
    p2.start()

    p1.join()
    p2.join()

    end = time.perf_counter()

    print(end-start)