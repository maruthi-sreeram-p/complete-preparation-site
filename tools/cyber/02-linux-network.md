@part cyber-linux-network | Linux and networking for security | foundations
## Linux for security work

Servers, containers, cloud machines and most security tools run on Linux, so you need to be comfortable at its command line. You do not need to be an administrator, but you must be able to look around a machine, read logs and understand permissions.

### Files, users and permissions

Everything is a file, arranged in one tree starting at `/`. The places security people look first:

| Path | What is there |
|---|---|
| `/etc/passwd` | account list (world-readable; no password hashes in it on modern systems) |
| `/etc/shadow` | password hashes, readable by root only |
| `/etc/sudoers` | who may run commands as root |
| `/var/log/` | logs: `auth.log` or `secure` (logins, sudo), `syslog`, web server logs |
| `/home/<user>/.ssh/` | a user's SSH keys and `authorized_keys` |
| `/tmp` | world-writable scratch space, a favourite place for attackers to drop files |
| `/proc` | live view of processes and the kernel |

Every file has an **owner**, a **group** and three permission sets (owner, group, others), each made of **r** (read = 4), **w** (write = 2) and **x** (execute = 1).

```bash Reading and setting permissions
ls -l report.txt
# -rw-r----- 1 alice staff 120 Nov 1 10:00 report.txt
#  rw- r-- ---  = 6 4 0  -> owner read+write, group read, others nothing
chmod 640 report.txt        # same, as an octal number
chmod u+x,g-r script.sh     # symbolic form: add execute for owner, remove read for group
chown alice:staff report.txt
```

- **Directories:** `x` means "may enter", `r` means "may list names", `w` means "may create and delete entries".
- **umask** removes bits from the default mode. Files start at 666 and directories at 777. With umask 022 a new file is 644 and a new directory 755. With umask 027 a new file is 640 and a directory 750.
- **setuid (4xxx)** makes a program run with its owner's rights (`passwd` is root-owned setuid so you can change your password). A setuid program with a bug is a classic route to root, so `find / -perm -4000` is a standard audit command.
- **sticky bit (1xxx)** on a directory such as `/tmp` stops users from deleting each other's files.
- **sudo** runs one command as root and leaves a log line. Prefer a short, specific `sudoers` rule over giving everyone full root.

### Processes, networking and logs from the shell

```bash A first look at a machine
whoami; id                      # who am I, which groups
ps aux --sort=-%cpu | head      # busiest processes
ss -tulpn                       # listening TCP/UDP ports and the process that owns each
ip addr; ip route               # addresses and routes
last -n 10                      # recent logins
sudo grep "Failed password" /var/log/auth.log | tail
journalctl -u ssh --since "1 hour ago"
find / -perm -4000 -type f 2>/dev/null     # setuid files
```

- **Text tools** are the security analyst's spreadsheet: `grep` filters lines, `cut` and `awk` take columns, `sort | uniq -c | sort -nr` counts and ranks. The pipeline `grep "Failed password" auth.log | awk '{print $(NF-3)}' | sort | uniq -c | sort -nr | head` shows the IP addresses with the most failed SSH logins.
- **Package updates** are a security control: `apt update && apt upgrade` or `dnf update` close known holes.
- **SSH** is the standard remote login. Use **key pairs** instead of passwords, disable root login and password login in `/etc/ssh/sshd_config` (`PermitRootLogin no`, `PasswordAuthentication no`), and treat a private key like a password.
- **Firewall tools:** `ufw` (simple) and `iptables` or `nftables` (full control) decide which packets are accepted.

!cheat Linux cheat codes ::
- **Octal:** r=4, w=2, x=1. `rwxr-x---` = **750**. `rw-r-----` = **640**.
- **umask** subtracts: files 666 − umask, directories 777 − umask. 022 gives 644 and 755.
- **Where did someone log in from?** `last`, `lastb`, `/var/log/auth.log`.
- **What is listening?** `ss -tulpn`. Anything you do not recognise is a question to ask.
- **Hardening first five:** patch, key-only SSH, no root login, firewall on, remove unused services.
- A file that is **world-writable** (`o+w`) and executed by root is a privilege-escalation gift.
!end

## Networking the way a security person sees it

### Layers and addresses

| Layer (TCP/IP) | Unit | Example protocols | Typical attacks at this layer |
|---|---|---|---|
| Application | message | HTTP, DNS, SMTP, SSH | injection, XSS, DNS tunnelling |
| Transport | segment | TCP, UDP | SYN flood, port scanning |
| Internet | packet | IP, ICMP | IP spoofing, ping floods |
| Link | frame | Ethernet, Wi-Fi, ARP | ARP spoofing, MAC flooding, rogue access point |

- **MAC address:** 48-bit hardware address, used inside one local network. **IP address:** logical address used across networks. **Port:** 16-bit number (0 to 65535) naming a service on a host.
- **IPv4** addresses are 32 bits. **CIDR notation** `192.168.1.0/26` means the first 26 bits are the network and the last 6 are for hosts. That gives 2⁶ = 64 addresses, of which **62 are usable** (the first is the network address, the last is the broadcast address).
- **Private ranges (RFC 1918):** `10.0.0.0/8`, `172.16.0.0/12` (172.16 to 172.31), `192.168.0.0/16`. They are not routed on the internet. `127.0.0.0/8` is loopback and `169.254.0.0/16` is link-local (what a machine gives itself when DHCP fails).
- **NAT** lets many private hosts share one public address. It is not a firewall, but it does block unsolicited inbound connections as a side effect.

| Prefix | Addresses | Usable hosts |
|---|---|---|
| /24 | 256 | 254 |
| /25 | 128 | 126 |
| /26 | 64 | 62 |
| /27 | 32 | 30 |
| /28 | 16 | 14 |
| /30 | 4 | 2 |

### TCP, UDP and the handshake

- **TCP** is connection-oriented and reliable. The **three-way handshake** is **SYN → SYN/ACK → ACK**. Teardown uses FIN (or RST to abort).
- **UDP** is connectionless and has no handshake, which makes it fast and easy to spoof. DNS, DHCP, NTP and VoIP use it.
- A **SYN flood** sends many SYNs and never completes the handshake, filling the server's half-open connection table. **SYN cookies** defend against it.
- **Port states** in a scan: **open** (a service answered), **closed** (the host replied with RST) and **filtered** (no reply, usually because a firewall dropped the packet).

| Port | Service | Note |
|---|---|---|
| 20/21 | FTP | clear text. Use SFTP or FTPS |
| 22 | SSH (and SFTP) | encrypted remote shell |
| 23 | Telnet | clear text, never expose it |
| 25 | SMTP | mail between servers |
| 53 | DNS | UDP for queries, TCP for large answers and zone transfers |
| 67/68 | DHCP | UDP |
| 80 / 443 | HTTP / HTTPS | |
| 110 / 143 | POP3 / IMAP | clear text. Use 995 / 993 (TLS) |
| 123 | NTP | UDP |
| 161 | SNMP | UDP; versions 1 and 2c use a clear-text "community string" |
| 389 / 636 | LDAP / LDAPS | directory service |
| 445 | SMB | Windows file sharing, a favourite worm target |
| 1433 / 3306 / 5432 | SQL Server / MySQL / PostgreSQL | never expose to the internet |
| 3389 | RDP | remote desktop, heavily attacked when exposed |
| 8080 / 8443 | alternative HTTP / HTTPS | |

### DNS, HTTP and the other protocols attackers love

- **DNS** turns names into addresses. It is usually unauthenticated, so attackers use **cache poisoning** (making a resolver store a false answer), **DNS tunnelling** (hiding data in queries) and **subdomain takeover** (a DNS record points to a service you no longer own). **DNSSEC** signs records so forged answers can be detected. **DNS over HTTPS/TLS** encrypts the lookup.
- **HTTP** is clear text, so anyone on the path can read and change it. **HTTPS** is HTTP inside TLS. A request has a method (GET, POST...), a path, headers (`Host`, `Cookie`, `Authorization`) and an optional body. The response has a status code: **2xx** success, **3xx** redirect, **4xx** client error (401 not authenticated, 403 forbidden), **5xx** server error.
- **ARP** maps an IP to a MAC address on the local network and has no authentication. **ARP spoofing** answers "that IP is at my MAC" to intercept traffic (a man-in-the-middle).
- **DHCP** hands out addresses; a **rogue DHCP server** can point clients at the attacker's gateway or DNS.
- **ICMP** carries ping and error messages. Blocking all of it breaks path MTU discovery, so filter selectively.

!cheat Network cheat codes ::
- **/n hosts:** 2^(32−n) addresses, minus 2 usable. /26 = 62, /27 = 30, /28 = 14.
- **Block size trick:** a /26 splits a /24 into blocks of 64 (0, 64, 128, 192). 192.168.1.70/26 is in the block starting at .64.
- **TCP handshake:** SYN, SYN/ACK, ACK. RST means refused or aborted.
- **Clear-text twins:** Telnet→SSH, FTP→SFTP, HTTP→HTTPS, POP3/IMAP→with TLS.
- **Scan reading:** RST = closed, silence = filtered, SYN/ACK = open.
- **DNS** = UDP/53 for queries, TCP/53 for zone transfers and big answers.
!end

## Seeing the traffic: scanning and packet analysis

### Nmap (only on machines you may scan)

Nmap discovers hosts and open ports. On your own lab network:

```bash Common nmap scans
nmap 192.168.56.101                  # top 1000 TCP ports
nmap -sn 192.168.56.0/24             # ping sweep: which hosts are up?
nmap -p- 192.168.56.101              # all 65535 ports
nmap -sV -p 22,80,443 192.168.56.101 # service and version detection
nmap -sS 192.168.56.101              # SYN ("half-open") scan, needs root
nmap -A 192.168.56.101               # OS detection, versions, default scripts, traceroute
nmap --script vuln 192.168.56.101    # run vulnerability-check scripts (lab machines only)
```

- A **connect scan** (`-sT`) completes the handshake and is logged by the application. A **SYN scan** (`-sS`) sends SYN, reads the reply and then sends RST, so the connection never completes.
- **Banner grabbing** (`-sV`, `nc host 80`) reads the version a service announces. That is why you should hide version banners in production.
- Scans are noisy and visible in logs. That is fine for testing, and a useful detection signal for defenders.

### Wireshark and tcpdump

Wireshark (a GUI) and `tcpdump` (a command line) capture packets. Filters you will use in practice:

| Goal | Wireshark display filter | tcpdump capture filter |
|---|---|---|
| one host | `ip.addr == 10.0.0.5` | `host 10.0.0.5` |
| one port | `tcp.port == 443` | `port 443` |
| DNS only | `dns` | `udp port 53` |
| HTTP requests | `http.request` | `tcp port 80` |
| SYN packets | `tcp.flags.syn == 1 && tcp.flags.ack == 0` | `tcp[tcpflags] & tcp-syn != 0` |

What to look for: a three-way handshake, a stream of SYNs with no ACKs (flood or scan), credentials in a clear-text protocol, many DNS queries with long random names (tunnelling), and a host answering ARP for an address that is not its own.

!tip Capture on your own network only :: Sniffing other people's traffic is illegal in most places. Use a home lab, a virtual machine network or a recorded `.pcap` from a training site.

## Network attacks and their defences

| Attack | How it works | Defence |
|---|---|---|
| **Sniffing** | reading traffic on a shared or compromised path | encryption (TLS, SSH, VPN), switched networks |
| **ARP spoofing / MITM** | forged ARP replies put the attacker on the path | dynamic ARP inspection, static entries for critical hosts, TLS everywhere |
| **DNS cache poisoning** | forged answers are accepted by the resolver | DNSSEC, randomised source ports and transaction IDs, patched resolvers |
| **SYN flood** | half-open connections exhaust the table | SYN cookies, rate limiting, upstream scrubbing |
| **DDoS amplification** | small spoofed requests to open resolvers or NTP servers produce large replies to the victim | disable open resolvers, filter spoofed source addresses (BCP 38), use a CDN |
| **Rogue access point / evil twin** | a fake Wi-Fi with a familiar name | WPA3 or WPA2-Enterprise, user training, certificate checks |
| **VLAN hopping** | tagged frames escape their VLAN | disable unused trunking, set the native VLAN to an unused one |
| **Port scanning** | mapping open services | close unused ports, firewall rules, detect and alert |

### The building blocks of network defence

- **Firewall:** a **packet filter** decides by address, port and protocol. A **stateful** firewall also remembers established connections, so return traffic is allowed without a separate rule. A **next-generation firewall** adds application awareness and intrusion prevention. A **WAF** (web application firewall) understands HTTP and blocks things like SQL injection patterns.
- **Rule order matters.** Rules are read top to bottom and the first match wins, and the last rule should be **deny all**.
- **DMZ:** a separate network segment for public-facing servers so a compromise does not land inside the internal network.
- **Segmentation (VLANs, subnets, security groups):** limits lateral movement. A printer should not be able to talk to the database.
- **VPN:** an encrypted tunnel (IPsec, WireGuard, OpenVPN). It protects traffic in transit and extends the private network, but it does not make the connecting device trustworthy.
- **IDS / IPS:** an intrusion **detection** system alerts, an intrusion **prevention** system sits inline and blocks. **Signature-based** engines (Snort, Suricata rules) match known patterns, **anomaly-based** engines flag deviations from a baseline and produce more false positives.
- **Proxy:** a **forward proxy** sits in front of users and filters outbound traffic. A **reverse proxy** or load balancer sits in front of servers, terminates TLS and hides them.
- **Honeypot:** a decoy system that exists to be attacked, so defenders can watch and learn.

!interview A firewall question that is asked often :: "Inbound rules: allow TCP 443 to the web server, allow TCP 22 only from the admin subnet, deny everything else. Outbound: allow what the server needs (DNS, updates) and deny the rest. Because the firewall is stateful, replies to allowed connections need no extra rule. Order matters: the specific allows come before the final deny."

!keypoints /n gives 2^(32−n) addresses and two fewer usable hosts ;; TCP opens with SYN, SYN/ACK, ACK and a closed port answers RST ;; Replace clear-text protocols (Telnet, FTP, HTTP) with encrypted ones ;; ARP and DNS have no built-in authentication, so they can be spoofed ;; Stateful firewalls remember connections and the last rule should be deny all ;; Scan and capture only on networks you own or may test

?? What does `chmod 750 deploy.sh` give to the owner, the group and others?
=> Owner read, write and execute (7), group read and execute (5), others nothing (0).
?? A new network needs 50 hosts. Which is the smallest IPv4 prefix that fits, and how many usable hosts does it have?
=> A /26: 64 addresses, 62 usable. A /27 has only 30 usable.
?? Describe how a SYN scan tells open, closed and filtered ports apart.
=> An open port answers SYN/ACK. A closed port answers RST. A filtered port gives no answer or an ICMP unreachable, because a firewall is dropping the probe.
?? Why is Telnet considered unsafe, and what replaces it?
=> It sends everything, including the password, in clear text, so anyone on the path can read it. SSH encrypts the session and supports key-based login.
?? How does a stateful firewall differ from a simple packet filter?
=> It tracks connections, so return traffic for an allowed outbound connection is accepted automatically without an explicit inbound rule.
?? You see hundreds of failed SSH logins from one IP in `auth.log`. List three responses.
=> Block or rate-limit the IP (a firewall rule or fail2ban), disable password logins in favour of keys, and check whether any login from that IP succeeded.
