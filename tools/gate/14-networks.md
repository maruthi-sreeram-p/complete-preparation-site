@part gate-networks | Computer Networks | systems
## Layering, switching and performance

### Layered models

Layering splits a complex job into layers, each offering a service to the layer above and using the service of the layer below. Each layer adds its own **header** (encapsulation) and the receiver removes them in reverse order.

| TCP/IP layer | OSI layers | Unit | Examples |
|---|---|---|---|
| Application | application, presentation, session | message | HTTP, DNS |
| **Transport** | transport | segment (TCP) / datagram (UDP) | TCP, UDP: **process-to-process** delivery |
| **Network (Internet)** | network | packet / datagram | IP, routing: host-to-host delivery |
| **Link** | data link, physical | frame | Ethernet, switches: hop-to-hop delivery |

### Switching

| Technique | Setup | Resources | Remarks |
|---|---|---|---|
| **Circuit switching** | call setup | bandwidth reserved for the whole call | constant delay, wasteful for bursty data |
| **Packet switching (datagram)** | none | shared, statistical multiplexing | each packet routed independently by full destination address |
| **Virtual circuit** | setup phase | per-connection state in routers | packets carry a short **VC identifier**, follow one path |

Statistical multiplexing is why packet switching wins for bursty traffic. A 1 Mbps link and users needing 100 kbps each: circuit switching supports 10 users, while packet switching can support many more whose peaks rarely coincide.

### Delays and metrics

- **Transmission delay = L / R** (packet size over link rate). A 1500-byte packet on 100 Mbps: 12 000 / 10⁸ = 120 µs.
- **Propagation delay = d / s** (distance over signal speed, about 2 × 10⁸ m/s).
- Plus **processing** and **queuing** delays. Total per hop is the sum.
- **Store and forward:** a router receives a whole packet before forwarding. A message of M bits over k links of rate R takes k·M/R if sent as one packet. Split into n equal packets it takes **(k + n − 1)·(M/n)/R**. A 12 000-bit message over 3 links at 1 Mbps in 3 packets of 4000 bits: (3 + 3 − 1) × 4 ms = **20 ms** (36 ms as one packet).
- **Bandwidth–delay product** = R × RTT, the number of bits "in flight" on the pipe. 100 Mbps and RTT 40 ms give 4 Mbit = 500 000 bytes.
- **Throughput** is the achieved rate. **Utilisation** is the fraction of time the sender is busy.

!cheat Layering and delay cheat codes ::
- **Pipeline formula:** n packets over k store-and-forward hops = (k + n − 1) packet times.
- **Per-hop delay** = L/R + propagation. Do not add propagation for each packet more than once per link in a pipelined stream.
- **Which layer?** Process-to-process = transport, host-to-host = network, hop-to-hop = link.
- **BDP** tells you how large a window must be to keep a link full: window ≥ R × RTT.
!end

## Data link layer

### Framing

Frames are delimited by a flag. With the flag 01111110, **bit stuffing** makes sure the flag cannot appear inside the data: the sender inserts a 0 after every **five consecutive 1s**, and the receiver removes it. The data 0111111011111011 becomes 011111010111110011 on the wire.

### Error detection and correction

| Method | Idea |
|---|---|
| Parity | one extra bit; detects any odd number of bit errors |
| **Internet checksum** | 16-bit one's-complement sum of the words, then complemented. For 0x1234 and 0xEDCB the sum is 0xFFFF, so the checksum is 0x0000 |
| **CRC** | the data, followed by r zeros, is divided modulo 2 by a generator polynomial of degree r; the remainder (r bits) is appended |
| Hamming code | check bits at the power-of-2 positions; r check bits are needed when 2^r ≥ m + r + 1 |

- **CRC example:** data 110101, generator 1011 (degree 3). Divide 110101000 by 1011 modulo 2; the remainder is **111**, so the frame sent is 110101111.
- A CRC with generator of degree r detects all burst errors of length ≤ r and all single- and double-bit errors for a suitable generator.
- **Hamming distance d** between code words: the code **detects d − 1** errors and **corrects ⌊(d − 1)/2⌋**. Distance 5 detects 4 and corrects 2. For 11 data bits you need 4 check bits (16 ≥ 11 + 4 + 1).

### Flow control and sliding window

Let Tt be the frame transmission time and Tp the one-way propagation time, with **a = Tp / Tt**.

| Protocol | Efficiency or window rule |
|---|---|
| **Stop-and-wait** | efficiency = 1 / (1 + 2a). With Tt = 1 ms, Tp = 4 ms (a = 4): 1/9 ≈ 11.1% |
| **Sliding window** (window N) | utilisation = min(1, N / (1 + 2a)). N = 5, a = 4: 5/9 ≈ 55.6% |
| **Go-Back-N** | window ≤ 2ᵏ − 1 with k-bit sequence numbers; on a loss the sender retransmits that frame and every later one |
| **Selective repeat** | window ≤ 2^(k−1); only the lost frame is retransmitted |

With 3-bit sequence numbers: Go-Back-N window ≤ 7, selective repeat ≤ 4. If frames 0 to 6 are sent and frame 3 is lost, Go-Back-N retransmits frames 3, 4, 5, 6 (four frames) while selective repeat resends only frame 3.

### Medium access and Ethernet

| Protocol | Maximum efficiency or note |
|---|---|
| Pure ALOHA | 1/(2e) ≈ **18.4%** |
| Slotted ALOHA | 1/e ≈ **36.8%** |
| CSMA/CD (Ethernet) | listen before sending, detect collisions while sending, back off |
| CSMA/CA (Wi-Fi) | avoids collisions using acknowledgements and waiting |

- **CSMA/CD minimum frame size:** a sender must still be transmitting when a collision signal returns, so **minimum frame time ≥ 2 × Tp**: minimum frame length ≥ 2 × Tp × R. With R = 100 Mbps and Tp = 5 µs: 2 × 5 µs × 100 Mbps = 1000 bits = **125 bytes**.
- **Binary exponential backoff:** after the n-th collision a station waits K slot times with K chosen uniformly from {0, 1, …, 2ⁿ − 1} (n capped at 10). After the 4th collision K ∈ {0, …, 15}.
- **Ethernet frame:** preamble 8 bytes, destination 6, source 6, type 2, **payload 46–1500**, FCS 4. The minimum frame (excluding preamble) is **64 bytes**, the maximum 1518.
- **Devices:** a hub repeats bits to all ports (one collision domain). A **switch** learns addresses, forwards frames only to the right port, and gives **each port its own collision domain** while all ports stay in one broadcast domain (unless VLANs are used). A router separates broadcast domains.

!cheat Data-link cheat codes ::
- **a = Tp / Tt:** stop-and-wait efficiency 1/(1 + 2a). A sliding window of N frames fills the pipe when N ≥ 1 + 2a.
- **Window limits:** GBN 2ᵏ − 1, SR 2^(k−1).
- **CRC by hand:** XOR the generator under each leading 1, shift, and repeat. The remainder has r bits.
- **Hamming distance rule:** detect d − 1, correct ⌊(d − 1)/2⌋.
- **Collision domains:** one per switch port. Broadcast domains: one per router interface (or VLAN).
- **Bit stuffing:** after 11111 insert 0. Count the extra zeros to get the frame length.
!end

## Routing

Routers build tables that map a destination to an outgoing link. Two main families:

| | Distance vector | Link state |
|---|---|---|
| What a router sends | its whole table (distance to every destination) | the state of its own links |
| To whom | neighbours only | all routers (flooding) |
| Algorithm | Bellman–Ford | Dijkstra on the complete topology |
| Examples | RIP | OSPF |
| Problems | slow convergence, **count to infinity** | more messages and memory |

- **Distance-vector update:** cost(X → D) = min over neighbours N of [cost(X, N) + dist(N, D)]. If A has neighbours B (cost 2) and C (cost 5), and B advertises 4 to D while C advertises 1, then A's cost to D is min(2 + 4, 5 + 1) = **6** via B.
- **Count-to-infinity:** after a link failure, routers keep raising the distance to an unreachable destination in small steps. **Split horizon** (do not advertise a route back to the neighbour it was learned from) and **poison reverse** reduce it. RIP treats a distance of **16** as infinity.
- **Link-state:** each router floods link-state advertisements, then every router runs Dijkstra. For the network A–B 1, A–C 4, B–C 2, B–D 5, C–D 1, the distances from A are B 1, C 3 (via B), D 4 (via B, then C). The next hop from A towards D is B.
- **Autonomous systems:** inside an AS an interior protocol (RIP, OSPF) is used. Between ASes BGP (a path-vector protocol) is used.

!cheat Routing cheat codes ::
- **Distance vector by hand:** for every destination take the minimum of (link cost to neighbour + the neighbour's advertised cost).
- **Link state by hand:** run Dijkstra from the router and record the first hop on each shortest path.
- **Count to infinity:** a distance-vector problem, not link-state.
- **Message complexity:** DV talks to neighbours only; LS floods everyone.
!end

## IPv4 addressing, fragmentation and NAT

### Addresses and CIDR

An IPv4 address has 32 bits. **CIDR notation** a.b.c.d/n means the first n bits are the network prefix. The remaining 32 − n bits are the host part.

- **Addresses per subnet = 2^(32−n)**, usable hosts = 2^(32−n) − 2 (the network and broadcast addresses are reserved). A /26 has 62 hosts; a /20 has the mask 255.255.240.0.
- **Network address = IP AND mask.** For 192.168.37.130/26: the block size is 64, 130 lies in 128–191, so the network is 192.168.37.128. The **broadcast address** is the last address in the block: for 172.16.5.77/27 (block 32, range 64–95) it is 172.16.5.95.
- **Subnetting** splits a block: 192.168.1.0/24 into /27 subnets gives 2³ = 8 subnets.
- **Aggregation (supernetting):** the eight blocks 200.1.16.0/24 to 200.1.23.0/24 combine into 200.1.16.0/21.
- **Longest prefix match:** a router picks the matching table entry with the **longest prefix**. With 10.0.0.0/8 → R1, 10.1.0.0/16 → R2, 10.1.2.0/24 → R3 and a default route → R4, the destination 10.1.9.5 goes to R2, 10.1.2.77 to R3 and 11.0.0.1 to R4.
- **Classful ranges** (historical): A 1–126 (/8), B 128–191 (/16), C 192–223 (/24). **Private ranges:** 10.0.0.0/8, 172.16.0.0/12 (172.16–172.31) and 192.168.0.0/16. So 172.20.5.9 is private but 172.32.1.1 is not.

### The IPv4 header and fragmentation

The header is 20 bytes without options; the **IHL** field gives the header length in **32-bit words** (IHL = 8 means 32 bytes). Important fields are the total length (16 bits), identification, flags (DF, MF), **fragment offset** (in units of 8 bytes), TTL (decremented by each router; the packet is dropped at 0) and the header checksum.

If a datagram is larger than a link's **MTU**, a router fragments it. Each fragment's data length (except the last) must be a multiple of 8, with its own header.

Example: a datagram of 4000 bytes (20-byte header, 3980 bytes data) and MTU 1500: the largest data size per fragment is ⌊(1500 − 20)/8⌋ × 8 = 1480. Fragments carry 1480, 1480 and 1020 bytes of data: **3 fragments**, with fragment offsets 0, 185 and 370 (2960 / 8 = 370 for the last), and MF = 1 on all but the last.

### NAT

**Network address translation** lets many hosts with private addresses share one public address. The NAT box rewrites the source address and port of outgoing packets and keeps a table mapping (private IP, port) to (public IP, new port), then reverses the mapping for replies.

!cheat IPv4 cheat codes ::
- **Block size = 2^(32−n)** within the interesting octet. Network = the largest multiple of the block size not above the address.
- **Hosts = 2^(32−n) − 2.**
- **Aggregation test:** blocks aggregate if they are contiguous, of equal size, and the first starts on a boundary of the combined size.
- **Fragments:** per-fragment data = ⌊(MTU − header)/8⌋ × 8. Offset = bytes before it ÷ 8.
- **Longest prefix wins,** not the first match in the table.
- **IHL × 4 = header bytes.**
!end

## Transport layer: TCP, UDP and sockets

**UDP** is connectionless and unreliable, with an 8-byte header (source port, destination port, length, checksum). It suits real-time traffic such as video calls, where a late packet is useless. **TCP** is connection-oriented, reliable, ordered, with flow and congestion control. Its header is at least 20 bytes (the data offset field counts 32-bit words, so offset 8 means 32 bytes).

### Connection management and numbering

- **Three-way handshake:** SYN → SYN-ACK → ACK. A SYN consumes one sequence number, so if the client's initial sequence number is 2000 the server's acknowledgement number is 2001.
- **Sequence numbers count bytes.** A segment whose first byte has number 1000 and carries 500 bytes is acknowledged by ACK 1500, the number of the next byte expected.
- Closing uses FIN and ACK exchanges in each direction.
- **Wrap-around:** 32-bit sequence numbers cover 2³² bytes. At 1 Gbps they wrap in 2³² × 8 / 10⁹ ≈ **34.4 s**.

### Flow control

The receiver advertises a **window** (rwnd) of free buffer space. The sender may have at most **min(cwnd, rwnd)** unacknowledged bytes in flight. The maximum throughput of a window W and round-trip time RTT is **W / RTT**: 64 KB and 100 ms give 64 × 1024 × 8 / 0.1 ≈ 5.24 Mbps.

### Congestion control

| Phase | Behaviour |
|---|---|
| **Slow start** | cwnd starts at 1 MSS and **doubles every RTT** (+1 MSS per ACK) until cwnd reaches ssthresh |
| **Congestion avoidance** | additive increase: **+1 MSS per RTT** |
| Timeout | ssthresh = cwnd / 2, cwnd = 1 MSS, back to slow start |
| Three duplicate ACKs (fast retransmit and recovery) | ssthresh = cwnd / 2, cwnd = ssthresh (then linear growth) |

With ssthresh = 16 MSS and no loss, the cwnd at the start of RTT 1, 2, 3, … is 1, 2, 4, 8, 16, 17, 18 … If the timeout happens at cwnd = 20, then ssthresh = 10 and cwnd restarts at 1.

**RTT estimation:** EstimatedRTT = (1 − α)·EstimatedRTT + α·SampleRTT with α = 1/8, so Estimated 100 ms and Sample 180 ms give 0.875 × 100 + 0.125 × 180 = 110 ms. The timeout is EstimatedRTT + 4 × DevRTT.

### The socket API

| Role | Call order (TCP) |
|---|---|
| Server | `socket()` → `bind()` → `listen()` → `accept()` → `recv()` / `send()` → `close()` |
| Client | `socket()` → `connect()` → `send()` / `recv()` → `close()` |

`accept()` blocks until a client connects and returns a **new socket** for that connection, while the listening socket keeps accepting. For UDP there is no `listen`, `accept` or `connect`: the server does `socket()`, `bind()`, then `recvfrom()` / `sendto()`.

!cheat Transport cheat codes ::
- **Throughput limit = window / RTT.** To fill a link you need window ≥ bandwidth × RTT.
- **cwnd sequence:** write it out per RTT: 1, 2, 4, … up to ssthresh, then +1 per RTT. After a loss, halve ssthresh.
- **ACK number = last byte received + 1.** SYN and FIN each take one sequence number.
- **Timeout vs duplicate ACKs:** timeout is the severe signal (cwnd to 1), triple duplicate ACK is mild (cwnd to ssthresh).
- **Server calls:** socket, bind, listen, accept. Client calls: socket, connect.
!end

## Application layer: DNS and HTTP

### DNS

DNS maps names to addresses using a hierarchical, distributed database: the **root** servers, **top-level domain** (TLD) servers (.com, .in…) and **authoritative** servers. Queries and answers use **UDP port 53**.

- A client asks its **local resolver**, which in **iterative** resolution contacts the servers itself. With an empty cache, resolving www.example.com contacts **3 servers**: a root server, a .com TLD server and the authoritative server for example.com. Caching shortens later lookups.
- Common records: **A** (name → IPv4 address), AAAA (IPv6), NS (name server), **CNAME** (alias), MX (mail exchanger).

### HTTP

HTTP is a request–response protocol over TCP (port 80, HTTPS 443). A request has a method (GET, POST, PUT, DELETE, HEAD), a path, headers and an optional body. The response has a status code: 200 OK, 301 moved permanently, **404 not found**, 500 server error. **GET, PUT and DELETE are idempotent; POST is not.** HTTP is stateless; cookies add state; caches use conditional GET.

Time to fetch a page with a base HTML file and 4 objects (RTT = 50 ms, transmission time ignored):

| Mode | RTTs | Time |
|---|---|---|
| **Non-persistent**, one object at a time | 2 per object (TCP setup + request) × 5 | 10 RTT = 500 ms |
| **Persistent, no pipelining** | 1 (setup) + 1 per object × 5 | 6 RTT = 300 ms |
| **Persistent with pipelining** | 1 (setup) + 1 (base file) + 1 (all objects together) | 3 RTT = 150 ms |

!cheat DNS and HTTP cheat codes ::
- **HTTP RTT counting:** non-persistent = 2 RTT per object, persistent = 1 RTT per object after one setup, pipelined = objects fetched together.
- **Iterative resolution with an empty cache:** root, then TLD, then authoritative.
- **HTTP 404 = not found, 200 = OK, 301 = moved.**
- **POST is the one standard method that is not idempotent.**
- **A record = name to IPv4 address.**
!end

## Cheat sheet: Computer Networks on one page

| Topic | Fact |
|---|---|
| Transmission delay | L / R |
| Pipelined store-and-forward | (k + n − 1) packet times |
| Bandwidth–delay product | R × RTT |
| Bit stuffing | 0 after five 1s |
| CRC | a generator of degree r appends an r-bit remainder |
| Hamming distance d | detect d − 1, correct ⌊(d − 1)/2⌋ |
| Stop-and-wait | 1 / (1 + 2a) |
| Sliding window | N / (1 + 2a) |
| GBN / SR window | 2ᵏ − 1 / 2^(k−1) |
| Pure / slotted ALOHA | 18.4% / 36.8% |
| CSMA/CD minimum frame | 2 × Tp × R |
| Ethernet frame | 64 to 1518 bytes |
| DV update | min(link + advertised) |
| /n hosts | 2^(32−n) − 2 |
| Longest prefix | most specific route wins |
| Fragment | data multiple of 8, offset in 8-byte units |
| TCP throughput | window / RTT |
| Slow start / avoidance | doubles per RTT / +1 per RTT |
| Timeout | ssthresh = cwnd / 2, cwnd = 1 |
| Server sockets | socket, bind, listen, accept |
| HTTP RTTs | non-persistent 2 per object; persistent 1 |

??  Why does a switch give every port its own collision domain, but a hub does not?
=> A hub repeats every bit to all ports, so all stations share one medium and collide. A switch stores each frame and forwards it only to the port of the destination, with a separate link per port, so collisions can happen only on that single link.
??  A link has bandwidth 100 Mbps and RTT 40 ms. What is the smallest window that keeps the link fully used?
=> The bandwidth–delay product: 100 × 10⁶ × 0.04 = 4 × 10⁶ bits = 500 000 bytes. A window of at least that many bytes is needed.
??  What is the difference between TCP flow control and congestion control?
=> Flow control protects the receiver: the sender never has more unacknowledged data than the receiver's advertised window. Congestion control protects the network: the sender limits cwnd based on signs of loss. The sender uses the minimum of the two.
??  Why does the IPv4 fragment offset use units of 8 bytes?
=> The offset field has only 13 bits, but datagrams can be up to 65 535 bytes. Counting in 8-byte units lets 13 bits cover the whole range, so every fragment except the last must carry a multiple of 8 data bytes.
