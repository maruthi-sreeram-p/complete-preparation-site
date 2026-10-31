"""Reasoning that needs judgement: written situations turned into questions by fixed logical forms."""
from core import Q, T

C = "Verbal Reasoning"
NAMES = ["Asha", "Bala", "Chitra", "Dev", "Esha", "Farhan", "Gita", "Hari", "Isha", "Jay", "Kiran", "Lata", "Mohan", "Nisha", "Om", "Priya", "Ravi", "Sara", "Tara", "Uma"]
GROUPS = [("engineers at the firm", "complete security training"), ("students in this college", "wear an ID card"), ("members of the club", "pay a yearly fee"), ("drivers on this route", "carry a permit"), ("doctors at this hospital", "attend the weekly review"), ("players in the team", "take a fitness test"), ("tenants in this building", "park in the basement"), ("employees in this branch", "use the new portal"), ("visitors to the museum", "sign the register"), ("teachers at this school", "submit lesson plans"), ("shareholders of the company", "get the annual report"), ("pilots at this airline", "train twice a year")]
YES, NO = "Yes, it follows", "No, it does not follow"
OTHERS = ["It follows only if the group is small", "It follows only if everyone agrees"]


@T(C, "Statement & conclusion")
def _(r):
    (g, p), m = r.choice(GROUPS), r.choice(NAMES)
    forms = [
        (f"All {g} must {p}. {m} is one of the {g}.", f"{m} must {p}.", YES, "A general rule applies to each member."),
        (f"Some {g} {p}.", f"All {g} {p}.", NO, "\"Some\" does not mean \"all\"."),
        (f"Most {g} {p}.", f"Some {g} {p}.", YES, "If most do, then at least some do."),
        (f"No {g} {p}. {m} is one of the {g}.", f"{m} does not {p}.", YES, "\"No\" covers each member."),
        (f"Only {g} {p}. {m} does {p.split()[0]} {' '.join(p.split()[1:])}.", f"{m} is one of the {g}.", YES, "Only members can do it."),
        (f"Only {g} {p}. {m} is one of the {g}.", f"{m} must {p}.", NO, "\"Only\" limits who can; it does not say that every member does."),
        (f"All {g} {p}.", f"Nobody else can {p}.", NO, "The statement says nothing about people outside the group."),
        (f"Most {g} {p}. {m} is one of the {g}.", f"{m} definitely does {p.split()[0]} {' '.join(p.split()[1:])}.", NO, "\"Most\" allows exceptions."),
    ]
    s, c, a, why = r.choice(forms)
    return Q(f"Statement: {s} Conclusion: {c} Does the conclusion follow?", a, why, [YES if a == NO else NO] + OTHERS)


ADVICE = """Hire more nurses to shorten hospital queues|more nurses can shorten the queues
Lower the fee to attract more students|a lower fee can attract students
Add a search box to help users find products|a search box can help users find products
Run the sale in December to raise revenue|a December sale can raise revenue
Plant trees along the road to cool the area|trees can cool the area
Send reminders to reduce missed appointments|reminders can reduce missed appointments
Install lights on the path to improve safety|lights can improve safety on the path
Offer night classes to reach working adults|night classes can reach working adults
Cache this response to speed up the page|caching can speed up the page
Run more buses to cut road traffic|more buses can cut traffic
Teach first aid in schools to save lives|first aid teaching can save lives
Add tests to reduce bugs in releases|tests can reduce bugs
Simplify the form to get more sign-ups|a simpler form can bring more sign-ups
Advertise on radio to reach farmers|radio can reach farmers
Open a branch here to serve the town|a branch can serve the town
Offer a discount to clear old stock|a discount can clear old stock
Give staff flexible hours to reduce resignations|flexible hours can reduce resignations
Publish the rules to reduce confusion|published rules can reduce confusion
Repair the roads to lower accident rates|better roads can lower accidents
Provide free meals to raise school attendance|free meals can raise attendance
Use a queue to smooth traffic spikes|a queue can smooth traffic spikes
Translate the app to reach new users|translation can reach new users
Add a helpline to support new customers|a helpline can support customers
Ban phones in class to improve attention|a phone ban can improve attention
Build a footbridge to prevent road accidents|a footbridge can prevent accidents
Add a bonus to improve staff performance|a bonus can improve performance
Reduce sugar in meals to improve health|less sugar can improve health
Open the library at night to help students study|longer hours can help students study
Start a recycling drive to reduce waste|recycling can reduce waste
Limit login attempts to stop password guessing|login limits can stop password guessing
Train the guards to reduce theft|trained guards can reduce theft
Hold mock tests to improve exam scores|mock tests can improve scores
Add subtitles to reach deaf viewers|subtitles can reach deaf viewers
Improve packaging to reduce damaged goods|better packaging can reduce damage""".split("\n")
NOT_ASSUMED = ["The step will cost nothing at all", "No other step could also help", "Everyone will support the step"]


@T(C, "Statement & assumption")
def _(r):
    s, a = r.choice(ADVICE).split("|")
    if r.random() < .5:
        return Q(f"Statement: \"{s}.\" What is assumed?", a[0].upper() + a[1:], "The advice only makes sense if this is true.", NOT_ASSUMED)
    wrong = r.choice(NOT_ASSUMED)
    return Q(f"Statement: \"{s}.\" Which of these is NOT assumed?", wrong, "The advice does not depend on this stronger claim.", [a[0].upper() + a[1:], "The goal in the statement matters to someone", "The step can actually be carried out"])


ARGS = """Should college attendance be tracked?|it helps identify students who need support|my friend dislikes roll calls
Should plastic bags be banned?|they pollute rivers and harm animals|my uncle sells plastic bags
Should offices allow remote work?|it saves commute time and many roles can be done from home|my neighbour likes to sleep late
Should the voting age be lowered?|younger citizens are also affected by laws|teenagers have nice handwriting
Should school uniforms be required?|they reduce visible differences between students|uniforms are usually blue
Should code reviews be required?|they catch defects when they are cheap to fix|reviews are boring
Should smoking in public be banned?|second-hand smoke harms other people|smoke has a strange colour
Should the city build a metro?|it can cut road congestion and pollution|trains are longer than cars
Should exams be held online?|they can reach students in remote places|everything modern is better
Should vaccines be subsidised?|wider vaccination reduces disease for everyone|needles are thin
Should banks open on Sundays?|working people could use them on holidays|Sunday comes after Saturday
Should junk food ads for children be limited?|children are easily influenced and obesity is rising|cartoons are colourful
Should parks stay open at night?|working people get more time for exercise|the moon is visible at night
Should libraries go digital?|more readers can access books at lower cost|paper is white
Should helmets be compulsory?|they greatly reduce deaths in accidents|helmets look odd
Should mobile phones be banned in exams?|they make cheating easier|phones have small screens
Should the company give paid leave?|rested employees work better and stay longer|the manager already took a holiday
Should tax be cut on medicines?|it makes treatment more affordable|medicines come in small boxes
Should rainwater harvesting be compulsory?|it protects groundwater in dry regions|rain is wet
Should passwords expire?|it limits the damage from old leaks|changing passwords annoys me
Should schools teach coding?|it builds problem-solving and job skills|computers have keyboards
Should coaching centres be regulated?|students need protection from false claims|coaching centres have many chairs
Should villages get free internet?|it opens access to education and services|villages are quiet
Should single-use cups be taxed?|the tax would discourage waste|cups are round
Should the working week be four days?|trials suggest it may improve wellbeing without losing output|everybody loves Fridays
Should restaurants show calorie counts?|customers can make informed choices|menus are printed
Should old buildings be preserved?|they hold cultural and historic value|old buildings have old doors
Should traffic fines be raised?|higher fines can deter dangerous driving|my cousin got a fine once
Should the cafeteria offer healthy meals?|better food supports staff health|the cafeteria has large tables
Should cities add cycle lanes?|they make cycling safer and reduce traffic|bicycles have two wheels
Should companies publish salary ranges?|it reduces pay gaps and saves hiring time|numbers are easy to print
Should students get career counselling?|it helps them make informed choices|counsellors have offices
Should backups be tested each month?|untested backups may fail when needed|backups are boring to run
Should elections be held on holidays?|more people may be free to vote|holidays are fun""".split("\n")


@T(C, "Statement & argument")
def _(r):
    q, s, w = r.choice(ARGS).split("|")
    if r.random() < .5:
        return Q(f"{q} Argument: Yes, because {s}. Is this argument strong or weak?", "Strong", "It gives a relevant, general reason linked to the outcome.", ["Weak", "Irrelevant to the question", "Cannot be judged"])
    return Q(f"{q} Argument: Yes, because {w}. Is this argument strong or weak?", "Weak", "It is a personal, trivial or irrelevant point.", ["Strong", "Strong only for experts", "Cannot be judged"])


ACTIONS = """A city's main bridge has developed cracks|close or restrict it and inspect it
A production service starts failing after a release|roll back the release and investigate
Many students failed a new exam|review the teaching and the exam, and offer support
A food stall is found selling spoiled food|stop the sale, inspect it and act under the rules
A team keeps missing its deadlines|find out the causes with the team
Heavy rain may flood low-lying areas|warn residents and prepare evacuation
Customer data may have leaked|contain it, assess it and notify as required
Accidents have risen at one junction|study the junction and improve signals or signs
A key employee has resigned with notice|arrange a handover and record their knowledge
A school's drinking water is contaminated|stop its use, provide safe water and find the source
A website slows badly during sales|load test it, fix the bottlenecks and scale
An employee is repeatedly late|talk to the employee and understand why
A vaccine shortage is reported in a district|move stocks there and prioritise those at risk
A factory is polluting a river|inspect it and enforce the pollution rules
Complaints about a new app feature are rising|review the feedback and fix the main issues
A bus route is always overcrowded|study demand and add services at peak times
A power line fell during a storm|cordon off the area and call the power company
Cheating is reported in an online test|investigate the evidence and strengthen the test process
A hospital is running out of beds|shift stable patients and arrange extra capacity
Fake notices are spreading about a college|publish a correction and report the source
A building's fire alarm has stopped working|repair it at once and arrange a temporary watch
A shipment arrives damaged|record the damage and raise a claim with the carrier
A village well has dried up|arrange tankers and plan a longer-term water source
A popular bank app is down|inform users, restore service and find the cause
Crop disease is spreading in a region|alert farmers and send experts with advice
A teacher reports repeated bullying in a class|investigate and support those affected
A new hire is struggling with the work|give mentoring and clear feedback
Prices of essentials are rising fast|study the causes and check for hoarding
Roads are full of potholes after rain|inspect them and schedule repairs by priority
A server's disk is nearly full|find what is using it, then clean up or add storage
An elevator stops between floors in an office|call the service team and reassure those inside
A public park is unsafe after dark|add lighting and patrols
A library's books are often not returned|send reminders and review its lending rules
A customer reports being charged twice|verify it and refund the duplicate""".split("\n")
BAD = ["Ignore it and hope that it goes away", "Publicly blame someone before checking any facts", "Hide the problem from everyone affected", "Shut everything down permanently", "Do nothing until next year"]


@T(C, "Course of action")
def _(r):
    p, a = r.choice(ACTIONS).split("|")
    a = a[0].upper() + a[1:]
    if r.random() < .5:
        return Q(f"Situation: {p}. What is the most suitable course of action?", a, "It deals with the problem directly and proportionately.", r.sample(BAD, 3))
    bad = r.choice(BAD)
    return Q(f"Situation: {p}. Which is NOT a sensible course of action?", bad, "It leaves the problem unsolved, or makes it worse.", [a, "Check the facts before deciding further steps", "Keep those affected informed"])


CAUSES = """Heavy rains destroyed the crops|Vegetable prices rose sharply
The factory closed|Hundreds of workers lost their jobs
The server ran out of memory|The service crashed
The government cut fuel tax|Fuel became cheaper
The exam paper was unusually easy|Many students scored full marks
The river overflowed|Nearby villages were flooded
The query had no index|The page took eight seconds to load
There was a power cut in the town|Street lights went off
The bridge collapsed|Traffic was diverted through the old road
A new metro line opened|Road traffic in the area fell
The company raised salaries|Fewer employees resigned
The bus driver fell ill|The morning service was cancelled
A virus spread through the city|Hospitals became crowded
Interest rates were increased|Home loans became more expensive
The monsoon failed|Reservoir levels fell sharply
The school introduced free meals|Attendance rose
The pipeline burst|The area had no water for two days
A cyclone hit the coast|Fishing boats stayed in harbour
The airline reduced its flights|Ticket prices rose
The app added a dark mode|Night-time usage increased
Police increased patrols|Thefts in the area declined
The shop stopped giving credit|Its sales to regular customers fell
The company leaked customer data|Many customers closed their accounts
The road was widened|Travel times became shorter
Wages rose faster than prices|People spent more on holidays
The dam released water|Downstream fields were submerged
The team lost its captain to injury|It lost the next three matches
The price of petrol doubled|Bus ridership went up
A fire broke out in the warehouse|The stored goods were destroyed
The server certificate expired|Users saw security warnings
The fog was very thick|Many flights were delayed
The school ended the term early|Students went home in March
The factory installed filters|Air quality nearby improved
The city banned plastic bags|Cloth bag sales rose""".split("\n")
CE = ["A is the cause and B is its effect", "B is the cause and A is its effect", "Both are independent", "Both are effects of a common cause"]


@T(C, "Cause & effect")
def _(r):
    c, e = r.choice(CAUSES).split("|")
    if r.random() < .5:
        return Q(f"A: {c}. B: {e}. How are A and B related?", CE[0], "A happened first and leads to B.", [CE[1], CE[2], CE[3]])
    return Q(f"A: {e}. B: {c}. How are A and B related?", CE[1], "B happened first and leads to A.", [CE[0], CE[2], CE[3]])


CORR = """Ice-cream sales|drownings|hot weather
Phone ownership|poor grades|family background
Coffee drinking|long life|income and lifestyle
Shoe size|reading skill in children|age
Firefighters at a scene|damage from a fire|the size of the fire
Hospital visits|illness rates in a town|an ageing population
Umbrella sales|road accidents|rainy weather
Gym membership|higher income|education and free time
Private tuition|higher marks|parents' support
Music lessons|maths scores|family income
Laptop use in class|lower marks|attention and motivation
Early wake-up times|higher salaries|the type of job
Tall buildings|higher wages in cities|city size
Breakfast eating|good grades|home routines
Dog ownership|better health|an active lifestyle
Sports participation|better grades|time management and support
Salad eating|lower heart disease|overall healthy habits
Library visits|longer careers|education and interest
Bigger houses|longer marriages|wealth and age
Cars per family|obesity|income and lifestyle
TV watching|poor sleep|late-night habits
App downloads|sales growth|a seasonal festival
Social media use|exam stress|exam season itself
Number of police|number of crimes|the size of the city
Company size|employee turnover|the type of industry
Ad spending|sales|the festive season
Sunscreen sales|sunburn cases|sunny weather
Air conditioner sales|electricity bills|hot weather
Number of doctors|disease cases|population size
Internet speed|house prices|location in a big city
Bicycle commuting|good health|general fitness habits
Number of churches|number of shops in a town|town size
Tea drinking|exam success|study routines
Shirt colour|interview success|overall preparation""".split("\n")


@T(C, "Critical reasoning")
def _(r):
    a, b, c = r.choice(CORR).split("|")
    k = r.randint(0, 2)
    claim = f"\"{a} and {b.lower()} tend to rise together, so the first must cause the second.\""
    if k == 0:
        return Q(f"{claim} What is the main flaw?", "It treats a correlation as a cause", f"A third factor, such as {c}, may explain both.", ["It uses too few words", "It quotes no famous person", "It is about numbers"])
    if k == 1:
        return Q(f"{claim} Which fact would most weaken this claim?", f"Both are driven by {c}", "A shared cause removes the need for a direct link.", ["Both are widely discussed online", "The data was printed in a table", "The claim was made recently"])
    return Q(f"{claim} Which evidence would best test it?", "A controlled comparison where only that factor changes", "Comparing like with like isolates the cause.", ["A survey of one person", "A popular opinion poll", "A larger font in the report"])


# ------------------------------------------------------------------- decisions: worked out from the rules
OUT = ["Select", "Reject", "Refer to the manager", "Data is inadequate"]


@T(C, "Decision making")
def _(r):
    m = r.choice(NAMES)
    need_s, need_e = r.choice([50, 55, 60, 65, 70]), r.randint(1, 4)
    s, e = r.randint(40, 90), r.randint(0, 7)
    show_s, show_e = r.random() > .12, r.random() > .12
    rule = f"Rule: Select candidates with at least {need_s}% marks and at least {need_e} years' experience. Candidates with lower marks but over {need_e + 3} years' experience are referred to the manager. Reject the rest."
    if show_s and show_e:
        ans = OUT[0] if s >= need_s and e >= need_e else OUT[2] if s < need_s and e > need_e + 3 else OUT[1]
        facts = f"{m} has {s}% and {e} years' experience."
        why = "Check marks first, then experience, against the rule."
    else:
        ans = OUT[3]
        facts = f"{m} has {s}% marks." if show_s else f"{m} has {e} years' experience."
        why = "One of the needed facts is missing."
    return Q(f"{rule} {facts} What is the decision?", ans, why, [o for o in OUT if o != ans])


@T(C, "Decision making")
def _(r):
    m = r.choice(NAMES)
    lim, d = r.choice([7, 10, 14, 15, 30]), r.randint(1, 40)
    rec = r.choice([True, False])
    ans = "Refund" if d <= lim and rec else "Refuse"
    return Q(f"Rule: Refund only if an item is returned within {lim} days with a receipt. {m} returns an item on day {d}, {'with' if rec else 'without'} a receipt. What is the decision?", ans, "Both conditions must hold.", ["Refund" if ans == "Refuse" else "Refuse", "Refer to the manager", "Data is inadequate"])


@T(C, "Decision making")
def _(r):
    m = r.choice(NAMES)
    sal, score = 1000 * r.randint(15, 60), 10 * r.randint(55, 85)
    ms, mc = 1000 * r.choice([20, 25, 30, 35, 40]), r.choice([650, 700, 750])
    ans = "Approve" if sal > ms and score > mc else "Decline"
    return Q(f"Rule: Approve a loan if the salary is over ₹{ms} and the credit score is over {mc}. {m} earns ₹{sal} and has a score of {score}. What is the decision?", ans, "Both conditions must hold, and \"over\" excludes the limit.", ["Decline" if ans == "Approve" else "Approve", "Refer to the manager", "Data is inadequate"])
