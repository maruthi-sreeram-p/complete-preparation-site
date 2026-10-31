"""Grammar: sentences assembled from word tables, so each form is produced by a rule rather than typed."""
from core import Q, T

C = "Grammar"
# base, third person, past, past participle, -ing, object
VERBS = [line.split("|") for line in """clean|cleans|cleaned|cleaned|cleaning|the room
paint|paints|painted|painted|painting|the wall
fix|fixes|fixed|fixed|fixing|the bug
test|tests|tested|tested|testing|the code
wash|washes|washed|washed|washing|the plates
open|opens|opened|opened|opening|the door
cook|cooks|cooked|cooked|cooking|the rice
write|writes|wrote|written|writing|the report
read|reads|read|read|reading|the notice
sing|sings|sang|sung|singing|the song
drive|drives|drove|driven|driving|the van
build|builds|built|built|building|the bridge
draw|draws|drew|drawn|drawing|the map
teach|teaches|taught|taught|teaching|the lesson
send|sends|sent|sent|sending|the email
buy|buys|bought|bought|buying|the tickets
catch|catches|caught|caught|catching|the ball
take|takes|took|taken|taking|the notes
eat|eats|ate|eaten|eating|the apple
break|breaks|broke|broken|breaking|the record""".split("\n")]
SG = ["She", "He", "Ravi", "Priya", "My brother", "The manager", "Our neighbour", "The driver"]
PL = ["They", "We", "The students", "My parents", "The workers"]
PRONOUN = {"She": "she", "He": "he", "Ravi": "he", "Priya": "she", "My brother": "he", "Our neighbour": "they", "The manager": "they", "The driver": "they"}


def lower_first(s):
    return s if s in ("Ravi", "Priya", "I") else s[0].lower() + s[1:]


@T(C, "Tenses")
def _(r):
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    sg = r.random() < .6
    S = r.choice(SG if sg else PL)
    be, have, was = ("is", "has", "was") if sg else ("are", "have", "were")
    frames = [
        ("{} .... {} every day.", s3 if sg else b, [b if sg else s3, ing, f"{have} {b}"], "A habit takes the simple present."),
        ("{} .... {} yesterday.", past, [f"will {b}", f"{be} {ing}", f"{have} {pp}"] , "\"Yesterday\" takes the simple past."),
        ("Look! {} .... {} right now.", f"{be} {ing}", [past, f"{have} {pp}", f"will have {pp}"], "\"Right now\" takes the present continuous."),
        ("{} .... {} tomorrow.", f"will {b}", [past, f"{have} {pp}", f"had {pp}"], "\"Tomorrow\" takes the future."),
        ("{} .... {} when the phone rang.", f"{was} {ing}", [f"{be} {ing}", f"will {b}", f"{have} {pp}"], "An action in progress in the past takes the past continuous."),
        ("{} .... already .... {}.", None, None, None),
        ("{} .... {} before the manager arrived.", f"had {pp}", [f"will {b}", f"{be} {ing}", f"{have} {pp}"], "The earlier of two past events takes the past perfect."),
        ("{} .... {} by next Friday.", f"will have {pp}", [past, f"{have} {pp}", f"had {pp}"], "Finished before a future point takes the future perfect."),
    ]
    f = r.choice(frames)
    if f[1] is None:
        return Q(f"Choose the correct option: {S} .... {obj} already.", f"{have} {pp}", f"\"Already\" with a present link takes the present perfect here; the other forms are incorrect in this sentence.", [ing, f"will {b}", f"{be} {b}"])
    return Q("Choose the correct option: " + f[0].format(S, obj), f[1], f[3], f[2])


NOUNS = [("boy", "boys"), ("student", "students"), ("player", "players"), ("engineer", "engineers"), ("teacher", "teachers"), ("driver", "drivers"), ("doctor", "doctors"), ("singer", "singers")]
THINGS = [("book", "books"), ("phone", "phones"), ("report", "reports"), ("laptop", "laptops"), ("chair", "chairs")]
SVA = [("Each of the {p}", 1), ("One of the {p}", 1), ("Every {s}", 1), ("Neither of the {p}", 1), ("The leader of the {p}", 1), ("The {s} along with the other {p}", 1), ("The {s} as well as the other {p}", 1), ("Many {p}", 0), ("Both {p}", 0), ("All the {p}", 0), ("A number of {p}", 0), ("The {s} and the {t}", 0), ("Neither the {s} nor the {p}", 0), ("Not only the {p} but also the {s}", 1), ("Either the {p} or the {s}", 1)]
PRED = [("ready", "is", "are"), ("late today", "is", "are"), ("in the room", "is", "are"), ("very busy", "was", "were"), ("finished the work", "has", "have"), ("a good idea", "has", "have")]


@T(C, "Subject-verb agreement")
def _(r):
    (s, p), (t, _) = r.sample(NOUNS, 2)
    frame, single = r.choice(SVA)
    rest, a, b = r.choice(PRED)
    subject = frame.format(s=s, p=p, t=t)
    return Q(f"Choose the correct option: {subject} .... {rest}.", a if single else b, ("The grammatical subject here is singular." if single else "The grammatical subject here is plural."), [b if single else a, "be", "being"])


@T(C, "Subject-verb agreement")
def _(r):
    n, ns = r.choice(THINGS + NOUNS)
    return Q(f"Choose the correct option: The number of {ns} .... rising.", "is", "\"The number\" is singular, though \"a number of\" is plural.", ["are", "were", "be"])


A_WORDS = "university|European trip|one-rupee coin|useful tool|uniform|horse|book|car|hotel|unicorn|user|young man|cat|house|ticket|laptop|bridge|teacher|ewe|one-way street|union leader|window|table|school|doctor".split("|")
AN_WORDS = "hour|honest man|apple|umbrella|engineer|MBA|X-ray|egg|orange|old friend|heir|idea|ant|elephant|island|hourglass|honour|owl|envelope|interview|SMS|FIR|umpire|ice cube|onion".split("|")
A_FRAMES = ["She saw .... {}.", "He talked about .... {}.", "They needed .... {}.", "We discussed .... {}."]


@T(C, "Articles")
def _(r):
    use_an = r.random() < .5
    w = r.choice(AN_WORDS if use_an else A_WORDS)
    return Q("Which indefinite article fits? " + r.choice(A_FRAMES).format(w), "an" if use_an else "a", f"The choice depends on the first sound of \"{w}\": {'a vowel sound takes an' if use_an else 'a consonant sound takes a'}.", ["a" if use_an else "an", "both a and an", "neither a nor an"])


DEFINITE = ["sun rises in the east|Only one exists", "Ganga is a holy river|Rivers take \"the\"", "Pacific is the largest ocean|Oceans take \"the\"", "Himalayas are in Asia|Mountain ranges take \"the\"", "moon goes round the earth|Only one exists", "richest man in town came|Superlatives take \"the\"", "best student won a prize|Superlatives take \"the\"", "first prize went to Asha|Ordinals take \"the\"", "Taj Mahal is in Agra|Famous monuments take \"the\"", "Netherlands is in Europe|Some plural country names take \"the\"", "Sahara is a vast desert|Deserts take \"the\"", "poor need our help|\"The\" with an adjective means a group", "Mahabharata is an epic|Well-known epics take \"the\"", "earth is round|Only one exists"]
NONE = ["She goes to bed at ten|\"Go to bed\" takes no article", "He plays cricket on Sundays|Sports take no article", "We have dinner at eight|Meals usually take no article", "Mount Everest is very high|A single mountain takes no article", "He speaks Hindi well|Language names take no article", "India is a large country|Most country names take no article", "Honesty is the best policy|An abstract idea takes no article here", "Delhi is the capital|City names take no article"]


@T(C, "Articles")
def _(r):
    s, why = r.choice(DEFINITE).split("|")
    return Q(f"Which article fits? .... {s}.", "The", why + ".", ["A", "An", "No article"])


@T(C, "Articles")
def _(r):
    s, why = r.choice(NONE).split("|")
    return Q(f"Does this sentence need an article added before its first noun? {s}.", "No article is needed", why + ".", ["Add a", "Add an", "Add the"])


PREPS = """She is interested .... music.|in
He is good .... chess.|at
The child is afraid .... the dark.|of
They are proud .... their daughter.|of
Asha is fond .... sweets.|of
He is tired .... waiting.|of
She is capable .... leading the team.|of
Are you aware .... the rule?|of
The jar is full .... water.|of
This model is similar .... that one.|to
He is addicted .... his phone.|to
She is married .... a pilot.|to
Who is responsible .... this error?|for
Agra is famous .... the Taj Mahal.|for
This film is suitable .... children.|for
Do not be late .... class.|for
Her answer is different .... mine.|from
He was absent .... school.|from
She suffers .... headaches.|from
It depends .... the weather.|on
They insisted .... paying.|on
You can rely .... her.|on
We congratulated him .... his win.|on
She believes .... hard work.|in
He succeeded .... passing.|in
We waited .... the bus.|for
Please listen .... the teacher.|to
This pen belongs .... Ravi.|to
He apologised .... the delay.|for
They laughed .... the joke.|at
Translate this .... French.|into
The cake was divided .... eight parts.|into
Water consists .... hydrogen and oxygen.|of
I prefer tea .... coffee.|to
She is jealous .... her sister.|of
He was accused .... theft.|of
Thank you .... your help.|for
She is keen .... learning French.|on
He is allergic .... nuts.|to
The room is filled .... smoke.|with
I am pleased .... the result.|with
He was charged .... murder.|with
She is good .... helping people, and everyone says so.|at
The ball rolled .... the sofa and vanished.|under
Divide it .... the two of them.|between
She was the tallest .... all the girls.|of
He jumped .... the wall and landed outside.|over
The train went .... a long tunnel.|through
The bird flew .... the window into the room.|through""".split("\n")
POOL = ["in", "on", "at", "of", "for", "with", "to", "from", "by", "into"]
ALSO_FINE = {"Do not be late": ("to",), "I am pleased": ("by", "at"), "Her answer is different": ("to",), "They laughed": ("with",), "He is good": ("in", "with"), "She is good": ("in", "with"), "He was charged": ("for",), "The room is filled": ("by",), "We waited": ("on",), "Divide it": ("to",)}
DAYS = "Monday Tuesday Wednesday Thursday Friday Saturday Sunday".split()
MONTHS = "January February March April May June July August September October November December".split()


@T(C, "Prepositions")
def _(r):
    s, a = r.choice(PREPS).split("|")
    # other prepositions that are also accepted here must not appear as wrong answers
    also_fine = next((v for k, v in ALSO_FINE.items() if s.startswith(k)), ())
    wrong = [p for p in POOL if p != a and p not in also_fine]
    r.shuffle(wrong)
    return Q(f"Choose the correct preposition: {s}", a, f"The standard usage here is \"{a}\".", wrong[:3])


@T(C, "Prepositions")
def _(r):
    k = r.randint(0, 4)
    if k == 0:
        return Q(f"Choose the correct preposition: The meeting is .... {r.choice(DAYS)}.", "on", "Days take \"on\".", ["in", "at", "of"])
    if k == 1:
        return Q(f"Choose the correct preposition: The exam is .... {r.choice(MONTHS)}.", "in", "Months take \"in\".", ["on", "at", "to"])
    if k == 2:
        return Q(f"Choose the correct preposition: We will meet .... {r.randint(1, 12)} p.m.", "at", "Clock times take \"at\".", ["on", "in", "of"])
    if k == 3:
        return Q(f"Choose the correct preposition: She has worked here .... {r.randint(2, 20)} years.", "for", "A length of time takes \"for\".", ["since", "from", "at"])
    return Q(f"Choose the correct preposition: She has worked here .... {r.randint(1990, 2020)}.", "since", "A starting point takes \"since\".", ["for", "from", "at"])


REFLEX = [("She", "herself"), ("He", "himself"), ("They", "themselves"), ("We", "ourselves"), ("I", "myself")]
ACTIONS = ["hurt", "blamed", "taught", "introduced", "praised", "reminded", "prepared", "calmed"]
POSSESS = [("she", "hers", ["her's", "she's", "shes"]), ("he", "his", ["he's", "hims", "his'"]), ("they", "theirs", ["their's", "they's", "theirs'"]), ("we", "ours", ["our's", "ours'", "we's"]), ("I", "mine", ["my's", "mines", "I's"])]
THINGS2 = ["book", "laptop", "bag", "seat", "idea", "phone", "pen", "plan"]


@T(C, "Pronouns")
def _(r):
    s, ans = r.choice(REFLEX)
    wrong = [x for _p, x in REFLEX if x != ans]
    r.shuffle(wrong)
    return Q(f"Choose the correct option: {s} {r.choice(ACTIONS)} .... after the event.", ans, "A reflexive pronoun refers back to the subject.", wrong[:3])


@T(C, "Pronouns")
def _(r):
    p, ans, wrong = r.choice(POSSESS)
    who = {"she": "her", "he": "him", "they": "them", "we": "us", "I": "me"}[p]
    return Q(f"Choose the correct option: The {r.choice(THINGS2)} belongs to {who}. It is .... .", ans, "Possessive pronouns take no apostrophe.", wrong)


@T(C, "Pronouns")
def _(r):
    name = r.choice(["Ravi", "Asha", "the manager", "my friend", "the coach", "our teacher"])
    prep = r.choice(["between", "with", "for", "to", "near", "behind"])
    if prep == "between":
        return Q(f"Choose the correct option: The task is shared between {name} and .... .", "me", "After a preposition, use the object form.", ["I", "my", "mine"])
    return Q(f"Choose the correct option: She came {prep} {name} and .... .", "me", "After a preposition, use the object form.", ["I", "my", "mine"])


@T(C, "Pronouns")
def _(r):
    n = r.choice(["woman", "man", "student", "singer", "driver", "doctor", "teacher", "engineer"])
    t = r.choice(["book", "car", "house", "phone", "bag", "plan"])
    k = r.randint(0, 3)
    if k == 0:
        return Q(f"Choose the correct option: The {n} .... helped you is here.", "who", "It is the subject of \"helped\".", ["whom", "whose", "which"])
    if k == 1:
        return Q(f"Choose the correct option: The {n} .... you met is here.", "whom", "It is the object of \"met\".", ["who's", "whose", "which"])
    if k == 2:
        return Q(f"Choose the correct option: The {n} .... {t} was lost is here.", "whose", "It shows possession.", ["who", "whom", "which"])
    return Q(f"Choose the correct option: The {t} .... you bought is new.", "which", "It refers to a thing.", ["who", "whom", "whose"])


CONTRAST = "She was tired, she kept working|He studied hard, he failed the test|It was raining, the match continued|The phone is old, it works well|He is rich, he lives simply|The road was empty, the bus was late|She was ill, she came to work|The room is small, it feels comfortable|The test was hard, many passed|He was late, nobody noticed|The food was cheap, it tasted good|She had no map, she found the way|The team was tired, it won the final|It was cold, they swam in the lake|The plan was risky, it worked|He is young, he leads the team|The work was boring, she finished it|The car is new, it broke down|We left early, we missed the train|The shop was closed, the lights were on".split("|")
REASON = "He stayed home, he had a fever|She took a taxi, she was late|They cancelled the match, it rained|We wore coats, it was cold|He failed, he did not study|The shop closed, the owner fell ill|She smiled, she got the job|I drank water, I was thirsty|The server crashed, it ran out of memory|He apologised, he had hurt her|We ran, the bus was leaving|The class ended early, the teacher was unwell|She saved money, she wanted a car|The price rose, demand was high|He slept, he was tired|The road closed, a bridge had collapsed|They moved, the rent had doubled|I called her, I needed help|The flight was delayed, the fog was thick|She left, the meeting had ended".split("|")
RESULT = "It was raining, we took an umbrella|He was hungry, he ordered food|The bus was late, she walked|The bug was serious, they fixed it first|The test is tomorrow, I am revising|It was dark, we turned on the lights|She was thirsty, she drank water|The shop was shut, we went home|He lost his key, he called a locksmith|The room was hot, she opened a window|The fee was high, few people joined|The road was closed, we took another route|It was late, they went to bed|He felt ill, he saw a doctor|The car was old, we sold it|The app was slow, users left|The sky was clear, we saw the stars|The pay was good, he took the job|She missed the train, she caught a bus|We had no milk, I went to the shop".split("|")
COND = "You will miss the bus, you hurry|You will fail, you study|He will not come, you invite him|The plant will die, you water it|I will not go, you come too|She will not sign, she reads it first|The app will not start, you restart it|You cannot enter, you have a ticket|We will lose, we practise|The door stays locked, you have the key|He will not speak, you ask him|You will not improve, you practise|I cannot help, you tell me the problem|The milk will spoil, you keep it cold|They will not pay, the work is done|You will get lost, you take a map|She will not agree, you explain|It will not work, you plug it in|He will not stop, you warn him|We cannot begin, everyone arrives".split("|")


@T(C, "Conjunctions")
def _(r):
    k = r.randint(0, 3)
    if k == 0:
        a, b = r.choice(CONTRAST).split(", ")
        return Q(f"Choose the correct option: {a}, .... {b}.", "but", "It shows contrast.", ["because", "so", "unless"])
    if k == 1:
        a, b = r.choice(REASON).split(", ")
        return Q(f"Choose the correct option: {a} .... {b}.", "because", "The second part gives the reason.", ["but", "although", "unless"])
    if k == 2:
        a, b = r.choice(RESULT).split(", ")
        return Q(f"Choose the correct option: {a}, .... {b}.", "so", "The second part is the result.", ["because", "unless", "although"])
    a, b = r.choice(COND).split(", ")
    return Q(f"Choose the correct option: {a} .... {b}.", "unless", "\"Unless\" means \"if not\".", ["because", "so", "although"])


DOERS = ["The teacher", "Ravi", "The team", "My sister", "The manager", "Asha", "The workers"]


@T(C, "Active & passive voice")
def _(r):
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    d = r.choice(DOERS)
    plural_doer = d == "The workers"
    plural_obj = obj.endswith("s") and obj not in ("the notes",) or obj == "the notes"
    be, was, has = ("are", "were", "have") if plural_obj else ("is", "was", "has")
    dhas = "have" if plural_doer else "has"
    dbe = "are" if plural_doer else "is"
    O = obj[0].upper() + obj[1:]
    agent = lower_first(d) if d not in ("Ravi", "Asha") else d
    tenses = [
        (f"{d} {past} {obj}", f"{O} {was} {pp} by {agent}"),
        (f"{d} {b if plural_doer else s3} {obj}", f"{O} {be} {pp} by {agent}"),
        (f"{d} will {b} {obj}", f"{O} will be {pp} by {agent}"),
        (f"{d} {dhas} {pp} {obj}", f"{O} {has} been {pp} by {agent}"),
        (f"{d} {dbe} {ing} {obj}", f"{O} {be} being {pp} by {agent}"),
        (f"{d} can {b} {obj}", f"{O} can be {pp} by {agent}"),
    ]
    i = r.randrange(len(tenses))
    act, pas = tenses[i]
    wrong = [t[1] for j, t in enumerate(tenses) if j != i]
    r.shuffle(wrong)
    if r.random() < .75:
        return Q(f"What is the passive voice of \"{act}\"?", pas, "Keep the same tense, and use a form of \"be\" plus the past participle.", wrong[:3])
    wrong = [t[0] for j, t in enumerate(tenses) if j != i]
    r.shuffle(wrong)
    return Q(f"What is the active voice of \"{pas}\"?", act, "The doer becomes the subject, and the tense stays the same.", wrong[:3])


REPORTERS = [("He", "he", "his"), ("She", "she", "her")]


@T(C, "Direct & indirect speech")
def _(r):
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    R, p, _h = r.choice(REPORTERS)
    forms = [
        (f"I {b} {obj} every day.", f"{p} {past} {obj} every day", "Present becomes past."),
        (f"I am {ing} {obj}.", f"{p} was {ing} {obj}", "Present continuous becomes past continuous."),
        (f"I {past} {obj}.", f"{p} had {pp} {obj}", "Past becomes past perfect."),
        (f"I will {b} {obj}.", f"{p} would {b} {obj}", "\"Will\" becomes \"would\"."),
        (f"I have {pp} {obj}.", f"{p} had {pp} {obj}", "Present perfect becomes past perfect."),
        (f"I can {b} {obj}.", f"{p} could {b} {obj}", "\"Can\" becomes \"could\"."),
    ]
    q, a, why = r.choice(forms)
    wrong = [f"I {b} {obj}", f"{p} will {b} {obj}", f"{p} {ing} {obj}", f"{p} is {ing} {obj}", f"{p} has {pp} {obj}"]
    r.shuffle(wrong)
    return Q(f"Change to indirect speech: {R} said, \"{q}\"", f"{R} said that {a}.", why, [f"{R} said that {w}." for w in wrong if w != a][:3])


@T(C, "Direct & indirect speech")
def _(r):
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    R, p, _h = r.choice(REPORTERS)
    k = r.randint(0, 3)
    if k == 0:
        return Q(f"Change to indirect speech: {R} said to me, \"{b.capitalize()} {obj}.\"", f"{R} told me to {b} {obj}.", "A command becomes \"told ... to\".", [f"{R} told me that {b} {obj}.", f"{R} said me {b} {obj}.", f"{R} told to me {ing} {obj}."])
    if k == 1:
        return Q(f"Change to indirect speech: {R} said to me, \"Do not {b} {obj}.\"", f"{R} told me not to {b} {obj}.", "A negative command takes \"not to\".", [f"{R} told me do not {b} {obj}.", f"{R} said not {b} {obj}.", f"{R} told me to not {ing} {obj}."])
    if k == 2:
        return Q(f"Change to indirect speech: {R} said to me, \"Did you {b} {obj}?\"", f"{R} asked me if I had {pp} {obj}.", "A yes/no question takes \"if\", and the past becomes past perfect.", [f"{R} asked me did I {b} {obj}.", f"{R} said me if I {b} {obj}.", f"{R} asked if did you {b} {obj}."])
    return Q(f"Change to indirect speech: {R} said to me, \"Please {b} {obj}.\"", f"{R} requested me to {b} {obj}.", "\"Please\" becomes \"requested ... to\".", [f"{R} said me please {b} {obj}.", f"{R} requested that {b} {obj}.", f"{R} told please to {ing} {obj}."])


OPENERS = ["Walking to the station", "Reading the notice", "Opening the door", "Finishing the report", "Climbing the stairs", "Crossing the road", "Looking out of the window", "Waiting for the bus", "After leaving the office", "While cooking dinner", "Running through the park", "After reading the email", "While checking the code", "Hearing the alarm", "Having eaten lunch", "Being late"]
DOERS2 = ["Ravi", "Asha", "the manager", "my sister", "the old man", "our teacher", "the driver"]
ACTS = ["noticed a stranger", "felt very tired", "made a phone call", "remembered the meeting", "saw a friend", "stopped for a moment"]
THINGS3 = ["the rain started suddenly", "the phone rang loudly", "a bag fell down", "the lights went out", "the door was locked", "a car was seen", "the file was deleted", "the sky turned dark"]


@T(C, "Modifiers")
def _(r):
    o, d, a = r.choice(OPENERS), r.choice(DOERS2), r.choice(ACTS)
    wrong = r.sample(THINGS3, 3)
    return Q("Which sentence has no dangling modifier?", f"{o}, {d} {a}.", f"The opening phrase must describe the subject right after the comma: {d} is doing it.", [f"{o}, {w}." for w in wrong])


@T(C, "Parallelism")
def _(r):
    x, y, z = r.sample(VERBS, 3)
    S = r.choice(["She", "He", "Ravi", "My friend"])
    v = r.choice(["enjoys", "likes", "is good at"])
    if v == "is good at":
        right = f"{S} is good at {x[4]}, {y[4]} and {z[4]}"
    else:
        right = f"{S} {v} {x[4]}, {y[4]} and {z[4]}"
    head = right.split(x[4])[0]
    return Q("Which sentence is parallel?", right + ".", "All the items use the same -ing form.", [f"{head}{x[4]}, to {y[0]} and {z[1]}.", f"{head}to {x[0]}, {y[4]} and {z[0]}.", f"{head}{x[1]}, {y[4]} and to {z[0]}."])


@T(C, "Parallelism")
def _(r):
    x, y, z = r.sample(VERBS, 3)
    S = r.choice(["The manager", "Our teacher", "The coach", "The trainer"])
    return Q("Which sentence is parallel?", f"{S} asked us to {x[0]} {x[5]}, to {y[0]} {y[5]} and to {z[0]} {z[5]}.", "All three actions are infinitives.", [f"{S} asked us to {x[0]} {x[5]}, {y[4]} {y[5]} and {z[0]} {z[5]}.", f"{S} asked us {x[4]} {x[5]}, to {y[0]} {y[5]} and {z[4]} {z[5]}.", f"{S} asked us to {x[0]} {x[5]}, {y[1]} {y[5]} and {z[4]} {z[5]}."])


ADJ = [("short", "shortly"), ("clear", "clearly"), ("quick", "quickly"), ("careful", "carefully"), ("honest", "honestly"), ("simple", "simply"), ("polite", "politely"), ("useful", "usefully"), ("neat", "neatly"), ("brave", "bravely"), ("kind", "kindly"), ("calm", "calmly")]


@T(C, "Parallelism")
def _(r):
    a, b, c = r.sample(ADJ, 3)
    n = r.choice(["The report", "The speech", "The answer", "Her work", "His letter", "The talk"])
    return Q("Which sentence is parallel?", f"{n} was {a[0]}, {b[0]} and {c[0]}.", "All three are adjectives.", [f"{n} was {a[0]}, {b[1]} and {c[0]}.", f"{n} was {a[1]}, {b[0]} and {c[0]}.", f"{n} was {a[0]}, {b[0]} and {c[1]}."])


UNCOUNT = ["information", "advice", "furniture", "luggage", "equipment", "scenery", "news", "machinery", "homework", "knowledge"]
COMPARE = [("tall", "taller"), ("fast", "faster"), ("small", "smaller"), ("strong", "stronger"), ("young", "younger"), ("old", "older"), ("cheap", "cheaper"), ("short", "shorter")]
REDUNDANT = [("discussed about", "discussed", "the plan", "\"Discuss\" takes no \"about\"."), ("returned back", "returned", "from Delhi", "\"Return\" already means \"back\"."), ("repeated again", "repeated", "the question", "\"Repeat\" already means \"again\"."), ("entered into", "entered", "the room", "\"Enter\" a room takes no \"into\"."), ("reached to", "reached", "the station", "\"Reach\" takes no \"to\"."), ("ordered for", "ordered", "the food", "\"Order\" takes no \"for\" here."), ("requested for", "requested", "a refund", "\"Request\" takes no \"for\".")]


def error_case(r):
    """-> (wrong sentence parts, index of the wrong part, right sentence, reason, other wrong rewrites)."""
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    S = r.choice(SG)
    P = r.choice(PL)
    k = r.randint(0, 6)
    if k == 0:
        return [f"{S} {b}", obj, "every day"], 0, f"{S} {s3} {obj} every day.", f"A singular subject needs \"{s3}\".", [f"{S} {ing} {obj} every day.", f"{S} has {b} {obj} every day.", f"{S} do {b} {obj} every day."]
    if k == 1:
        return [f"{P} {s3}", obj, "every day"], 0, f"{P} {b} {obj} every day.", f"A plural subject needs \"{b}\".", [f"{P} {ing} {obj} every day.", f"{P} is {b} {obj} every day.", f"{P} does {b} {obj} every day."]
    if k == 2:
        return [f"{S} did not {past if past != b else b + 's'}", obj, "yesterday"], 0, f"{S} did not {b} {obj} yesterday.", "After \"did not\", use the base form.", [f"{S} not did {b} {obj} yesterday.", f"{S} did not {ing} {obj} yesterday.", f"{S} did not {s3} {obj} yesterday."]
    if k == 3:
        u = r.choice(UNCOUNT)
        return [f"The {u}s", "you gave me", "were useful"], 0, f"The {u} you gave me was useful.", f"\"{u.capitalize()}\" is uncountable.", [f"The {u}s you gave me was useful.", f"A {u} you gave me were useful.", f"The {u} you gave me were usefully."]
    if k == 4:
        a, c = r.choice(COMPARE)
        return [S, f"is more {c}", "than the others"], 1, f"{S} is {c} than the others.", "Do not use \"more\" with a comparative ending in -er.", [f"{S} is most {c} than the others.", f"{S} is {a}er than of the others.", f"{S} is more {a}er than the others."]
    if k == 5:
        n = r.randint(2, 15)
        return [S, f"has worked here", f"since {n} years"], 2, f"{S} has worked here for {n} years.", "A length of time takes \"for\".", [f"{S} is working here since {n} years.", f"{S} worked here since {n} years.", f"{S} has working here from {n} years."]
    w, ok, rest, why = r.choice(REDUNDANT)
    return [S, w, rest], 1, f"{S} {ok} {rest}.", why, [f"{S} was {w} {rest}.", f"{S} {w} of {rest}.", f"{S} has {w} {rest}."]


@T(C, "Error spotting")
def _(r):
    parts, idx, right, why, _w = error_case(r)
    text = " / ".join(f"{p} ({'ABC'[i]})" for i, p in enumerate(parts))
    return Q(f"Find the part with an error: {text}.", "ABC"[idx], why, [x for x in ["A", "B", "C", "No error"] if x != "ABC"[idx]])


@T(C, "Error spotting")
def _(r):
    b, s3, past, pp, ing, obj = r.choice(VERBS)
    S = r.choice(SG)
    return Q(f"Find the part with an error: {S} {r.choice([s3 + ' ', 'has ' + pp + ' ']).strip()} (A) / {obj} (B) / this week (C).", "No error", "The sentence is correct.", ["A", "B", "C"])


@T(C, "Sentence correction")
def _(r):
    parts, idx, right, why, wrong = error_case(r)
    return Q(f"Improve this sentence: \"{' '.join(parts)}.\"", right, why, wrong)


POS = {
    "an adjective": ("The {} boy won the prize.", "tall|clever|young|quiet|brave|shy|happy|strong|polite|honest|lazy|lucky|kind|proud|calm|smart|gentle|funny|bold|cheerful"),
    "an adverb": ("She spoke {} at the meeting.", "softly|clearly|loudly|calmly|briefly|politely|slowly|quickly|boldly|sadly|angrily|gently|firmly|proudly|quietly|honestly|nervously|happily|wisely|bravely"),
    "a noun": ("The {} was new.", "table|car|house|phone|teacher|garden|school|bridge|window|machine|camera|library|office|bicycle|kitchen|market|shirt|laptop|road|printer"),
    "a verb": ("They {} every morning.", "run|sing|study|walk|swim|pray|read|dance|cook|exercise|practise|write|meet|work|jog|paint|argue|travel|shop|train"),
    "a preposition": ("The cat sat {} the table.", "on|under|near|beside|behind|below|by|underneath|above|against"),
    "a pronoun": ("{} arrived late.", "They|He|She|We|Everyone|Someone|Nobody|I|You"),
    "a conjunction": ("Tea {} coffee is fine.", "or|and"),
    "an interjection": ("{}! That was close.", "Wow|Oh|Oops|Ouch|Phew|Alas|Hurray|Hey"),
}


@T(C, "Parts of speech")
def _(r):
    kind = r.choice(list(POS))
    frame, words = POS[kind]
    w = r.choice(words.split("|"))
    wrong = [k for k in POS if k != kind]
    r.shuffle(wrong)
    return Q(f"In \"{frame.format(w)}\", the word \"{w}\" is ....", kind, f"Here \"{w}\" works as {kind}.", wrong[:3])
