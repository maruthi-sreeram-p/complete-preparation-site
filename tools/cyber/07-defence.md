@part cyber-defence | Defence: logging, detection and incident response | defence
## The blue team and the security operations centre

The **blue team** defends: it prevents what it can, detects what gets through and responds when something goes wrong. Most entry-level jobs are on this side. A **SOC (security operations centre)** is the team and the tooling that watch systems around the clock.

| Level | Typical work |
|---|---|
| **Tier 1 analyst** | watch the alert queue, triage (is it real?), close false positives, escalate real ones |
| **Tier 2 analyst** | investigate escalated incidents, scope the damage, contain, write the report |
| **Tier 3 / threat hunter** | proactively search for attackers that alerts missed, build detections, analyse malware |
| **SOC engineer / detection engineer** | build and tune the pipelines and rules |
| **Incident commander** | coordinates a major incident across teams |

Two numbers every SOC reports: **MTTD** (mean time to detect) and **MTTR** (mean time to respond or recover). Attackers who stay hidden for weeks are far more costly than ones caught in hours.

## Logs: the raw material

You cannot defend what you cannot see. Useful sources:

| Source | Tells you |
|---|---|
| **Authentication logs** (Linux `auth.log`, Windows Security log, identity provider) | who logged in, from where, how often they failed |
| **Web server and application logs** | requests, status codes, user agents, errors |
| **Firewall and network flow logs** | which hosts talk to which, on which ports, how much data |
| **DNS logs** | which names were looked up (malware beaconing, tunnelling) |
| **Endpoint (EDR) telemetry** | processes started, files written, registry changes |
| **Cloud audit logs** (AWS CloudTrail, GuardDuty) | who called which API, who changed an IAM policy |
| **Email gateway** | phishing attempts, attachments, sender checks |

A good log line has **time (with time zone), source, user, action, object and outcome**. Clocks must be synchronised (NTP) or events cannot be ordered. Logs should be **shipped to a central store** and protected from tampering.

### Windows event IDs you should recognise

| ID | Meaning |
|---|---|
| **4624** | successful logon |
| **4625** | failed logon |
| **4672** | special privileges assigned to a new logon (an administrator logged in) |
| **4688** | a new process was created |
| **4720** | a user account was created |
| **4732** | a member was added to a security-enabled local group |
| **1102** | the Security audit log was cleared (very suspicious) |
| **7045** | a new service was installed |

### Reading a web access log

```text One line of an access log (Common Log Format)
203.0.113.9 - - [01/Nov/2026:10:15:32 +0530] "GET /products?id=5%20UNION%20SELECT%20name,pass%20FROM%20users HTTP/1.1" 200 1843 "-" "sqlmap/1.7"
```

Clues: a `UNION SELECT` inside the query, the user agent `sqlmap`, and a **200** response (the request worked, which is worse than a 400 or 500). Typical triage commands:

```bash Find the noisiest sources and the failures
awk '{print $1}' access.log | sort | uniq -c | sort -nr | head          # top client IPs
awk '$9 ~ /^(401|403)/ {print $1}' access.log | sort | uniq -c | sort -nr   # who gets denied most
grep -iE "union(%20|\+| )select|<script|\.\./" access.log | head          # obvious attack strings
```

!cheat Log analysis cheat codes ::
- **401/403 floods from one IP** → brute force or forced browsing. **404 floods** → scanning. **500s after odd input** → injection attempts.
- **200 on a suspicious request** is the one to escalate, because it may have succeeded.
- **Windows:** 4625 many times then 4624 for the same account = a brute force that worked.
- **Linux:** `Failed password` lines followed by `Accepted password` from the same IP = the same story.
- **4688 plus an unusual parent** (Word starting PowerShell) = classic malicious macro.
- **Event 1102 / log cleared** = the attacker is covering tracks.
!end

## Detection: SIEM, rules and alert quality

A **SIEM** (security information and event management: Splunk, Microsoft Sentinel, Elastic Security, Wazuh) collects logs from everywhere, normalises them, stores them and runs **correlation rules** that turn raw events into alerts.

Examples of useful detections:

| Detection | Logic |
|---|---|
| **Brute force** | more than 10 failed logins for one account or from one IP in 5 minutes |
| **Successful login after many failures** | 4625 × N followed by 4624 for the same user |
| **Impossible travel** | the same user logs in from two countries within minutes |
| **New administrator** | a user is added to a privileged group outside change windows |
| **Mass download / exfiltration** | one account reads far more data than its baseline |
| **Beaconing** | an internal host contacts one external address at fixed intervals |
| **Persistence** | a new scheduled task, service or autorun entry |

Rules can be written in a portable format called **Sigma** and translated to each SIEM's query language.

### Alert outcomes and quality

| | The activity is really malicious | The activity is benign |
|---|---|---|
| **Alert fires** | **True positive (TP)** | **False positive (FP)** |
| **No alert** | **False negative (FN)**: the dangerous miss | **True negative (TN)** |

- **Precision** = TP / (TP + FP): of the alerts, how many were real. **Recall** (detection rate) = TP / (TP + FN): of the real attacks, how many were caught.
- Too many false positives cause **alert fatigue**: analysts start ignoring alerts, and the real one gets missed. Tune rules, add context (asset criticality, user role), and automate the routine triage (**SOAR**).
- **Baselines** (what is normal for this user and host) make anomaly detection possible but need care.

Other detection tools: **IDS/IPS** (Snort, Suricata) on the network, **EDR** (endpoint detection and response) on hosts, **honeypots** and **canary tokens** (a fake credential or file that alerts when touched), and **threat hunting** (a human searching a hypothesis such as "has any server beaconed to a rare domain?").

### Threat intelligence

**Indicators of compromise (IOCs)** are artefacts of an attack: IP addresses, domains, file hashes, URLs. They are easy to share but attackers change them quickly. **TTPs** (tactics, techniques and procedures, as in MITRE ATT&CK) describe behaviour and are much harder to change, so they are more valuable. Sources: MISP, AlienVault OTX, VirusTotal, CISA advisories, vendor reports. Look up a suspicious file by its **hash**, not by uploading sensitive files to public services.

## Phishing and malware triage

### Analysing a suspicious email

1. Look at the **headers**, not just the display name: `From`, `Return-Path`, `Reply-To`, `Received` chain.
2. Check authentication results:

| Mechanism | What it does |
|---|---|
| **SPF** | a DNS record listing the servers allowed to send mail for a domain |
| **DKIM** | the sending server signs the message; the receiver verifies it with a key published in DNS |
| **DMARC** | a policy (`none`, `quarantine`, `reject`) telling receivers what to do when SPF or DKIM fail to align with the visible From domain, and where to send reports |

3. Hover over links (do not click). Look for look-alike domains (`rn` instead of `m`), URL shorteners, mismatched display text.
4. Detonate attachments and links **only** in a sandbox, never on your own machine.
5. Search the mail system for other recipients and remove the message from all inboxes. If anyone clicked, treat their account as compromised: reset credentials, revoke sessions, check for mailbox rules.

### Static and dynamic malware analysis

- **Static analysis** inspects the file without running it: hash it, read strings, check imports and file type.
- **Dynamic analysis** runs it in an isolated **sandbox** and watches processes, files, registry and network traffic.
- Never analyse live malware on a machine connected to your network or your accounts.

## Incident response

An **incident** is an event that harms or threatens confidentiality, integrity or availability. NIST SP 800-61 and the SANS model describe the same lifecycle:

| Phase | What happens |
|---|---|
| **1. Preparation** | policies, contact lists, playbooks, tools, backups, training, tabletop exercises |
| **2. Detection and analysis** (identification) | decide whether it is an incident, scope it, rate severity, start a timeline |
| **3. Containment** | stop the spread: isolate hosts, disable accounts, block IPs. Short-term first, then long-term |
| **4. Eradication** | remove the cause: malware, backdoors, the vulnerability that let them in |
| **5. Recovery** | restore from clean backups, monitor closely, return to normal |
| **6. Lessons learned** | a blameless review within days: what worked, what failed, what to change |

Principles during an incident:

- **Contain before you clean.** Isolating a machine (network, not power) keeps evidence in memory.
- **Preserve evidence** following the **order of volatility** (most volatile first): CPU registers and cache → **memory (RAM)** → network connections and running processes → disk → remote logs and backups → archives. Record who handled what and when (**chain of custody**) and work on copies.
- **Keep a timeline and write things down.** Decisions made at 3 a.m. need to be explained at 10 a.m.
- **Communicate:** a named incident lead, a separate channel for the response team, careful statements for management, legal and customers. Know your legal reporting duties (for example, CERT-In reporting in India).
- **Do not pay** a ransom without legal and executive involvement. Restoration from tested backups is the plan.

### Three mini playbooks

| Incident | First steps |
|---|---|
| **Compromised account** | reset the password, revoke sessions and tokens, require MFA, review the sign-in history and mailbox rules, find what the account accessed |
| **Ransomware** | isolate affected hosts and shares, protect backups, identify the strain and the entry point, notify, restore from clean backups, patch the entry |
| **Web application attack** | preserve logs, block the source, find the vulnerable endpoint, patch, rotate secrets that may have been read, check for web shells |

## Vulnerability management and resilience

- **CVE** gives a vulnerability a public ID (CVE-2021-44228). **CWE** classifies the weakness type (CWE-89 SQL injection). **CVSS** scores severity from 0 to 10 (Low, Medium, High, Critical). **EPSS** estimates the probability that a CVE will be exploited soon. CISA's **KEV catalogue** lists vulnerabilities known to be exploited in the wild.
- **Prioritise** by exploitability (is there a public exploit? is it in KEV?), **exposure** (internet-facing?) and **asset value**. A medium-scored flaw on an exposed, exploited system can outrank a critical one on an isolated test box.
- **Patch cadence:** critical and exploited issues in days, others on a regular cycle. If you cannot patch, use compensating controls (segmentation, a WAF rule, disabling the feature).
- **Scanners** (Nessus, OpenVAS, Qualys, Trivy for containers) find known issues. They miss logic flaws and they report false positives, so verify.

**Backups** are the last line of defence against ransomware. Follow **3-2-1**: three copies of the data, on two different media, with one offsite. Add an **immutable** or offline copy and **test restores** regularly. **RPO** (recovery point objective) is how much data loss is acceptable, **RTO** (recovery time objective) is how long recovery may take. A **business continuity plan** keeps the business running and a **disaster recovery plan** restores IT.

### Frameworks you will hear about

| Framework | Use |
|---|---|
| **NIST Cybersecurity Framework 2.0** | six functions: Govern, Identify, Protect, Detect, Respond, Recover |
| **CIS Controls** | a prioritised list of practical safeguards |
| **ISO/IEC 27001** | a certifiable information security management system |
| **PCI DSS** | rules for organisations that handle payment card data |
| **MITRE ATT&CK** | a library of attacker behaviour for detection and testing |

!interview Walk me through an alert about many failed logins :: "First check the context: which account, which source, how many, over what time, and what the system is. Then look for a success afterwards for the same account or source. If there is none, check whether the source is a known scanner or user error. If there is a success, treat the account as compromised: reset credentials, kill sessions, look at what it did, escalate. Document the steps, and tune the rule or add the source to a watchlist if it was benign."

!keypoints Logs from authentication, web, network, DNS, endpoint and cloud are what detection is built from ;; A false negative is the dangerous miss and too many false positives cause alert fatigue ;; Incident response runs prepare, detect and analyse, contain, eradicate, recover, learn ;; Contain before you clean and preserve volatile evidence first ;; Prioritise patching by exploitability, exposure and asset value, not CVSS alone ;; Backups need three copies, two media, one offsite and tested restores

?? What is the difference between a false positive and a false negative, and which is worse for security?
=> A false positive is an alert on benign activity. A false negative is a real attack with no alert. The false negative is worse because the attack goes unnoticed, although too many false positives hide real alerts.
?? You see Windows events 4625 repeatedly for one account followed by 4624 from the same IP. What do you conclude?
=> A brute force attack that probably succeeded. Treat the account as compromised: reset it, kill sessions and investigate what it accessed.
?? Why is the order of volatility important?
=> Evidence in memory and network state disappears when a machine is powered off or rebooted, so it must be captured before the more permanent disk and log evidence.
?? Explain SPF, DKIM and DMARC in one sentence each.
=> SPF lists which servers may send for a domain. DKIM signs messages so the receiver can verify them. DMARC sets the policy for failures and ties the checks to the visible From domain.
?? What does 3-2-1 mean for backups and why test restores?
=> Three copies, on two media types, one offsite. A backup you have never restored may be corrupt, incomplete or too slow to meet the recovery time objective.
?? A CVSS 9.8 flaw exists on an isolated lab server and a CVSS 6.5 flaw is on a public web server listed in the KEV catalogue. Which is patched first?
=> Usually the 6.5 flaw on the exposed, actively exploited system. Prioritisation uses exploitation, exposure and asset value, not the score alone.
