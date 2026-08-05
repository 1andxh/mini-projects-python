import bcrypt
import time
import threading
import multiprocessing
import random


def hash_pass(password: str):
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt())
    return hashed

passwords = [f"password{i}" for i in range(20)]

# === SEQUENTIAL ===
# start = time.perf_counter()

# for password in passwords:
#     hash_pass(password)

# end = time.perf_counter()
# print("SEQUENTILAL TOTAL: ", end - start)


# === THREADED ===
# threads = []
# start = time.perf_counter()

# for password in passwords:
#     t = threading.Thread(target=hash_pass, args=(password,))
#     threads.append(t)
#     t.start()

# for t in threads:
#     t.join()

# end = time.perf_counter()
# print("THREADED TOTAL: ", end - start)


# === MULTIPROCESSING === 
if __name__ == "__main__":
    processses = []
    start = time.perf_counter()

    for password in passwords:
        p = multiprocessing.Process(target=hash_pass, args=(password,))
        processses.append(p)
        p.start()

    
    for p in processses:
        p.join()

    end = time.perf_counter()
    print("MULTIPROCESSING TOTAL: ", end - start)

