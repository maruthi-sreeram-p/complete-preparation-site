"""Verbal ability: English questions need a human eye, so they are written by hand; only their order and options are generated."""
from core import Q, T, hand

C = "Grammar"


def fill(topic, chapter, rows):
    """rows: (sentence with ...., answer, three wrong words, reason)."""
    hand(chapter, topic, [(f"Choose the correct option: {s}", a, x, y, z, why) for s, a, x, y, z, why in rows])


fill("Parts of speech", C, [
    ("In \"She runs quickly\", the word \"quickly\" is ....", "an adverb", "an adjective", "a noun", "a verb", "It describes how she runs."),
    ("In \"The tall boy won\", the word \"tall\" is ....", "an adjective", "an adverb", "a verb", "a pronoun", "It describes the noun."),
    ("In \"He sat under the tree\", the word \"under\" is ....", "a preposition", "a conjunction", "an adverb", "a noun", "It relates \"sat\" to \"tree\"."),
    ("In \"Happiness matters\", the word \"happiness\" is ....", "a noun", "an adjective", "a verb", "an adverb", "It names a quality and is the subject."),
    ("In \"Tea or coffee?\", the word \"or\" is ....", "a conjunction", "a preposition", "an interjection", "a pronoun", "It joins two choices."),
    ("In \"Wow! That was fast\", the word \"Wow\" is ....", "an interjection", "a noun", "an adverb", "a conjunction", "It expresses sudden feeling."),
    ("In \"They arrived late\", the word \"They\" is ....", "a pronoun", "a noun", "an adjective", "a verb", "It replaces a noun."),
    ("In \"Birds sing\", the word \"sing\" is ....", "a verb", "a noun", "an adverb", "an adjective", "It is the action."),
])
fill("Tenses", C, [
    ("She .... to the office every day.", "goes", "go", "going", "gone", "Habit: simple present with a singular subject."),
    ("Look! It .... outside.", "is raining", "rains", "rained", "has rain", "Happening now: present continuous."),
    ("I .... him yesterday.", "met", "have met", "meet", "am meeting", "\"Yesterday\" takes the simple past."),
    ("They .... here since 2020.", "have lived", "live", "lived", "are living in", "\"Since\" with a continuing situation takes the present perfect."),
    ("By next June, she .... her degree.", "will have finished", "finishes", "finished", "has finished", "Done before a future point: future perfect."),
    ("When I arrived, the train .... already left.", "had", "has", "have", "was", "Earlier of two past events: past perfect."),
    ("He .... for two hours when the bell rang.", "had been studying", "studies", "has studied", "is studying", "Continuing up to a past moment: past perfect continuous."),
    ("If it rains tomorrow, we .... at home.", "will stay", "stayed", "stay had", "would stayed", "First conditional: present, then will."),
])
fill("Subject-verb agreement", C, [
    ("Each of the boys .... a prize.", "has", "have", "are having", "were having", "\"Each\" is singular."),
    ("The team of players .... ready.", "is", "are", "were", "have", "The subject \"team\" is singular here."),
    ("Neither the manager nor the employees .... present.", "were", "was", "is", "has been", "The verb agrees with the nearer subject, \"employees\"."),
    ("Bread and butter .... my usual breakfast.", "is", "are", "were", "have been", "Treated as a single dish."),
    ("One of my friends .... abroad.", "lives", "live", "are living", "have lived", "The subject is \"one\"."),
    ("A number of students .... absent today.", "are", "is", "was", "has been", "\"A number of\" takes a plural verb."),
    ("The number of students .... rising.", "is", "are", "were", "have been", "\"The number\" is singular."),
    ("Everybody .... the rules.", "knows", "know", "are knowing", "have known", "\"Everybody\" is singular."),
])
fill("Articles", C, [
    ("She is .... honest person.", "an", "a", "the", "no article", "\"Honest\" starts with a vowel sound."),
    ("He is .... university student.", "a", "an", "the", "no article", "\"University\" starts with a \"y\" sound."),
    ("..... sun rises in the east.", "The", "A", "An", "No article", "There is only one sun."),
    ("I saw .... elephant at the zoo.", "an", "a", "the", "no article", "First mention, with a vowel sound."),
    ("Mount Everest is .... highest peak.", "the", "a", "an", "no article", "Superlatives take \"the\"."),
    ("She plays .... piano well.", "the", "a", "an", "no article", "Musical instruments usually take \"the\"."),
    ("He goes to .... bed at ten.", "no article", "a", "an", "the", "\"Go to bed\" takes no article."),
    ("It took .... hour to finish.", "an", "a", "the", "no article", "\"Hour\" starts with a vowel sound."),
])
fill("Prepositions", C, [
    ("She is good .... maths.", "at", "in", "on", "for", "\"Good at\" is the set phrase."),
    ("The meeting is .... Monday.", "on", "in", "at", "by", "Days take \"on\"."),
    ("He was born .... 2001.", "in", "on", "at", "by", "Years take \"in\"."),
    ("We will meet .... 5 p.m.", "at", "in", "on", "for", "Clock times take \"at\"."),
    ("She is afraid .... dogs.", "of", "from", "with", "by", "\"Afraid of\" is the set phrase."),
    ("I agree .... you.", "with", "to", "on", "at", "One agrees with a person."),
    ("He has lived here .... ten years.", "for", "since", "from", "by", "A length of time takes \"for\"."),
    ("This phone is different .... that one.", "from", "than", "of", "at", "\"Different from\" is standard."),
])
fill("Pronouns", C, [
    ("Between you and .... , this is wrong.", "me", "I", "my", "mine", "After a preposition, use the object form."),
    ("This book is .... .", "hers", "her's", "she", "herself's", "Possessive pronouns take no apostrophe."),
    ("Ravi and .... went home.", "I", "me", "myself", "mine", "It is part of the subject."),
    ("Everyone must do .... duty.", "their", "his's", "them", "theirs", "Singular \"their\" is widely accepted for \"everyone\"."),
    ("The person .... called you is here.", "who", "whom", "whose", "which", "It is the subject of \"called\"."),
    ("To .... should I send this?", "whom", "who", "whose", "which", "Object of the preposition \"to\"."),
    ("She hurt .... while cooking.", "herself", "her", "she", "hers", "A reflexive pronoun refers back to the subject."),
    ("He is taller than .... .", "I am", "me am", "myself", "mine", "Complete the comparison: than I am."),
])
fill("Conjunctions", C, [
    ("She was ill, .... she came to work.", "but", "because", "so", "and if", "It shows contrast."),
    ("He left early .... he had a train to catch.", "because", "but", "although", "unless", "It gives the reason."),
    ("You will fail .... you study.", "unless", "if", "because", "and", "\"Unless\" means \"if not\"."),
    (".... it was raining, we went out.", "Although", "Because", "So", "Or", "It marks contrast."),
    ("Both Ravi .... Sara passed.", "and", "or", "nor", "but", "\"Both ... and\" is a pair."),
    ("Neither Ravi .... Sara passed.", "nor", "or", "and", "but", "\"Neither ... nor\" is a pair."),
    ("Wait here .... I return.", "until", "because", "so", "but", "It gives a time limit."),
    ("Not only did she sing, .... she danced.", "but also", "and too", "so that", "nor", "\"Not only ... but also\" is a pair."),
])
hand(C, "Active & passive voice", [
    ("Passive of \"The cat chased the mouse\"?", "The mouse was chased by the cat", "The mouse is chased by the cat", "The cat was chased by the mouse", "The mouse has chased the cat", "Past simple: was + past participle."),
    ("Passive of \"She writes a letter\"?", "A letter is written by her", "A letter was written by her", "A letter is wrote by her", "She is written a letter", "Present simple: is + past participle."),
    ("Passive of \"They will finish the work\"?", "The work will be finished by them", "The work will finish by them", "The work is finished by them", "They will be finished by the work", "Future: will be + past participle."),
    ("Passive of \"He has broken the glass\"?", "The glass has been broken by him", "The glass was broken by him", "The glass is broken by him", "The glass has broke by him", "Present perfect: has been + past participle."),
    ("Passive of \"Someone stole my bag\"?", "My bag was stolen", "My bag is stolen by someone's", "My bag stole", "My bag has stealing", "An unknown doer is usually dropped."),
    ("Active of \"The song was sung by Asha\"?", "Asha sang the song", "Asha sings the song", "Asha has sung the song", "The song sang Asha", "Past simple active."),
    ("Passive of \"Is she cooking food?\"?", "Is food being cooked by her?", "Was food cooked by her?", "Is food cooked by her?", "Has food been cooking by her?", "Present continuous: is being + past participle."),
    ("Passive of \"Open the door\"?", "Let the door be opened", "The door opened", "The door is opening", "Door has been open", "Imperatives use \"let ... be\"."),
])
hand(C, "Direct & indirect speech", [
    ("Indirect form of: He said, \"I am tired.\"", "He said that he was tired", "He said that I am tired", "He said that he is tired yesterday", "He told I was tired", "Present becomes past; the pronoun changes."),
    ("Indirect form of: She said, \"I will come.\"", "She said that she would come", "She said that she will came", "She says I would come", "She said she comes", "\"Will\" becomes \"would\"."),
    ("Indirect form of: He said to me, \"Where do you live?\"", "He asked me where I lived", "He asked me where do you live", "He said where I live", "He told me where did I live", "A question becomes a statement order."),
    ("Indirect form of: Ravi said, \"I bought a car.\"", "Ravi said that he had bought a car", "Ravi said that he bought a car tomorrow", "Ravi said I bought a car", "Ravi says he has buying a car", "Past becomes past perfect."),
    ("Indirect form of: She said to him, \"Please sit down.\"", "She requested him to sit down", "She said him sit down", "She asked that sit down", "She told please sit", "A request uses \"requested ... to\"."),
    ("Indirect form of: He said, \"The earth moves round the sun.\"", "He said that the earth moves round the sun", "He said that the earth moved round the sun yesterday", "He said the earth had moved", "He says earth moving", "A universal truth keeps its tense."),
    ("Indirect form of: Mother said, \"Do not run.\"", "Mother told me not to run", "Mother said do not run", "Mother told me that do not run", "Mother asked not running", "A negative command uses \"not to\"."),
    ("Indirect form of: He said, \"I saw her here today.\"", "He said that he had seen her there that day", "He said that he saw her here today", "He said he has seen her here today", "He said I saw her here today", "\"Here\" and \"today\" change to \"there\" and \"that day\"."),
])
hand(C, "Modifiers", [
    ("Which sentence is correct?", "Walking in the park, I saw a snake", "Walking in the park, a snake bit my eye", "Walking in the park, the snake was seen by me crawl", "A snake, walking in the park, I saw", "The modifier must attach to the walker."),
    ("Which sentence is correct?", "She served cold soup to the guests", "She served soup to the guests cold", "Cold she served soup the guests", "Guests soup she served cold to", "\"Cold\" should sit next to \"soup\"."),
    ("Which sentence is correct?", "I ate nearly the whole cake", "I nearly ate the whole cake", "Nearly the whole I ate cake", "The cake I whole nearly ate", "\"Nearly\" limits \"the whole cake\". \"I nearly ate\" would mean that no eating happened."),
    ("Which sentence is correct?", "After finishing the report, I went home", "After finishing the report, the home was reached", "After finishing the report, home it was", "After finishing, the report went home", "The doer follows the opening phrase."),
    ("Which sentence is correct?", "He bought a shirt with blue stripes from the shop", "He bought from a shirt the shop with stripes blue", "With blue stripes he bought from the shop a shirt", "A shirt from the shop with stripes bought he blue", "Keep \"with blue stripes\" next to \"shirt\"."),
    ("Which sentence is correct?", "Only she knows the answer", "Knows only the answer she only", "She knows answer the only only", "The only answer knows she", "\"Only\" must sit next to what it limits."),
    ("Which sentence is correct?", "Being late, Ravi took a taxi", "Being late, the taxi took Ravi", "Being late, a taxi was taken", "Late being, taxi Ravi took", "\"Being late\" describes Ravi."),
    ("Which sentence is correct?", "To pass the test, you must study", "To pass the test, studying must be done by the test", "To pass, the test must study", "Study must pass the test, to you", "The implied doer is \"you\"."),
])
hand(C, "Parallelism", [
    ("Which sentence is parallel?", "She likes reading, writing and swimming", "She likes reading, to write and swims", "She likes to read, writing and swim", "She likes read, writes and swimming", "All three use the same form."),
    ("Which sentence is parallel?", "He was asked to sit, to read and to wait", "He was asked to sit, reading and wait", "He was asked sitting, to read and waiting", "He was asked sit, reads and to wait", "All three are infinitives."),
    ("Which sentence is parallel?", "The job needs skill and patience", "The job needs skill and being patient", "The job needs skilled and patience", "The job needs to skill and patient", "Two nouns."),
    ("Which sentence is parallel?", "Not only is she smart but also kind", "Not only she smart but kindness", "Not only is she smart but also kindness", "Not only smart is she but also being kind", "Both follow with adjectives."),
    ("Which sentence is parallel?", "He runs fast and jumps high", "He runs fast and jumping high", "He running fast and jumps high", "He runs fast and to jump high", "Matching verb forms."),
    ("Which sentence is parallel?", "I prefer walking to driving", "I prefer walking to drive", "I prefer to walk to driving", "I prefer walk to driving", "Two -ing forms."),
    ("Which sentence is parallel?", "The report was short, clear and useful", "The report was short, clearly and useful", "The report was short, clear and usefulness", "The report was shortly, clear and useful", "Three adjectives."),
    ("Which sentence is parallel?", "She either will call or will write", "She either will call or writing", "She either calling or will write", "She will either call or writing", "\"Either\" and \"or\" need matching forms."),
])
hand(C, "Error spotting", [
    ("Find the error: \"He do not (A) / like (B) / coffee (C).\"", "A", "B", "C", "No error", "It should be \"does not\"."),
    ("Find the error: \"She (A) / has went (B) / home (C).\"", "B", "A", "C", "No error", "It should be \"has gone\"."),
    ("Find the error: \"The informations (A) / you gave (B) / were useful (C).\"", "A", "B", "C", "No error", "\"Information\" is uncountable."),
    ("Find the error: \"I am (A) / knowing (B) / the answer (C).\"", "B", "A", "C", "No error", "\"Know\" is not used in the continuous."),
    ("Find the error: \"He is (A) / more taller (B) / than me (C).\"", "B", "A", "C", "No error", "It should be \"taller\"."),
    ("Find the error: \"She (A) / discussed about (B) / the plan (C).\"", "B", "A", "C", "No error", "\"Discussed\" takes no \"about\"."),
    ("Find the error: \"Each student (A) / must bring (B) / their own lunches (C).\"", "C", "A", "B", "No error", "It should be \"lunch\", matching a single student's item."),
    ("Find the error: \"The news (A) / are (B) / good (C).\"", "B", "A", "C", "No error", "\"News\" takes a singular verb."),
    ("Find the error: \"She (A) / goes to (B) / work by walk (C).\"", "C", "A", "B", "No error", "It should be \"on foot\"."),
    ("Find the error: \"He told (A) / to me (B) / a secret (C).\"", "B", "A", "C", "No error", "\"Told\" takes a direct object: told me."),
])
hand(C, "Sentence correction", [
    ("Improve: \"He don't know nothing.\"", "He doesn't know anything", "He don't know anything", "He doesn't knows nothing", "He do not knows", "Fix agreement and the double negative."),
    ("Improve: \"Me and him went there.\"", "He and I went there", "Him and me went there", "Me and he went there", "I and him went there", "Subjects take subject pronouns."),
    ("Improve: \"She is more smarter.\"", "She is smarter", "She is more smart than", "She is most smarter", "She smarter is", "Avoid the double comparative."),
    ("Improve: \"I have seen him yesterday.\"", "I saw him yesterday", "I have see him yesterday", "I am seen him yesterday", "I was saw him yesterday", "\"Yesterday\" takes the simple past."),
    ("Improve: \"Despite of the rain, we played.\"", "Despite the rain, we played", "Despite of rain we played", "In despite the rain, we played", "Although of the rain, we played", "\"Despite\" takes no \"of\"."),
    ("Improve: \"The reason is because he was ill.\"", "The reason is that he was ill", "The reason because he was ill", "The reason is why because he was ill", "The reason he is because ill", "Use \"the reason is that\"."),
    ("Improve: \"She suggested him to go.\"", "She suggested that he go", "She suggested him going to", "She suggested to him to go", "She suggests him go", "\"Suggest\" is followed by \"that\" or an -ing form."),
    ("Improve: \"He is senior than me.\"", "He is senior to me", "He is seniorer than me", "He is senior from me", "He is senior of me", "\"Senior\" takes \"to\"."),
    ("Improve: \"I am agree with you.\"", "I agree with you", "I am agreeing to you", "I agreed you", "I am agree you", "\"Agree\" is a verb."),
    ("Improve: \"Please revert back to me.\"", "Please reply to me", "Please revert back me", "Please to revert back", "Please back revert me", "\"Revert back\" is redundant, and \"reply\" is what is meant."),
])

# =================================================================== Vocabulary
C = "Vocabulary"
# word, synonym, antonym: chosen to be far apart in meaning, so other rows' words are safe wrong options
BANK = """abundant plentiful scarce
brave courageous cowardly
candid frank secretive
diligent hardworking lazy
eager keen reluctant
fragile delicate sturdy
genuine authentic fake
humble modest arrogant
hostile unfriendly welcoming
increase expand shrink
join connect separate
kind gentle cruel
lucid clear confusing
meagre insufficient ample
novice beginner expert
obscure unclear famous
praise commend criticise
quiet silent noisy
rapid fast slow
stubborn obstinate flexible
tiny minute enormous
urgent pressing trivial
vacant empty occupied
wealthy rich poor
ancient old modern
accept receive reject
bitter sour sweet
calm peaceful agitated
dull boring exciting
expand enlarge contract
frugal thrifty wasteful
gloomy sad cheerful
huge giant small
innocent blameless guilty
victory triumph defeat
permanent lasting temporary
polite courteous rude
strength power weakness
transparent see-through opaque
wise sensible foolish""".split("\n")
BANK = [line.split() for line in BANK]


@T(C, "Synonyms & antonyms")
def _(r):
    i = r.randrange(len(BANK))
    w, s, a = BANK[i]
    others = [row for j, row in enumerate(BANK) if j != i]
    r.shuffle(others)
    if r.random() < .5:
        return Q(f"Choose the word closest in meaning to {w.upper()}.", s, f"{w} means {s}.", [a, others[0][1], others[1][1]])
    return Q(f"Choose the word most opposite in meaning to {w.upper()}.", a, f"{w} is the opposite of {a}.", [s, others[0][2], others[1][2]])


hand(C, "One-word substitution", [
    ("One who loves books", "Bibliophile", "Philanthropist", "Misanthrope", "Atheist", "\"Biblio\" means book."),
    ("One who does not believe in God", "Atheist", "Theist", "Pagan", "Optimist", "\"A-\" means without."),
    ("A person who hates mankind", "Misanthrope", "Philanthropist", "Egoist", "Altruist", "\"Mis-\" means hate."),
    ("Fear of water", "Hydrophobia", "Claustrophobia", "Acrophobia", "Xenophobia", "\"Hydro\" means water."),
    ("Fear of heights", "Acrophobia", "Hydrophobia", "Agoraphobia", "Xenophobia", "\"Acro\" means height."),
    ("A speech made without preparation", "Extempore", "Monologue", "Soliloquy", "Eulogy", "Off the cuff."),
    ("A person who walks in their sleep", "Somnambulist", "Insomniac", "Pedestrian", "Nomad", "\"Somnus\" means sleep."),
    ("Government by the people", "Democracy", "Monarchy", "Autocracy", "Oligarchy", "\"Demos\" means people."),
    ("Rule by a few", "Oligarchy", "Democracy", "Monarchy", "Theocracy", "\"Oligo\" means few."),
    ("A cure for all problems", "Panacea", "Placebo", "Antidote", "Elixir of death", "A universal remedy."),
    ("That which cannot be read", "Illegible", "Eligible", "Inaudible", "Invisible", "Handwriting can be illegible."),
    ("One who eats no animal products", "Vegan", "Carnivore", "Omnivore", "Cannibal", "No animal products at all."),
    ("A life story written by oneself", "Autobiography", "Biography", "Memorandum", "Novel", "\"Auto\" means self."),
    ("A place where bees are kept", "Apiary", "Aviary", "Aquarium", "Kennel", "An aviary is for birds."),
    ("One who speaks many languages", "Polyglot", "Linguist only", "Orator", "Translator only", "\"Poly\" means many."),
])
hand(C, "Idioms & phrases", [
    ("\"Break the ice\" means", "Start a friendly conversation", "Destroy something", "Feel cold", "Go skating", "It eases a first meeting."),
    ("\"Once in a blue moon\" means", "Very rarely", "Every month", "At night", "Very often", "A rare event."),
    ("\"Spill the beans\" means", "Reveal a secret", "Waste food", "Cook badly", "Plant seeds", "Let out a secret."),
    ("\"Hit the nail on the head\" means", "Be exactly right", "Injure oneself", "Do carpentry", "Make a mistake", "Exact."),
    ("\"Under the weather\" means", "Slightly ill", "In the rain", "Very happy", "Outdoors", "Unwell."),
    ("\"Bite the bullet\" means", "Face something unpleasant bravely", "Eat quickly", "Get hurt", "Attack someone", "Accept a hardship."),
    ("\"A piece of cake\" means", "Very easy", "A dessert", "A small share", "Very costly", "Easy."),
    ("\"Burn the midnight oil\" means", "Work late into the night", "Waste fuel", "Cook at night", "Start a fire", "Late-night work."),
    ("\"Let the cat out of the bag\" means", "Reveal a secret by accident", "Free an animal", "Lose a pet", "Buy something", "Accidental reveal."),
    ("\"Cost an arm and a leg\" means", "Be very expensive", "Be painful", "Be cheap", "Cause an injury", "Very costly."),
    ("\"Beat around the bush\" means", "Avoid the main point", "Do gardening", "Hit someone", "Win easily", "Not direct."),
    ("\"Back to square one\" means", "Start again from the beginning", "Win a game", "Be on the first floor", "Be first in the class", "No progress."),
    ("\"Call it a day\" means", "Stop working for now", "Name a date", "Make a phone call", "Begin a project", "Finish for the day."),
    ("\"In hot water\" means", "In trouble", "Having a bath", "Very angry", "Cooking", "In difficulty."),
    ("\"Blessing in disguise\" means", "A good result from apparent bad luck", "A costume party", "A religious event", "A hidden enemy", "Good in the end."),
])
SPELL = [("accommodate", "acommodate", "accomodate", "acomodate"), ("receive", "recieve", "receeve", "receve"), ("necessary", "neccessary", "necesary", "neccesary"), ("separate", "seperate", "seprate", "separete"), ("definitely", "definately", "definitly", "defanitely"), ("occurrence", "occurence", "ocurrence", "occurance"), ("embarrass", "embarass", "embaras", "embarras"), ("maintenance", "maintainance", "maintenence", "maintanance"), ("privilege", "priviledge", "privelege", "privilage"), ("committee", "comittee", "commitee", "comitee"), ("restaurant", "restaraunt", "resturant", "restarant"), ("calendar", "calender", "calandar", "calander"), ("colleague", "collegue", "colleage", "colegue"), ("guarantee", "garantee", "guarentee", "guarantie"), ("rhythm", "rythm", "rhythem", "rhytm"), ("conscience", "concience", "consciense", "conscence"), ("beginning", "begining", "beggining", "begginning"), ("business", "buisness", "bussiness", "busness"), ("environment", "enviroment", "environmant", "enviornment"), ("government", "goverment", "governmant", "govermant"), ("immediately", "immediatly", "imediately", "immedietly"), ("knowledge", "knowlege", "knowledg", "nowledge"), ("library", "libarary", "libray", "liberary"), ("mischievous", "mischievious", "mischevous", "mischeivous"), ("pronunciation", "pronounciation", "pronunsiation", "pronounsiation"), ("questionnaire", "questionaire", "questionnare", "questionare"), ("successful", "succesful", "successfull", "sucessful"), ("tomorrow", "tommorow", "tomorow", "tommorrow"), ("vacuum", "vaccum", "vacum", "vaccuum"), ("weird", "wierd", "wierdd", "weard")]
hand(C, "Spelling check", [("Which spelling is correct: " + a[0].upper() + "...?", a, x, y, z, f"The standard spelling is \"{a}\".") for i, (a, x, y, z) in enumerate(SPELL)])
fill("Homonyms & confusables", C, [
    ("The noise had no .... on her.", "effect", "affect", "effects", "affects", "Noun: effect."),
    ("Bad sleep can .... your work.", "affect", "effect", "effects", "affection", "Verb: affect."),
    ("I need your .... on this plan.", "advice", "advise", "advices", "advised", "Noun: advice."),
    ("I .... you to rest.", "advise", "advice", "advices", "advisory", "Verb: advise."),
    ("The dog wagged .... tail.", "its", "it's", "its'", "it is", "Possessive: its."),
    ("She is taller .... me.", "than", "then", "that", "them", "Comparison: than."),
    ("We ate, and .... we left.", "then", "than", "them", "that", "Sequence: then."),
    ("The team did not want to .... the final.", "lose", "loose", "loss", "lost", "To be defeated: lose."),
    ("These jeans are too .... .", "loose", "lose", "loss", "lost", "Not tight: loose."),
    ("Do not .... your keys.", "lose", "loose", "loss", "lost of", "Misplace: lose."),
    ("The school .... spoke at the event.", "principal", "principle", "principals'", "principled", "Head of a school."),
    ("Honesty is an important .... .", "principle", "principal", "principality", "principally", "A basic rule."),
    ("All .... the cake was eaten, except one slice.", "of", "off", "for", "from", "\"All of\" the cake."),
    ("I will buy some office .... .", "stationery", "stationary", "stationaries", "station", "Paper and pens."),
    ("The car remained .... .", "stationary", "stationery", "station", "stations", "Not moving."),
])
for_analogy = [("Bird", "Flock", "Fish", "School", ["River", "Fin", "Sea"]), ("Book", "Read", "Song", "Sing", ["Tune", "Voice", "Band"]), ("Hunger", "Food", "Thirst", "Water", ["Glass", "Cup", "River"]), ("Painter", "Brush", "Writer", "Pen", ["Book", "Word", "Story"]), ("Wheel", "Car", "Wing", "Plane", ["Bird", "Fly", "Sky"]), ("Sad", "Happy", "Dark", "Bright", ["Night", "Black", "Shadow"]), ("Pilot", "Plane", "Captain", "Ship", ["Sea", "Crew", "Anchor"]), ("Knife", "Cut", "Needle", "Stitch", ["Thread", "Sharp", "Cloth"]), ("Lion", "Pride", "Wolf", "Pack", ["Howl", "Forest", "Hunter"]), ("Student", "School", "Patient", "Hospital", ["Doctor", "Medicine", "Nurse"]), ("Hour", "Minute", "Minute", "Second", ["Hour", "Day", "Week"]), ("Cold", "Ice", "Hot", "Fire", ["Water", "Sun only", "Wind"]), ("Bee", "Honey", "Spider", "Web", ["Fly", "Legs", "Corner"]), ("Doctor", "Stethoscope", "Carpenter", "Saw", ["Wood", "Chair", "Nail only"]), ("Foot", "Sock", "Head", "Cap", ["Hair", "Neck", "Face"])]
hand(C, "Word analogy", [(f"{a} is to {b} as {c} is to ....", d, w[0], w[1], w[2], f"The same relation links {a} to {b} and {c} to {d}.") for a, b, c, d, w in for_analogy])
hand(C, "Foreign words & phrases", [
    ("\"Ad hoc\" means", "For a particular purpose", "Permanent", "Without reason", "From the start", "Made for this case."),
    ("\"Vice versa\" means", "The other way round", "A wrong action", "In a verse", "Very often", "Reversed."),
    ("\"Status quo\" means", "The existing state of things", "High status", "A question", "A change", "Things as they are."),
    ("\"Bona fide\" means", "Genuine", "Bad faith", "A good dog", "Foreign", "In good faith."),
    ("\"Per se\" means", "By itself", "For each", "Per person", "Perhaps", "In itself."),
    ("\"De facto\" means", "In fact, whether or not legally", "By law", "Without facts", "Before the fact", "In reality."),
    ("\"Alma mater\" means", "One's former school or college", "A mother", "A strong spirit", "A soul", "Nourishing mother."),
    ("\"En route\" means", "On the way", "In a restaurant", "At home", "Finished", "French: on the road."),
    ("\"Faux pas\" means", "A social mistake", "A fake passport", "A step forward", "A dance", "French: false step."),
    ("\"Carte blanche\" means", "Complete freedom to act", "A white card", "A menu", "A blank map", "Full authority."),
    ("\"Modus operandi\" means", "A way of working", "A surgery", "A mood", "An operation theatre", "Method of operating."),
    ("\"Pro bono\" means", "Done free for the public good", "Very professional", "A music star", "For a bonus", "Free professional work."),
])

# =================================================================== Sentence structure
C = "Sentence Structure & Flow"
fill("Fill in the blanks", C, [
    ("The manager .... the proposal because it was too costly.", "rejected", "accepted", "repeated", "invented", "\"Too costly\" points to refusal."),
    ("Despite the heavy traffic, she arrived .... .", "on time", "late", "lately", "never", "\"Despite\" signals an unexpected outcome."),
    ("The bridge was closed for .... repairs.", "urgent", "ancient", "tasty", "absent", "Repairs can be urgent."),
    ("A good leader .... the team to do its best.", "motivates", "ignores", "punishes", "forgets", "Positive sense required."),
    ("The experiment failed, so they .... it with a new design.", "repeated", "praised", "avoided", "buried", "A failure leads to trying again."),
    ("The medicine had a .... effect, and she recovered in days.", "positive", "harmful", "useless", "negative", "Recovery shows benefit."),
    ("He was so .... that he gave half his salary to charity.", "generous", "greedy", "selfish", "stingy", "Giving shows generosity."),
    ("The evidence was .... , so the court dismissed the case.", "insufficient", "strong", "complete", "convincing", "A dismissal suggests weak evidence."),
    ("The data was .... before training the model.", "cleaned", "eaten", "sung", "painted", "Data gets cleaned."),
    ("Her speech was so .... that everyone stayed awake.", "engaging", "dull", "tedious", "sleepy", "People stayed awake."),
    ("The price is .... : it can be discussed.", "negotiable", "fixed", "rigid", "final", "It can be discussed."),
    ("Because the road was icy, drivers were told to be .... .", "cautious", "careless", "reckless", "fast", "Ice demands care."),
    ("He has a .... memory and forgets nothing.", "sharp", "weak", "poor", "fading", "He forgets nothing."),
    ("The new law .... smoking in public places.", "prohibits", "promotes", "invents", "enjoys", "Laws can ban actions."),
    ("The two companies decided to .... into one.", "merge", "split", "scatter", "divide", "\"Into one\" means joining."),
    ("Her answer was .... ; it had no errors.", "flawless", "faulty", "careless", "wrong", "No errors."),
    ("The company .... its profits in new products.", "invested", "wasted away", "swallowed", "forgot", "Profits are invested."),
    ("The rules are .... to everyone without exception.", "applicable", "unknown", "unavailable", "foreign", "They apply to all."),
    ("The storm caused .... damage across the coast.", "extensive", "tiny", "no", "minor", "\"Across the coast\" implies wide damage."),
    ("He is .... to change his mind; arguing is useless.", "unlikely", "eager", "quick", "ready", "Arguing is useless."),
])
CLOZE = [
    ("Regular exercise has many benefits. It (1) the heart, reduces (2) and improves sleep. Even a short walk (3) help. Doctors (4) at least thirty minutes a day.",
     [("strengthens", "weakens", "stops", "hides"), ("stress", "strength", "health", "energy"), ("can", "cannot", "never", "did"), ("recommend", "refuse", "forget", "deny")]),
    ("The internet has changed how people (1). Information that once took days to find is now (2) in seconds. However, not everything online is (3), so readers must (4) their sources.",
     [("learn", "sleep", "cook", "walk"), ("available", "absent", "unknown", "lost"), ("accurate", "long", "colourful", "funny"), ("check", "ignore", "delete", "hide")]),
    ("Saving money is a (1) habit. People who plan their spending are (2) to face sudden problems. A small amount saved each month (3) over time. It is never too (4) to start.",
     [("useful", "useless", "harmful", "rare"), ("better prepared", "unready", "unable", "afraid"), ("grows", "shrinks", "disappears", "stops"), ("late", "early", "soon", "fast")]),
    ("Trees are vital for life. They (1) oxygen, give shade and (2) soil from erosion. When forests are cut (3), animals lose their homes. We must plant (4) trees than we cut.",
     [("produce", "destroy", "hide", "steal"), ("protect", "remove", "sell", "burn"), ("down", "up", "in", "over"), ("more", "fewer", "less", "none")]),
    ("A good resume is (1) and clear. It should highlight your (2), not list every task. Recruiters spend only seconds on each, so the most important facts must come (3). Always (4) it for errors.",
     [("short", "endless", "secret", "blank"), ("achievements", "hobbies only", "weaknesses", "relatives"), ("first", "last", "never", "late"), ("check", "ignore", "lose", "burn")]),
    ("Teamwork matters in software. Developers (1) their code so that errors are found early. Clear communication (2) confusion. When something fails, a good team looks for the (3), not for someone to (4).",
     [("review", "hide", "delete", "sell"), ("reduces", "causes", "increases", "creates"), ("cause", "weather", "price", "colour"), ("blame", "praise", "pay", "hire")]),
]
cloze_rows = []
for passage, blanks in CLOZE:
    for i, (a, x, y, z) in enumerate(blanks):
        cloze_rows.append((f"Passage: {passage}\n\nWhich word best fits blank ({i + 1})?", a, x, y, z, "It alone fits the grammar and the meaning of the passage."))
hand(C, "Cloze test", cloze_rows)
JUMBLES = [
    ["Ravi woke up late.", "He rushed to the station.", "The train had already left.", "So he took a bus to the office."],
    ["First, collect the requirements.", "Next, design the system.", "Then, write and test the code.", "Finally, deploy it to production."],
    ["Water evaporates from the sea.", "It rises and forms clouds.", "The clouds cool down.", "Rain falls back on the earth."],
    ["The company launched a new phone.", "Customers rushed to buy it.", "Stocks ran out within days.", "The company then raised production."],
    ["A seed is planted in the soil.", "It absorbs water and swells.", "A small shoot appears above ground.", "Over time it grows into a plant."],
    ["A customer places an order.", "The payment is verified.", "The warehouse packs the item.", "A courier delivers it."],
    ["The alarm rang at midnight.", "The guards searched the building.", "They found an open window.", "The police were then called."],
    ["She applied for the job.", "She was called for an interview.", "She answered the questions well.", "She received an offer a week later."],
    ["Mix the flour and water.", "Knead it into a dough.", "Roll it into flat circles.", "Cook them on a hot pan."],
    ["The bug was reported by a user.", "A developer reproduced it.", "The cause was found and fixed.", "The fix was released in the next version."],
    ["Heavy rain fell for three days.", "The river rose quickly.", "Nearby fields were flooded.", "Farmers lost their crops."],
    ["He saved money for two years.", "He then bought a small shop.", "The business slowly grew.", "Today he owns three stores."],
]


@T(C, "Para jumbles")
def _(r):
    s = r.choice(JUMBLES)
    labels = list("ABCD")
    order = list(range(4))
    r.shuffle(order)
    shown = "\n".join(f"- {labels[i]}. {s[order[i]]}" for i in range(4))
    right = "".join(labels[order.index(k)] for k in range(4))
    wrong = set()
    while len(wrong) < 3:
        w = labels[:]
        r.shuffle(w)
        w = "".join(w)
        if w != right:
            wrong.add(w)
    return Q(f"Arrange these sentences in a logical order:\n\n{shown}", right, "The correct sequence is: " + " ".join(s), sorted(wrong))


ODDS = [
    (["Regular reading builds vocabulary.", "It also improves concentration.", "My neighbour bought a new scooter.", "Many successful people read daily."], 2),
    (["Java runs on the JVM.", "Its bytecode is portable.", "Bananas are rich in potassium.", "The JVM manages memory."], 2),
    (["Cricket is popular in India.", "Millions watch the league.", "The moon orbits the earth.", "Young players dream of playing for the country."], 2),
    (["Exercise lowers stress.", "It keeps the heart strong.", "The printer is out of ink.", "It also improves sleep."], 2),
    (["Caching reduces database load.", "It speeds up responses.", "Stale data is its main risk.", "Rivers often begin in mountains."], 3),
    (["Solar power is clean.", "Panel prices have fallen.", "Many homes now use it.", "My cat sleeps all day."], 3),
    (["The Himalayas are young mountains.", "They are still rising.", "Rice is cooked in water.", "They hold many glaciers."], 2),
    (["Trains are cheap for long trips.", "They produce less pollution than cars.", "The class test is on Friday.", "They rarely get stuck in traffic."], 2),
    (["Bees pollinate crops.", "Their numbers are falling.", "Farmers are concerned.", "The laptop has two USB ports."], 3),
    (["A resume should be short.", "It must highlight results.", "Penguins cannot fly.", "Errors in it create a bad impression."], 2),
    (["Vaccines train the immune system.", "They have reduced many diseases.", "The bus leaves at noon.", "Doctors recommend them widely."], 2),
    (["Recycling saves resources.", "It reduces waste in landfills.", "Paper and glass are easy to recycle.", "The film received poor reviews."], 3),
]
hand(C, "Odd sentence out", [("Which sentence does not belong in this paragraph?\n\n" + "\n".join(f"- {'ABCD'[i]}. {x}" for i, x in enumerate(s)), "ABCD"[k], *[l for l in "ABCD" if l != "ABCD"[k]], f"Sentence {'ABCD'[k]} is unrelated to the topic.") for s, k in ODDS])
INSERT = [
    (["Cloud platforms let companies rent computers.", "(blank)", "This turns a large upfront cost into a monthly bill."], "They no longer need to buy their own servers.", ["Elephants live in herds.", "My exam was very difficult.", "However, the river is dry."]),
    (["Many people fear public speaking.", "(blank)", "With practice, this fear usually fades."], "Their hands shake and their voices tremble.", ["The sun is a star.", "Rice grows in water.", "Prices of steel fell."]),
    (["He had studied for months.", "(blank)", "He was naturally disappointed."], "Yet he failed by a single mark.", ["He then won the top prize.", "Dogs bark at night.", "Also, the sky is blue."]),
    (["The first version of the app crashed often.", "(blank)", "After that, complaints fell sharply."], "So the team spent a month fixing bugs.", ["So the team deleted the logo.", "Mountains are tall.", "Next, it rained in Pune."]),
    (["Plastic takes centuries to break down.", "(blank)", "It then harms fish and birds."], "Much of it ends up in the sea.", ["Much of it is made of gold.", "My brother is an engineer.", "It tastes very sweet."]),
    (["Sleep affects memory.", "(blank)", "So cramming all night can backfire."], "The brain stores what you learnt while you rest.", ["The brain has no use for rest.", "Bread is made from flour.", "The train was late again."]),
    (["An index makes reads faster.", "(blank)", "So add only the indexes you need."], "But it slows down writes and uses storage.", ["And it makes writes faster too.", "Cats like milk.", "The index finger is long."]),
    (["The village had no clean water.", "(blank)", "Illness fell within a year."], "A charity then dug a deep well.", ["A charity then opened a cinema.", "Fish swim in rivers.", "Clouds are white."]),
    (["Automated tests catch regressions.", "(blank)", "This gives teams the confidence to release often."], "They run on every change, without human effort.", ["They are written on paper and posted.", "The tea was cold.", "Trees lose leaves."]),
    (["India has many languages.", "(blank)", "This diversity is reflected in its literature."], "Each region has its own script and traditions.", ["Each mountain has a river.", "My laptop is slow.", "Nobody speaks there."]),
    (["Kafka stores events in a log.", "(blank)", "This allows new services to replay old data."], "Consumers read it at their own pace.", ["Consumers must delete it at once.", "Kafka was a writer of novels only.", "The log was made of oak."]),
    (["He started running every morning.", "(blank)", "He soon felt much fitter."], "He also stopped eating junk food.", ["He also started smoking more.", "Roses are red.", "The sea is salty."]),
]
hand(C, "Sentence insertion", [("Which sentence best fills the blank?\n\n" + " ".join(p), a, w[0], w[1], w[2], "It links the sentence before to the sentence after.") for p, a, w in INSERT])

# =================================================================== Comprehension
C = "Comprehension"
PASSAGES = [
    ("India's railways carry millions of passengers every day. Most tickets are now booked online, which has shortened queues at stations. Yet many travellers in rural areas still buy tickets at counters, because they lack internet access or prefer paying in cash. Officials say counters will therefore remain open, even as online booking grows.",
     [("How are most tickets booked now?", "Online", "At counters", "By post", "By phone only", "Stated."), ("What has online booking shortened?", "Queues at stations", "Train journeys", "Platforms", "Rural roads", "Stated."), ("Why do some rural travellers use counters?", "They lack internet access or prefer cash", "Counters are cheaper by law", "Online booking is banned there", "Trains do not run online", "Stated."), ("What will officials do?", "Keep counters open", "Close all counters", "Stop online booking", "Raise all fares", "Stated."), ("The word \"yet\" signals", "A contrast", "A result", "An example", "A time sequence", "It introduces a contrast with the earlier point."), ("A suitable title is", "Railway Tickets: Online Growth and Lasting Counters", "How Trains Are Built", "Why Cash Is Illegal", "The End of Rural Travel", "It covers the whole passage.")]),
    ("A city introduced a bicycle-sharing scheme in 2021. In the first year, 40,000 people signed up, far above the forecast of 25,000. Short car trips in the centre fell by about 8%. However, bicycles were often unavailable at popular stations in the morning, and the council added trucks to move them around. Critics said the money should have gone to buses, but a survey found that most users had previously used cars or walked, not buses.",
     [("How many people signed up in the first year?", "40,000", "25,000", "8,000", "21,000", "Stated directly."), ("What problem did the scheme face?", "Bicycles were unavailable at busy stations", "Nobody signed up", "All buses stopped", "Cars were banned", "Stated in the passage."), ("What did the survey suggest?", "Most users did not switch from buses", "Most users gave up buses", "Most users disliked cycling", "Nobody used cars", "Most had used cars or walked."), ("What is the tone towards the scheme?", "Mostly positive, with noted problems", "Fully negative", "Angry", "Humorous", "Success is noted along with issues."), ("By about how much did short car trips fall?", "8%", "25%", "40%", "80%", "Stated."), ("Which title suits it best?", "A City's Bicycle Scheme: Results and Problems", "Why Buses Are Better", "The History of Trucks", "How to Repair Bicycles", "It covers the whole passage.")]),
    ("Honey does not spoil easily. It has very little water and is acidic, which makes it hard for bacteria to grow. Bees also add an enzyme that produces small amounts of hydrogen peroxide. Sealed honey found in ancient tombs has remained edible. But honey is not safe for babies under one, because it can carry spores that their immature gut cannot handle.",
     [("Why does honey resist spoiling?", "Low water and acidity", "It is kept cold", "It contains salt", "It is always cooked", "Stated."), ("What do bees add?", "An enzyme", "Salt", "Vinegar", "Sugar cane", "Stated."), ("Who should not eat honey?", "Babies under one", "Adults", "Older people", "Athletes", "Stated."), ("Ancient honey is mentioned to show that", "Honey can last a very long time", "Tombs were sweet", "Bees are ancient", "Honey is dangerous", "It supports the main claim."), ("\"Immature\" here means", "Not fully developed", "Silly", "Old", "Strong", "It refers to a baby's gut."), ("What is the passage mainly about?", "Why honey keeps well, and one risk", "How bees fly", "Ancient tombs", "Baby food recipes", "It covers both parts.")]),
    ("Remote work grew quickly after 2020. Many employees report saving commuting time and feeling more in control of their day. Some companies save on office costs. Yet managers worry about onboarding and mentoring, as junior staff can miss informal learning. Many firms now use a hybrid model, with staff in the office on some days.",
     [("What do many employees save?", "Commuting time", "Salary", "Laptops", "Annual leave", "Stated."), ("What worries managers?", "Onboarding and mentoring", "Too much office space", "Rising commute time", "Low taxes", "Stated."), ("Who may lose out most on informal learning?", "Junior staff", "Directors", "Customers", "Landlords", "Stated."), ("What is a hybrid model?", "Some days in the office, some at home", "All days at home", "All days in the office", "Working at night", "Stated."), ("Which statement is supported?", "Remote work has both benefits and costs", "Remote work has no benefits", "Offices have closed everywhere", "Nobody commutes now", "It gives both sides."), ("The author's approach is", "Balanced", "One-sided", "Sarcastic", "Fearful", "It presents both sides.")]),
    ("A database index works like the index of a book: rather than reading each page, you look up a term and jump to the right place. This makes reads far faster. But each index must be updated when data changes, so writes become slower, and the index takes up storage. Engineers therefore add indexes for the queries that really matter, rather than indexing every column.",
     [("What does the book comparison explain?", "How an index speeds up finding data", "How books are printed", "How storage is priced", "How to write queries", "It is the analogy's point."), ("What is one cost of indexes?", "Slower writes", "Slower reads", "Fewer rows", "Lost data", "Stated."), ("What should engineers do?", "Index the queries that really matter", "Index every column", "Avoid all indexes", "Delete tables", "Stated."), ("Why do writes slow down?", "Each index must be updated", "Reads block forever", "Disks stop", "The table shrinks", "Stated."), ("What do indexes also use?", "Storage", "Extra users", "Bandwidth only", "Electric meters", "Stated."), ("The main idea is that indexes", "Trade slower writes for faster reads", "Are always good", "Are always bad", "Replace tables", "It covers the trade-off.")]),
    ("Elephants are highly social. Herds are led by the oldest female, known as the matriarch, whose memory of water sources can save the group in droughts. Calves are raised by the whole family. Elephants also respond to the bones of other elephants, which some researchers take as a sign of emotional awareness, although this remains debated.",
     [("Who leads a herd?", "The oldest female", "The largest male", "The youngest calf", "Any male", "Stated."), ("Why is her memory valuable?", "It helps find water in droughts", "It helps fight lions", "It helps find mates", "It helps in migration to the sea", "Stated."), ("Who raises the calves?", "The whole family", "Only the mother", "Only males", "No one", "Stated."), ("What is debated?", "Whether the response to bones shows emotion", "Whether elephants are social", "Whether droughts occur", "Whether calves exist", "Stated."), ("\"Matriarch\" means", "A female leader", "A male leader", "A calf", "A water source", "Defined in the passage."), ("The passage is mainly about", "Elephant social life", "Water conservation", "Hunting", "Zoo care", "It covers their social life.")]),
    ("Many people think that multitasking increases productivity. Research suggests otherwise: most people are actually switching quickly between tasks, and each switch costs time and attention. Errors go up, especially on complex work. Simple habits help, such as turning off notifications and working in focused blocks.",
     [("What does research suggest about multitasking?", "It is really rapid switching", "It doubles output", "It reduces errors", "It is impossible to attempt", "Stated."), ("What does each switch cost?", "Time and attention", "Money", "Sleep", "Memory chips", "Stated."), ("When do errors rise most?", "On complex work", "On simple work only", "On holidays", "At night only", "Stated."), ("Which habit is suggested?", "Working in focused blocks", "Adding more notifications", "Doing many tasks at once", "Working without breaks at all", "Stated."), ("The writer's purpose is to", "Correct a common belief", "Sell a phone", "Tell a story", "Describe a holiday", "It challenges a belief."), ("A suitable title is", "The Myth of Multitasking", "How to Buy Notifications", "The Best Phones", "History of Work", "It fits the main idea.")]),
    ("Rainwater harvesting collects rain from rooftops and stores it for later use or sends it into the ground. In places with seasonal rain, it can raise groundwater levels and reduce pressure on city supplies. The cost is modest for new buildings, though older buildings may need more changes. Filters must be cleaned, or the stored water can become unsafe.",
     [("Where is rain collected from?", "Rooftops", "Rivers", "Oceans", "Wells", "Stated."), ("What benefit is stated?", "Higher groundwater levels", "Lower electricity bills", "Fewer cars", "Cheaper rice", "Stated."), ("Which buildings may need more changes?", "Older buildings", "New buildings", "Tall buildings only", "Glass buildings", "Stated."), ("Why must filters be cleaned?", "Stored water can become unsafe", "To increase rain", "To lower taxes", "To cool the roof", "Stated."), ("\"Modest\" here means", "Fairly low", "Very high", "Shy", "Unknown", "It describes cost."), ("The passage mainly", "Explains a practice with its benefits and care needed", "Attacks new buildings", "Argues rain is harmful", "Tells a personal story", "It explains and qualifies.")]),
    ("A phishing email tricks people into revealing passwords or clicking harmful links. Attackers often create urgency, such as claiming that an account will close today. Checking the sender's real address and avoiding links in unexpected messages reduce the risk. Companies add multi-factor authentication because even a stolen password is then not enough to log in.",
     [("What does a phishing email try to do?", "Trick people into revealing details", "Repair computers", "Deliver parcels", "Speed up networks", "Stated."), ("What tactic is common?", "Creating urgency", "Offering nothing", "Using no links", "Being very slow", "Stated."), ("Which precaution is stated?", "Checking the sender's real address", "Replying to all emails", "Sharing passwords", "Clicking links fast", "Stated."), ("Why use multi-factor authentication?", "A stolen password alone is not enough", "Passwords become unnecessary to remember", "It removes all email", "It stops all spam", "Stated."), ("The author's tone is", "Informative", "Humorous", "Angry", "Poetic", "It explains facts."), ("A good title is", "Recognising and Reducing Phishing", "How to Fish", "Email Marketing Tips", "Why Passwords Are Useless", "It matches the content.")]),
]
rc = []
for passage, qs in PASSAGES:
    for q, a, x, y, z, why in qs:
        rc.append((f"**Passage.** {passage}\n\n**Question.** {q}", a, x, y, z, why))
hand(C, "Reading comprehension", rc)
SUMMARY = [
    ("Regular backups protect a company from losing data. But backups that have never been tested may fail when needed. Teams should restore from them regularly.", "Backups are only useful if tested by restoring them", "Backups should be avoided", "Testing is costly", "Companies never lose data"),
    ("Cities are planting trees to cool streets. Shaded roads can be several degrees cooler. Trees also absorb rain and improve the air.", "City trees cool streets and bring other benefits", "Trees cause floods", "Roads should be hotter", "Rain is harmful"),
    ("Students often reread notes, but testing oneself is more effective. Recalling information strengthens memory. Short, regular quizzes work well.", "Self-testing beats rereading for learning", "Rereading is the best method", "Quizzes harm memory", "Notes must be long"),
    ("Small shops survive by knowing their customers. They offer personal service that big chains cannot match. Many also now sell online.", "Small shops compete through personal service and online sales", "Big chains have closed", "Customers hate shops", "Online sales are illegal"),
    ("Eating late at night can disturb sleep. The body must digest food when it should be resting. An early, lighter dinner helps.", "Late meals disturb sleep, so eat earlier and lighter", "Dinner should be skipped forever", "Food improves all sleep", "Night is for digestion only"),
    ("Code reviews catch bugs, but they also spread knowledge. Junior developers learn from feedback, and seniors see other approaches.", "Code reviews improve both quality and team learning", "Reviews only slow teams", "Juniors should not code", "Seniors never learn"),
    ("Electric cars have no tailpipe emissions. Their total benefit, though, depends on how the electricity is produced. Coal-heavy grids reduce the gain.", "Electric cars' benefit depends on the power source", "Electric cars emit more than all others", "Coal is clean", "Tailpipes improve air"),
    ("Monsoon rains feed India's farms. A weak monsoon hurts crops and raises food prices. Irrigation reduces but does not remove this risk.", "India's food supply and prices depend heavily on the monsoon", "The monsoon is unimportant", "Irrigation removes all risk", "Food prices never change"),
    ("Passwords are often reused across websites. When one site is breached, attackers try them elsewhere. Password managers solve this by creating unique passwords.", "Reused passwords are risky, and managers help avoid this", "Passwords should be shared", "Breaches never spread", "Websites do not need passwords"),
    ("Libraries are changing. Many now lend e-books, host events and offer free internet. They remain useful even in the digital age.", "Libraries stay relevant by offering new services", "Libraries have disappeared", "E-books are banned", "The internet replaced all events"),
    ("Sleep-deprived drivers react as slowly as drunk ones. Many road accidents happen late at night for this reason. Rest breaks reduce risk.", "Tired driving is dangerous, and breaks help", "Night roads are empty and safe", "Drunk driving is safe", "Accidents are random"),
    ("A startup should test demand before building. A simple prototype shows whether customers care. This avoids wasting months on unwanted features.", "Test demand early to avoid wasted work", "Build everything first", "Customers never care", "Prototypes waste months"),
    ("Coral reefs support a quarter of marine species. Warmer seas cause them to bleach and die. Protecting them requires reducing emissions and local damage.", "Reefs are vital and threatened, and need protection", "Reefs prefer warm seas", "Few species live in reefs", "Emissions help coral"),
    ("Writing clear commit messages takes a minute. It can save hours later, when someone needs to know why a change was made.", "Clear commit messages save time later", "Commit messages waste hours", "Nobody reads history", "Changes need no reasons"),
    ("Handwashing is one of the cheapest health measures. It greatly reduces the spread of infections. Schools teaching it see fewer absences.", "Handwashing is a cheap and effective health measure", "Handwashing is costly", "Schools should close", "Infections cannot be reduced"),
]
hand(C, "Paragraph summary", [(f"Which is the best summary?\n\n{p}", a, x, y, z, "It captures the main point and leaves nothing essential out.") for p, a, x, y, z in SUMMARY])
hand(C, "Critical reasoning (verbal)", [
    ("\"This shop must be the best, as it has the longest queue.\" What assumption does this make?", "A long queue means high quality", "Queues are short elsewhere", "Everyone likes waiting", "The shop has few staff", "It may just be slow service."),
    ("\"Our sales rose after hiring Priya, so she caused the rise.\" What weakens this?", "A festival season began at the same time", "Priya is new", "Sales are recorded daily", "The shop has a website", "Another explanation."),
    ("\"Nobody has proved this claim false, so it is true.\" What is the flaw?", "Lack of disproof is not proof", "It is too short", "Claims cannot be true", "It uses \"nobody\"", "An appeal to ignorance."),
    ("\"Phones cause poor grades, as students with phones score lower.\" What should be checked first?", "Whether other factors explain the difference", "Phone colours", "The price of phones", "Exam paper size", "Correlation is not causation."),
    ("What most strengthens \"Tutoring improves scores\"?", "Randomly chosen tutored students improved more than others", "Tutors like teaching", "Scores are printed", "Some students study", "A randomised comparison."),
    ("\"He cannot be right about tax, as he is rude.\" What is the flaw?", "It attacks the person, not the argument", "Tax is simple", "He is polite", "It is too logical", "An ad hominem argument."),
    ("\"Everyone is buying this, so it must be good.\" What is the flaw?", "Popularity does not prove quality", "Nobody buys things", "It is too expensive", "It uses the word good", "A bandwagon appeal."),
    ("\"If we allow one late submission, everyone will always be late.\" What is the flaw?", "It assumes an extreme chain of events", "It is correct", "It is a fact", "It is about time", "A slippery slope."),
    ("A survey of gym members finds that 90% exercise regularly. Why can't this describe all adults?", "Gym members are not a representative sample", "90 is a high number", "Gyms are closed", "Exercise is unhealthy", "Sample bias."),
    ("\"Sales are down, so the marketing team must be failing.\" What is assumed?", "Marketing is the main cause of the fall", "Sales cannot fall", "The market is growing", "The product is free", "It ignores other causes."),
    ("\"Coffee drinkers live longer, so coffee extends life.\" What is the best question to ask?", "Do coffee drinkers differ in other ways?", "What colour is coffee?", "Who invented coffee?", "Is coffee hot?", "It looks for confounders."),
    ("\"This drug must be safe, as it is natural.\" What is the flaw?", "Natural things are not automatically safe", "Drugs are not natural", "It is about drugs", "Safety is impossible", "An appeal to nature."),
    ("Which is a fact, not an opinion?", "Water boils at 100 °C at sea level", "Summer is the best season", "Cricket is the most exciting sport", "Blue is a lovely colour", "It can be checked."),
    ("\"My grandfather smoked and lived to 95, so smoking is harmless.\" What is the flaw?", "One case does not outweigh wide evidence", "He lived too long", "It is about family", "95 is a small number", "An anecdote is not a general rule."),
    ("\"The plan succeeded because it was bound to succeed.\" What is the flaw?", "It is circular", "It is about plans", "It is too detailed", "It uses numbers", "The reason merely repeats the claim."),
])
