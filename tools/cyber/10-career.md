@part cyber-career | Careers, certifications and interviews | career
## The honest picture for a fresher

Cybersecurity is a growing field, but **"entry level" security jobs are scarce compared with the number of people who want them.** Many employers hire into security from development, system administration, networking or IT support. That is good news for you: a Java full stack background is a real advantage, and the job titles below are realistic doors.

| Role | What a fresher does | Skills that matter |
|---|---|---|
| **SOC analyst (L1)** | triage alerts, read logs, escalate, follow playbooks | networking, Windows and Linux logs, SIEM basics, attention, shift work |
| **Junior application security engineer / security-focused developer** | review code and designs, run scanners, help fix findings, secure pipelines | secure coding, OWASP Top 10, a language (Java), Git, CI |
| **Vulnerability management analyst** | run scans, validate and prioritise findings, track fixes | CVSS, scanners, patching process, communication |
| **Junior penetration tester** | assist on web or network tests, write findings | web security, Burp, Linux, reporting. Usually needs proof of lab work |
| **Cloud security associate** | review IAM, configuration and logs in AWS or Azure | cloud basics, IAM, CloudTrail, scripting |
| **GRC analyst** | policies, risk registers, audits, evidence collection | frameworks (ISO 27001, NIST), writing, process |
| **Security intern / trainee** | whatever the team needs | curiosity and reliability |

Where they are: IT services companies, managed security service providers (MSSPs) that run SOCs for many clients, banks and insurers, product companies, consultancies and the "Big 4" advisory firms. Job posts change often, so read several and note which skills repeat.

!tip Developer-first is a strategy, not a detour :: Working as a Java developer and then moving into AppSec or DevSecOps is one of the most common and best-paid routes. If a security job does not come immediately, a developer job at a company with a security team, where you volunteer for security work, keeps you moving toward your goal.

## Certifications: what each is for

Certificates help get past filters and structure your learning, but **they do not replace skills.** Do not collect them. Confirm current exam names, prices and prerequisites on the issuer's site before you plan.

| Certificate | Level and focus | When it helps |
|---|---|---|
| **CompTIA Security+** | vendor-neutral foundation across threats, architecture, operations, governance | a common baseline requirement in job posts; a good first certificate |
| **ISC2 Certified in Cybersecurity (CC)** | entry level concepts | a low-cost start; check current training and exam offers |
| **Google Cybersecurity Certificate** (Coursera) | guided course for beginners | learning path, little recognition on its own |
| **eJPT** (INE) | practical entry-level pentesting exam in a lab | proves hands-on basics |
| **CEH** (EC-Council) | broad ethical hacking theory | frequently listed in Indian job posts, though many practitioners favour practical certificates |
| **CompTIA CySA+ / Blue Team Level 1** | analyst and defender skills | SOC career path |
| **OSCP** (OffSec) | hard, 24-hour practical penetration test | strongly respected, but a later goal rather than a first certificate |
| **AWS Security Specialty, Azure AZ-500** | cloud security | after you have cloud experience |
| **CISSP, CISM, CISA** | management and audit | later in a career; CISSP requires years of experience |

A practical order for you: **fundamentals (this tree) → Security+ (if job posts ask for it) → one practical path (eJPT or Blue Team Level 1) → cloud certificate that matches your AWS skills.**

## Skills checklist

Tick these honestly. Anything below "can do" is your next study item.

| Area | Can you... |
|---|---|
| **Foundations** | explain CIA, risk, STRIDE, defence in depth, least privilege? |
| **Linux and networking** | use `grep`, `awk`, `ss`, `chmod`; subnet a /26; read a TCP handshake; explain DNS and TLS? |
| **Cryptography** | pick hash vs HMAC vs AES-GCM vs RSA correctly; store passwords properly? |
| **Web security** | exploit and fix SQL injection and XSS in a lab; explain CSRF and IDOR; describe SSRF? |
| **Auth** | explain sessions vs JWT, OAuth with PKCE, MFA and Spring Security configuration? |
| **Secure Java** | validate input, avoid secrets in Git, scan dependencies, write security tests? |
| **Defence** | read a log and spot a brute force; describe the incident response phases? |
| **Cloud and DevSecOps** | write a least-privilege IAM policy; add scanning to a pipeline? |
| **Practice** | have solved labs on a platform and written them up? |
| **Communication** | write a clear finding and explain a risk to a non-technical person? |

## A 6-month plan

Adjust the pace to your time. The aim is to **finish with proof of work.**

| Month | Focus | Output |
|---|---|---|
| **1** | foundations, Linux, networking (parts 1 and 2); OverTheWire Bandit; TryHackMe pre-security | a notes repository; a home lab with two VMs |
| **2** | cryptography and web attacks (parts 3 and 4); Juice Shop and PortSwigger labs | ten written lab summaries |
| **3** | authentication and secure Java (parts 5 and 6) | your "break and fix" Spring Boot project on GitHub with tests |
| **4** | defence, logs and incident response (part 7); Wazuh home SIEM; CyberDefenders | three detections plus an incident write-up |
| **5** | cloud and DevSecOps (part 8); a secure pipeline for your project | a CI workflow with scans and a short README |
| **6** | interviews; apply; optionally sit Security+ | a polished profile, 5 mock interviews, applications sent |

## Presenting yourself honestly

- Put security work under **Projects and Labs**, not under Experience. Learning is real and worth showing, but it is not job experience, and recruiters and interviewers notice when the two are mixed.
- Describe each project with **what you built or tested, the tools, what you found and what you fixed**, plus a link to the repository or write-up. Numbers help ("fixed 5 vulnerabilities; added 12 security tests").
- Show a **short GitHub profile** with a readable README on each project. Remove secrets and anything you were not allowed to publish. Do not publish step-by-step solutions to active challenges or confidential details of any employer.
- On LinkedIn, follow security communities and share short learning notes. Quality beats volume.
- Join communities: local **OWASP** and **null** chapters, college security clubs, CTF teams on CTFtime. They are where referrals happen.

## Interview preparation

Security interviews for freshers mix **fundamentals, scenarios and a little coding**. Interviewers want to see structured thinking more than memorised lists.

### A structure for scenario questions

> **Clarify → Contain → Investigate → Remediate → Prevent → Communicate**

1. **Clarify:** ask what you know and do not know (what system, when, what data, who is affected).
2. **Contain:** stop the damage first, in the least disruptive way.
3. **Investigate:** logs, timeline, scope, root cause.
4. **Remediate:** remove the cause and restore safely.
5. **Prevent:** the control that would have stopped or detected it.
6. **Communicate:** who must be told, and what you record.

### Questions you should be able to answer in 60 seconds

1. What are the CIA triad and an example of each failing?
2. Difference between authentication and authorisation?
3. Symmetric vs asymmetric encryption: when is each used?
4. Hashing vs encryption vs encoding?
5. What happens when you type `https://` in the browser? (DNS, TCP, TLS, HTTP)
6. SQL injection: what, why, how to prevent?
7. XSS types and defences?
8. CSRF and how SameSite and tokens help?
9. What is a man-in-the-middle attack and how does TLS stop it?
10. IDS vs IPS; stateful firewall vs WAF?
11. Black, grey and white box testing?
12. What is the OWASP Top 10, and which category is number one?
13. How should passwords be stored?
14. Explain session vs JWT authentication.
15. What is least privilege? Give a cloud example.
16. What does a SOC analyst do on a failed-login alert?
17. How do you secure a REST API?
18. What is a zero-day? A CVE? CVSS?
19. How would you respond to a suspected phishing click?
20. How do you stay current? (name two sources you actually follow)

!interview "How would you secure a REST API?" :: "Authenticate every request with short-lived tokens over HTTPS only. Authorise on the server for each object and function, deny by default. Validate and size-limit input with DTOs, and use parameterised queries. Rate-limit, return generic errors, log security events without secrets, set security headers and strict CORS, keep dependencies patched, and test the unhappy paths. Keep secrets in a secret manager and give the service a least-privilege database account."

!interview "What would you do if you accidentally found a vulnerability in a website you do not own?" :: "Stop at the minimum needed to confirm, do not access or change data, and report it through the site's security contact or disclosure programme with clear steps. I would not publish it or ask for payment."

!interview "Tell me about a security project you built." :: Use a short story: the problem, what you built, the vulnerabilities you found or fixed (name them), the tools, one thing you got wrong and learned, and what you would improve. A concrete example of an IDOR you fixed with an ownership check and a test beats a list of tools.

### Keeping up to date

Sources worth following: the **OWASP Cheat Sheet Series** (practical and concise), **PortSwigger** research and labs, **CISA** and **CERT-In** advisories, the **NVD** (National Vulnerability Database), **SANS** reading room and newsletters, and security news sites. Choose a few and read regularly, rather than skimming everything.

!keypoints Entry-level security roles exist but are competitive, and a developer background is an advantage ;; Certificates help but projects and labs prove skill ;; List learning under Projects and Labs and never as work experience ;; Use clarify, contain, investigate, remediate, prevent and communicate for scenario answers ;; Prepare 60-second answers to the core fundamentals ;; Build a break-and-fix project, a home SIEM and a secure pipeline as proof

?? Why might a developer job first be a good route into AppSec?
=> Application security relies on reading and writing code, understanding frameworks and working with developers. Experience as a developer, plus security work and projects, makes the move credible.
?? Name two practical, entry-level steps that prove skill better than a certificate alone.
=> Written lab or CTF reports and a break-and-fix project on GitHub (or a home SIEM with custom detections).
?? Where should a fresher list lab work on a CV?
=> Under Projects and Labs, described accurately. It should not appear as work experience.
?? Give the six-step structure for answering a security scenario question.
=> Clarify, contain, investigate, remediate, prevent, communicate.
?? What is the first thing you do with a suspected phishing click?
=> Treat the account as compromised: reset credentials, revoke sessions, check mailbox rules and sign-in logs, and look for other recipients.
?? Name three sources to keep up with security news and techniques.
=> For example the OWASP Cheat Sheet Series, PortSwigger research, and CISA or CERT-In advisories.
