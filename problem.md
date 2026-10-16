Internship Assignment
AI Knowledge Graph & Cloud Engineering Internship
Deadline: Monday, 19 October 2026, 11:59 pm
Hello, and thank you for your interest in joining us.
Congratulations on being shortlisted. This assignment has two questions:
- Question 1: Knowledge Graph
- Question 2: Cloud (taking a small AI app live)
Please attempt both. Question 1 should take about 3 hours and Question 2 about 2 to 3 hours. You
are welcome to spread the work over a few days.
Important note on using AI tools
You are free to use AI tools such as ChatGPT, Claude or Copilot. We use them too. However,
please keep the following in mind:
1. Every answer will be checked thoroughly.
2. After you submit, we will have a short call (about 25 to 30 minutes) in which you will explain
your work in your own words, answer a few "what if" questions, and may be asked to make a
small change to your work during the call.
3. If you cannot explain something you have submitted, we will treat it as not done.
So please use AI as a helper, but the thinking should be your own. A simple answer that you truly
understand is better than a perfect answer that you cannot explain. Being honest about how you used
AI will never count against you.
Question 1: Knowledge Graph
Below is a short problem we'd like you to think over. There's no single correct answer — we're
interested in how you reason, not in a model solution.
A seasoned loan officer reviews two applications for a small-business loan. At a glance they look
similar — comparable credit scores, comparable collateral, the same amount requested. Yet she
approves one and rejects the other. The reason isn't a big, obvious number. It's a small detail in the
application — something a beginner would skim past — that she, with years of experience, reads as
decisive.
Your task: model this situation as a knowledge graph, built in Python. Use whatever you're
comfortable with — NetworkX, RDFLib, or even plain classes and dictionaries; we care far more
about how you model it than which library you choose. The graph should not merely store the facts
in the applications. It must capture the officer's judgment — how a seemingly minor fact gets
connected, through knowledge she carries that the form never states, to a consequence for whether
the loan is repaid.
Please send back three things. First, the code — as a GitHub repo, a Colab notebook, or a plain .py
file with a short readme on how to run it. Second, a note of no more than half a page: why you
modelled the judgment the way you did, and, importantly, what you chose to leave out and why.
Third, be ready to walk us through it on a brief call.
Using AI tools to help write the code is completely fine — we all do. What we're assessing is
whether you genuinely understand how a knowledge graph can represent reasoning, not just facts.
Page 1
Please send your response by Monday, 19 October, 11:59 pm. A considered answer matters more
than a fast one.
We look forward to seeing how you approach it.
Question 2: Cloud — Taking a Small AI App Live
Background
We have a small AI web application that runs on one computer (Ubuntu Linux) in an office. The
computer has an NVIDIA graphics card (GPU) with 24 GB of memory. The application has five
parts:
1. A website (frontend)
2. A Python API (backend)
3. A PostgreSQL database
4. A background worker
5. An open-source AI model (Llama 3.1, 8 billion parameters), running on the GPU
In front of all of this sits Caddy, a program that receives web traffic and takes care of HTTPS (the
padlock in the browser) for the address app.example.in. About 20 people use the app today. It stores
private case notes about the people it helps, so security is important.
Part A: The padlock has broken (find the problem)
On Monday morning, users report that their browser shows the warning "Your connection is not
private". You log in to the office computer and run a few checks. The results are given below, with a
short note on what each check does.
One more fact: in early September, the internet provider replaced the office router.
Check 1 — Where does our website address point?
$ dig +short app.example.in
203.0.113.24 <-- this is the office's public IP address (correct)
Check 2 — Is the app itself working on the computer?
$ curl -s http://localhost:8000/health
{"status":"ok"}
Check 3 — Is Caddy running?
$ systemctl status caddy
 caddy.service - Caddy
 Active: active (running) since Wed 2026-09-30 11:02:17 IST
Check 4 — Which certificate are visitors receiving, and what are its dates?
$ echo | openssl s_client -connect app.example.in:443 -servername app.example.in \
 2>/dev/null | openssl x509 -noout -dates
notBefore=Jul 14 09:12:03 2026 GMT
notAfter=Oct 12 09:12:02 2026 GMT
Check 5 — The latest error in Caddy's log (shortened)
$ journalctl -u caddy --since "2026-09-14" | grep -i error | tail -1
... "msg":"could not get certificate from issuer",
"error":"[app.example.in] solving challenges: ... acme: error: 403 ::
urn:ietf:params:acme:error:unauthorized :: Invalid response from
http://app.example.in/.well-known/acme-challenge/kX9...: 401"
Check 6 — Opening the site from outside the office (using a phone's mobile data)
$ curl -sI http://app.example.in
HTTP/1.1 401 Unauthorized
Server: micro_httpd
WWW-Authenticate: Basic realm="Broadband Router"
Page 2
Please answer:
1. What is the real cause of the problem? Explain it step by step, and mention which check results
support your answer.
2. How would you fix it today? List the steps in order. If there is more than one way, say which
one you would choose and why.
3. What would you set up so that this never surprises us again? In other words, how would we find
out before our users do?
4. Do you notice anything else in these results that worries you?
Part B: Moving to the cloud (make a plan)
We now want the app to be available on the internet for about 200 users, running reliably, with a
total budget of Rs. 25,000 per month. Write a short plan (maximum 1.5 pages; bullet points are
fine) that answers the following:
1. Where should it run? Compare at least two options, for example:
(a) keep everything on the office computer, but make it more reliable;
(b) rent a GPU server from a cloud or GPU hosting company; or
(c) a mix: the website and database on a cheap cloud server, while the AI model stays on the
office GPU and connects securely.
Choose one and explain why, keeping the budget in mind.
2. GPU calculation (please show your working):
(a) Roughly how much GPU memory does an 8-billion-parameter model need when stored in
16-bit form? And in 4-bit form? Will it fit in 24 GB?
(b) Suppose each of the 200 users asks about 5 questions per working day, 80% of these come
between 10 am and 6 pm, and each answer takes about 10 seconds of GPU time. Is one
GPU enough? What happens if 10 people ask a question at the same moment?
3. Monthly cost: a small table of what you would pay for. For each item, write the price, the link
where you found it, and the date you checked it.
4. Keeping the data safe: how you would take backups (what, where and how often) and check
that a backup can actually be restored; how you would protect passwords and keys; and how
you would control who can log in to the server.
5. Knowing when something breaks: what you would monitor, and how the team would be
alerted.
6. Moving day: how you would move from the office computer to the new setup without losing
any data, and roughly how long the app would be down.
Please also draw a simple diagram of your setup by hand (boxes and arrows on paper are enough)
and take a photo of it.
Part C (optional): For those comfortable with Docker
Write a docker-compose.yml file for your chosen setup (all five parts plus Caddy), with the data
saved in volumes, GPU access for the AI model, and health checks. Also write a small script (bash
or Python) that takes a daily database backup and keeps only the last 7 backups. This part is optional
and skipping it will not count against you. A good attempt will earn extra credit.
Page 3
Page 4
What to Submit
Please send one link (a GitHub repository or a Google Drive folder) through Internshala chat before
the deadline. It should contain the following.
For Question 1:
- Your code, with a short readme on how to run it (as described in Question 1).
- Your half-page note.
- A photo of a hand-drawn sketch of your graph. A rough sketch is perfectly fine.
For Question 2:
- Your answers to Part A and Part B (as a Word, PDF, text or markdown file).
- A photo of your hand-drawn diagram.
- The Part C files, if you attempted it.
A short "How I worked" note (half a page to one page), covering:
1. Which AI tools you used, and for what. Please mention at least one time when you did not
accept what the AI suggested, and why.
2. A few dated points on how your work progressed: what you tried first, what did not work, and
what you changed.
3. In one sentence, in your own words: what is the difference between a graph that stores facts and
a graph that stores reasoning?
If you use GitHub, please save (commit) your work as you go, rather than uploading everything at
once at the end.
About the Call
After you submit, we will schedule a call of about 25 to 30 minutes. During the call, you will be
asked to:
- explain your graph and your cloud plan in your own words;
- walk us through a part of your code that we choose;
- tell us how your answer would change if the situation changes (for example, a new detail in a
loan application, or a smaller budget);
- tell us where AI helped you and where it got things wrong.
To help us schedule the call, please include the following details along with your submission (in
your Internshala chat message, or in a short file named contact.txt in your folder):
1. Contact number (preferably one that is also on WhatsApp).
2. When we can contact you: the days and times that suit you for a call over the next week (for
example, "weekdays after 5 pm" or "Saturday, 10 am to 1 pm").
3. Your profile link, if you have an active one.
If anything in this assignment is unclear, please ask us on Internshala chat. Asking good questions is
a good sign.
Deadline: Monday, 19 October 2026, 11:59 pm.
Thank you, and all the best.
