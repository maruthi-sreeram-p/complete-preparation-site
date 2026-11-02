@part cyber-cloud-devsecops | Cloud security and DevSecOps | defence
## The shared responsibility model

A cloud provider and its customer split the security work. The provider secures **the cloud** (data centres, hardware, the virtualisation layer). You secure **what you put in the cloud** (your data, identities, configuration, code and network rules).

| Layer | IaaS (EC2) | PaaS (Elastic Beanstalk, RDS) | SaaS (Microsoft 365) |
|---|---|---|---|
| Physical, hypervisor | provider | provider | provider |
| Operating system and patching | **you** | provider | provider |
| Application code | **you** | **you** | provider |
| Identities, access and data | **you** | **you** | **you** |
| Configuration of the service | **you** | **you** | **you** |

The pattern in almost every public cloud breach is not that the provider failed. It is a **customer misconfiguration**: a public bucket, an over-permissive role, a leaked access key, or a database open to the internet. The AWS foundations are in the AI and Cloud tree (AWS Part 1: IAM and networking). This part looks at them as a defender.

## Identity and access management (IAM) in AWS

Identity is the new perimeter. In AWS:

| Concept | Meaning |
|---|---|
| **Root user** | the account owner, with unlimited power. Protect it with MFA, create **no access keys** for it, and use it only for the few tasks that need it |
| **IAM user** | a long-term identity with a password and optional access keys. Prefer a federated login (IAM Identity Center) for people |
| **IAM role** | an identity with **temporary credentials** that something *assumes*: an EC2 instance, a Lambda function, a person from another account |
| **Policy** | a JSON document that allows or denies actions on resources |
| **Access key** | an ID and a secret for programmatic access. A leaked key is a very common breach |

### Policy evaluation rules

1. Everything is **denied by default** (implicit deny).
2. An **explicit `Allow`** in an applicable policy permits the action.
3. An **explicit `Deny` always wins**, overriding any Allow.
4. Other layers can still block it: permission boundaries, service control policies (SCPs) from AWS Organizations, session policies.

```json A least-privilege policy: read one prefix of one bucket
{
  "Version": "2012-10-17",
  "Statement": [{
    "Effect": "Allow",
    "Action": ["s3:GetObject"],
    "Resource": "arn:aws:s3:::orders-reports-prod/exports/*",
    "Condition": { "Bool": { "aws:SecureTransport": "true" } }
  }]
}
```

Compare this with `"Action": "*", "Resource": "*"`, which gives away the whole account. **Wildcards on both action and resource are the warning sign** to look for in a review.

!cheat AWS IAM cheat codes ::
- **Default deny. Explicit deny beats allow.**
- **Roles over keys:** workloads use instance roles or task roles with short-lived credentials, never long-lived access keys in code.
- **Root:** MFA on, no keys, not for daily use.
- **Least privilege** is built by starting narrow and widening with evidence (IAM Access Analyzer and CloudTrail show what is actually used).
- **A leaked key** → deactivate it, rotate, review CloudTrail for what it did, then find how it leaked.
- **Separate accounts** for production, development and security logging limit the blast radius.
!end

## Network and data protection

### Security groups versus network ACLs

| | Security group | Network ACL |
|---|---|---|
| Attached to | an instance or network interface | a subnet |
| State | **stateful** (replies are allowed automatically) | **stateless** (allow replies explicitly) |
| Rule type | **allow only** | allow **and deny**, evaluated in rule-number order |
| Default | deny all inbound | allows all (default NACL) |

Design rules: put databases and internal services in **private subnets** with no public IP, expose only a load balancer, let the database's security group accept connections **only from the application's security group**, and never open `0.0.0.0/0` to SSH (22), RDP (3389) or a database port.

### Storage and keys

- **S3:** turn on **Block Public Access** (account-wide), use bucket policies with least privilege, enable **versioning**, **encryption at rest** (SSE-S3 or SSE-KMS) and **access logging**. New buckets already block public access by default, so a public bucket usually means someone deliberately changed it.
- **KMS (Key Management Service):** keeps master keys inside hardware. **Envelope encryption** encrypts data with a data key and encrypts the data key with a KMS key. Key policies and grants control who may use a key, and every use is logged.
- **Secrets:** AWS Secrets Manager or SSM Parameter Store, with automatic rotation. Never put secrets in user data, environment variables of public images or source code.
- **Databases:** not publicly accessible, encrypted, with automated backups and TLS enforced.
- **IMDSv2:** the instance metadata service version that needs a session token. It blocks the simple SSRF attack on `169.254.169.254` that steals instance role credentials.

### Logging and detection services

| Service | Purpose |
|---|---|
| **CloudTrail** | records AWS API calls (who did what, from where). Send trails to a protected S3 bucket with log file validation |
| **CloudWatch** | metrics, logs and alarms |
| **GuardDuty** | threat detection from CloudTrail, VPC flow logs and DNS logs (unusual API calls, crypto-mining, known-bad IPs) |
| **AWS Config** | records resource configuration and flags non-compliant changes (public bucket, unencrypted volume) |
| **Security Hub** | aggregates findings and checks against standards such as CIS |
| **VPC Flow Logs** | network connection metadata |

!interview "How would you secure a new AWS account?" :: "Enable MFA on the root user and stop using it. Set up IAM Identity Center with MFA and least-privilege roles. Turn on CloudTrail in all regions to a locked-down bucket, plus GuardDuty, Config and Security Hub. Block public S3 access account-wide. Keep workloads in private subnets, use security groups that reference each other, and encrypt data with KMS. Use roles for workloads, set budget alerts, and separate production into its own account."

## Containers and Kubernetes

Containers share the host kernel, so their isolation is weaker than a virtual machine's.

| Area | Good practice |
|---|---|
| **Images** | small trusted base images (distroless, alpine, slim), pin versions or digests, **scan** for vulnerabilities (Trivy, Grype), rebuild regularly |
| **Runtime user** | run as a **non-root user**; drop capabilities; read-only root filesystem |
| **Secrets** | never in the image or in `ENV` at build time; inject at runtime |
| **Privilege** | no `--privileged`, never mount the Docker socket (`/var/run/docker.sock`), which is root on the host |
| **Resources** | memory and CPU limits so one container cannot starve others |
| **Kubernetes** | RBAC with least privilege, **NetworkPolicies** (default deny between pods), Pod Security Standards ("restricted"), secrets encrypted at rest, an admission controller that blocks unsigned or vulnerable images, API server not public |

```dockerfile A hardened Dockerfile for a Spring Boot jar
FROM eclipse-temurin:21-jre-alpine
RUN addgroup -S app && adduser -S app -G app
WORKDIR /app
COPY --chown=app:app target/orders.jar app.jar
USER app
EXPOSE 8080
ENTRYPOINT ["java", "-jar", "app.jar"]
```

## Securing the pipeline: DevSecOps

**DevSecOps** means security is part of the delivery pipeline and everyone's job, not a gate at the end. The principle: **automate checks, fail the build on serious findings, and give developers fast feedback.**

| Stage | Control | Example tools |
|---|---|---|
| **Commit** | pre-commit hooks, secret scanning, signed commits | gitleaks, git hooks |
| **Build** | SAST, dependency scan (SCA), SBOM generation | CodeQL, SpotBugs, Dependency-Check, Syft |
| **Package** | container image scan, image signing | Trivy, cosign |
| **Infrastructure as code** | scan Terraform, CloudFormation and Kubernetes manifests | Checkov, Trivy config, tfsec, OPA policies |
| **Test** | DAST against a staging deployment | OWASP ZAP |
| **Deploy** | approvals for production, signed artefacts only, least-privilege deploy role | |
| **Run** | monitoring, runtime detection, patching, drift detection | CloudWatch, Falco, Config |

```yaml A GitHub Actions job with security built in
name: ci
on: [pull_request]
permissions:
  contents: read                     # least privilege for the pipeline's own token
jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4    # pin third-party actions to a full commit SHA for stronger protection
      - uses: actions/setup-java@v4
        with: { distribution: temurin, java-version: 21 }
      - run: mvn -B verify                                  # unit and security tests
      - run: mvn org.owasp:dependency-check-maven:check     # fail on high CVSS dependencies
      - uses: aquasecurity/trivy-action@0.28.0              # scan the image and IaC
        with: { scan-type: fs, severity: 'HIGH,CRITICAL', exit-code: '1' }
```

### Supply chain and pipeline attacks

The pipeline holds the keys to production, so attackers go after it.

| Attack | Real example or idea | Defence |
|---|---|---|
| **Poisoned dependency** | a maintainer account is hijacked or a malicious package version is published (event-stream, 2018) | pin and verify, review updates, SCA, private registry proxy |
| **Compromised build system** | attackers inject code during the build (SolarWinds, 2020) | hardened, isolated build servers, reproducible builds, provenance (SLSA) |
| **Leaked CI secrets** | a third-party CI script exposed credentials (Codecov, 2021) | short-lived credentials, secret masking, minimal permissions |
| **Poisoned pipeline execution** | a pull request from a fork changes the workflow and runs with secrets | do not run untrusted PR code with secrets, require review for workflow changes |
| **Typosquatting / dependency confusion** | a public package with the name of an internal one | scoped registries, reserved names |

Best practices: **protect the main branch** (reviews, status checks, no force pushes), use **OIDC federation** so the pipeline assumes a short-lived AWS role instead of storing access keys, keep the pipeline's own permissions minimal, sign and verify artefacts, and generate an **SBOM** for every release.

### Infrastructure as code (IaC)

Scan Terraform and CloudFormation **before** they create anything, because a one-line mistake (`acl = "public-read"`, an unencrypted volume, `0.0.0.0/0` on port 22) is cheaper to fix in a pull request than in production. Remember that **Terraform state files can contain secrets**, so store them encrypted in a remote backend with restricted access and versioning. **Drift detection** compares real resources with the code to catch manual changes.

!realworld Why this suits a Java developer :: DevSecOps jobs are largely "developer who knows pipelines". If you can write a Maven build, a Dockerfile and a GitHub Actions workflow, adding scanners, least-privilege roles and a policy check is a small step with a large value to employers.

!keypoints The provider secures the cloud and you secure your configuration, identities and data ;; IAM is default deny, explicit deny wins and wildcards are the warning sign ;; Prefer roles with temporary credentials over long-lived access keys ;; Private subnets and security groups that reference each other limit exposure ;; Containers run as non-root with scanned minimal images and no secrets inside ;; Automate SAST, SCA, secret, image and IaC scans in the pipeline and protect the pipeline itself

?? In the shared responsibility model, who is responsible for an S3 bucket being public?
=> The customer. The provider secures the infrastructure, but bucket policies, ACLs and Block Public Access settings are the customer's configuration.
?? An IAM user has one policy that allows s3:* and another that explicitly denies s3:DeleteObject. Can they delete objects?
=> No. An explicit Deny always overrides an Allow.
?? Name two differences between a security group and a network ACL.
=> A security group is stateful and allow-only and attaches to instances, whereas a network ACL is stateless, supports allow and deny rules in numbered order and attaches to subnets.
?? Why is mounting /var/run/docker.sock into a container dangerous?
=> Whoever controls that socket can start privileged containers on the host, which is effectively root access to the host machine.
?? A pipeline stores a long-lived AWS access key as a secret. What is a better design?
=> Use OIDC federation so the pipeline assumes a role and gets short-lived credentials, with a narrowly scoped role policy.
?? What does a SAST step in CI find, and what does an SCA step find?
=> SAST finds insecure patterns in your own code. SCA finds known vulnerabilities in the third-party libraries you depend on.
