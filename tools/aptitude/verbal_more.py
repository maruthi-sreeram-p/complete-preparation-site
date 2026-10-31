"""More vocabulary, sentence and comprehension questions. Wrong options come from other rows of the same list."""
from core import Q, T, hand

C = "Vocabulary"
ONE_WORD = """One who collects stamps|Philatelist
A doctor for children|Paediatrician
A doctor for the eyes|Ophthalmologist
A doctor for the skin|Dermatologist
A doctor for the heart|Cardiologist
A doctor for the teeth|Dentist
One who studies rocks|Geologist
One who studies stars|Astronomer
One who studies birds|Ornithologist
One who studies insects|Entomologist
One who studies the mind|Psychologist
One who makes maps|Cartographer
One who draws building plans|Architect
One who repairs shoes|Cobbler
One who sells flowers|Florist
One who sells medicines|Pharmacist
One who writes plays|Playwright
One who writes poems|Poet
One who rides horses|Equestrian
One who flies aircraft|Pilot
One who travels in space|Astronaut
One who looks after a building|Caretaker
One who gives money to good causes|Philanthropist
One who looks on the bright side|Optimist
One who expects the worst|Pessimist
One who thinks only of oneself|Egotist
One who lives alone and avoids people|Recluse
One who wanders from place to place|Nomad
One who eats only plants|Herbivore
One who eats only meat|Carnivore
One who eats both plants and meat|Omnivore
One who eats human flesh|Cannibal
One who does not drink alcohol|Teetotaller
One who cannot read or write|Illiterate
One who is new to a job|Novice
One who has retired from fighting|Veteran
One who pays rent|Tenant
One who owns rented property|Landlord
One who dies for a cause|Martyr
A person who leaves their country to live abroad|Emigrant
A person who enters a new country to settle|Immigrant
A person who gives evidence|Witness
Fear of closed spaces|Claustrophobia
Fear of foreigners|Xenophobia
Fear of spiders|Arachnophobia
Fear of open spaces|Agoraphobia
Government by one ruler with total power|Autocracy
Government by a king or queen|Monarchy
Government by priests|Theocracy
Government by the wealthy|Plutocracy
A place where dead bodies are kept|Mortuary
A place where birds are kept|Aviary
A place where fish are kept|Aquarium
A place where grain is stored|Granary
A place where wine is made|Winery
A place where orphans live|Orphanage
A place where coins are made|Mint
That which can be eaten|Edible
That which cannot be corrected|Incorrigible
That which cannot be heard|Inaudible
That which cannot be avoided|Inevitable
That which can catch fire easily|Inflammable
That which cannot be seen|Invisible
That which lasts for a very short time|Transient
A speech at a funeral|Eulogy
A speech by a character alone on stage|Soliloquy
A list of books used in a work|Bibliography
A yearly celebration|Anniversary""".split("\n")


@T(C, "One-word substitution")
def _(r):
    d, w = r.choice(ONE_WORD).split("|")
    others = [x.split("|")[1] for x in ONE_WORD if x.split("|")[1] != w]
    return Q(f"Choose one word for: {d}.", w, f"{w} means: {d.lower()}.", r.sample(others, 3))


IDIOMS = """A bolt from the blue|A complete surprise
A dime a dozen|Very common
Add fuel to the fire|Make a bad situation worse
At the eleventh hour|At the last moment
Barking up the wrong tree|Blaming or pursuing the wrong thing
Best of both worlds|Benefits of two different things
Bite off more than you can chew|Take on too much
Bury the hatchet|Make peace
By hook or by crook|By any means possible
Cry over spilt milk|Regret what cannot be undone
Cut corners|Do something cheaply or carelessly
Down in the dumps|Feeling sad
Face the music|Accept the consequences
Feel like a fish out of water|Feel uncomfortable in a new place
Get cold feet|Become nervous and back out
Give the benefit of the doubt|Believe someone without proof
Go the extra mile|Make more effort than expected
Hit the sack|Go to bed
In a nutshell|In a few words
Jump on the bandwagon|Join something popular
Keep at arm's length|Avoid getting close
Kill two birds with one stone|Achieve two aims with one action
Leave no stone unturned|Try every possible way
Miss the boat|Lose an opportunity
Off the cuff|Without preparation
On cloud nine|Extremely happy
On thin ice|In a risky position
Out of the blue|Unexpectedly
Pull someone's leg|Tease someone
Rain cats and dogs|Rain very heavily
Red-letter day|A very special day
See eye to eye|Agree with someone
Sit on the fence|Avoid taking sides
Steal someone's thunder|Take the attention from someone
Take with a pinch of salt|Doubt what is heard
The ball is in your court|It is your decision now
The last straw|The final problem that makes things unbearable
Throw in the towel|Give up
Turn a blind eye|Pretend not to notice
Under one's nose|Very close, yet unnoticed
Up in the air|Not yet decided
White elephant|A costly thing of no use
Wild goose chase|A hopeless search
Apple of one's eye|Someone very dear
Black sheep|One who brings shame on a group
Crocodile tears|False sorrow
Hard nut to crack|A difficult problem
Herculean task|A very hard job
Lion's share|The largest part
Nip in the bud|Stop something at an early stage
Once bitten, twice shy|Careful after a bad experience
Bed of roses|An easy, comfortable situation
Blow one's own trumpet|Boast about oneself
Burn one's boats|Leave no way back
Eat humble pie|Admit a mistake and apologise
Get the sack|Be dismissed from a job
Have a chip on one's shoulder|Hold a lasting resentment
In black and white|In writing
In the same boat|Sharing the same problem
Keep one's fingers crossed|Hope for a good result
Know the ropes|Understand how things work
Make ends meet|Earn just enough to live
Rome was not built in a day|Great things take time
Smell a rat|Suspect something is wrong
Spill over|Spread beyond limits
Tongue-tied|Unable to speak from shyness""".split("\n")


@T(C, "Idioms & phrases")
def _(r):
    i, m = r.choice(IDIOMS).split("|")
    others = [x.split("|")[1] for x in IDIOMS if x.split("|")[1] != m]
    return Q(f"What does \"{i}\" mean?", m, f"\"{i}\" means: {m.lower()}.", r.sample(others, 3))


FOREIGN = """A la carte|Ordering each dish separately
Ad infinitum|Going on forever
Ad nauseam|To a tiresome extent
Alter ego|A second self
Avant-garde|New and experimental
Bon voyage|Have a good journey
Bourgeois|Middle class in attitude
Carpe diem|Seize the day
Caveat emptor|Let the buyer beware
Coup d'etat|A sudden seizure of government
Cul-de-sac|A dead-end street
Deja vu|The feeling of having seen something before
Double entendre|A phrase with two meanings
En masse|All together, as a group
En passant|In passing
Ergo|Therefore
Et cetera|And so on
Ex gratia|Given as a favour, not by right
Ex officio|By virtue of one's office
Fait accompli|A thing already done
Femme fatale|A dangerously attractive woman
Habeas corpus|A right against unlawful detention
Hoi polloi|The common people
In camera|In private, away from the public
In toto|As a whole
Ipso facto|By that very fact
Laissez-faire|A policy of not interfering
Magnum opus|A person's greatest work
Mea culpa|My fault
Modus vivendi|An arrangement that lets parties coexist
Non sequitur|A statement that does not follow
Nouveau riche|People who have recently become rich
Par excellence|The best of its kind
Persona non grata|An unwelcome person
Post mortem|An examination after death
Prima facie|At first sight
Pro rata|In proportion
Quid pro quo|Something given in return
Raison d'etre|The reason for existing
Rendezvous|A meeting at an agreed place
RSVP|Please reply
Sine qua non|An essential condition
Sub judice|Under consideration by a court
Summa cum laude|With highest honours
Tete-a-tete|A private talk between two people
Terra firma|Solid ground
Tour de force|A remarkable achievement
Verbatim|Word for word
Vis-a-vis|In relation to
Viva voce|An oral examination
Wanderlust|A strong desire to travel
Zeitgeist|The spirit of the time
Gratis|Free of charge
Ad lib|Spoken without preparation
Annus horribilis|A terrible year
Au revoir|Goodbye for now
Blase|Unimpressed because of familiarity
Cause celebre|A controversial public issue
Cliche|An overused phrase
Connoisseur|An expert judge of taste
Debut|A first appearance
Encore|A call for a repeat performance
Entrepreneur|One who starts a business
Exempli gratia|For example
Id est|That is
In situ|In the original place
Nota bene|Note well
Sotto voce|In a quiet voice""".split("\n")


@T(C, "Foreign words & phrases")
def _(r):
    i, m = r.choice(FOREIGN).split("|")
    others = [x.split("|")[1] for x in FOREIGN if x.split("|")[1] != m]
    return Q(f"What does \"{i}\" mean?", m, f"\"{i}\" means: {m.lower()}.", r.sample(others, 3))


SPELL = """acquaintance acquaintence aquaintance acquaintanse
address adress addres addrress
aggressive agressive aggresive agresive
apparent apparant aparent apparrent
argument arguement argumant arguemant
atheist athiest atheest athaist
believe beleive belive beleve
benefit benifit benefitt benafit
bureaucracy bureacracy beurocracy burocracy
category catagory categorey cateogry
cemetery cemetary cemetry semetery
changeable changable chageable changeble
collectible collectable colectible collectibel
column colum collumn colomn
criticism criticisim critisism critcism
disappear dissapear disapear dissappear
disappoint dissapoint disapoint dissappoint
ecstasy ecstacy extasy ecstesy
exaggerate exagerate exagerrate exxagerate
existence existance existense exsistence
experience experiance expirience experence
fascinate facinate fasinate fascinait
foreign foriegn forein forign
friend freind frend frined
gauge guage gaige gaje
grammar grammer gramar grammor
harass harrass haras herass
height heighth hight heigth
hierarchy heirarchy hierachy hirearchy
humorous humourous humerous humarous
independent independant indipendent independint
intelligence inteligence intelligance intellegence
jewellery jewelery jewlery jewellry
judgement judgemint jugement judgemant
leisure liesure lesure leasure
liaison liason liasion leiason
lightning lightening litening lightnig
medicine medecine medicin medisine
millennium millenium milennium millenniem
miniature miniture minature minitiure
misspell mispell misspel missspell
noticeable noticable notisable noticeble
occasion ocassion occassion ocasion
parliament parliment parlament parlaiment
perseverance perseverence perserverance persaverance
possession posession possesion posesion
recommend reccommend recomend reccomend
schedule shedule scedule schedual
vegetable vegatable vegtable vegetible
sincerely sincerly sinceerly sincerley
truly truely trully truley""".split("\n")


@T(C, "Spelling check")
def _(r):
    a, x, y, z = r.choice(SPELL).split()
    return Q(f"Which spelling is correct: {a[0].upper()}...?", a, f"The standard spelling is \"{a}\".", [x, y, z])


CONFUSE = """accept|except|Please .... this small gift.|Everyone came .... Ravi.
access|excess|You need a pass to .... the lab.|An .... of salt is unhealthy.
allusion|illusion|The poem makes an .... to the Ramayana.|The magician created an .... of flying.
altar|alter|The couple stood before the .... .|We may .... the plan slightly.
beside|besides|She sat .... her friend.|.... maths, he teaches physics.
breath|breathe|Take a deep .... .|It is hard to .... at high altitude.
canvas|canvass|He painted on .... .|They went to .... for votes.
capital|capitol|Delhi is the .... of India.|The US Congress meets in the .... .
cite|site|Always .... your sources.|The building .... is closed.
coarse|course|This cloth feels .... .|She joined a Java .... .
compliment|complement|He paid her a .... on her speech.|The red wall will .... the sofa.
council|counsel|The town .... met today.|A lawyer can .... you on this.
desert|dessert|Camels cross the .... .|We had ice-cream for .... .
dual|duel|The car has .... airbags.|They fought a .... with swords.
elicit|illicit|The question did not .... an answer.|Police seized .... liquor.
emigrate|immigrate|Many left to .... from their country.|They chose to .... to Canada.
eminent|imminent|He is an .... scientist.|Rain looks .... , so hurry.
ensure|insure|Please .... the door is locked.|You should .... your car.
farther|further|The shop is .... than the park.|We need .... discussion.
formally|formerly|He was .... invited by letter.|She was .... a teacher.
hoard|horde|Do not .... food during shortages.|A .... of fans rushed in.
later|latter|I will call you .... .|Of tea and coffee, I prefer the .... .
lead|led|Pipes were once made of .... .|She .... the team last year.
moral|morale|The story has a clear .... .|The win raised the team's .... .
passed|past|She .... the exam.|We walked .... the school.
peace|piece|The treaty brought .... .|Have a .... of cake.
personal|personnel|This is my .... opinion.|All .... must wear badges.
precede|proceed|Lightning can .... thunder.|Please .... to gate four.
quiet|quite|Please keep .... in the library.|The film was .... good.
role|roll|She played the main .... .|Please .... the dough flat.
weather|whether|The .... is pleasant today.|I do not know .... he will come.
stationary|stationery|The bus stayed .... at the signal.|The shop sells pens and other .... .
vain|vein|All his efforts were in .... .|The nurse found a .... in his arm.
waist|waste|The belt fits her .... .|Do not .... water.""".split("\n")


@T(C, "Homonyms & confusables")
def _(r):
    row = r.choice(CONFUSE).split("|")
    a, b, s1, s2 = row
    (w, other, s) = r.choice([(a, b, s1), (b, a, s2)])
    extra = [x.split("|")[r.randint(0, 1)] for x in r.sample(CONFUSE, 3) if x.split("|")[0] != a][:2]
    return Q(f"Choose the correct word: {s}", w, f"\"{w}\" is right here; \"{other}\" has a different meaning.", [other] + extra + ["none of these"])


RELATIONS = {
    "a worker and what they use": "Carpenter:Saw Painter:Brush Tailor:Needle Writer:Pen Farmer:Plough Barber:Scissors Doctor:Stethoscope Chef:Knife Surgeon:Scalpel Gardener:Spade",
    "a young animal and its adult": "Puppy:Dog Kitten:Cat Calf:Cow Lamb:Sheep Foal:Horse Cub:Lion Chick:Hen Tadpole:Frog Fawn:Deer Duckling:Duck",
    "an animal and its home": "Bird:Nest Bee:Hive Lion:Den Horse:Stable Dog:Kennel Cow:Shed Pig:Sty Rabbit:Burrow Spider:Web Ant:Anthill",
    "a word and its opposite": "Hot:Cold Tall:Short Up:Down Early:Late Rich:Poor Wet:Dry Empty:Full Hard:Soft Open:Shut Near:Far",
    "a tool and what it measures": "Thermometer:Temperature Clock:Time Scale:Weight Ruler:Length Barometer:Pressure Speedometer:Speed Compass:Direction Hygrometer:Humidity Odometer:Distance Ammeter:Current",
    "a part and its whole": "Page:Book Wheel:Car Petal:Flower Finger:Hand Brick:Wall Leaf:Tree Key:Keyboard Screen:Phone Chapter:Novel Room:House",
    "a member and its group": "Soldier:Army Sheep:Flock Fish:School Cow:Herd Wolf:Pack Player:Team Bee:Swarm Actor:Cast Singer:Choir Student:Class",
    "a maker and what they make": "Author:Book Baker:Bread Composer:Music Sculptor:Statue Potter:Pot Tailor:Shirt Mason:Wall Cobbler:Shoe Poet:Poem Goldsmith:Ring",
    "a unit and its quantity": "Metre:Length Kilogram:Mass Second:Time Ampere:Current Volt:Potential Litre:Volume Watt:Power Joule:Energy Newton:Force Hertz:Frequency",
    "a country and its capital": "India:Delhi France:Paris Japan:Tokyo Egypt:Cairo Italy:Rome Spain:Madrid Russia:Moscow China:Beijing Nepal:Kathmandu Kenya:Nairobi",
}
REL = {k: [p.split(":") for p in v.split()] for k, v in RELATIONS.items()}


@T(C, "Word analogy")
def _(r):
    name = r.choice(list(REL))
    (a, b), (c, d) = r.sample(REL[name], 2)
    # wrong options of the same kind, so that the relation has to be applied exactly
    pool = [x[1] for x in REL[name] if x[1] not in (b, d)]
    return Q(f"{a} : {b} :: {c} : ?", d, f"The relation is {name}.", r.sample(pool, 3))


# =================================================================== sentences
C = "Sentence Structure & Flow"
FILL = """Although the task was hard, she finished it .... .|on time|never|badly|too late
The new policy will .... all employees from next month.|apply to|apologise to|argue with|hide from
He was .... for his honesty and received an award.|praised|punished|forgotten|ignored
The heavy rain .... the outdoor match.|delayed|improved|cooked|painted
Her .... attitude made her popular with the team.|friendly|hostile|rude|cold
The students were .... to hear the results, as they had worked hard.|eager|unwilling|asleep|angry
The doctor advised him to .... sugar.|avoid|collect|invent|worship
The software update .... several security bugs.|fixed|caused all|drew|sang
The old bridge was declared .... and closed to traffic.|unsafe|beautiful|cheap|empty
The company made a large .... last year and paid a bonus.|profit|loss|mistake|debt
He spoke so .... that nobody could hear him.|softly|loudly|clearly|boldly
She is .... in three languages and works as a translator.|fluent|silent|weak|absent
The price of gold has .... sharply this year, making it costly.|risen|dropped|melted|slept
The manager .... the meeting because many were absent.|postponed|enjoyed|painted|tasted
The garden looks .... after the rains, full of green leaves.|lush|dry|dead|grey
They .... the plan after finding a serious flaw.|abandoned|celebrated|cooked|praised
The witness gave a .... account, and the court believed it.|credible|false|funny|silly
We must .... water during the dry season.|conserve|waste|sell|burn
The noise was so loud that it .... my sleep.|disturbed|helped|improved|repaired
The new law aims to .... road accidents.|reduce|increase|celebrate|paint
Her .... explanation left no one confused.|clear|vague|confusing|missing
He .... his mistake and apologised at once.|admitted|denied|hid|sold
Good teachers .... curiosity in their students.|encourage|destroy|forbid|erase
The mountain path was .... , so we walked slowly.|steep|flat|easy|short
After months of practice, her skills greatly .... .|improved|vanished|fell|froze
The bank .... his loan as his income was too low.|rejected|approved|sang|enjoyed
The medicine should be kept .... the reach of children.|out of|inside|near|within
A .... diet includes fruit, vegetables and grains.|balanced|harmful|poor|empty
The team was .... by the loss but promised to return stronger.|disappointed|delighted|thrilled|amused
The fire spread quickly because the wood was .... .|dry|wet|cold|frozen
His speech was too .... , and many people left early.|long|short|brief|exciting
This phone is .... than the older model and costs less.|cheaper|costlier|heavier and dearer|rarer
She .... the exam on her first attempt and celebrated.|passed|failed|missed|skipped
The project needs careful .... before any money is spent.|planning|sleeping|singing|wasting
He felt .... after running ten kilometres.|exhausted|fresh|rested|cold
The river is .... here, so do not try to swim.|deep|dry|shallow|tiny
The judge listened .... to both sides.|patiently|rudely|angrily|never
The village has no hospital, so the sick must .... to the town.|travel|sing|sleep|write
The clouds .... , and the sun came out.|cleared|gathered|fell|cried
It was an .... decision, made without any thought.|impulsive|careful|planned|wise
The machine stopped because of a .... part.|faulty|new|strong|shiny
Exercise helps to .... stress.|relieve|create|increase|sell
The museum displays .... coins from the Mughal period.|ancient|modern|plastic|future
We need to .... the cost before we approve the plan.|estimate|forget|eat|paint
The children were .... by the magic show.|fascinated|bored|angered|hurt
She has a .... for languages and learnt French in a year.|talent|fear|hatred|dislike
His rude reply .... everyone in the room.|offended|pleased|fed|cured
The road is closed .... repairs.|for|by|of|at
Regular backups .... data loss.|prevent|cause|enjoy|invite
The result was .... : no one had expected it.|surprising|ordinary|usual|known
The rules are strict, and .... are punished.|violators|winners|guests|readers
The company will .... fifty new engineers this year.|hire|fire all|eat|sell
The candidate gave a .... answer and impressed the panel.|thoughtful|careless|rude|blank
The bridge was built to .... heavy trucks.|withstand|avoid|scare|repair
The team worked .... to finish before the deadline.|tirelessly|lazily|rarely|never
He is known for his .... and always tells the truth.|honesty|greed|anger|laziness
The two sides reached an .... after long talks.|agreement|argument|accident|illness
The app became .... , with millions of downloads.|popular|unknown|broken|rare
The storm left many families .... , without homes.|homeless|wealthy|cheerful|asleep
She .... the book on the table and left the room.|placed|sang|cooked|melted""".split("\n")
hand(C, "Fill in the blanks", [(f"Choose the best word: {r.split('|')[0]}", *r.split("|")[1:], "It alone fits the meaning of the sentence.") for r in FILL])

CLOZE = [
    ("Good sleep is (1) for health. Adults need about seven hours a night. Too little sleep (2) memory and mood. Keeping a regular (3) helps the body rest, and screens should be (4) before bedtime.",
     [("essential", "useless", "harmful", "rare"), ("affects", "repairs", "improves", "cures"), ("schedule", "argument", "colour", "price"), ("avoided", "bought", "repaired", "shared")]),
    ("Interviews can be stressful, but (1) helps. Candidates should research the company and (2) answers aloud. During the interview, it is better to (3) a question than to guess its meaning. A short thank-you note leaves a good (4).",
     [("preparation", "sleep", "luck alone", "silence"), ("practise", "forget", "hide", "sell"), ("clarify", "ignore", "burn", "avoid"), ("impression", "debt", "mistake", "shadow")]),
    ("Water covers most of the earth, yet clean water is (1). Rivers are polluted by waste from (2). Many cities now treat sewage before (3) it. Saving water at home also (4) the supply.",
     [("limited", "endless", "free", "useless"), ("factories", "clouds", "stars", "songs"), ("releasing", "drinking", "singing", "painting"), ("protects", "destroys", "hides", "wastes")]),
    ("A database stores data in an (1) way. Tables hold rows and columns, and queries (2) the data needed. An index makes searching (3), but adds work when writing. Backups (4) against data loss.",
     [("organised", "untidy", "unknown", "illegal"), ("fetch", "paint", "burn", "bury"), ("faster", "slower", "louder", "older"), ("protect", "cause", "invite", "enjoy")]),
    ("Solar panels turn sunlight into (1). Their prices have (2) greatly over ten years. Homes can reduce their bills, and extra power may be (3) to the grid. Panels work best when kept (4) and free of shade.",
     [("electricity", "water", "food", "paper"), ("fallen", "frozen", "sung", "grown teeth"), ("sold", "eaten", "drunk", "painted"), ("clean", "dirty", "covered", "broken")]),
    ("The first day at a new job can feel (1). It helps to arrive early and (2) questions. New staff should note names and take (3) of what they learn. Most colleagues are happy to (4).",
     [("overwhelming", "boring forever", "illegal", "impossible"), ("ask", "avoid", "hide", "steal"), ("notes", "naps", "money", "shoes"), ("help", "shout", "leave", "complain")]),
    ("Bees play a vital part in farming. They carry pollen between (1), which allows crops to grow. Their numbers are (2) because of pesticides and habitat loss. Farmers can help by planting (3) and reducing chemical (4).",
     [("flowers", "cars", "clouds", "houses"), ("falling", "singing", "rising fast", "cooking"), ("wildflowers", "plastic", "concrete", "machines"), ("use", "taste", "colour", "song")]),
    ("Public transport reduces traffic and (1). A full bus takes many cars off the road. For this to work, services must be (2) and affordable. If buses are late, people (3) to driving. Cities therefore (4) in better routes and timetables.",
     [("pollution", "rain", "mountains", "birds"), ("reliable", "broken", "invisible", "rare"), ("return", "sing", "sleep", "write"), ("invest", "sink", "melt", "laugh")]),
    ("Reading widely builds (1). It exposes readers to new words and ideas. Even fifteen minutes a day can make a (2) over a year. Readers should (3) books they enjoy, as this makes the habit easier to (4).",
     [("vocabulary", "muscles", "houses", "bridges"), ("difference", "mess", "storm", "noise"), ("choose", "burn", "hide", "fear"), ("maintain", "destroy", "forget", "sell")]),
    ("Version control tracks every (1) to a project. Developers work on separate branches and (2) their work when it is ready. If a bug appears, the team can go (3) to an earlier version. This makes teamwork far (4).",
     [("change", "holiday", "meal", "song"), ("merge", "bury", "cook", "burn"), ("back", "up the wall", "to sleep", "shopping"), ("safer", "harder", "louder", "older")]),
    ("Festivals bring (1) together. Families meet, share food and exchange gifts. Markets grow busy, which (2) local traders. However, crowds and noise can also cause (3), so towns must plan for safety and (4) waste afterwards.",
     [("communities", "machines", "planets", "rivers"), ("benefits", "harms only", "closes", "buries"), ("problems", "rainbows", "holidays", "profits only"), ("clear", "add", "sell", "cook")]),
    ("Cyber attacks are becoming more (1). Attackers often trick people rather than break systems. Strong passwords and two-step login (2) the risk. Companies should also train staff and (3) software up to date. Quick reporting can (4) the damage.",
     [("common", "colourful", "tasty", "ancient"), ("reduce", "raise", "paint", "sing"), ("keep", "throw", "burn", "hide"), ("limit", "increase", "enjoy", "invite")]),
    ("Learning to swim is a useful (1). It builds strength and could save a life. Beginners should learn in (2) water with a trained instructor. Practice gives (3), and fear slowly fades. Safety rules must always be (4).",
     [("skill", "disease", "debt", "fear"), ("shallow", "deep", "boiling", "frozen"), ("confidence", "sickness", "anger", "debts"), ("followed", "broken", "eaten", "hidden")]),
    ("Online shopping has changed retail. Buyers can compare (1) in seconds and read reviews. Yet they cannot touch the goods, and returns can be (2). Fake reviews are another problem, so buyers should (3) sellers carefully before they (4).",
     [("prices", "rivers", "clouds", "songs"), ("difficult", "delicious", "musical", "tall"), ("check", "ignore", "feed", "paint"), ("pay", "swim", "fly", "bake")]),
]
rows = []
for passage, blanks in CLOZE:
    for i, (a, x, y, z) in enumerate(blanks):
        rows.append((f"Passage: {passage}\n\nWhich word best fits blank ({i + 1})?", a, x, y, z, "It alone fits the grammar and the meaning of the passage."))
hand(C, "Cloze test", rows)

PARAS = [
    ["Ravi woke up late.", "He rushed to the station.", "The train had already left.", "So he took a bus to the office."],
    ["First, collect the requirements.", "Next, design the system.", "Then, write and test the code.", "Finally, deploy it to production."],
    ["Water evaporates from the sea.", "It rises and forms clouds.", "The clouds cool down.", "Rain then falls back on the earth."],
    ["The company launched a new phone.", "Customers rushed to buy it.", "Stocks ran out within days.", "The company then raised production."],
    ["A seed is planted in the soil.", "It absorbs water and swells.", "A small shoot appears above ground.", "Over time it grows into a plant."],
    ["A customer places an order.", "The payment is verified.", "The warehouse packs the item.", "A courier delivers it."],
    ["The alarm rang at midnight.", "The guards searched the building.", "They found an open window.", "The police were then called."],
    ["She applied for the job.", "She was called for an interview.", "She answered the questions well.", "She received an offer a week later."],
    ["Mix the flour and water.", "Knead it into a dough.", "Roll it into flat circles.", "Cook them on a hot pan."],
    ["A user reported the bug.", "A developer reproduced it.", "The cause was found and fixed.", "The fix went out in the next version."],
    ["Heavy rain fell for three days.", "The river rose quickly.", "Nearby fields were flooded.", "Farmers lost their crops."],
    ["He saved money for two years.", "He then bought a small shop.", "The business slowly grew.", "Today he owns three stores."],
    ["The bell rang for the exam.", "Students took their seats.", "The papers were handed out.", "Everyone began writing."],
    ["The plane reached the runway.", "The engines grew louder.", "It raced forward and lifted off.", "Soon the city looked tiny below."],
    ["The team lost its first match.", "The coach changed the training.", "Players grew much fitter.", "They went on to win the league."],
    ["A fire started in the kitchen.", "The smoke alarm went off.", "The family ran outside.", "Firefighters soon put out the flames."],
    ["The farmer ploughed the field.", "He sowed the wheat in winter.", "The crop ripened by spring.", "Then it was harvested and sold."],
    ["A student borrowed a book.", "She forgot to return it.", "The library sent her a reminder.", "She returned it and paid a small fine."],
    ["The city faced traffic jams.", "Planners studied the busy roads.", "A new metro line was built.", "Travel times fell sharply."],
    ["The startup built a simple app.", "A few users tried it.", "Their feedback shaped new features.", "Downloads then began to grow."],
    ["Clouds gathered in the afternoon.", "The wind grew stronger.", "Lightning lit up the sky.", "Then the storm broke."],
    ["He felt a sharp pain in his tooth.", "He booked a dentist's appointment.", "The dentist found a cavity.", "It was filled, and the pain stopped."],
    ["A letter is written and sealed.", "It is posted in a letter box.", "The post office sorts it.", "A postman delivers it."],
    ["The server began to slow down.", "Engineers checked the metrics.", "They found a memory leak.", "A patch fixed the problem."],
    ["Milk is collected from farms.", "It is heated to kill germs.", "It is packed in clean cartons.", "Trucks carry it to the shops."],
    ["She joined a gym in January.", "At first, exercise felt very hard.", "Slowly her strength increased.", "By June she ran her first race."],
    ["The children found a lost puppy.", "They looked for its owner.", "A neighbour recognised it.", "The puppy was soon back home."],
    ["The government announced an election.", "Parties chose their candidates.", "Citizens cast their votes.", "The results were declared days later."],
    ["Cotton is picked from the fields.", "It is spun into thread.", "The thread is woven into cloth.", "Tailors then make it into clothes."],
    ["He forgot his password.", "He clicked the reset link.", "A code arrived on his phone.", "He then set a new password."],
    ["The ship left the harbour at dawn.", "By noon, a storm had begun.", "The captain changed course.", "The ship reached port safely next day."],
    ["The artist bought a blank canvas.", "She sketched a village scene.", "She added colour over many days.", "The finished painting won a prize."],
    ["The volcano had been quiet for years.", "Small earthquakes began to occur.", "Villagers were moved to safety.", "Days later, it erupted."],
    ["A new teacher joined the school.", "She was nervous on the first day.", "The students welcomed her warmly.", "Soon she felt at home."],
    ["The shop raised its prices.", "Customers moved to a rival.", "Sales fell for three months.", "The owner then cut prices again."],
    ["Grapes are picked in autumn.", "They are crushed for their juice.", "The juice ferments in tanks.", "The wine is later bottled."],
    ["A boy found a wallet on the road.", "It held money and an address.", "He took it to the owner.", "The grateful owner thanked him."],
    ["The company adopted a new tool.", "Staff were trained to use it.", "Work became much faster.", "Other teams then adopted it too."],
    ["The bridge was found to have cracks.", "Engineers closed it for checks.", "Repairs took three months.", "It then reopened to traffic."],
    ["The rover landed on Mars.", "It sent back its first pictures.", "Scientists studied the rocks.", "They found signs of ancient water."],
]
LABELS = "ABCD"


@T(C, "Para jumbles")
def _(r):
    s = r.choice(PARAS)
    order = list(range(4))
    while order == [0, 1, 2, 3]:
        r.shuffle(order)
    shown = "\n".join(f"- {LABELS[i]}. {s[order[i]]}" for i in range(4))
    right = "".join(LABELS[order.index(k)] for k in range(4))
    wrong = set()
    while len(wrong) < 3:
        w = "".join(r.sample(LABELS, 4))
        if w != right:
            wrong.add(w)
    return Q(f"Arrange these sentences in a logical order:\n\n{shown}", right, "The correct sequence is: " + " ".join(s), sorted(wrong))


@T(C, "Sentence insertion")
def _(r):
    i = r.randrange(len(PARAS))
    s = PARAS[i]
    k = r.choice([1, 2])
    gap = " ".join(s[:k] + ["(blank)"] + s[k + 1:])
    others = [p[j] for n, p in enumerate(PARAS) if n != i for j in (1, 2)]
    return Q(f"Which sentence best fills the blank?\n\n{gap}", s[k], "It links what comes before to what comes after.", r.sample(others, 3))


# paragraphs on related subjects: a sentence from one could fit in another, so they are never mixed
SIMILAR = [{4, 8, 10, 16, 24, 28, 35}, {1, 9, 19, 23, 29, 37}, {7, 12, 17, 33}, {0, 13, 18, 30, 38}, {15, 20, 32, 38}]


@T(C, "Odd sentence out")
def _(r):
    i, j = r.sample(range(len(PARAS)), 2)
    while any(i in g and j in g for g in SIMILAR):
        i, j = r.sample(range(len(PARAS)), 2)
    s = PARAS[i][:]
    odd = r.choice(PARAS[j])
    pos = r.randint(1, 3)
    s[pos] = odd
    shown = "\n".join(f"- {LABELS[n]}. {x}" for n, x in enumerate(s))
    return Q(f"Which sentence does not belong in this paragraph?\n\n{shown}", LABELS[pos], f"Sentence {LABELS[pos]} is unrelated to the others.", [x for x in LABELS if x != LABELS[pos]])


# =================================================================== comprehension
C = "Comprehension"
PASSAGES = [
    ("Mangroves are trees that grow in salty coastal water. Their tangled roots slow waves and hold soil in place, which protects coasts during storms. They also shelter young fish. Yet large areas have been cleared for shrimp farms and buildings. Some countries are now replanting them, because this often costs less than building sea walls.",
     [("Where do mangroves grow?", "In salty coastal water", "On high mountains", "In dry deserts", "In city parks"), ("How do they protect coasts?", "Their roots slow waves and hold soil", "They block all rain", "They raise sea levels", "They repel fish"), ("Why were they cleared?", "For shrimp farms and buildings", "Because they spread disease", "To make paper only", "To create deserts"), ("Why replant them?", "It often costs less than sea walls", "They grow gold", "It stops all storms", "It removes all fish"), ("\"Shelter\" here means", "Protect", "Sell", "Eat", "Move"), ("A suitable title is", "Mangroves: Natural Coastal Guards", "How to Farm Shrimp", "Sea Walls Are Best", "Life in the Desert")]),
    ("Many users click \"accept\" without reading privacy terms. These documents are long and full of legal language. Regulators in some countries now require clearer wording. Researchers found that short summaries help people understand their choices, but only if the options are real and easy to change.",
     [("Why do users skip privacy terms?", "They are long and full of legal language", "They are banned", "They are always short", "They cost money"), ("What do some regulators require?", "Clearer wording", "Longer documents", "No terms at all", "Paper copies only"), ("What did researchers find?", "Short summaries help understanding", "Nobody reads anything ever", "Summaries always confuse", "Legal language is simplest"), ("What condition is added?", "The options must be real and easy to change", "Summaries must be in verse", "Users must pay", "Apps must close"), ("The passage is mainly about", "Making privacy terms understandable", "How to write contracts for houses", "Why apps are free", "How to hack accounts"), ("The tone is", "Informative", "Mocking", "Angry", "Romantic")]),
    ("The printing press spread books across Europe from the fifteenth century. Before it, books were copied by hand and were costly. Cheaper books meant more people learnt to read, and ideas travelled faster. Rulers and religious authorities sometimes tried to control printing, but with limited success.",
     [("How were books made earlier?", "Copied by hand", "Printed by computer", "Carved in stone only", "Dictated by radio"), ("What resulted from cheaper books?", "More people learnt to read", "Fewer readers", "No new ideas", "Higher book prices"), ("Who tried to control printing?", "Rulers and religious authorities", "Farmers", "Sailors", "Students"), ("How successful were they?", "Only partly", "Fully", "They banned it forever", "They never tried"), ("\"Costly\" means", "Expensive", "Heavy", "Rare in size", "Old"), ("The main idea is that the press", "Widened access to books and ideas", "Was a failure", "Made books costlier", "Ended reading")]),
    ("Good code review is about the code, not the coder. Reviewers should explain why a change is needed and separate must-fix issues from preferences. Authors should keep changes small, as large ones get weaker reviews. When reviews are done well, teams find bugs earlier and share knowledge.",
     [("What should reviews focus on?", "The code, not the coder", "The coder's character", "Only style", "Office politics"), ("What should reviewers explain?", "Why a change is needed", "Their salaries", "Their holidays", "Nothing"), ("Why keep changes small?", "Large ones get weaker reviews", "Small ones are banned", "Reviewers like long ones", "Big changes have no bugs"), ("What are two benefits?", "Earlier bugs found and shared knowledge", "Fewer staff and no tests", "Longer meetings and more bugs", "No need to code"), ("\"Preferences\" here means", "Personal choices", "Serious errors", "Customers", "Deadlines"), ("The writer's purpose is to", "Advise on doing reviews well", "Attack reviewers", "Tell a story", "Sell a tool")]),
    ("Glaciers store much of the world's fresh water. As temperatures rise, many are shrinking. In the short term, this can increase river flow. Over time, however, smaller glaciers mean less water in dry seasons for the millions who rely on them, and sudden floods from glacial lakes are a growing risk.",
     [("What do glaciers store?", "Fresh water", "Oil", "Salt only", "Gold"), ("What happens in the short term?", "River flow may increase", "Rivers vanish", "Lakes freeze for good", "Rain stops"), ("What is the long-term problem?", "Less water in dry seasons", "Too many glaciers", "More ice each year", "Cooler rivers everywhere"), ("Which risk is growing?", "Floods from glacial lakes", "Volcanoes", "Earthquakes in deserts", "Forest growth"), ("\"Shrinking\" means", "Getting smaller", "Getting colder", "Moving faster", "Turning blue"), ("The best title is", "Shrinking Glaciers and Water Supply", "How to Ski", "The Coldest Cities", "Rivers of Gold")]),
]
rc = []
for passage, qs in PASSAGES:
    for q, a, x, y, z in qs:
        rc.append((f"**Passage.** {passage}\n\n**Question.** {q}", a, x, y, z, "The passage supports this answer."))
hand(C, "Reading comprehension", rc)

SUMMARY = """Night shifts disturb the body clock. Workers on them sleep less and face more health problems. Regular schedules and rest days can reduce this harm.|Night shifts harm health, but schedules and rest can help|Night shifts are healthier than day shifts
Many apps ask for more data than they need. This raises privacy risks if they are hacked. Users should review permissions regularly.|Review app permissions, as excess data creates risk|Apps never collect data
A good diet is not about banning foods. It relies on balance, variety and moderate portions. Extreme diets are rarely sustained.|Balance and moderation work better than extreme diets|All foods should be banned
Rural broadband can bring telemedicine and online classes to villages. But laying cables is costly, so subsidies are often needed.|Rural broadband is valuable but often needs subsidies|Villages do not need broadband
Teams that write down decisions avoid repeating old debates. New members also learn why things are done a certain way.|Recording decisions saves time and helps new members|Writing things down wastes time
Public libraries lend more than books. Many offer internet access, job help and children's programmes, especially in poorer areas.|Libraries provide many community services|Libraries only lend books
Antibiotics do not work on viruses. Overuse helps bacteria become resistant, making infections harder to treat.|Overusing antibiotics breeds resistance, and they do not treat viruses|Antibiotics cure every virus
Traffic rules save lives only when enforced. Cameras and fines change behaviour more than signs alone.|Enforcement makes traffic rules effective|Signs alone are enough
Small businesses often fail because of poor cash flow, not low sales. Careful tracking of money coming in and out is essential.|Cash-flow control is vital for small businesses|Small businesses only need more sales
Learning a language is easier with daily practice. Short sessions work better than rare long ones. Speaking early builds confidence.|Short daily practice and early speaking help language learning|Long rare sessions work best
Stray plastic breaks into tiny pieces that enter the food chain. Scientists have found them in fish and even in drinking water.|Plastic fragments are entering food and water|Plastic disappears harmlessly
Flexible working can raise loyalty and productivity. But it needs clear goals and good communication to succeed.|Flexible work helps when goals and communication are clear|Flexible work always fails
Logging helps engineers understand failures. But too many logs raise costs and hide useful signals. Teams should log what matters.|Log what matters, as too much is costly and noisy|Logging has no cost
Hand-me-down clothes and repair cafes extend the life of goods. This reduces waste and saves money for families.|Reusing and repairing goods cuts waste and costs|New goods always save money
Earthquakes cannot be predicted precisely. So cities focus on strong building codes and drills to limit damage.|As prediction is unreliable, cities prepare to limit damage|Earthquakes are predicted exactly
Children learn from what they see. Parents who read at home often raise children who read too.|Children tend to copy their parents' reading habits|Children ignore their parents
Meetings without an agenda tend to wander. A clear goal and a time limit make them shorter and more useful.|Agendas and time limits improve meetings|Meetings need no goals
Urban trees reduce heat and improve air. They need care in early years, so planting alone is not enough.|Urban trees help cities, but they need ongoing care|Planting alone is enough
Scam calls often pretend to come from banks. Banks do not ask for passwords, so such calls should be reported.|Bank-style scam calls should be reported, as banks never ask for passwords|Share passwords with callers
Vaccination protects individuals and those around them. High coverage makes outbreaks far less likely.|High vaccination coverage protects whole communities|Vaccines protect nobody else
Too much choice can make buyers anxious. Shops that offer fewer options sometimes sell more.|Fewer options can raise sales by easing choice|More options always sell more
Tests catch regressions, but only if they run often. Teams therefore run them on every change.|Running tests on every change catches regressions|Tests should run once a year
Crop rotation keeps soil fertile. Different crops use and return different nutrients, and pests are disrupted.|Rotating crops protects soil and disrupts pests|One crop forever is best
Sitting for hours harms the back and the heart. Short walking breaks reduce the damage.|Short breaks reduce the harm of long sitting|Sitting is good for the heart
Tourism brings income but can damage fragile places. Limits on visitors can protect them while still earning money.|Limits let tourism earn money without harming places|Tourism has no downsides
Mentors speed up learning at work. They share unwritten knowledge and help new staff avoid common mistakes.|Mentors help new staff learn faster|Mentors slow new staff down
Dams store water and create power, but they can displace people and harm rivers. Their costs and benefits must be weighed.|Dams bring benefits and costs that must be weighed|Dams have only benefits
Plain language makes government forms easier. Fewer people make errors, and offices spend less time correcting them.|Plain language saves effort for citizens and offices|Complex forms reduce errors
Cats were kept by early farmers because they hunted rats in grain stores. Over time they became house pets.|Cats moved from pest control to being pets|Cats were first kept for milk
Software estimates are often too low. Breaking work into small tasks and tracking past results improves them.|Smaller tasks and past data improve estimates|Estimates are always accurate
Street food provides cheap meals and jobs, but hygiene varies. Training vendors and providing clean water can improve safety.|Street food is valuable, and training can make it safer|Street food should be banned
Forests store carbon and hold soil. When they are cut, the carbon is released, and floods become more common.|Cutting forests releases carbon and raises flood risk|Cutting forests prevents floods
Sharing a screen is not the same as teaching. New learners improve most when they do the task themselves.|Learners improve most by doing the task themselves|Watching is always the best way
Clean cooking stoves reduce smoke indoors. This lowers lung disease, especially among women and children.|Clean stoves reduce indoor smoke and disease|Indoor smoke is harmless
Electric scooters are cheap to run. But batteries need safe charging, and poor charging habits have caused fires.|E-scooters are cheap but need safe charging|Charging scooters has no risk
Honest feedback helps people grow, if given kindly and specifically. Vague praise teaches little.|Specific, kind feedback works better than vague praise|Vague praise teaches the most
The stock market rises and falls in the short term. Investors often lose by reacting to every change.|Reacting to short-term moves often costs investors|Daily trading always wins
Bats eat large numbers of insects each night. Farmers benefit, as they need fewer pesticides.|Bats help farmers by eating insects|Bats harm all crops
Group projects teach communication, but unequal effort can cause resentment. Clear roles reduce this problem.|Clear roles make group projects fairer|Group projects teach nothing
Good maps once took years to make. Satellites now update them quickly, and phones put them in every pocket.|Satellites and phones made maps fast and widely available|Maps have become harder to get
Noise pollution affects sleep and stress levels. Cities are adding quieter road surfaces and limits on night traffic.|Cities are tackling noise because it harms health|Noise has no effect on health
Old phones contain valuable metals. Recycling recovers these and prevents toxic waste, yet most phones are never recycled.|Recycling old phones recovers metals and avoids toxins, but is rare|Most phones are recycled
A clear error message saves users time. It should say what went wrong and what to do next.|Good error messages explain the problem and the next step|Error messages should say nothing
Kitchen waste can become compost. It enriches soil and reduces what goes to landfill.|Composting enriches soil and cuts landfill|Compost harms soil
Clean air laws have saved many lives. Though industry feared the costs, health gains have far outweighed them.|Clean air laws brought health gains above their costs|Clean air laws only hurt health
Children who play outside tend to have better eyesight. Daylight seems to slow short-sightedness.|Outdoor play may protect children's eyesight|Daylight harms eyesight
Rewriting software from scratch is tempting, but risky. Old code holds fixes for many hidden problems. Gradual change is usually safer.|Gradual change is usually safer than a full rewrite|Always rewrite from scratch
Railways moved goods faster than carts. New towns grew around stations, and trade expanded.|Railways sped up trade and created towns|Railways slowed trade
Reading labels helps shoppers avoid hidden sugar. Many foods that look healthy contain a lot of it.|Labels reveal hidden sugar in foods|Healthy-looking foods have no sugar
Free online courses reach millions, but few finish them. Deadlines and peer groups improve completion.|Deadlines and peers help people finish online courses|Everyone completes online courses
Coastal towns are building sea walls and raising houses. Rising seas make such changes more urgent each year.|Rising seas are pushing coastal towns to adapt|Sea levels are falling
Volunteers keep many charities running. Yet they need training and thanks if they are to stay.|Charities must train and value volunteers to keep them|Volunteers need no support
Strong passwords help, but reuse undoes the benefit. One leak can then open many accounts.|Password reuse undermines strong passwords|Reusing passwords is safest
Elephants need wide ranges. As forests shrink, they enter farms, and conflict with people rises.|Shrinking habitat drives conflict between elephants and people|Elephants prefer small spaces
Short videos hold attention, but may weaken deep reading. Schools are trying to balance both.|Schools are balancing short videos and deep reading|Short videos have no effect on reading
A cold start slows the first request to a server. Keeping instances warm reduces delay, but costs more.|Warm instances cut delay at higher cost|Cold starts make servers faster
Local languages help young children learn. Lessons in the mother tongue improve understanding in the early years.|Early lessons in the mother tongue help understanding|Young children learn best in foreign languages only
Wetlands filter water and absorb floods. Many have been drained for building, with costly results.|Draining wetlands removes valuable natural protection|Wetlands cause floods
Good lighting reduces eye strain at work. Natural light also seems to lift mood.|Good and natural light helps eyes and mood|Dim light is best for work
Queues absorb bursts of traffic in software. But if they grow without limit, delays and failures follow.|Queues smooth traffic but must be kept bounded|Queues can grow forever safely
Handwritten notes may aid memory. Writing slowly forces the brain to summarise.|Handwriting notes may help memory through summarising|Typing is proven useless
Ports are becoming automated. This raises efficiency but changes jobs, so workers need retraining.|Automated ports need retrained workers|Automation changes no jobs
Community gardens supply fresh food and bring neighbours together. They also make empty land useful.|Community gardens offer food, connection and use of land|Gardens divide neighbours
Backups stored in one place can all be lost together. A copy in a separate location protects against disasters.|Keep a backup in a separate location|One location is safest for backups
Teaching others is a strong way to learn. Explaining a topic reveals gaps in one's knowledge.|Teaching reveals gaps and strengthens learning|Teaching stops learning""".split("\n")


@T(C, "Paragraph summary")
def _(r):
    i = r.randrange(len(SUMMARY))
    p, a, trap = SUMMARY[i].split("|")
    others = [SUMMARY[j].split("|")[1] for j in r.sample(range(len(SUMMARY)), 6) if j != i][:2]
    return Q(f"Which is the best summary?\n\n{p}", a, "It captures the main point; the others contradict the passage or are about something else.", [trap] + others)


FLAWS = {
    "It attacks the person, not the argument": "He is lazy, so his plan must be wrong|Do not trust her report, as she failed maths in school|You are too young, so your point is invalid|He dresses badly, so his design is poor|She is rude, so her numbers are wrong|He comes from a small town, so his idea cannot work|She once made a mistake, so nothing she says is right|He is not an expert, so his simple arithmetic is wrong|They only want money, so their test results are false",
    "Popularity does not prove quality": "Everyone uses this app, so it must be secure|This film is number one, so it must be the best ever|All my classmates chose this course, so it is right for me|Millions buy it, so it must be healthy|Everyone believes it, so it must be true|The whole office uses it, so it cannot have bugs|It trends online, so it must be correct|Most people voted for it, so it must be a fact|Everybody is investing in it, so it must be safe",
    "It generalises from too few cases": "My two friends failed, so this exam is impossible|I met one rude waiter, so people in that city are rude|One user complained, so the whole app is broken|The first two days were hot, so this whole year will be hot|My cousin got rich from it, so anyone can|I tried one Java book and it was bad, so all are bad|One test passed, so the program has no bugs|Our last intern was late, so all interns are late|This bus was late today, so the service is always late",
    "It offers only two choices when more exist": "Either we rewrite everything or the company fails|You are either with us or against us|We must raise fees or close the school|Use microservices or never scale|Either you work weekends or you do not care|Buy this now or lose forever|We either ban cars or live with pollution|Study all night or fail the test|Hire ten people or miss all deadlines",
    "It assumes an extreme chain of events": "If we allow one late submission, soon nobody will submit at all|If one student uses a phone, the school will collapse|Skip one class, and you will end up with no career|If we fix one small bug late, all deadlines will vanish|Allow one exception and all rules will end|If prices rise once, everyone will soon be homeless|Let one person work from home and the office will empty|Eat one sweet and you will lose all your health|Change one line, and the entire project will die",
    "It relies on an irrelevant authority": "A film star uses this bank, so it is the safest|A cricketer recommends this medicine, so it works|A famous singer says the economy will boom|My favourite actor says this code editor is best|A chef says this tax law is unfair, so it must be|An influencer says this vaccine is unsafe|A famous poet says the bridge design is flawed|A footballer says this database is the fastest|A model says this diet cures disease",
    "Its reason merely repeats its claim": "This is the best plan because no plan is better|He is reliable because he can be relied on|The law is right because it is just|It is true because it is not false|This code is clean because it is tidy|The team won as it scored more than the other team, so it is the winner|She is a great leader since she leads greatly|It is expensive because it costs a lot|The book is boring because it is dull",
    "One example does not outweigh wider evidence": "My grandfather smoked and lived to ninety, so smoking is harmless|I never wear a helmet and am fine, so helmets are pointless|My neighbour never studied and got rich, so study is useless|I drove fast for years without a crash, so speed is safe|My friend skipped vaccines and stayed well, so vaccines do nothing|I never backed up my files and lost nothing, so backups are useless|One person won the lottery, so it is a sound plan|My aunt eats only sweets and is fine, so sugar is safe|That startup succeeded with no tests, so tests are unnecessary",
}
FLAW_ROWS = [(k, s) for k, v in FLAWS.items() for s in v.split("|")]


@T(C, "Critical reasoning (verbal)")
def _(r):
    flaw, s = r.choice(FLAW_ROWS)
    return Q(f"\"{s}.\" What is the main flaw in this reasoning?", flaw, f"{flaw}.", r.sample([k for k in FLAWS if k != flaw], 3))
