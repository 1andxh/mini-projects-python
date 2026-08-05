Parent threads don't automatically wait for the child threads created, unless explicitly
paused with .join()

in this benchmark without .join the main thread is near instant, before the sub threads finish

---

GIL (Global Interpreter Lock) - only one thread can run actual python code at a time,
no matter how many cpu cores i have. threads still get created, they still run, but they
take turns, never actually at the same time.

ran a CPU-bound test (pure computation, 50 million loop iterations, no waiting) single
threaded first - took ~3 seconds consistently.

ran the same work in 2 threads at once - expected it to be faster or at least close to 3s
if it was truly parallel. got ~7 seconds instead, basically double. that's the GIL - the
two threads were fighting over the same lock, taking strict turns instead of running
simultaneously, so i paid for both workloads back to back plus extra overhead from all
the switching between them.

compare that to an I/O-bound test i did earlier (time.sleep(5) in 2 threads) - that one
DID finish in ~5s total, not 10. why the difference? sleep() isn't python code doing
work, it's telling the OS "do nothing, wake me up later" - so python actually releases
the GIL while sleeping since there's nothing to protect. no one's fighting over the lock
if no one's using it.

the actual rule i'm taking from this:
- threading helps when the bottleneck is WAITING (network calls, db queries, sleeping) -
  I/O bound work. GIL gets released during the wait.
- threading does NOT help when the bottleneck is COMPUTING (math, loops, processing) -
  CPU bound work. GIL forces threads to take turns anyway, so no speedup, sometimes
  even a little slower from switching overhead.

also learned: main thread doesn't wait for the threads it spins up either, unless you
explicitly .join() them. found this out by timing my 2-thread benchmark WITHOUT .join -
got 0.017 seconds, looked like a crazy speedup at first, but that was just because the
main thread hit the print statement and moved on before the actual work was anywhere
close to done. proved it by adding a print inside the worker function itself - the
"completed at: " prints showed up a full 7+ seconds AFTER my timing already printed. classic case
of measuring the starting line instead of the finish line.


---

Multiprocessing - tested multiprocessing.Process instead of threading.Thread for the same CPU-bound work.

result: 4.6 seconds total (vs ~3s single-threaded, vs ~7s with threading). way better than
threading, but not exactly 3s like i expected from "true parallelism" - why?

because creating a PROCESS is expensive. a thread is cheap - just a new lane inside memory
that already exists. a process is basically starting python fresh - its own interpreter,
its own memory space, nothing shared with the parent by default. that setup cost eats into
the total time. so what i actually measured was ~3s of real parallel computation + ~1.5s
of process spawn overhead on top.

the actual tradeoff:
- threads: cheap to create, share memory easily, but GIL kills CPU-bound speedup
- processes: genuinely parallel (own GIL each), no GIL fighting, but expensive to spin up
  and don't share memory by default - need special tools (multiprocessing.Queue, shared
  memory objects) if processes need to talk to each other

so processes aren't "just better" - they trade GIL problems for spawn overhead and lost
memory sharing. for a short task the overhead can eat most of the win. for a long task
(minutes, not seconds) that same overhead becomes tiny by comparison and processes win big.

also: multiprocessing needs `if __name__ == "__main__":` around the code that creates
processes - threading didn't need this. reason: each new process basically re-runs the
script from scratch as its own interpreter, re-importing the file top to bottom. without
the guard, that re-import would ALSO try to create p1/p2 again inside the child process,
which creates more children, which try to create more children... the guard makes sure
"create these processes" only happens in the actual main run, not every time the file
gets re-imported by a spawned child.
