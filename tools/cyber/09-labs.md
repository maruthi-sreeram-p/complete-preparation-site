@part cyber-labs | Ethical hacking labs and methodology | career
## Penetration testing in one page

A **penetration test (pentest)** is an authorised, time-boxed attempt to find and demonstrate weaknesses, ending in a report that helps the owner fix them. It is not the same as a **vulnerability assessment**, which lists weaknesses (usually from a scanner) without trying to exploit them.

| Term | Meaning |
|---|---|
| **Black box** | the tester has no prior knowledge (like an outsider) |
| **Grey box** | partial knowledge, such as a normal user account (the most common web test) |
| **White box** | full access to source code and documentation |
| **Red team** | simulates a real adversary against the whole organisation, usually including detection and response |
| **Blue team** | defenders |
| **Purple team** | red and blue working together so each attack improves a detection |
| **Bug bounty** | a public programme paying researchers for valid reports within its rules |

### The phases

| Phase | What happens |
|---|---|
| **1. Pre-engagement** | scope (what is in and out), rules of engagement, testing windows, contacts, **written authorisation** ("get out of jail" letter), data handling |
| **2. Reconnaissance** | gather information: passive (public sources, no contact with the target) and active (touching the target) |
| **3. Scanning and enumeration** | find hosts, ports, services, versions, users, endpoints |
| **4. Vulnerability analysis** | work out which findings are real weaknesses |
| **5. Exploitation** | carefully prove the weakness (a controlled proof, not damage) |
| **6. Post-exploitation** | show impact within the rules: what could an attacker reach from here? Clean up afterwards |
| **7. Reporting** | clear findings, evidence, risk ratings and fixes |
| **8. Retest** | verify the fixes |

For web applications, follow the **OWASP Web Security Testing Guide (WSTG)**. It is a free checklist of what to test, organised by area (information gathering, configuration, identity, authentication, authorisation, sessions, input validation, error handling, cryptography, business logic, client side).

!warning The golden rules :: Stay inside the written scope. Do not test denial of service unless it is explicitly agreed. Do not read, copy or modify real customer data more than the minimum needed to prove a finding. Stop and report at once if you find something dangerous or outside scope. Keep evidence secure and delete it when the engagement ends as agreed.

## Build a safe home lab

You can learn nearly everything legally and for free on your own machine.

| Part | Options |
|---|---|
| **Hypervisor** | VirtualBox or VMware Workstation Player; or Docker for single applications |
| **Attacker VM** | Kali Linux or Parrot OS (pre-loaded tools). You can also use a normal Linux install and add tools |
| **Network** | a **host-only** or **internal** network between the VMs so vulnerable machines are never reachable from your home network or the internet |
| **Snapshots** | take one before every experiment so you can roll back |
| **Resources** | 8 GB RAM is enough for two VMs; 16 GB is comfortable |

### Targets you are allowed to attack (because they are made for it)

| Target | What it teaches |
|---|---|
| **OWASP Juice Shop** | a modern, deliberately insecure JavaScript shop covering the whole OWASP Top 10, with a score board. Run: `docker run -p 3000:3000 bkimminich/juice-shop` |
| **DVWA** (Damn Vulnerable Web Application) | PHP/MySQL app with adjustable security levels for SQL injection, XSS, CSRF, file upload |
| **OWASP WebGoat** | guided Java lessons, ideal for a Java developer |
| **PortSwigger Web Security Academy** | free, high-quality online labs for every web vulnerability class from the makers of Burp Suite |
| **TryHackMe** | guided "rooms" in the browser, very friendly for beginners (free and paid) |
| **Hack The Box / HTB Academy** | harder machines and structured modules |
| **OverTheWire (Bandit)** | learn the Linux command line through a wargame |
| **picoCTF** | beginner-friendly capture-the-flag competition and archive |
| **VulnHub** | downloadable vulnerable VMs for offline practice |
| **CyberDefenders, LetsDefend, Blue Team Labs** | defender-side investigations with logs and packet captures |

!tip Order of learning :: Linux basics (Bandit) → networking and Nmap (TryHackMe pre-security path) → web fundamentals with Juice Shop and PortSwigger labs → one structured path of your choice → defender labs. Writing a short note after each lab (what the flaw was, how it works, how to fix it) is the best revision and later becomes your portfolio.

## The tools and what they are for

| Tool | Purpose | Notes |
|---|---|---|
| **Nmap** | host and port discovery, service versions | start with `nmap -sV` on your lab hosts |
| **Burp Suite Community** | an intercepting proxy: see, replay and change every request your browser makes | the central tool of web testing. Repeater resends a modified request. Decoder converts encodings |
| **OWASP ZAP** | free open-source alternative with an automated scanner | easy to run in a pipeline (DAST) |
| **ffuf / gobuster** | find hidden paths and files by trying a wordlist | noisy; only on scope |
| **sqlmap** | automates SQL injection testing | lab or authorised tests only; understand the manual technique first |
| **Wireshark / tcpdump** | packet capture and analysis | follow a TCP stream to see clear-text credentials |
| **Netcat / curl** | talk to any port or HTTP endpoint by hand | `curl -i -X POST ...` shows headers; learn it well |
| **hashcat / John the Ripper** | crack password hashes you own, with wordlists | shows why salting and slow hashes matter |
| **Metasploit** | framework of exploits and payloads | learn it in the lab; real tests lean on manual understanding |
| **Nikto** | web server misconfiguration scanner | quick and noisy |
| **CyberChef** | the "Swiss army knife" for decoding and transforming data | Base64, hex, XOR, hashes in a browser |

```bash Hash cracking in a lab (your own test hashes only)
# hashcat modes: 0 = MD5, 100 = SHA-1, 1400 = SHA-256, 3200 = bcrypt
echo -n 'welcome1' | md5sum                      # unsalted MD5 of a weak password
hashcat -m 0 -a 0 hashes.txt rockyou.txt         # dictionary attack: seconds for common passwords
hashcat -m 3200 -a 0 bcrypt.txt rockyou.txt      # same wordlist against bcrypt: orders of magnitude slower
```

The point of that exercise is the contrast: an unsalted fast hash falls instantly, a salted bcrypt hash does not.

## Testing a web application, step by step

Use Burp Suite (or ZAP) as a proxy between your browser and a lab application.

1. **Map the application:** browse every feature while Burp records it. List endpoints, parameters, cookies, roles and file uploads.
2. **Understand the technology:** response headers, frameworks, error pages.
3. **Authentication tests:** weak passwords, error message differences, lockout behaviour, password reset flow, MFA bypass, session cookie flags.
4. **Session tests:** is the ID random? Does it change at login? Does logout invalidate it?
5. **Authorisation tests (the most productive):** log in as two users and a low and a high role. Replay user A's requests with user B's identifiers. Try admin URLs as a normal user.
6. **Input tests:** for each parameter ask what it reaches (a query, a file path, a template, a URL, HTML output). Test for injection, XSS, path traversal and SSRF with harmless probes first.
7. **Business logic:** what happens if you skip a step, repeat a request, change a price, use a negative number, or send two requests at once?
8. **Client side and configuration:** CORS, headers, source maps, secrets in JavaScript, exposed files like `/.git/` and `/actuator`.
9. **Record everything:** request, response, screenshot and the impact.

!cheat Web testing cheat codes ::
- **Two accounts, one app.** Most serious bugs are access control bugs, found by swapping identifiers between users.
- **Every parameter is a question:** where does this value go?
- **Change one thing at a time** and compare responses (status, length, time).
- **Harmless probes first:** a single quote, `<b>test</b>`, `../`. A tiny change that behaves differently is a lead.
- **Never trust the UI.** If a button is hidden, call the endpoint anyway.
- **Stay in scope.** Out of scope means untouched, even if it is reachable.
!end

## Reporting: the part that gets you hired

A finding is worth only as much as the clarity of its report. A good report has:

| Section | Content |
|---|---|
| **Executive summary** | one page for non-technical readers: overall risk, key findings, what to do first |
| **Scope and method** | what was tested, when, how, with what limits |
| **Findings** | one entry per issue (below), sorted by severity |
| **Appendix** | tool output, evidence, references |

Each **finding** contains: a clear title, **severity** (CVSS score and rating), affected endpoint, **description**, **reproduction steps** anyone can follow, **evidence** (request, response, screenshot), **impact** in business terms, a specific **remediation** and references (CWE, OWASP).

```text A compact example of a good finding
Title:        Insecure direct object reference in GET /api/invoices/{id}
Severity:     High (CVSS 6.5, AV:N/AC:L/PR:L/UI:N/S:U/C:H/I:N/A:N); rated High because invoices contain personal data
Description:  The endpoint returns the invoice for any id if the caller is logged in. It does not check that the invoice belongs to the caller.
Steps:        1. Log in as user A, request /api/invoices/1042 (own invoice, 200).
              2. With A's token request /api/invoices/1043 (belongs to user B). Response 200 with B's data.
Impact:       Any customer can read every other customer's name, address and purchases by counting ids.
Fix:          Check invoice.ownerId == authenticatedUser.id in the service layer; return 404 otherwise. Use unguessable ids as extra depth.
References:   CWE-639, OWASP Top 10 A01 Broken Access Control
```

Avoid: "The site is insecure." Avoid: tool dumps with no explanation. Avoid: exaggerating severity. Say what you did **not** test.

## CTFs and bug bounties

- **CTF (capture the flag):** competitions where you solve challenges to find hidden "flags". **Jeopardy** style has categories (web, crypto, forensics, reverse engineering, binary exploitation/"pwn", misc). **Attack-defence** style has teams attacking and defending live services. Start with picoCTF, then join a team via CTFtime.org.
- **Bug bounty:** platforms such as HackerOne, Bugcrowd and Intigriti list programmes with scope, rules and rewards. Read the policy fully. Never test out-of-scope assets or perform denial of service, social engineering or data extraction. Duplicates and "informational" results are normal for beginners, so do not expect income quickly. The reputation and write-ups are worth more than the first payments.
- **Responsible disclosure:** report privately, give the vendor reasonable time to fix, do not publish exploit details early and never extort.

## Defender labs

Offence teaches how attacks work. Defence labs teach how they look in logs.

- Install **Wazuh** or **Security Onion** on a VM as your own SIEM and send logs from your lab machines.
- Install **Sysmon** on a Windows VM for rich process, network and file events.
- Run small attack simulations from **Atomic Red Team** against your lab and write a detection for each (a Sigma rule), then confirm the alert fires.
- Investigate **packet captures and log sets** on CyberDefenders or LetsDefend and write an incident summary.
- Practise **phishing triage** with sample emails: read headers, check SPF/DKIM/DMARC, extract indicators.

### Portfolio-sized project ideas

1. **Break and fix your own app:** take a small Spring Boot API, deliberately add five vulnerabilities (SQL injection, IDOR, weak password hashing, stored XSS, missing authorisation), attack them, then fix each and write a before/after note with tests.
2. **Juice Shop write-up:** complete ten challenges and write a report in the format above.
3. **Home SIEM:** Wazuh plus three custom detections and a short README with screenshots.
4. **Threat model:** STRIDE analysis of a system you built, with a data flow diagram and a ranked mitigation list.
5. **Secure pipeline:** GitHub Actions with secret scanning, dependency scanning, SAST and a container scan on a sample project, with a failing and a passing run.

!keypoints A pentest is authorised, scoped and ends in a report ;; Practise only on deliberately vulnerable targets or platforms that give permission ;; Burp Suite as a proxy and two user accounts find most access control bugs ;; Good findings have steps, evidence, impact and a specific fix ;; Defender labs teach detection as much as offence labs teach attacks ;; Small written projects become your portfolio

?? What is the difference between a vulnerability assessment and a penetration test?
=> A vulnerability assessment identifies and lists weaknesses, usually with scanners. A penetration test goes further by safely exploiting them within an agreed scope to show real impact.
?? Why should the lab network be host-only or internal?
=> Vulnerable machines and attack tools must not be reachable from your home network or the internet, where they could be attacked or could attack others.
?? You find an IDOR while testing a bug bounty programme and can see another user's data. What should you do?
=> Stop after the minimum needed to confirm it, do not collect or share the data, and submit a report with clear reproduction steps. Using only your own test accounts is the safest way to prove it.
?? Name three sections every good finding contains.
=> Any three of: description, reproduction steps, evidence, impact, severity, remediation and references.
?? Why compare hashcat speed on MD5 and bcrypt?
=> It shows that password storage algorithms matter: a fast unsalted hash falls to a dictionary in moments, a slow salted one makes each guess expensive.
?? What is a purple team exercise?
=> Red and blue teams work together: the red team runs a technique and the blue team checks whether it was detected and improves the detection if not.
