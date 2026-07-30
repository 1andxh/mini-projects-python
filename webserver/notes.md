Everything FastAPI/uvicorn does, you can do by hand with just the
`socket` module. HTTP is not magic — it's a plain-text protocol sitting on
top of TCP, which itself sits on top of the OS's socket API.

---

## 1. Sockets are files
- On Unix (Linux, macOS, WSL), a socket is represented as a **file
  descriptor** — same underlying interface as a regular file (`read`,
  `write`, `close`).
- A **port** is not physical. It's just a number (0–65535) the OS uses as
  a lookup key: "who owns port 8000? → this process → this file
  descriptor."
- Two sockets can't `bind()` to the same (IP, port) at the same time —
  that's the `OSError: Address already in use` error.

## 2. Server job vs client job
- **Server**: `bind()` (claim a known port) + `listen()` (queue up
  incoming connections). Needed because others must be able to *find*
  you at a fixed address.
- **Client**: no `bind()` needed — OS silently assigns a random unused
  ("ephemeral") port. This is why outgoing requests show a random port
  you never chose.

## 3. The 4-tuple
Every TCP connection is uniquely identified by:
```
(source IP, source port, destination IP, destination port)
```
This is how a server can talk to thousands of clients on the *same*
port (e.g. 8000) at once — each client has a different source
IP/port, so each connection is still unique. The OS tracks this
automatically; you never manage it directly.

## 4. Server sequence (the actual steps)
1. `socket.socket(AF_INET, SOCK_STREAM)` — create (AF_INET = IPv4,
   SOCK_STREAM = TCP)
2. `.bind((host, port))` — claim the address
3. `.listen(backlog)` — start queuing incoming connections
4. `.accept()` — **blocks** until a client connects; returns a **new**
   socket + the client's address. This new socket is separate from the
   listening socket.
5. `.recv(bufsize)` / `.send(bytes)` — talk to that one client, on the
   **new** connection socket, never the listening one
6. `.close()` the connection socket when done

**Why `accept()` returns a separate socket:** if the listening socket
also handled the conversation, it couldn't accept new connections while
busy with an existing one — new arrivals would just pile up in the
backlog queue with nobody free to serve them.

## 5. HTTP request format (plain text, strict grammar)
```
GET / HTTP/1.1\r\n
Host: 127.0.0.1:8000\r\n
User-Agent: curl/8.5.0\r\n
Accept: */*\r\n
\r\n
```
- **Request line**: `METHOD PATH VERSION` (exactly one space between
  each)
- **Headers**: `Name: value` pairs, one per line
- **Blank line** (`\r\n\r\n`) marks end of headers
- Anything after the blank line = the body (empty for a simple GET)

## 6. HTTP response format
```
HTTP/1.1 200 OK\r\n
Content-Length: 5\r\n
\r\n
hello
```
- **Status line**: `VERSION CODE REASON` — note the order flips vs the
  request line (version comes first here)
- `Content-Length` tells the client exactly how many body bytes to
  read. TCP is a continuous stream with no built-in "message over"
  signal — without Content-Length (or chunked encoding), the client
  can't know when to stop waiting for more bytes.

## 7. Debugging lessons learned
- A server that only calls `accept()` once will die after serving one
  request — real servers wrap accept/recv/send/close in a `while True`
  loop, keeping the *listening* socket alive forever and only closing
  each connection socket after it's done.

---

