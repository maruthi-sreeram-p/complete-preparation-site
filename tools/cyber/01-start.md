@part cyber-start | Start here: security thinking and your path | foundations
## What security is: the CIA triad and its friends

Cybersecurity is the work of keeping systems and data **confidential**, **intact** and **available** while people use them. Almost every concept in the field hangs off these three words.

| Property | Meaning | Attack that breaks it | Control that protects it |
|---|---|---|---|
| **Confidentiality** | only authorised people can read the data | data breach, sniffing, leaked backup | encryption, access control, MFA |
| **Integrity** | data and systems change only in authorised ways | tampered request, modified file, SQL injection | hashes, signatures, input validation, version control |
| **Availability** | the system works when it is needed | DDoS, ransomware, a deleted database | redundancy, backups, rate limiting, patching |

Three more ideas are used constantly:

- **Authentication** answers "who are you?", **authorisation** answers "what may you do?", and **accounting (auditing)** answers "what did you do?". Together they are AAA.
- **Non-repudiation** means a person cannot later deny an action. Digital signatures and tamper-evident logs provide it.
- **Privacy** is about the rules for personal data (who collects it, why, for how long). Security is one of the tools that enforces those rules.

!tip The triad in one sentence each :: Confidentiality is "no one reads it", integrity is "no one changes it", availability is "it is there when I need it". A ransomware attack hits availability first (files locked) and often confidentiality too (data stolen before encryption).

### The vocabulary people mix up

| Term | Meaning | Example |
|---|---|---|
| **Asset** | something worth protecting | customer table, signing key, the login page |
| **Vulnerability** | a weakness | a query built by string concatenation |
| **Threat** | something or someone that could exploit it | a criminal, a careless insider, malware |
| **Exploit** | the technique or code that uses a vulnerability | the string `' OR '1'='1` |
| **Risk** | the chance a threat uses a vulnerability, times the harm | likelihood × impact |
| **Control** (countermeasure) | anything that reduces risk | prepared statements, a firewall rule, a policy |
| **Attack surface** | all the places an attacker can interact with the system | every endpoint, port, input field and dependency |

**Risk is not a yes or no.** You can accept it, reduce it with a control, transfer it (insurance, a cloud provider) or avoid it (do not collect the data at all).

### Quantifying risk

Risk assessments often use simple formulas:

- **SLE** (single loss expectancy) = asset value × exposure factor, where the exposure factor is the fraction of the asset lost in one incident.
- **ARO** (annual rate of occurrence) = how many times a year you expect the incident.
- **ALE** (annualised loss expectancy) = SLE × ARO.

An asset worth ₹10,00,000 with an exposure factor of 40% has an SLE of ₹4,00,000. If it happens once every two years (ARO 0.5) the ALE is ₹2,00,000. A control is worth buying when it costs less per year than the ALE it removes.

!cheat Risk cheat codes ::
- **Risk = likelihood × impact.** Remove either side and risk drops.
- **ALE = SLE × ARO**, and **SLE = asset value × exposure factor**.
- Four responses: **accept, mitigate, transfer, avoid**.
- **Residual risk** is what is left after controls. It is never zero.
- Security that costs more than the asset it protects is a bad control.
!end

## How attackers think: threat actors and the attack lifecycle

### Who attacks

| Actor | Usual motive | Typical skill and resources |
|---|---|---|
| **Opportunistic criminals** | money: ransomware, card fraud, selling data | automated tools, bought access, large scale |
| **Organised crime** | money, run like a business | skilled, patient, uses phishing kits and initial-access brokers |
| **Nation-state (APT)** | espionage, disruption | very high, long-term access |
| **Hacktivists** | a cause, publicity | defacement, DDoS, leaks |
| **Insiders** | grievance, money, or simple mistakes | already have legitimate access |
| **Script kiddies** | curiosity, status | run other people's tools |

Most real incidents are not clever. They are **stolen or reused passwords, phishing, unpatched software and misconfigured cloud storage**. A fresher who fixes the boring things well is already valuable.

### The attack lifecycle

Frameworks describe an attack as a chain of steps, so defenders can break the chain at any link.

| Step (Lockheed Martin kill chain) | What the attacker does | Where defenders can act |
|---|---|---|
| Reconnaissance | collects emails, subdomains, technologies | reduce what is public |
| Weaponisation | prepares a malicious file or exploit | (mostly out of your sight) |
| Delivery | sends phishing, hosts a malicious page | email filtering, awareness |
| Exploitation | triggers a vulnerability or a user action | patching, hardening |
| Installation | drops malware, a backdoor or a web shell | EDR, application allow-listing |
| Command and control | the implant talks to the attacker | egress filtering, DNS monitoring |
| Actions on objectives | steals data, encrypts files, moves sideways | segmentation, logging, backups |

**MITRE ATT&CK** is a public knowledge base of real attacker behaviour, organised as tactics (the goal, such as *Initial Access* or *Persistence*) and techniques (how, such as *Phishing* or *Scheduled Task*). SOC teams label alerts with ATT&CK technique IDs, and interviewers like candidates who know it exists.

### The attacks you will hear about every day

- **Phishing:** a fake message that tricks the user into revealing a password or running a file. **Spear phishing** targets a specific person. **Vishing** is by phone, **smishing** by SMS.
- **Malware:** a virus needs a host file and a user action, a **worm** spreads by itself, a **trojan** pretends to be useful, **ransomware** encrypts and demands payment, **spyware** watches, a **rootkit** hides, a **botnet** is a network of infected machines.
- **Social engineering:** manipulating people. Pretexting (a made-up story), baiting (a free USB stick), tailgating (following someone through a door).
- **Password attacks:** brute force tries everything, a **dictionary attack** tries likely words, **credential stuffing** replays passwords leaked from another site, and **password spraying** tries one common password against many accounts.
- **Denial of service:** DoS from one source, **DDoS** from many.
- **Man-in-the-middle:** the attacker sits between two parties and reads or alters traffic.
- **Supply chain attacks:** the attacker compromises a library, build tool or vendor that you trust.
- **Zero-day:** a vulnerability the vendor does not know about yet, so no patch exists.

## Defence principles you will reuse everywhere

| Principle | Idea | Example |
|---|---|---|
| **Defence in depth** | several independent layers, so one failure is not fatal | firewall, WAF, input validation, least-privilege database user |
| **Least privilege** | give the minimum access needed, for the minimum time | the app's DB user cannot `DROP TABLE` |
| **Separation of duties** | no single person can complete a sensitive task alone | the developer who writes code does not approve its deploy |
| **Fail securely** | on error, deny rather than allow | a failed permission check returns 403, not the page |
| **Secure by default** | the safe setting is the default | new S3 buckets are private |
| **Minimise attack surface** | remove what you do not need | close unused ports, delete unused endpoints |
| **Zero trust** | never trust a request because of where it came from; verify every time | internal services still authenticate each other |
| **Keep it simple** | complexity hides bugs | prefer one well-reviewed library over custom crypto |
| **Never trust input** | all data from outside the trust boundary is hostile until validated | request parameters, headers, uploaded files |

**Security through obscurity** (hiding how it works and hoping) is not a control by itself. **Kerckhoffs's principle** says a system should stay secure even if everything about it except the key is public.

### Types of control

| By function | Purpose | Example |
|---|---|---|
| **Preventive** | stop it happening | MFA, input validation, a locked door |
| **Detective** | notice that it happened | log monitoring, IDS, CCTV |
| **Corrective** | fix it afterwards | restore from backup, patch, revoke a key |
| **Deterrent** | discourage attackers | warning banners, visible cameras |
| **Compensating** | a substitute when the ideal control is impossible | extra monitoring on a legacy system that cannot be patched |

By nature, controls are **technical** (encryption), **administrative** (policy, training) and **physical** (locks, badges).

!cheat Principles cheat codes ::
- **Prevent, detect, respond** is the shape of every security programme. Prevention will fail eventually, so detection and response matter as much.
- **Default deny:** allow-list what you know is safe instead of block-listing what you know is bad.
- **Least privilege** is the answer to "how do we limit the damage?" more often than any other.
- **Defence in depth** is the answer to "what if this control fails?".
- A **compensating** control stands in for one you cannot deploy.
!end

## Threat modelling: thinking before you build

Threat modelling asks four questions: **What are we building? What can go wrong? What are we going to do about it? Did we do a good job?** You can do it on a whiteboard in an hour.

1. **Draw the system** as a data flow diagram: external actors, processes, data stores, data flows and **trust boundaries** (the lines where the level of trust changes, such as the internet to your server, or your app to the database).
2. **List threats at each element and each boundary crossing.**
3. **Rank them** by likelihood and impact.
4. **Decide the mitigation** and write it down.

### STRIDE

STRIDE gives you a checklist of six threat types. Each one breaks a security property.

| Letter | Threat | Property broken | Example | Typical mitigation |
|---|---|---|---|---|
| **S** | Spoofing | authentication | logging in as someone else with a stolen token | strong authentication, MFA |
| **T** | Tampering | integrity | editing the price in the request | validation, signatures, server-side checks |
| **R** | Repudiation | non-repudiation | "I never placed that order" | audit logs, signatures |
| **I** | Information disclosure | confidentiality | stack trace shown to users | encryption, access control, generic errors |
| **D** | Denial of service | availability | flooding the login endpoint | rate limiting, quotas, scaling |
| **E** | Elevation of privilege | authorisation | a normal user calls an admin endpoint | server-side authorisation checks |

!interview Example answer :: "For a login endpoint, STRIDE gives me spoofing (credential stuffing, so rate limit and MFA), tampering (a modified request, so validate on the server), repudiation (log every attempt with time and IP), information disclosure (do not say whether the username exists), denial of service (lock out or slow down, but do not let attackers lock real users out), and elevation of privilege (check roles on the server for every action)."

## Who does what: security careers

| Path | What you do | Where your Java background helps |
|---|---|---|
| **Application security (AppSec)** | review code and designs, run scanners, fix vulnerabilities with developers | a lot: you can read the code and write the fix |
| **SOC analyst (blue team)** | watch alerts, investigate, escalate | little, but scripting helps |
| **Penetration tester (red team)** | attack with permission and report findings | moderate; web testing needs HTTP and code understanding |
| **Cloud security** | IAM, network and storage configuration, posture checks | high if you know AWS (see the AI and Cloud tree) |
| **DevSecOps** | put security checks into the build pipeline | high |
| **GRC (governance, risk, compliance)** | policies, audits, frameworks like ISO 27001 | low |
| **Digital forensics and incident response** | investigate breaches, preserve evidence | moderate |

The honest picture for freshers: entry-level security jobs are competitive, and many employers prefer people who already worked as developers, system administrators or network engineers. A Java developer who can find and fix security bugs in the code is easier to hire than a person who only knows tool names.

!realworld Why AppSec suits you :: Developers write the code that gets attacked. Teams that cannot hire enough security specialists value developers who can threat-model a feature, review a pull request for injection, configure Spring Security properly and read a dependency scan. This tree is built around that route.

## Law, ethics and permission

**The rule that matters most: only test systems you own or have written permission to test.** "I was only looking" and "I told them afterwards" are not defences.

- In India, the **Information Technology Act, 2000** treats unauthorised access and damage to computer systems as offences (see sections 43 and 66 and their penalties). The **Digital Personal Data Protection Act, 2023** sets duties for handling personal data. **CERT-In** is the national agency for incident response and, under its 2022 directions, requires many organisations to report certain incidents within hours. Laws change, so read the current text before relying on this summary. Other countries have their own (the CFAA in the USA, the Computer Misuse Act in the UK).
- **Scope** is the written list of what you may test, when and how. Anything outside it is off limits, even if it is reachable.
- **Responsible disclosure:** if you find a flaw in someone else's system by accident, stop, do not download or change data, and report it through their security contact or a **security.txt** page. Bug bounty programmes on platforms such as HackerOne and Bugcrowd publish their scope and rules.
- **Professional ethics:** protect client data, report honestly, do not oversell findings, and never keep copies of customer data after an engagement.

!warning Learning on live websites :: Running a scanner against a site you do not own is illegal in many places even if you do not exploit anything. Use deliberately vulnerable practice apps (OWASP Juice Shop, DVWA, WebGoat) running on your own machine, or platforms that give you permission, such as TryHackMe and Hack The Box.

!keypoints Security is protecting confidentiality, integrity and availability ;; Risk is likelihood times impact, and you can accept, mitigate, transfer or avoid it ;; Most real attacks use boring weaknesses: weak passwords, phishing, missing patches and misconfiguration ;; Defence in depth and least privilege answer most "what if" questions ;; Threat model with STRIDE before you build ;; Only ever attack systems you have written permission to test

?? A website goes down during a flash sale because a flood of traffic overwhelms it. Which part of the CIA triad was attacked?
=> Availability. If the traffic came from many machines it is a DDoS attack.
?? What is the difference between a vulnerability, a threat and a risk?
=> A vulnerability is a weakness. A threat is something that could exploit it. Risk is the likelihood that it happens multiplied by the harm it would cause.
?? An asset is worth ₹5,00,000, an incident destroys 20% of it, and it happens twice a year. What is the ALE?
=> SLE = 5,00,000 × 0.2 = ₹1,00,000. ALE = SLE × ARO = 1,00,000 × 2 = ₹2,00,000 per year.
?? Name the six STRIDE threats and the property each one breaks.
=> Spoofing (authentication), tampering (integrity), repudiation (non-repudiation), information disclosure (confidentiality), denial of service (availability) and elevation of privilege (authorisation).
?? Why is "default deny" safer than a block list?
=> A block list only stops what you thought of. A default-deny allow list stops everything you did not explicitly approve, including attacks nobody has invented yet.
?? You find an exposed admin panel on a company website while browsing. What should you do?
=> Do not log in or touch any data. Report it to the company through their security contact or security.txt, with enough detail to reproduce, and offer no demands.
