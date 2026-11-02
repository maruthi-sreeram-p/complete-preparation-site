"""Practice subject: Computer Networks. Subnetting and delay figures are computed here, so a wrong number cannot ship."""
import ipaddress

from common import subject, written

# ---- subnetting
NET = ipaddress.ip_network("192.168.10.77/26", strict=False)
HOSTS = NET.num_addresses - 2
assert (str(NET.network_address), str(NET.broadcast_address), HOSTS, str(NET.netmask)) == ("192.168.10.64", "192.168.10.127", 62, "255.255.255.192")
SUBNETS = list(ipaddress.ip_network("10.0.0.0/24").subnets(new_prefix=26))
assert len(SUBNETS) == 4 and str(SUBNETS[1]) == "10.0.0.64/26"

# ---- delays: 1 MB file over a 10 Mbps link that is 2,000 km long (signal speed 2 x 10^8 m/s)
FILE_BITS, RATE, DIST, SPEED = 8 * 10**6, 10 * 10**6, 2_000_000, 2 * 10**8
TRANSMISSION, PROPAGATION = FILE_BITS / RATE, DIST / SPEED
assert (TRANSMISSION, PROPAGATION) == (0.8, 0.01)

# ---- TCP slow start: window doubling each RTT from 1 MSS until ssthresh 16, then +1 per RTT
cwnd, trace, ssthresh = 1, [], 16
for _ in range(8):
    trace.append(cwnd)
    cwnd = cwnd * 2 if cwnd < ssthresh else cwnd + 1
assert trace == [1, 2, 4, 8, 16, 17, 18, 19]

QUESTIONS = [
    written("cn-osi-tcpip", "OSI model versus TCP/IP", "Easy",
        "Name the layers of the OSI model and map them to the TCP/IP model. What does each layer's data unit look like?",
        "**OSI (7):** Physical, Data link, Network, Transport, Session, Presentation, Application. **TCP/IP (4):** Link (physical + data link), Internet, Transport, Application (session + presentation + application).\n\n"
        "| Layer | Protocol examples | Data unit | Addressing |\n|---|---|---|---|\n| Application | HTTP, DNS, SMTP | message | name / URL |\n| Transport | TCP, UDP | segment / datagram | **port** |\n| Network | IP, ICMP | packet | **IP address** |\n| Data link | Ethernet, Wi-Fi | frame | **MAC address** |\n| Physical | cable, radio | bits | - |\n\n"
        "Each layer wraps the data from above with its own header (**encapsulation**) and the receiver unwraps it. Remember it as: *Please Do Not Throw Sausage Pizza Away*."),
    written("cn-tcp-udp", "TCP versus UDP", "Easy",
        "Compare TCP and UDP and give an application for each.",
        "**TCP** is **connection-oriented and reliable**: a handshake sets up the connection, data is numbered, acknowledged and retransmitted if lost, delivered **in order**, with **flow control** and **congestion control**. It costs latency and overhead. Used by HTTP(S), SSH, e-mail, file transfer.\n\n"
        "**UDP** is **connectionless and unreliable**: it sends independent datagrams with a tiny 8-byte header, no ordering, no retransmission. Low latency and no connection state. Used by DNS, video and voice calls, online games, streaming, and as the base of QUIC (HTTP/3), where the application decides what to retransmit."),
    written("cn-handshake", "The TCP three-way handshake", "Medium",
        "Explain the three-way handshake and how a connection is closed. Why are three messages needed?",
        "1. Client → server: **SYN** (seq = x): \"I want to connect; my initial sequence number is x\".\n2. Server → client: **SYN-ACK** (seq = y, ack = x + 1).\n3. Client → server: **ACK** (ack = y + 1).\n\n"
        "Three messages are needed so that **both sides** confirm that the other can send and receive and agree on both initial sequence numbers; two messages could not confirm the server's number. Closing uses **FIN** and **ACK** in each direction (a four-way close), because each direction is closed independently (half-close). The side that closes first waits in **TIME_WAIT** for about 2 × MSL to ensure the last ACK arrives and old packets die. A flood of SYNs without the final ACK is a **SYN flood** attack."),
    written("cn-url", "What happens when you type a URL", "Medium",
        "Describe everything that happens from typing https://example.com in a browser until the page appears.",
        "1. The browser checks its **caches** and the OS resolves the name: a **DNS** query (recursive resolver → root → TLD → authoritative server) returns an **IP address**.\n"
        "2. It opens a **TCP connection** to port 443 (three-way handshake).\n"
        "3. A **TLS handshake** negotiates the cipher, verifies the server's **certificate** chain against trusted authorities and derives session keys.\n"
        "4. The browser sends an **HTTP request** (`GET / HTTP/1.1` or HTTP/2) with headers and cookies.\n"
        "5. The request may pass **load balancers, reverse proxies and CDNs** before reaching the application server, which may query a **database** or cache and returns an HTTP response (status, headers, body).\n"
        "6. The browser parses the HTML, requests the **CSS, JavaScript and images** (reusing the connection), builds the DOM, runs scripts and **renders** the page.\n\n"
        "Each hop uses **ARP** to find the next MAC address, and routers forward packets by IP; NAT may rewrite addresses on the way."),
    written("cn-dns", "How DNS works", "Medium",
        "Explain DNS resolution and record types.",
        "DNS maps names to addresses through a **hierarchy** of servers. A **recursive resolver** (your ISP or 8.8.8.8) does the work: it asks a **root server** for the `.com` servers, a **TLD server** for the servers of `example.com`, and the **authoritative server** for the final answer, then **caches** it for the record's **TTL**.\n\n"
        "Records: **A** (name → IPv4), **AAAA** (IPv6), **CNAME** (alias to another name), **MX** (mail servers), **NS** (name servers of a zone), **TXT** (text such as SPF and verification), **PTR** (reverse lookup). DNS uses **UDP port 53** for small queries and TCP for large responses and zone transfers. Low TTLs allow quick changes (failover) but cause more queries."),
    written("cn-subnetting", "Subnetting", "Medium",
        "A host has the address 192.168.10.77/26. Find the subnet mask, the network address, the broadcast address and the number of usable hosts. Then split 10.0.0.0/24 into four equal subnets.",
        f"**/26** means 26 network bits, so the mask is **{NET.netmask}** (the last octet has 2 network bits: 11000000 = 192). Host bits = 32 − 26 = 6, so each subnet has 2⁶ = 64 addresses, of which **{HOSTS}** are usable (the first is the network address, the last the broadcast).\n\n"
        f"The block size in the last octet is 64, so 77 falls in the block starting at 64: network address **{NET.network_address}**, broadcast **{NET.broadcast_address}**, usable range .65 to .126.\n\n"
        f"Four equal subnets of 10.0.0.0/24 need 2 more bits (/26): **{', '.join(str(s) for s in SUBNETS)}**. In general, for n subnets borrow ⌈log₂ n⌉ bits and each has 2^(host bits) − 2 usable addresses.",
        hint="Block size = 256 − (last octet of the mask)."),
    written("cn-https-tls", "HTTP versus HTTPS", "Medium",
        "What does HTTPS add to HTTP and how does the TLS handshake establish a secure channel?",
        "**HTTPS = HTTP over TLS.** It gives **confidentiality** (encryption), **integrity** (tampering is detected) and **authentication** of the server (a certificate). The handshake: the client sends the TLS versions and cipher suites it supports; the server replies with its **certificate** and key-exchange data; the client **verifies the certificate** (a chain to a trusted CA, a matching hostname, not expired or revoked); both sides run a **key exchange** (ephemeral Diffie-Hellman gives forward secrecy) and derive **symmetric session keys**. After that, data is encrypted with the fast symmetric cipher. TLS 1.3 completes the handshake in one round trip. Asymmetric cryptography is used only to set up the keys, because symmetric encryption is far faster."),
    written("cn-http-methods", "HTTP methods and status codes", "Easy",
        "Which HTTP methods are safe and idempotent? Give the meaning of the status code classes.",
        "**Safe** methods do not change server state: GET, HEAD, OPTIONS. **Idempotent** methods give the same result if repeated: GET, HEAD, PUT, DELETE (and OPTIONS); POST is neither safe nor idempotent, so repeating it may create a second resource. PATCH is generally not idempotent.\n\n"
        "Status classes: **1xx** informational, **2xx** success (200 OK, 201 Created, 204 No Content), **3xx** redirection (301 permanent, 302/307 temporary, 304 Not Modified), **4xx** client error (400, 401 unauthenticated, 403 forbidden, 404, 429 too many requests), **5xx** server error (500, 502 bad gateway, 503 unavailable, 504 gateway timeout)."),
    written("cn-delay", "Transmission and propagation delay", "Medium",
        "A 1 MB file is sent over a 10 Mbps link that is 2,000 km long (signals travel at 2 × 10⁸ m/s). Compute the transmission delay and the propagation delay.",
        f"**Transmission delay** = size / bandwidth = (8 × 10⁶ bits) / (10 × 10⁶ bits/s) = **{TRANSMISSION} s**: the time to push all the bits onto the wire.\n\n"
        f"**Propagation delay** = distance / signal speed = (2 × 10⁶ m) / (2 × 10⁸ m/s) = **{PROPAGATION} s** (10 ms): the time for a bit to travel along the wire.\n\n"
        "Total ≈ 0.81 s here, dominated by transmission. For a small packet on a long link propagation dominates instead, which is why latency (RTT) matters more than bandwidth for small requests. The full delay of a packet is processing + queueing + transmission + propagation."),
    written("cn-flow-congestion", "Flow control versus congestion control", "Hard",
        "What is the difference between TCP flow control and congestion control? Describe slow start.",
        "**Flow control** protects the **receiver**: the receiver advertises a window (**rwnd**) saying how much buffer space it has, and the sender never has more unacknowledged data than that. **Congestion control** protects the **network**: the sender keeps its own **congestion window (cwnd)** and sends at most min(rwnd, cwnd).\n\n"
        f"**Slow start** begins with cwnd = 1 MSS and **doubles each RTT** (each ACK adds one MSS) until it reaches **ssthresh**; then **congestion avoidance** adds 1 MSS per RTT. With ssthresh = 16 the window grows {', '.join(str(x) for x in trace)}... On loss, **fast retransmit** (3 duplicate ACKs) halves cwnd (multiplicative decrease); a timeout resets cwnd to 1. This **AIMD** (additive increase, multiplicative decrease) behaviour makes competing flows share a link fairly."),
    written("cn-devices", "Hub, switch and router", "Easy",
        "What is the difference between a hub, a switch and a router?",
        "A **hub** (layer 1) repeats every signal to all ports: one shared collision domain, no intelligence. A **switch** (layer 2) learns which **MAC addresses** are on which port and forwards frames only to the right port: each port is its own collision domain, and a VLAN separates broadcast domains. A **router** (layer 3) forwards **IP packets** between different networks using a routing table and separates broadcast domains. A modern home 'router' is a router + switch + Wi-Fi access point + NAT + DHCP in one box."),
    written("cn-routing", "Distance vector and link state routing", "Hard",
        "Compare distance vector (RIP) and link state (OSPF) routing. What is the count-to-infinity problem?",
        "**Distance vector:** each router tells its **neighbours** its whole table of (destination, distance) and updates its own by the Bellman-Ford rule: simple, but slow to converge and it only knows what neighbours say. **Link state:** each router **floods** the state of its own links to **all** routers, so everyone has the full topology map and runs **Dijkstra** locally: fast convergence and loop-free, at the cost of more memory and flooding traffic.\n\n"
        "**Count to infinity:** when a link fails, routers can keep advertising stale routes to each other through each other and the distance slowly counts up. Mitigations are **split horizon** (do not advertise a route back to where you learned it), **poison reverse** and a small maximum metric (RIP's 16 = infinity). Between autonomous systems the Internet uses the path-vector protocol **BGP**."),
    written("cn-nat-arp-dhcp", "NAT, ARP and DHCP", "Medium",
        "What do NAT, ARP and DHCP do?",
        "**DHCP** gives a host that joins a network its **IP address, mask, gateway and DNS server** automatically (the DORA exchange: Discover, Offer, Request, Acknowledge). **ARP** maps an **IP address to a MAC address** on the local network: the host broadcasts 'who has 192.168.1.1?' and the owner replies; the answer is cached. **NAT** lets many devices with **private** addresses (10.x, 172.16-31.x, 192.168.x) share one **public** address: the router rewrites the source address and port and keeps a translation table to map the replies back. NAT saved IPv4 addresses but breaks end-to-end connectivity, which IPv6 (with its huge address space) restores."),
    written("cn-cors-rest", "CORS and the same-origin policy", "Medium",
        "What is the same-origin policy, and what problem does CORS solve?",
        "Browsers enforce the **same-origin policy**: a script from one **origin** (scheme + host + port) cannot read responses from another, which stops a malicious site from using your logged-in session to read data from your bank. A React app on `localhost:5173` calling an API on `localhost:8080` is a different origin and would be blocked.\n\n"
        "**CORS (cross-origin resource sharing)** lets the **server** opt in: it sends headers such as `Access-Control-Allow-Origin: https://app.example.com`, `-Methods` and `-Headers`. For 'non-simple' requests the browser first sends a **preflight** `OPTIONS` request and proceeds only if the server allows it. CORS is enforced by the **browser**, not the server: it does not protect an API from curl or other servers, so it is no substitute for authentication."),
]

SUBJECT = subject("core-cn", "Computer Networks", "Core subjects", 41,
    "Layers, TCP and UDP, DNS, subnetting, TLS, routing and everyday web networking. Subnetting and delay answers are computed, not estimated.",
    QUESTIONS,
    platforms=[
        {"name": "GeeksforGeeks: Computer Networks", "url": "https://www.geeksforgeeks.org/computer-networks/computer-network-tutorials/", "note": "Tutorials and practice questions"},
        {"name": "Beej's Guide to Network Programming", "url": "https://beej.us/guide/bgnet/", "note": "Sockets explained from first principles, free"},
    ])
