"""
The shape of the Python Full Stack tree: its stages, the guides shared with the Java Full Stack tree, and the study order.
tools/build_python_fs.py reads this; the written parts live next to it as NN-<name>.md (header line "@part <id> | <title> | <stage id>").

The tree mirrors the Java Full Stack tree stage by stage. Where a Java guide is about a language-neutral subject (operating systems,
networks, SQL and NoSQL, the inside of Redis and Kafka, high-level system design, Git, Docker concepts, HTML/CSS and React) it is
SHARED, not copied: the topic's contentId points at the page in content/roadmaps/interview-prep/, and progress is still kept per tree.
Everything that is about the Java language or its frameworks has a Python counterpart written for this tree.
"""

JAVA_TREE = "interview-prep"

# id, title, description, colour: the same eleven stages as the Java tree (colours as in content/roadmaps/interview-prep/roadmap.json)
STAGES = [
    ("core-python", "Core Python", "Start here: the language, properly", "violet"),
    ("advanced-python", "Concurrency, CPython and advanced Python", "The depth that experienced developers are expected to have", "blue"),
    ("dsa", "DSA Patterns in Python", "Start early and keep going: 2 problems a day", "cyan"),
    ("web", "FastAPI, Django and Flask", "Build real REST APIs and web apps, then learn how they work inside", "teal"),
    ("data-stores", "Databases and Redis", "Indexes, query plans, isolation and caching", "fuchsia"),
    ("os-networks", "Operating systems and networks", "The fundamentals that explain how software behaves", "amber"),
    ("distributed", "Microservices, background work and Kafka", "Failure handling and delivery guarantees", "rose"),
    ("design", "System design", "High-level and low-level design, on paper with a timer", "green"),
    ("delivery", "Git, Docker and CI/CD", "Ship what you build", "slate"),
    ("frontend", "Frontend: JavaScript, TypeScript and React", "From HTML to a tested, deployed React app on a Python API", "violet"),
    ("interview", "Interviews", "Project deep dives, production thinking, behavioural rounds and mocks", "blue"),
]

# Guides of the Java Full Stack tree shown here without copying them: (topic id there = topic id here, stage)
SHARED = [(i, "data-stores") for i in ("databases-part-1", "databases-part-2", "redis-part-1", "redis-part-2", "redis-part-3", "redis-part-4",
                                       "redis-part-5", "redis-part-8", "redis-part-9", "redis-part-11", "redis-part-12")] \
    + [(f"operating-systems-part-{n}", "os-networks") for n in range(1, 7)] \
    + [(f"computer-networks-part-{n}", "os-networks") for n in range(1, 7)] \
    + [(i, "distributed") for i in ("kafka-part-1", "kafka-part-2", "kafka-part-8", "kafka-part-9")] \
    + [(i, "design") for i in ("system-design-part-1", "system-design-part-2", "system-design-part-4", "exp-architecture-judgement")] \
    + [(i, "delivery") for i in ("git-docker-cicd-part-1", "git-docker-cicd-part-2", "git-docker-cicd-part-4")] \
    + [(i, "frontend") for i in ("frontend-html-css", "frontend-react-fundamentals", "frontend-react-hooks", "frontend-react-state",
                                 "frontend-routing-forms", "frontend-react-performance", "frontend-testing", "frontend-nextjs-ssr", "frontend-interview")] \
    + [(i, "interview") for i in ("exp-expectations", "exp-project-deep-dive", "exp-behavioural", "plan-day-54-mock-databases-design")]

# The study order, one row of the tree per list. Reading rows top to bottom and left to right gives the learning order, and each row depends on
# the one above it. A row never mixes stages (the tree layout draws a stage heading wherever a row's stage changes).
ROWS = [
    # Core Python
    ["py-core-1"], ["py-core-2", "py-core-3", "py-core-4"], ["py-core-5", "py-core-6", "py-core-7"],
    # Concurrency, CPython and advanced Python
    ["py-core-8"], ["py-core-9", "py-core-10", "py-core-11"], ["py-core-12", "py-core-13", "py-core-14"], ["py-core-15", "py-core-16"],
    # DSA
    ["py-dsa-1"], ["py-dsa-2", "py-dsa-3", "py-dsa-4"], ["py-dsa-5", "py-dsa-6", "py-dsa-7"],
    # FastAPI, Django and Flask
    ["py-web-1"], ["py-web-2", "py-web-3", "py-web-4"], ["py-web-5", "py-web-6"], ["py-web-7", "py-web-8", "py-web-9"], ["py-web-10"],
    ["py-django-1"], ["py-django-2", "py-django-3"], ["py-flask-1", "py-web-extras"],
    # Databases and Redis
    ["databases-part-1"], ["databases-part-2", "redis-part-1"], ["redis-part-2", "redis-part-3", "redis-part-4"],
    ["redis-part-5", "py-redis-1", "py-redis-2"], ["redis-part-8"], ["redis-part-9", "py-redis-3", "redis-part-11"], ["redis-part-12"],
    # Operating systems and networks
    ["operating-systems-part-1"], ["operating-systems-part-2", "operating-systems-part-3", "operating-systems-part-4"],
    ["operating-systems-part-5", "operating-systems-part-6", "computer-networks-part-1"], ["computer-networks-part-2", "computer-networks-part-3"],
    ["computer-networks-part-4"], ["computer-networks-part-5", "computer-networks-part-6"],
    # Microservices, background work and Kafka
    ["py-web-11"], ["kafka-part-1", "kafka-part-2"], ["py-kafka-1", "py-kafka-2", "py-kafka-3"], ["py-kafka-4", "py-kafka-5", "py-kafka-6"],
    ["kafka-part-8", "kafka-part-9"], ["py-celery-1"], ["py-web-12"],
    # System design
    ["system-design-part-1"], ["system-design-part-2", "py-lld-1", "py-lld-2"], ["system-design-part-4", "exp-architecture-judgement"],
    # Git, Docker and CI/CD
    ["git-docker-cicd-part-1"], ["git-docker-cicd-part-2", "py-delivery-1", "py-delivery-2"], ["git-docker-cicd-part-4", "py-delivery-3"],
    # Frontend
    ["frontend-html-css"], ["py-fe-js", "py-fe-ts", "frontend-react-fundamentals"], ["frontend-react-hooks", "frontend-react-state", "frontend-routing-forms"],
    ["py-fe-react-api", "frontend-react-performance"], ["frontend-testing"], ["frontend-nextjs-ssr", "frontend-interview"],
    # Interviews
    ["exp-expectations"], ["py-exp-debugging", "exp-project-deep-dive", "exp-behavioural"],
    ["py-mock-core", "plan-day-54-mock-databases-design", "py-mock-dsa-lld"],
]
