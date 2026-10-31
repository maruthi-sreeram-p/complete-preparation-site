"""
Writes the experienced-level pages that no PDF covers: AWS, AI engineering,
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
    section("intro", "introduction", "Fresher today, experienced-level knowledge", NOTICE,
            "A fresher is usually asked **what** something is. An experienced developer is asked **why they chose it, "
            "what went wrong, and what they would change**. You can learn to answer at the second level before you have "
            "the job title, and that is what makes a fresher stand out.",
            table(["Area", "Typical fresher answer", "The deeper answer to aim for"], [
                ["HashMap", "Stores key-value pairs in buckets", "Resizing cost, treeification, why you presize, and when ConcurrentHashMap is needed"],
                ["Transactions", "`@Transactional` makes it atomic", "Self-invocation, propagation, isolation anomalies, and keeping transactions away from remote calls"],
                ["Kafka", "A message queue with topics", "Partition key choice, duplicates, retries, a dead-letter topic, and consumer lag"],
                ["A project", "The features it has", "The architecture, your part, the hardest bug, numbers, and what you would redesign"],
            ], "The same topic, asked at two levels."),
            note("warning", "Knowledge is not experience", "Never present learning or projects as paid work experience. Say what you built and how you tested it. Background checks and follow-up questions expose inflated resumes, and honest depth is impressive by itself.")),
    section("rounds", "visual", "Fresher hiring versus experienced hiring",
            diagram("A common fresher process", """
flowchart LR
  A[Online test: aptitude and coding] --> B[Technical round: DSA and core CS]
  B --> C[Project discussion]
  C --> D[Manager or HR]
""", "Companies differ. Service companies lean on aptitude; product companies lean on DSA."),
            table(["Round", "Who usually faces it", "Where on this site"], [
                ["Aptitude test", "Mostly freshers", "Aptitude tree"],
                ["Coding", "Everyone", "DSA Patterns"],
                ["Java, OOP, DBMS, OS, networks", "Freshers especially", "Core Java, Databases, OS and networks"],
                ["Spring and project discussion", "Everyone, deeper with experience", "Spring Boot, Project deep dive"],
                ["Low-level design", "Sometimes freshers; usually experienced", "System Design Part 3"],
                ["High-level design", "Mostly experienced", "System Design Parts 1 and 2"],
                ["Behavioural", "Everyone", "Behavioural and HR rounds"],
            ])),
    section("use", "notes", "How to use the three trees",
            table(["Tree", "When", "Pace"], [
                ["Java Full Stack", "Your main path, from step 1", "Every day"],
                ["Aptitude", "From day one if you are applying for fresher roles", "20 to 30 questions a day"],
                ["AI and Cloud", "After you can build a Spring Boot API", "A few evenings a week"],
            ], "A suggested rhythm: adjust it to your target companies."),
            note("tip", "Depth comes from building", "Reading about production problems is a start, but real understanding needs a project: deploy it, load test it, break it and fix it. The project deep dive step shows what to add."),
            keypoints("Learn why, trade-offs and failures, not just definitions.", "Tie every concept to something you built.",
                      "Do not skip aptitude and DSA: they get you past the first filter.", "Be honest about what is project work and what is job experience.")),
    practice(("Why is \"I used Redis for caching\" a weak answer?",
              "It states a tool, not a decision. Say what was slow, what you cached, how you invalidated it, how you handled stampedes, and the measured result."),
             ("As a fresher, should you study system design at all?",
              "Yes, but after the basics. It is rarely the deciding round for freshers, yet it helps you explain your own project and prepares you for your next job.")),
]

TOPICS["exp-production-debugging"] = [
    section("intro", "introduction", "Why this gets asked", NOTICE,
            "\"The API became slow in production. What do you do?\" is a favourite question for experienced candidates, because the "
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
            interview("**Tell me about a production issue you handled.** A strong answer gives the impact in numbers, how it was noticed and mitigated, the root cause, the fix, and what was added so it cannot recur. As a fresher you will not have an on-call story: debug a real problem in your own project under load, and tell that story honestly."),
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
            "A fresher who can defend a project in depth is rare and memorable. Prepare each project so that you can draw it, defend "
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
                ["One AI feature using RAG", "Current skills", "AI and Cloud tree"],
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
            "Interviewers look for ownership and honesty, and for experienced candidates, influence and mentoring too. Prepare stories "
            "before the interview: inventing one live rarely goes well."),
    section("star", "concept", "STAR, used properly",
            table(["Part", "Share", "Content"], [
                ["Situation", "10%", "Just enough context"],
                ["Task", "10%", "Your responsibility"],
                ["Action", "60%", "What you did, and why: use \"I\""],
                ["Result", "20%", "The outcome in numbers, and what you learned"],
            ], "Most weak answers spend their time on the situation.")),
    section("bank", "example", "Stories to prepare",
            "Your `10-Interview-Prep` plan lists teamwork, conflict, failure, learning fast and taking the lead. As a fresher, draw on college projects, internships and team work. The last four below are what experienced candidates are asked, so prepare them when you have the stories.",
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

def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for topic_id, sections in TOPICS.items():
        (OUT / f"{topic_id}.json").write_text(
            json.dumps({"source": SOURCE, "sections": sections}, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(len(TOPICS), "topics written")


if __name__ == "__main__":
    main()
