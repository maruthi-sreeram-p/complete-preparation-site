"""
Writes the pages a 3-4 year experienced candidate needs that no PDF covers: AWS, AI engineering,
architecture judgement, production debugging and the experienced interview.

These pages are written for this site, not extracted from the user's PDFs, and each one says so at the top.

Usage: python -I tools/build_experience_topics.py
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from build_frontend_topics import OUT, SOURCE, code, diagram, interview, keypoints, note, practice, section, table  # noqa: E402

NOTICE = note("note", "Not from your PDFs",
              "No guide of yours covers this, so this page was written for the site, as of October 2026. "
              "Tools and versions change quickly: check the official documentation before relying on details.")

TOPICS = {}

# =================================================================== experienced candidate
TOPICS["exp-expectations"] = [
    section("intro", "introduction", "What changes at 3 to 4 years", NOTICE,
            "A fresher is asked **what** something is. At 3 to 4 years you are asked **why you chose it, what went "
            "wrong, and what you would change**. Knowing Spring is assumed; owning a service in production is what "
            "is being tested.",
            table(["Area", "Fresher answer", "3 to 4 year answer"], [
                ["HashMap", "Stores key-value pairs in buckets", "Resizing cost, treeification, why you presize, and when you chose ConcurrentHashMap in a real service"],
                ["Transactions", "`@Transactional` makes it atomic", "Self-invocation, propagation, isolation anomalies you met, and keeping transactions away from remote calls"],
                ["Kafka", "A message queue with topics", "Partition key choice, duplicates, retries, a dead-letter topic, and how you handled consumer lag"],
                ["A project", "The features it has", "The architecture, your part, the hardest bug, numbers, and what you would redesign"],
            ], "The same topic, asked at two levels.")),
    section("rounds", "visual", "A typical interview loop",
            diagram("Common rounds", """
flowchart LR
  A[Recruiter screen] --> B[Coding: DSA, medium level]
  B --> C[Java and Spring depth]
  C --> D[Low-level design or machine coding]
  D --> E[High-level design]
  E --> F[Project deep dive]
  F --> G[Manager and behavioural]
""", "Companies differ: service companies often skip design rounds, and product companies weigh coding and design more."),
            table(["Round", "What decides it", "Where on this site"], [
                ["Coding", "Pattern recognition, clean Java, tests aloud", "DSA Patterns"],
                ["Java and Spring", "Internals and real pitfalls", "Core Java, Spring internals"],
                ["Low-level design", "Working code, clear classes, concurrency", "System Design Part 3"],
                ["High-level design", "Requirements, estimates, trade-offs, failures", "System Design Parts 1 and 2"],
                ["Project deep dive", "Ownership and honest numbers", "Project deep dive step"],
                ["Behavioural", "Specific stories, not opinions", "Behavioural interview step"],
            ])),
    section("use", "notes", "How to use this site at your level",
            table(["Stage", "How to treat it", "Depth"], [
                ["Core Java", "Skim the basics; test yourself with the practice questions", "Refresh"],
                ["Concurrency, JVM", "Study properly: this separates candidates", "Deep"],
                ["Spring internals, data, security", "Study properly, and map it to your projects", "Deep"],
                ["Databases and Redis", "Indexes, plans, isolation, cache failure modes first", "Deep"],
                ["Microservices and Kafka", "Failure handling and delivery guarantees first", "Deep"],
                ["System design", "Practise on paper, with a timer", "Deep"],
                ["Cloud", "Be able to deploy and defend an architecture", "Working"],
                ["Frontend", "Enough to own a feature end to end", "Working"],
                ["AI engineering", "Build one real feature", "Working"],
                ["OS and networks", "Revise what explains production behaviour", "Refresh"],
                ["DSA", "Daily, alongside everything else", "Ongoing"],
                ["Aptitude", "Only if your target company tests it", "Optional"],
            ], "My suggested emphasis, not a rule: adjust it to your target companies."),
            note("tip", "Skip by testing, not by assuming", "Answer a part's practice questions before reading it. If you get them right, tick it off and move on."),
            keypoints("Expect why, trade-offs and failures, not definitions.", "Tie every concept to something you built.",
                      "Numbers you measured beat adjectives.", "Do DSA in parallel: 2 problems a day beats a final cram.")),
    practice(("Why is \"I used Redis for caching\" a weak answer?",
              "It states a tool, not a decision. Say what was slow, what you cached, how you invalidated it, how you handled stampedes, and the measured result."),
             ("Which rounds are usually new compared with a fresher's interview?",
              "Low-level and high-level design, the project deep dive, and behavioural questions about ownership.")),
]

TOPICS["exp-production-debugging"] = [
    section("intro", "introduction", "Why this gets asked", NOTICE,
            "\"The API became slow in production. What do you do?\" is a favourite question at this level, because the "
            "order you do things in shows real experience. The method matters more than knowing every tool."),
    section("method", "visual", "The method",
            diagram("Incident flow", """
flowchart TD
  A[Alert or user report] --> B[Assess impact: who, how many, since when]
  B --> C{Did something just change?}
  C -->|yes| D[Roll back or disable the flag first]
  C -->|no| E[Mitigate: scale, shed load, fail over]
  D --> F[Service recovered]
  E --> F
  F --> G[Find the root cause from metrics, logs, traces]
  G --> H[Fix and add a test or alert]
  H --> I[Blameless review]
""", "Restore service first. Understanding comes after users stop hurting.")),
    section("scenarios", "example", "Scenarios to practise out loud",
            table(["Symptom", "First checks", "Likely causes", "Fix"], [
                ["Latency rose, CPU normal", "Traces, connection pool wait, thread dump", "Pool exhausted, slow dependency, lock contention", "Timeouts, pool sizing, fix the slow query"],
                ["One endpoint slow", "Slow query log, `EXPLAIN`, Hibernate SQL count", "N+1, missing index, plan change", "Fetch join or batch size, add an index"],
                ["Heap grows until OOM", "GC logs, heap dump, dominator tree", "Unbounded cache, ThreadLocal, listeners", "Bound it, clean up, fix the retention path"],
                ["CPU at 100%", "`top -H`, `jstack`, profiler", "Hot loop, regex backtracking, GC thrashing", "Fix the code, or size the heap"],
                ["Consumer lag growing", "Lag per partition, consumer logs", "Slow handler, poison message, rebalancing", "Dead-letter topic, scale, tune polling"],
                ["Database deadlocks", "Database deadlock log", "Different lock order", "Consistent ordering, shorter transactions, retry"],
                ["Works locally, fails after deploy", "Config diff, recent changes, startup logs", "Config, secrets, network, schema mismatch", "Roll back, then compare environments"],
                ["Intermittent 502 or 504", "Load balancer logs, keep-alive and timeouts", "Timeout mismatch, instances restarting", "Align timeouts, graceful shutdown"],
            ], "The guides on JVM, databases, Kafka and networks explain each of these in depth.")),
    section("commands", "code", "Commands to know",
            code("bash", """
jcmd <pid> Thread.print                       # thread dump: BLOCKED threads, pool states
jcmd <pid> GC.heap_info                       # heap usage now
jcmd <pid> GC.heap_dump /tmp/app.hprof        # heap dump, then open in Eclipse MAT
jstat -gcutil <pid> 1000                      # GC activity every second
top -H -p <pid>                               # busiest threads of the process
kubectl logs <pod> --previous                 # logs of the crashed container
kubectl describe pod <pod>                    # OOMKilled? failed probes?
""", "First-response toolkit"),
            note("warning", "Gotcha", "A heap dump pauses the JVM and may contain user data and secrets. On a busy service, take it from one instance out of rotation, and handle the file as sensitive.")),
    section("notes", "notes", "Important notes",
            interview("**Tell me about a production issue you handled.** Use a real one: the impact in numbers, how you noticed, how you mitigated, the root cause, the fix, and what you added so it cannot recur. If you have never been on call, debug a real problem in your own project under load, and tell that story honestly."),
            keypoints("Mitigate first, then investigate.", "Ask what changed: most incidents follow a change.",
                      "Check traces, metrics, then logs, then dumps.", "Every incident ends with a test or an alert.")),
    practice(("An API went from 100 ms to 3 s after a deploy. What is your first action?",
              "Confirm the impact and correlate with the deploy, then roll back to restore service. Investigate the cause afterwards using the diff, traces and slow queries."),
             ("Threads are mostly waiting for a database connection. What does that suggest?",
              "Pool exhaustion: slow queries, long transactions, or remote calls held inside a transaction. Fix the holding time first; a bigger pool only moves the pressure to the database."),
             ("A pod restarts repeatedly and shows OOMKilled, but heap metrics look fine. Why?",
              "The container limit counts all process memory: metaspace, thread stacks, direct buffers and the code cache, not only heap. Check native memory and the heap's share of the limit.")),
]

TOPICS["exp-project-deep-dive"] = [
    section("intro", "introduction", "Own your projects", NOTICE,
            "At this level, the deep dive can decide the interview. Prepare each project so that you can draw it, defend "
            "it and criticise it. Your own question list is on the **Resume and project walkthroughs** step (plan day 52)."),
    section("structure", "concept", "A 3-minute walkthrough",
            table(["Time", "Cover", "Example of the level of detail"], [
                ["30 s", "The problem and users", "Who uses it and what hurt before"],
                ["60 s", "Architecture, drawn", "Services, data stores, why this shape"],
                ["45 s", "Your part", "What you personally designed and built: say \"I\""],
                ["30 s", "The hardest problem", "One real bug or trade-off, and how you solved it"],
                ["15 s", "Result and regret", "A measured result, and what you would change"],
            ])),
    section("sheet", "example", "Fill this in for every project",
            table(["Question", "Your answer must include"], [
                ["Why this database?", "Access patterns and what you rejected"],
                ["How does it fail?", "What happens when each dependency is down"],
                ["What is the load?", "Real or tested requests per second and data size"],
                ["How do you deploy it?", "Pipeline, rollback, configuration and secrets"],
                ["How do you know it works?", "Tests, metrics, alerts"],
                ["What is your worst bug?", "Symptom, cause, fix, prevention"],
                ["How is it secured?", "Authentication, authorisation, input handling"],
                ["What would you redesign?", "A specific change with its reason"],
            ]),
            note("warning", "Be honest about numbers", "Never invent metrics: interviewers probe them. If you have none, run a load test on your project now, and quote what you measured and how.")),
    section("gap", "notes", "If your projects feel too small",
            "Add one production-grade concern to an existing project rather than starting another CRUD app:",
            table(["Add", "Proves", "Guide"], [
                ["Load test and fix a real bottleneck", "Performance thinking", "Databases, Spring performance"],
                ["Idempotent consumer and dead-letter topic", "Distributed reliability", "Kafka Part 6"],
                ["Tracing, metrics and an alert", "Operability", "Beyond Basics Part 5"],
                ["Deployment to AWS with CI/CD", "Ownership to production", "Git, Docker and CI/CD Part 4"],
                ["One AI feature using RAG", "Current skills", "AI engineering stage"],
            ]),
            keypoints("Be able to draw every project from memory.", "Say \"I\" for your work and \"we\" for the team's.",
                      "Prepare the failure modes, not just the happy path.", "Only quote numbers you can defend.")),
    practice(("Your project uses Kafka. What will the follow-ups be?",
              "Why not a simple queue or a direct call, the partition key, ordering, duplicate handling, retries, lag, and what happens when the consumer is down."),
             ("How do you answer \"what was your contribution\" on a team project?",
              "Name specific components and decisions you owned, and credit the rest to the team. Be ready to go deep on exactly what you claim.")),
]

TOPICS["exp-behavioural"] = [
    section("intro", "introduction", "Behavioural rounds at this level", NOTICE,
            "You are expected to show ownership, influence without authority, and some mentoring. Prepare stories "
            "before the interview: inventing one live rarely goes well."),
    section("star", "concept", "STAR, used properly",
            table(["Part", "Share", "Content"], [
                ["Situation", "10%", "Just enough context"],
                ["Task", "10%", "Your responsibility"],
                ["Action", "60%", "What you did, and why: use \"I\""],
                ["Result", "20%", "The outcome in numbers, and what you learned"],
            ], "Most weak answers spend their time on the situation.")),
    section("bank", "example", "Stories to prepare",
            "Your `10-Interview-Prep` plan lists teamwork, conflict, failure, learning fast and taking the lead. At 3 to 4 years, add the last four below.",
            table(["Story", "Shows"], [
                ["Teamwork on a difficult delivery", "Collaboration"],
                ["A conflict with a colleague or manager", "Disagreeing well, and committing"],
                ["A failure or production mistake you caused", "Accountability"],
                ["Learning something fast under pressure", "Adaptability"],
                ["Taking the lead without being asked", "Initiative"],
                ["Mentoring or unblocking a junior", "Growing others"],
                ["Pushing back on a requirement or deadline", "Judgement"],
                ["Paying down technical debt: how you justified it", "Business sense"],
                ["A design you changed after feedback", "Humility"],
            ])),
    section("hr", "example", "Common questions",
            table(["Question", "What they want"], [
                ["Tell me about yourself", "60 to 90 seconds: current work, strengths, why this role"],
                ["Why are you leaving?", "Moving towards something; never criticise your employer"],
                ["Why this company?", "Specifics from your research: product, stack, challenges"],
                ["Strengths and weaknesses", "A real weakness and what you are doing about it"],
                ["Where in 5 years?", "A direction that fits this role"],
                ["Salary expectations", "A researched range, after you understand the role"],
                ["Do you have questions?", "Ask about on-call, how decisions get made, and team challenges"],
            ]),
            keypoints("Prepare 8 to 10 stories that can each answer several questions.", "Spend most of the time on your actions.",
                      "End with a measurable result and a lesson.", "Practise aloud and time yourself.")),
    practice(("What is wrong with \"we had a tight deadline and the team worked hard and delivered\"?",
              "No personal action, no specific decision and no measurable result."),
             ("How do you describe a failure without hurting yourself?",
              "Choose a real but recoverable one. Own it, then spend most of the answer on how you fixed it and what you changed afterwards.")),
]

TOPICS["exp-architecture-judgement"] = [
    section("intro", "introduction", "Beyond the framework", NOTICE,
            "These ideas come up when interviewers check whether you can shape a codebase, not only add to one."),
    section("ddd", "concept", "Domain-driven design: the useful parts",
            table(["Idea", "Meaning", "In practice"], [
                ["Ubiquitous language", "Code uses the business's words", "`Shipment.dispatch()`, not `updateStatus(3)`"],
                ["Bounded context", "A model is valid inside a boundary", "\"Customer\" differs in billing and support: often a service boundary"],
                ["Aggregate", "A consistency boundary, changed as a unit", "`Order` protects its lines; one transaction per aggregate"],
                ["Value object", "Identified by value, immutable", "`Money` as a record, never a raw `double`"],
                ["Domain event", "Something that happened", "`OrderPlaced` published through an outbox"],
            ]),
            note("tip", "Do not over-apply it", "Simple CRUD does not need DDD. Use it where the business rules are the hard part.")),
    section("hex", "architecture", "Layered versus hexagonal",
            diagram("Hexagonal architecture", """
flowchart LR
  A[REST controller] --> B[Input port]
  C[Kafka listener] --> B
  B --> D[Domain and use cases<br/>no framework imports]
  D --> E[Output port]
  E --> F[JPA adapter]
  E --> G[HTTP client adapter]
""", "Dependencies point inward: the domain knows interfaces, and adapters implement them."),
            "Layered controller-service-repository code is fine for most services. Hexagonal pays off when domain logic is rich, or several inputs and outputs must be swappable and tested without a framework."),
    section("decisions", "concept", "Decisions, debt and multi-tenancy",
            "**Architecture decision records (ADRs)** are short files that record the context, the decision, the options rejected and the consequences. They answer \"why is it like this?\" a year later.",
            "**Technical debt** should be argued in business terms: \"this module caused 3 of the last 5 incidents, and changes take twice as long\" gets time allocated. \"The code is ugly\" does not.",
            table(["Multi-tenancy model", "Isolation", "Cost", "Risk"], [
                ["Shared tables with `tenant_id`", "Lowest", "Lowest", "One missing filter leaks data; use row-level security"],
                ["A schema per tenant", "Medium", "Medium", "Migrations multiply"],
                ["A database per tenant", "Highest", "Highest", "Operational overhead"],
            ])),
    section("notes", "notes", "Important notes",
            interview("**Monolith or microservices for a new product?** Usually a well-modularised monolith first. Microservices solve team and scaling problems at the price of distributed-systems problems. Split when a boundary and a real reason exist, such as independent deployment or scaling."),
            keypoints("A bounded context is often the right service boundary.", "One transaction per aggregate; use events between them.",
                      "Use hexagonal only where the domain justifies it.", "Record decisions, and argue debt in business terms.")),
    practice(("Why is one transaction per aggregate a useful rule?",
              "It keeps locks small and makes later splitting possible. Other aggregates are updated through events, with eventual consistency."),
             ("How do you convince a manager to fund a refactor?",
              "Show its cost in incidents, delivery time or defects, propose a small incremental step, and say how you will measure the improvement.")),
]

TOPICS["exp-backend-extras"] = [
    section("intro", "introduction", "Technologies your guides only touch", NOTICE,
            "You do not need these all in depth. Know what each is for and when you would refuse to use it; go deeper "
            "only if a job description asks."),
    section("webflux", "concept", "Reactive Spring (WebFlux)",
            code("java", """
@GetMapping("/orders/{id}")
Mono<OrderView> order(@PathVariable long id) {
    return orders.findById(id)                          // non-blocking
        .zipWith(customers.fetch(id))                   // runs both concurrently
        .map(t -> OrderView.of(t.getT1(), t.getT2()))
        .timeout(Duration.ofSeconds(2));
}
""", "Mono is 0 or 1 item; Flux is many"),
            table(["", "Spring MVC plus virtual threads", "WebFlux"], [
                ["Code style", "Plain sequential", "Reactive chains"],
                ["Debugging", "Normal stack traces", "Harder"],
                ["Fits", "Most services, with blocking JDBC", "Streaming, backpressure, gateways"],
            ], "Since Java 21, virtual threads remove much of the reason to go reactive just for concurrency."),
            note("warning", "Gotcha", "One blocking call on a WebFlux event-loop thread stalls many requests. Blocking JDBC does not belong there.")),
    section("batch", "concept", "Spring Batch",
            "For large, restartable jobs such as nightly settlements: a **Job** has **Steps**; a chunk step reads, processes and writes N items per transaction. Its job repository records progress, so a failed run restarts where it stopped. Prefer it over a hand-written `@Scheduled` loop when volume or restartability matters."),
    section("graphql", "concept", "GraphQL",
            "The client asks for exactly the fields it wants from one endpoint. It suits varied clients and aggregating several sources. The costs: harder HTTP caching, query-cost limits are needed, and N+1 calls unless you batch (`@BatchMapping` in Spring for GraphQL).",
            table(["Prefer", "When"], [
                ["REST", "Public or simple APIs, cacheable resources"],
                ["GraphQL", "Many client shapes, an aggregation layer"],
                ["gRPC", "Internal service-to-service, strict contracts, performance"],
            ])),
    section("load", "concept", "Load testing",
            "k6, Gatling and JMeter generate realistic traffic. Test at the expected load, then find the breaking point, and watch **p95 and p99**, not averages. Generate load from a separate machine, use production-like data, and warm up the JVM first. Your numbers then have a defensible source for your resume.",
            code("javascript", """
import http from 'k6/http';
import { check } from 'k6';

export const options = {
  stages: [{ duration: '1m', target: 50 }, { duration: '3m', target: 50 }, { duration: '1m', target: 0 }],
  thresholds: { http_req_duration: ['p(95)<300'], http_req_failed: ['rate<0.01'] },
};

export default function () {
  check(http.get('http://localhost:8080/api/books'), { 'status 200': (r) => r.status === 200 });
}
""", "A k6 script"),
            keypoints("Virtual threads cover most concurrency needs without reactive code.", "Spring Batch for large restartable jobs.",
                      "REST by default; GraphQL and gRPC for specific reasons.", "Measure p95 and p99, on realistic data.")),
    practice(("Why not rewrite a Spring MVC service in WebFlux for scale?",
              "With blocking JDBC there is little gain, and the code gets harder to debug. Virtual threads usually give the throughput with simpler code."),
             ("Why is average latency a poor load-test metric?",
              "It hides the slow tail that real users hit. Report p95 and p99 along with the error rate.")),
]

# =================================================================== AWS
TOPICS["aws-foundations"] = [
    section("intro", "introduction", "AWS for a backend developer", NOTICE,
            "Your Git, Docker and CI/CD guide (Part 4) already covers cloud foundations, IAM and running a service on "
            "ECS. This page adds the map of services you will be asked about. You do not need all of AWS: learn these, "
            "and what each is for.",
            table(["Need", "AWS service", "Think of it as"], [
                ["Run containers", "ECS with Fargate, or EKS", "Managed containers; EKS is Kubernetes"],
                ["Run servers", "EC2", "Virtual machines"],
                ["Run functions", "Lambda", "Code on events, no servers"],
                ["Relational database", "RDS, Aurora", "Managed PostgreSQL or MySQL"],
                ["Key-value at scale", "DynamoDB", "Partition key design is everything"],
                ["Cache", "ElastiCache", "Managed Redis-compatible cache"],
                ["Files", "S3", "Object storage; not a file system"],
                ["Queue", "SQS", "Point-to-point work queue"],
                ["Fan-out", "SNS, EventBridge", "Publish to many subscribers"],
                ["Streaming", "MSK, Kinesis", "Managed Kafka; AWS's own stream"],
                ["Entry point", "ALB, API Gateway, CloudFront", "Load balancer, API front door, CDN"],
                ["Identity", "IAM, Cognito", "Permissions for services; user sign-in"],
                ["Secrets", "Secrets Manager, Parameter Store", "Configuration outside the image"],
                ["Observability", "CloudWatch, X-Ray", "Logs, metrics, alarms; tracing"],
            ])),
    section("iam", "concept", "Three ideas that come up constantly",
            "**Shared responsibility.** AWS secures the cloud; you secure what you put in it: IAM, open ports, encryption settings and your code.",
            "**IAM roles, not keys.** A service gets temporary credentials through a role. Long-lived access keys in code or configuration are the classic leak. Grant the least privilege needed.",
            "**Regions and Availability Zones.** A region holds several isolated AZs. Run across at least two AZs for availability; go multi-region only when the business truly needs it, because it is far more complex.",
            code("java", """
// No keys in code: the SDK finds the role's temporary credentials automatically
S3Client s3 = S3Client.builder().region(Region.AP_SOUTH_1).build();

s3.putObject(
    PutObjectRequest.builder().bucket("invoices").key("2026/inv-42.pdf").build(),
    RequestBody.fromBytes(pdf));
""", "AWS SDK for Java v2")),
    section("notes", "notes", "Important notes",
            note("warning", "Gotcha: surprise bills", "Set a budget alarm before you create anything. NAT gateways, idle RDS instances, and data transfer are common surprises when practising."),
            interview("**ECS or EKS?** ECS with Fargate is simpler and enough for most teams. EKS makes sense when you need Kubernetes' portability and ecosystem, or already have the skills, because it costs more to operate."),
            keypoints("Learn the service map, not all of AWS.", "Use IAM roles and least privilege; no long-lived keys.",
                      "Run across two or more Availability Zones.", "Set a budget alarm first.")),
    practice(("SQS or SNS?", "SQS is a queue that one group of workers consumes. SNS pushes to many subscribers. They are often combined: SNS fans out to several SQS queues."),
             ("Why is S3 a poor place for frequently edited files?", "Objects are replaced whole, with no partial update or file locking. It suits immutable objects served at scale.")),
]

TOPICS["aws-architecture"] = [
    section("intro", "introduction", "A Spring Boot app on AWS", NOTICE,
            "This is the reference shape to draw from memory, and then adapt to your project.",
            diagram("Reference architecture", """
flowchart TD
  U[Users] --> CF[CloudFront CDN]
  CF --> S3[S3: React build]
  CF --> ALB[Application Load Balancer<br/>public subnets, two AZs]
  ALB --> ECS[ECS Fargate tasks: Spring Boot<br/>private subnets]
  ECS --> RDS[(RDS PostgreSQL<br/>primary and standby)]
  ECS --> REDIS[(ElastiCache)]
  ECS --> SQS[SQS queue]
  SQS --> W[Worker tasks]
  ECS -. role .-> SM[Secrets Manager]
  ECS -. logs .-> CW[CloudWatch]
""", "Only the load balancer and CDN face the internet; everything else stays private.",
                    [{"name": "CloudFront and S3", "description": "Serve the React build cheaply and globally, and route `/api` to the load balancer."},
                     {"name": "ALB", "description": "Terminates TLS, health-checks tasks and spreads traffic across AZs."},
                     {"name": "ECS Fargate", "description": "Runs your container in private subnets, scaled on CPU or request count."},
                     {"name": "RDS Multi-AZ", "description": "A synchronous standby for failover. Add read replicas for read scale; they are different things."},
                     {"name": "SQS and workers", "description": "Move slow work out of the request, with a dead-letter queue for failures."}])),
    section("network", "concept", "VPC basics",
            table(["Piece", "Purpose"], [
                ["Public subnet", "Has a route to an internet gateway: load balancers"],
                ["Private subnet", "No inbound internet: applications and databases"],
                ["NAT gateway", "Lets private resources call out; costs per hour and per GB"],
                ["VPC endpoint", "Private path to services such as S3, avoiding NAT"],
                ["Security group", "Stateful firewall per resource: database allows only the app's group"],
            ])),
    section("deliver", "concept", "Deploy and scale",
            table(["Concern", "Choice"], [
                ["Infrastructure", "Terraform or AWS CDK, in Git: no console clicking"],
                ["Pipeline", "GitHub Actions with an OIDC role, no stored AWS keys; push to ECR, then update the service"],
                ["Release", "Rolling, or blue-green; schema changes stay backward compatible"],
                ["Scaling", "Target tracking on ECS; connection pool sizes must fit the database's limit"],
                ["Backups", "Automated RDS snapshots, and test the restore"],
            ]),
            note("warning", "Gotcha", "Autoscaling can exhaust database connections: tasks times pool size must stay under the limit. RDS Proxy can help.")),
    section("notes", "notes", "Important notes",
            interview("**Design this for 99.9% availability on AWS.** Stateless tasks across at least two AZs behind an ALB, RDS Multi-AZ, health checks, autoscaling, backups with tested restores, alarms on user-facing symptoms, and safe deployments. Then state the costs and what you left out, such as multi-region."),
            keypoints("Public: load balancer and CDN only.", "Multi-AZ gives availability; read replicas give read scale.",
                      "Infrastructure as code, and OIDC instead of stored keys.", "Check autoscaling against database connection limits.")),
    practice(("What is the difference between RDS Multi-AZ and a read replica?",
              "Multi-AZ is a synchronous standby for failover, not used for reads in the classic setup. A read replica is asynchronous and serves reads, so it can lag."),
             ("A task in a private subnet cannot reach an external API. What do you check?",
              "The route to a NAT gateway, the security group's outbound rules, and DNS. Check the network ACL too.")),
]

TOPICS["aws-serverless"] = [
    section("intro", "introduction", "Serverless and messaging", NOTICE,
            "Lambda and the messaging services appear in many Java job descriptions, usually for event processing."),
    section("lambda", "concept", "Lambda with Java",
            code("java", """
public class InvoiceHandler implements RequestHandler<SQSEvent, SQSBatchResponse> {

    // created once per execution environment and reused between invocations
    private static final S3Client S3 = S3Client.create();

    @Override
    public SQSBatchResponse handleRequest(SQSEvent event, Context context) {
        List<SQSBatchResponse.BatchItemFailure> failures = new ArrayList<>();
        for (SQSEvent.SQSMessage message : event.getRecords()) {
            try {
                process(message);                     // must be idempotent
            } catch (Exception e) {
                failures.add(new SQSBatchResponse.BatchItemFailure(message.getMessageId()));
            }
        }
        return new SQSBatchResponse(failures);        // only failed messages are retried
    }
}
""", "An SQS-triggered handler"),
            table(["Fact", "Why it matters"], [
                ["Cold starts", "The JVM and Spring start slowly. Use SnapStart, keep dependencies few, avoid full Spring where you can"],
                ["15-minute limit", "Not for long jobs: use ECS tasks or Step Functions"],
                ["Concurrency", "Scales fast and can overwhelm a database: set reserved concurrency, use RDS Proxy"],
                ["Billing", "By duration and memory; memory also increases CPU"],
            ]),
            table(["Choose", "When"], [
                ["Lambda", "Spiky, event-driven, short tasks; low traffic"],
                ["ECS or EKS", "Steady traffic, long requests, existing Spring services"],
            ])),
    section("messaging", "concept", "Choosing messaging",
            table(["Service", "Model", "Ordering", "Use for"], [
                ["SQS Standard", "Queue, at-least-once", "Best effort", "Background jobs"],
                ["SQS FIFO", "Queue, deduplication window", "Per message group", "Order per customer"],
                ["SNS", "Push to subscribers", "None (FIFO variant exists)", "Fan-out"],
                ["EventBridge", "Rule-based event routing", "None", "Integrating services and SaaS"],
                ["MSK or Kinesis", "Replayable log", "Per partition or shard", "Streams, multiple consumers, replay"],
            ]),
            note("warning", "Gotcha", "SQS may deliver a message twice, and the visibility timeout must exceed processing time, or it is redelivered while still being processed. Make consumers idempotent and configure a dead-letter queue.")),
    section("dynamo", "concept", "DynamoDB in one minute",
            "You design the table from your **access patterns**, not from entities. Items are found by partition key and optional sort key; other queries need a secondary index or a scan, which is slow and expensive. A bad partition key creates a hot partition. Choose it for strongly known, key-based access at huge scale. If you need flexible queries and joins, stay with PostgreSQL.",
            keypoints("Handlers must be idempotent, and report partial batch failures.", "Use SnapStart and few dependencies for Java cold starts.",
                      "Protect the database from Lambda concurrency.", "Kafka-like replay needs MSK or Kinesis, not SQS.")),
    practice(("Why might you not run your Spring Boot API on Lambda?",
              "Cold starts, per-instance connection handling and long-lived behaviour fit containers better when traffic is steady."),
             ("Messages are processed twice during a slow period. Why?",
              "Processing exceeded the visibility timeout, so SQS redelivered. Increase the timeout, and make processing idempotent anyway.")),
]

TOPICS["aws-interview"] = [
    section("intro", "introduction", "Getting AWS onto your resume honestly", NOTICE,
            "For a 3 to 4 year Java role, **having deployed something real** usually counts for more than a certificate. "
            "A certificate helps with resume filters, mainly at service companies and for career changes."),
    section("path", "concept", "Suggested order",
            diagram("From zero to credible", """
flowchart LR
  A[Budget alarm, IAM, S3] --> B[Deploy a Spring Boot app on ECS Fargate]
  B --> C[Add RDS, Secrets Manager and CloudWatch]
  C --> D[CI/CD with GitHub Actions and OIDC]
  D --> E[Add SQS and one Lambda]
  E --> F[Terraform everything]
  F --> G[Optional: certification]
""", "Your day-by-day plan's CareerFlux deployment is the natural project for this."),
            table(["Certification", "Fit for you", "Note"], [
                ["AWS Developer Associate", "Best fit for a Java developer", "Third-party sources report DVA-C03 replacing DVA-C02 around December 2026: confirm on the AWS site"],
                ["AWS Solutions Architect Associate (SAA-C03)", "Broader; recognised by many recruiters", "Useful for design interviews"],
                ["AWS AI Practitioner (AIF-C01)", "Optional, entry level", "Shows awareness, not engineering skill"],
            ], "Check the current exam details on the official AWS Certification site before you book."),
            "**Other clouds:** the concepts transfer to Azure and Google Cloud. Learn one properly, and check job descriptions: many enterprises and service companies ask for Azure.",
            table(["AWS", "Azure", "Google Cloud"], [
                ["ECS, EKS", "Container Apps, AKS", "Cloud Run, GKE"],
                ["Lambda", "Functions", "Cloud Run functions"],
                ["S3", "Blob Storage", "Cloud Storage"],
                ["RDS", "Azure Database", "Cloud SQL"],
                ["SQS, SNS", "Service Bus", "Pub/Sub"],
                ["IAM", "Entra ID, RBAC", "IAM"],
            ])),
    section("scenarios", "example", "Scenario questions",
            table(["Question", "Good answer covers"], [
                ["Reduce a high AWS bill", "Tagging and Cost Explorer first; rightsizing, autoscaling, S3 lifecycle rules, Savings Plans, NAT traffic"],
                ["Handle a traffic spike", "Autoscaling, a CDN, caching, queues to absorb writes, database limits"],
                ["A credential was leaked", "Revoke, audit CloudTrail, rotate, and remove the cause"],
                ["Upload large files", "Pre-signed S3 URLs, so that files bypass your servers"],
                ["AZ failure", "Multi-AZ tasks and database, health checks, no state on instances"],
            ]),
            keypoints("Deploy something real before you study for an exam.", "Learn one cloud well; concepts transfer.",
                      "Always mention cost and failure modes.", "Only list on your resume what you have actually used.")),
    practice(("How do clients upload a 2 GB file without loading your API?",
              "The API issues a time-limited pre-signed S3 URL, and the client uploads directly. S3 can then notify a queue for processing."),
             ("Certificate or project, if you only have time for one?",
              "The project: it gives you interview stories. Add the certificate if your target employers filter on it.")),
]

# =================================================================== AI
TOPICS["ai-what-employers-mean"] = [
    section("intro", "introduction", "What \"AI skills\" means in job descriptions", NOTICE,
            "It usually does **not** mean training neural networks. For a Java full stack developer it means two things: "
            "using AI tools to work faster and safely, and building features on top of AI models using normal engineering.",
            table(["Level", "What it means", "Who needs it", "Your priority"], [
                ["1. AI-assisted development", "Copilot, Claude Code, Cursor: generating, reviewing, testing and debugging with AI", "Every developer now", "Must have"],
                ["2. AI application engineering", "Calling LLM APIs, RAG, vector search, tools and agents from Spring", "Many backend and full stack roles", "Should have: your differentiator"],
                ["3. AI platform and operations", "Evaluations, cost, guardrails, model gateways", "AI-focused product teams", "Know the basics"],
                ["4. Machine learning engineering", "Training models, statistics, PyTorch, GPUs", "Specialist ML roles", "Not needed"],
            ], "My reading of the market, not a formal survey."),
            note("note", "What postings actually say", "A small sample of 2026 listings asks for things like LLMs, RAG, vector databases and AI APIs, Java libraries such as Spring AI and LangChain4j, and using copilots for development tasks. "
                 "Many of these are senior or contract roles, so read this as a direction rather than a requirement for every 3 to 4 year job.")),
    section("path", "visual", "What to learn, in order",
            diagram("AI learning path", """
flowchart TD
  A[How LLMs behave] --> B[AI-assisted development]
  B --> C[Spring AI: chat and structured output]
  C --> D[RAG and vector search]
  D --> E[Tools, agents and MCP]
  E --> F[Production: evaluation, security, cost]
  F --> G[Build and ship one project]
""", "This is the rest of this stage. Steady pace: 3 to 4 weeks of evenings.")),
    section("interview", "example", "How it shows up in interviews",
            table(["Question", "They are checking"], [
                ["How do you use AI tools in your work?", "Productive and critical: you review and test the output"],
                ["Add a support chatbot over our documents", "RAG design, citations, failure handling, cost"],
                ["How do you stop it inventing answers?", "Grounding, evaluation, saying \"I don't know\""],
                ["How do you know it works?", "Evaluation sets, not a few manual tries"],
                ["What could go wrong?", "Prompt injection, data leakage, cost, latency"],
            ]),
            keypoints("You do not need to train models.", "AI-assisted development is now a baseline.",
                      "Integrating LLMs is backend engineering you can already mostly do.", "One shipped feature beats many courses.")),
    practice(("A posting asks for \"GenAI experience\". What can you honestly offer after this stage?",
              "A deployed feature using RAG with Spring AI, its evaluation results and costs, and how you use AI tools in development. Describe it as project experience; do not claim production experience you lack."),
             ("Do you need to learn Python for AI roles?",
              "Not for Java application roles: Spring AI and LangChain4j cover integration. Reading basic Python helps, as many examples use it. Dedicated AI teams may require it.")),
]

TOPICS["ai-llm-fundamentals"] = [
    section("intro", "introduction", "How LLMs behave", NOTICE,
            "You can treat an LLM as an unusual remote service: stateless, slow, priced per use, and non-deterministic. "
            "Those properties drive all of the engineering."),
    section("concepts", "concept", "The vocabulary",
            table(["Term", "Meaning", "Engineering consequence"], [
                ["Token", "A chunk of text; the unit of billing and limits", "Count them; long prompts cost more"],
                ["Context window", "The most tokens a model can consider in one request", "Select what you send; you cannot send everything"],
                ["Stateless", "The model remembers nothing between calls", "You resend history: chat memory is your job"],
                ["Temperature", "How random the output is", "Low for extraction; higher for creative text"],
                ["Hallucination", "Confident but wrong output", "Ground answers in data; verify; never trust blindly"],
                ["Embedding", "A vector representing meaning", "Enables similarity search"],
                ["Structured output", "Output constrained to a schema", "Parse into a Java record, and validate"],
                ["Tool calling", "The model asks your code to run a function", "Your code runs it, and is the security boundary"],
            ])),
    section("call", "architecture", "What one request looks like",
            diagram("A chat request", """
sequenceDiagram
  participant U as User
  participant A as Your Spring service
  participant M as LLM API
  U->>A: question
  A->>A: build prompt: instructions, context, history
  A->>M: HTTPS request with messages
  M-->>A: stream of tokens
  A-->>U: stream to browser using SSE
  A->>A: log tokens, cost, latency
""", "To the service it is a slow HTTP call: apply timeouts, retries with backoff, and rate limits."),
            table(["Compared with a normal API", "So you must"], [
                ["Seconds of latency", "Stream responses; never hold a database transaction during the call"],
                ["Same input, different output", "Test with evaluations rather than exact matches"],
                ["Cost per request", "Track usage per user; set limits; choose smaller models where they are enough"],
                ["Rate limits and outages", "Retry with backoff, and design a fallback"],
            ])),
    section("prompt", "code", "Prompting that works",
            code("text", """
You are a support assistant for an online bookstore.

Answer using only the context below.
If the context does not contain the answer, say "I don't know" and suggest contacting support.
Reply in at most three sentences, and cite the document id, for example [doc-12].

<context>
{retrieved_documents}
</context>

<question>
{user_question}
</question>
""", "Clear role, rules, delimited data, output format"),
            keypoints("LLMs are stateless, slow, costly and non-deterministic.", "Everything sent counts against the context window.",
                      "Wrap calls with timeouts, retries, limits and logging.", "Separate instructions from untrusted data.")),
    practice(("Why does a long chat get more expensive per message?",
              "The model is stateless, so the history is resent every time. Summarise or trim it."),
             ("Why not hold a database transaction open during an LLM call?",
              "The call can take many seconds, so it holds a connection and locks, and could exhaust the pool."),
             ("When would you use a low temperature?",
              "When you need consistency, such as extracting fields or classifying.")),
]

TOPICS["ai-assisted-development"] = [
    section("intro", "introduction", "Working with AI coding tools", NOTICE,
            "Tools such as GitHub Copilot, Claude Code and Cursor are now common at work. The skill being tested isn't "
            "typing prompts; it's staying the engineer responsible for the result."),
    section("where", "concept", "Where they help and where to be careful",
            table(["Good uses", "Be careful with"], [
                ["Boilerplate, DTOs, mappers", "Security-sensitive code: authentication, authorisation, cryptography"],
                ["Unit tests from existing behaviour", "Concurrency and transactions: errors look plausible"],
                ["Explaining unfamiliar code", "Library APIs: may be invented or outdated"],
                ["Refactoring with tests in place", "Large unreviewed changes"],
                ["Stack traces and first debugging hypotheses", "Secrets and customer data: never paste them"],
            ])),
    section("flow", "visual", "A workflow that holds up",
            diagram("Task flow", """
flowchart LR
  A[Describe the task and constraints] --> B[Ask for a plan first]
  B --> C[Generate a small change]
  C --> D[Read every line]
  D --> E[Run tests and add missing ones]
  E --> F{Correct?}
  F -->|no| C
  F -->|yes| G[Commit and open a normal review]
""", "You remain the author: if you can't explain it, don't commit it."),
            code("text", """
Add rate limiting to POST /api/orders in this Spring Boot 3 service.
Constraints: use the existing Redis connection; limit 10 requests per minute per user;
return 429 with a Retry-After header; follow the style of RateLimitFilter in the auth package.
First list the files you would change and any risks. Do not write code yet.
""", "A prompt with context and constraints")),
    section("risk", "notes", "Risks to name in an interview",
            table(["Risk", "Mitigation"], [
                ["Plausible but wrong code", "Tests, review, reading it yourself"],
                ["Invented dependencies", "Check that packages exist, and scan them"],
                ["Leaking company code or secrets", "Follow company policy; use approved tools only"],
                ["Prompt injection through files or web pages", "Treat tool output as untrusted; review actions"],
                ["Losing your own skills", "Practise DSA and design without the tool"],
            ]),
            note("warning", "Interviews", "Many coding rounds ban AI tools, and some test using them. Ask beforehand, and keep practising unaided."),
            keypoints("Give context and constraints; ask for a plan first.", "Keep changes small, read all of it, and test it.",
                      "Never paste secrets or customer data.", "You own what you commit.")),
    practice(("\"Do you use AI tools?\" How do you answer?",
              "Give a specific example: the task, how you checked the output, a time it was wrong, and how you caught it."),
             ("AI wrote a passing test suite for your code. Is that enough?",
              "No. Tests can simply assert current behaviour, including bugs. Check that they would fail for a wrong implementation, and cover edge cases.")),
]

TOPICS["ai-spring-ai"] = [
    section("intro", "introduction", "LLMs from Spring Boot", NOTICE,
            "Spring AI gives you a portable API over model providers, in normal Spring style. LangChain4j is the main "
            "alternative, and the concepts are the same. The examples here follow the Spring AI 2.0 documentation."),
    section("setup", "code", "Setup",
            code("xml", """
<dependency>
  <groupId>org.springframework.ai</groupId>
  <artifactId>spring-ai-starter-model-anthropic</artifactId>   <!-- or -model-openai and others -->
</dependency>
""", "pom.xml, with the Spring AI BOM managing the version"),
            code("properties", """
spring.ai.anthropic.api-key=${ANTHROPIC_API_KEY}
""", "The key comes from the environment, never from Git"),
            note("note", "Provider property names", "Model names and properties change often. Take current values from the Spring AI and provider documentation.")),
    section("chat", "code", "Chat and structured output",
            code("java", """
@Service
class TicketTriage {

    record Triage(String category, int priority, String summary) {}

    private final ChatClient chat;

    TicketTriage(ChatClient.Builder builder) {
        this.chat = builder
            .defaultSystem("You triage support tickets for a bookstore. Priority is 1 (urgent) to 3 (low).")
            .build();
    }

    Triage triage(String ticket) {
        return chat.prompt()
            .user(ticket)
            .call()
            .entity(Triage.class);
    }
}
""", "A real feature in 20 lines", [
                {"lines": "4", "title": "A record as schema", "text": "The output is mapped to a Java record, so the rest of your code stays typed."},
                {"lines": "8-11", "title": "Builder injection", "text": "Spring Boot auto-configures `ChatClient.Builder`. The system prompt holds your instructions."},
                {"lines": "14-17", "title": "The call", "text": "`entity` converts the response. The model is called at this point, so it needs a timeout and error handling."},
            ]),
            note("warning", "Validate the result", "A typed result can still be wrong. Validate it (for example, priority within 1 to 3) before acting on it.")),
    section("stream", "code", "Streaming to the browser",
            code("java", """
@GetMapping(value = "/api/chat", produces = MediaType.TEXT_EVENT_STREAM_VALUE)
Flux<String> chat(@RequestParam String message) {
    return chat.prompt().user(message).stream().content();
}
""", "The user sees text at once rather than waiting")),
    section("resilience", "concept", "Treat it like any remote dependency",
            table(["Concern", "Approach"], [
                ["Timeouts and retries", "Set explicitly; retry only rate limits and transient errors"],
                ["Cost", "Log token usage per feature and user, and rate-limit users"],
                ["Fallback", "Degrade gracefully: the app should work when the model is down"],
                ["Tests", "Mock `ChatModel` in unit tests; use evaluations for quality"],
                ["Privacy", "Know what data you send to the provider, and remove what isn't needed"],
            ]),
            keypoints("`ChatClient` is the entry point.", "`entity()` maps output to records, but validate the values.",
                      "Stream for user-facing text.", "Add timeouts, limits and fallbacks as for any remote call.")),
    practice(("Why inject `ChatClient.Builder` rather than hard-coding a provider?",
              "Configuration chooses the model, so you can switch providers, and tests can substitute it."),
             ("When is `.call()` actually sent to the model?",
              "When a terminal method such as `content()`, `entity()` or `chatResponse()` runs.")),
]

TOPICS["ai-rag"] = [
    section("intro", "introduction", "RAG: answering from your own data", NOTICE,
            "A model doesn't know your documents. **Retrieval-augmented generation** finds relevant text and puts it in "
            "the prompt. This is the most common AI feature you'll be asked to build, and the most useful to practise.",
            diagram("The two RAG pipelines", """
flowchart TD
  subgraph ingest[Ingestion, ahead of time]
    A[Documents] --> B[Split into chunks] --> C[Embed each chunk] --> D[(Vector store)]
  end
  subgraph query[Query, per request]
    Q[Question] --> E[Embed the question] --> F[Find similar chunks]
    D --> F
    F --> G[Prompt: rules, chunks, question] --> H[LLM] --> I[Answer with citations]
  end
""", "Retrieval quality limits answer quality: most bad RAG answers are retrieval problems.")),
    section("store", "concept", "Embeddings and vector stores",
            "An embedding model turns text into a vector so that similar meanings land close together. A vector store finds the nearest vectors, even when no words match. **You likely already run one:** PostgreSQL with the `pgvector` extension is a sensible first choice over a new database.",
            table(["Decision", "Starting point", "Why it matters"], [
                ["Chunk size", "A few hundred tokens with some overlap", "Too large dilutes; too small loses context"],
                ["Number retrieved", "Start around 3 to 5, then tune", "More costs more and adds noise"],
                ["Search", "Combine keyword and vector search", "Vector search misses exact codes and names"],
                ["Filtering", "Filter by tenant and permissions", "Security: never retrieve what the user can't see"],
            ], "Starting values only: measure on your own data.")),
    section("code", "code", "With Spring AI",
            code("java", """
@Service
class DocsAssistant {

    private final VectorStore store;
    private final ChatClient chat;

    DocsAssistant(VectorStore store, ChatClient.Builder builder) {
        this.store = store;
        this.chat = builder.build();
    }

    void ingest(Resource pdf) {
        List<Document> pages = new PagePdfDocumentReader(pdf).get();
        store.add(new TokenTextSplitter().apply(pages));      // embeds and stores the chunks
    }

    String ask(String question) {
        return chat.prompt()
            .advisors(QuestionAnswerAdvisor.builder(store).build())   // retrieves and adds the context
            .user(question)
            .call()
            .content();
    }
}
""", "Ingest and ask"),
            note("tip", "Good practice project", "RAG over your own guides would make a strong portfolio project, because you can judge whether the answers are correct.")),
    section("quality", "notes", "Making it good",
            table(["Symptom", "Likely cause", "Try"], [
                ["Wrong or missing answers", "Retrieval misses the right chunk", "Better chunking, hybrid search, reranking"],
                ["Invents facts", "Prompt allows it, or context is weak", "Answer only from context; allow \"I don't know\"; add citations"],
                ["Outdated answers", "Stale index", "Re-ingest on change, and track document versions"],
                ["Shows others' data", "No filter at retrieval", "Filter by user permissions in the search itself"],
            ]),
            interview("**Design a chatbot over company documents.** Cover ingestion and updates, chunking, embeddings, hybrid retrieval, access control at retrieval, the prompt with citations, streaming, evaluation, cost limits, and a fallback when nothing relevant is found."),
            keypoints("RAG: retrieve relevant text, then generate from it.", "Start with pgvector if you already use PostgreSQL.",
                      "Enforce permissions during retrieval, never only in the prompt.", "Evaluate retrieval separately from generation.")),
    practice(("Why not simply send all your documents to the model?",
              "They won't fit the context window, cost would be high, and irrelevant text reduces quality."),
             ("Vector search misses the error code `ERR-4021`. Why, and how do you fix it?",
              "Embeddings capture meaning and handle exact identifiers poorly. Add keyword search and combine the results."),
             ("Why isn't \"don't reveal other tenants' data\" in the prompt a security control?",
              "A prompt can be overridden or ignored. If a chunk isn't retrieved, it can't leak, so filter in the query.")),
]

TOPICS["ai-agents-tools"] = [
    section("intro", "introduction", "Tools, agents and MCP", NOTICE,
            "With **tool calling**, the model can request that your code run a function. An **agent** is that loop repeated "
            "until the task is done. The term is heavily hyped: it's a loop with an LLM deciding the next step.",
            diagram("Agent loop", """
sequenceDiagram
  participant A as Your app
  participant M as LLM
  participant T as Your tool
  A->>M: goal and available tools
  M-->>A: please call getOrder(42)
  A->>T: run it, with the user's permissions
  T-->>A: result
  A->>M: here is the result
  M-->>A: final answer
""", "The model never runs anything itself: your code decides whether to.")),
    section("code", "code", "A tool in Spring AI",
            code("java", """
@Component
class OrderTools {

    private final OrderService orders;

    OrderTools(OrderService orders) { this.orders = orders; }

    @Tool(description = "Get the delivery status of one of the current user's orders")
    String orderStatus(long orderId) {
        return orders.statusForCurrentUser(orderId);   // permission check is here, in your code
    }
}

String reply = chat.prompt()
    .tools(orderTools)
    .user("Where is my order 42?")
    .call()
    .content();
""", "The model chooses when to call it")),
    section("safety", "concept", "Keeping agents safe",
            table(["Rule", "Why"], [
                ["Start with a workflow if steps are known", "Fixed code is cheaper, faster and more testable than an agent"],
                ["Use the user's permissions in every tool", "The model can be manipulated"],
                ["Read-only first; confirm actions that change data", "Limits the damage from mistakes"],
                ["Limit steps, time and spend", "Loops can run away and cost money"],
                ["Log every step and tool call", "You'll need it for debugging and audit"],
                ["Treat tool results as untrusted", "Content from web pages and emails can contain injected instructions"],
            ])),
    section("mcp", "concept", "MCP",
            "The **Model Context Protocol** is an open standard for connecting AI applications to tools and data. Rather than writing a custom integration for each assistant, you expose tools through an MCP server, and any compatible client can use them. Spring AI supports building both MCP clients and servers. Treat a third-party MCP server like any dependency that can run code: check who publishes it and what it can access.",
            keypoints("Agents are loops of model decisions and tool calls.", "Your code runs tools, so permissions live there.",
                      "Prefer simple workflows when the steps are known.", "Limit steps and spend, and log everything.")),
    practice(("When is an agent the wrong choice?",
              "When the steps are known. Plain code is cheaper, faster and more reliable."),
             ("A document tells the agent to \"email all customers\". What protects you?",
              "Treat retrieved content as data, scope tools to least privilege, and require human confirmation for actions with real effects.")),
]

TOPICS["ai-production"] = [
    section("intro", "introduction", "From demo to production", NOTICE,
            "Demos are easy; reliable features are the hard part, and that's where backend experience gives you an edge."),
    section("eval", "concept", "Evaluation: how you know it works",
            "You can't assert exact text, so you build an **evaluation set**: real questions with expected facts, and score each change against it. Without one, a prompt or model change is a guess.",
            diagram("Evaluation loop", """
flowchart LR
  A[Collect real questions] --> B[Write expected facts]
  B --> C[Run the system]
  C --> D[Score: retrieval and answer]
  D --> E[Change prompt, chunks or model]
  E --> C
  D --> F[Run in CI to catch regressions]
""")),
    section("security", "concept", "Security",
            table(["Risk", "Example", "Defence"], [
                ["Prompt injection", "A document says \"ignore your instructions\"", "Treat all retrieved and user content as untrusted; limit what tools can do"],
                ["Sensitive data leakage", "Personal data sent to a provider or logged", "Remove what isn't needed; check provider terms; control logs"],
                ["Excessive agency", "A tool deletes real data", "Least privilege; confirmation for writes"],
                ["Unsafe output", "Model HTML rendered directly", "Escape output as you would any untrusted input"],
                ["Cost attack", "A user sends huge requests", "Per-user limits, and maximum input and output tokens"],
            ], "There is no complete fix for prompt injection today, so limit the damage it can do.")),
    section("ops", "concept", "Cost, latency and observability",
            table(["Lever", "Effect"], [
                ["Use a smaller model where it is good enough", "Often the largest saving"],
                ["Cache repeated or similar requests", "Saves cost and time; be careful with per-user data"],
                ["Send less context", "Saves cost and may improve quality"],
                ["Batch offline work", "Providers may offer cheaper batch processing"],
            ]),
            "Log per request: model, tokens, cost, latency, retrieved documents and user feedback. Tracing with Micrometer and OpenTelemetry works as for any other service. Pin model versions, because a provider change can alter your results.",
            interview("**Your AI feature's quality dropped after a release. How do you investigate?** Compare against the evaluation set, then check what changed: prompt, model, data or retrieval. Inspect traces for failing examples, roll back the change, and add those cases to the set."),
            keypoints("No evaluation set means no way to know.", "Assume injection is possible, and limit the blast radius.",
                      "Track cost and tokens per feature.", "Version your prompts and pin your models.")),
    practice(("How do you test an LLM feature in CI when output varies?",
              "Mock the model for unit tests, and run a scored evaluation set with pass thresholds for quality."),
             ("What usually reduces cost the most?",
              "Using a smaller model where quality allows, then sending less context, and caching.")),
]

TOPICS["ai-portfolio-project"] = [
    section("intro", "introduction", "Your AI portfolio project", NOTICE,
            "One deployed project turns everything in this stage into interview stories. Add it to a project you already "
            "have, rather than starting from nothing.",
            table(["Option", "Shows", "Note"], [
                ["Chat over your own guides, with citations", "RAG, evaluation, streaming", "Keep the guides private if you don't own them"],
                ["Support assistant for an existing project", "RAG plus tools with permissions", "Most realistic"],
                ["Resume and job description matcher", "Structured output, evaluation", "Handle personal data carefully"],
            ], "My pick: add an assistant to a project you already have. It also deepens your project deep dive.")),
    section("plan", "example", "A four-week plan",
            table(["Week", "Build", "Done when"], [
                ["1", "Spring AI, chat with streaming, React UI", "Streams answers; has timeouts and limits"],
                ["2", "Ingestion, pgvector, retrieval with citations", "Answers cite the right documents"],
                ["3", "Evaluation set of 30+ questions; one tool with permissions", "You have a score and improved it"],
                ["4", "Deploy on AWS, with tracing, cost tracking and a demo", "Public demo, or a recording; README with numbers"],
            ]),
            diagram("Target architecture", """
flowchart LR
  R[React] --> S[Spring Boot and Spring AI]
  S --> P[(PostgreSQL and pgvector)]
  S --> L[LLM API]
  S --> O[Tracing and cost metrics]
""")),
    section("resume", "notes", "Putting it on your resume",
            code("text", """
Built a document assistant with Spring Boot, Spring AI and pgvector: streaming answers with citations.
Created a 30-question evaluation set and raised answer accuracy from X% to Y% by changing chunking and search.
Added per-user limits and cost tracking; average cost $Z per question.
""", "Fill in with your real measured numbers"),
            note("warning", "Keep it honest", "This is project experience, so label it that way. Interviewers will ask how you evaluated it and what failed."),
            keypoints("Extend a real project.", "Evaluation and cost numbers set you apart.", "Deploy it, and be ready to demo it.")),
    practice(("What will interviewers ask about this project?",
              "Why RAG, the chunking choice, how you measured quality, failure cases, cost, and how you handled security and prompt injection."),)
]


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for topic_id, sections in TOPICS.items():
        (OUT / f"{topic_id}.json").write_text(
            json.dumps({"source": SOURCE, "sections": sections}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(TOPICS), "topics written")


if __name__ == "__main__":
    main()
