from claude_utils import get_full_resume_review

resume_text = """
('[PERSON_1]   [ADDRESS 1] • New York, NY, 10128 • [EMAIL_16] • [PHONE_17] • 
LinkedIn • GitHub EDUCATION Harvard University                                              
Cambridge, MA A.B. Candidate, Computer Science and Statistics           
Expected graduation: May 2026 ● 3.98 GPA. Coursework: [PERSON_2], 
Graduate-level Data Science, Data Structures and Algorithms, Probability, 
Statistical Inference, Linear Models, Systems Programming. Spring 2025: Deep 
Statistics for Sustainable Development, Causal Inference, Spatial Statistics. 
Fall 2025 (intended): Causal Inference with Applications. SKILLS Programming: 
Python ([PERSON_3], Keras, Flask, Numpy, [PERSON_4], [PERSON_5], API development), 
C/C++, R, JavaScript (React), HTML/CSS, SQL. Proficient in web development, 
data analysis, AI/ML, [PERSON_6], NLP, and quantum computing. Foundational: 
Strong initiative, problem solving, teamwork, and communication. Strong quantitative 
and qualitative analytical skills. RESEARCH EXPERIENCE Kempner Institute for the 
Study of Natural and Artificial Intelligence, Harvard University     Cambridge, 
MA Research Intern                  September 2024 – December 2024 ● Engineered, 
implemented, and extended Bayesian data filtering algorithms in Python for Language 
Model pre-training. Atmospheric Chemistry Modeling Group, Harvard University                              
Cambridge, MA Research Intern, PRISE Fellow                                 
June 2023  –  December 2024 ● Created a novel methodology analyzing high-resolution 
geospatial data to project smoke risk and public health impacts from Western United 
States wildfires. Developed a Google Earth Engine software tool using R and JavaScript 
for land management practitioners to simulate these impacts. Results in revision for 
journal publication in ES&T (tool, preprint). ● Presented findings at AGU 2023, the 
largest gathering of environmental scientists in the U.S. with 22,000+ scientists 
in attendance. Selected as one of 12 presenters from AGU 2023 to present at the 
post-conference Climate and Health Showcase.  Salata Institute for Climate and 
Sustainability, Harvard University                             Cambridge, MA Research Assistant, 
Seamless EV Charging Project                            September 2023  –  May 2024 
● Developed a data scraping and analysis pipeline in Python assessing real-time 
data availability for 1,500+ electric vehicle chargers. Prepared results to present 
to White House stakeholders including the Director of the National Economic Council, 
along with EV charging providers, manufacturers, and policymakers at the Salata 
Institute’s Stakeholder Roundtable. Economics Department, Harvard University                                            
Cambridge, MA Research Assistant                                     January – 
May 2023 ● Developed, trained, and evaluated a transformer-based topic classification 
NLP model in Python using thousands of historical newspaper articles within an 
end-to-end deep learning pipeline to catalyze social science research. [PERSON_7], 
Harvard Forest                        Petersham, MA; Remote Research Intern, 
Harvard Forest Winter Internship Program                              January – 
May 2023 ● Analyzed over 2 million rows of ground sensor and LiDAR data, 
implemented regression models, and conducted significance testing in R to 
investigate the effect of Eastern Hemlock decline on understory microclimates 
at the Harvard Forest. WORK EXPERIENCE The [PERSON_8] Group                                     
New York, NY Summer Analyst                              June – August 2024 ● 
Evaluated potential investment opportunities aligned with [PERSON_8]’s investment 
thesis combining a qualitative and quantitative approach. Identified 40 short-listed 
opportunities to proceed with due diligence. ● Created a data mining methodology in Python 
to automate company sourcing, allowing the investment team to save 10 hours of manual work 
weekly. Automated sourcing of over 2000 companies in the climate adaptation and 
resilience sector to date.  ● Designed concrete equity and sustainability impact 
metrics for a Brazilian healthcare diagnostics company synthesizing findings from 
scientific literature, company documents, and government documents. [PERSON_9] 
AND ACTIVITIES Harvard Computer Society                                   Cambridge, 
MA Co-President (Jan 2025 – Present), Co-Director of Professional Development 
(Jan 2024 – Dec 2024)      January 2024 – Present ● Lead Harvard’s largest and 
oldest computer science student organization with over 400 members. ● Organized 
and ran eleven professional development events featuring panelists from Google, 
Microsoft, [PERSON_10], Hudson River Trading, [PERSON_11], Codeium, Robust 
Intelligence, and Pear.[PERSON_12]. Harvard ReCompute                                    
Cambridge, MA Co-President (Jan 2025 – Present), [PERSON_13] (Jan 2024 – Dec 2024)              
January 2024 – Present ● Lead a student organization focused on the responsible 
use of AI and other technologies. ● Organized and ran four professional development 
events featuring panelists from Microsoft, Amazon, Harvard, MIT, and the Responsible 
Innovation Labs. Grew the email list from 100 to 200 members in one semester. IBM                                                           
Remote Accelerate Program Software Developer Track Participant                            
June 2024 – July 2024 ● Built an end-to-end to-do list application using React, 
Express.JS, IBM Cloudant, and MongoDB. Accepted within the top 5% of over 10,000 
applicants to a highly selective 8-week virtual learning course led by IBM 
software developers. AWARDS AND RECOGNITION ● Recipient, 2023-2024 Detur Book 
Prize for outstanding academic achievement in the first three semesters. ● 2023 
[PERSON_14] for outstanding academic achievement in the first two semesters. 
● Nominee, [PERSON_15] for the most promising scholar in the Class of 2026. 
● Winner, KODING with KAGR 2023, a sports analytics and consulting competition 
sponsored by the Kraft Analytics Group.'
"""

# Replace this with the job description you want to test against
job_description = """
The Internship

The Summer Intern Program is an internship for talented, highly motivated students 
in the class of 2027.  As professional members of our firm, Summer Interns:

Work in teams to solve high level business problems facing Fortune 1000 clients

Structure and carry out essential research and data management

Lead complex quantitative, strategic and financial analyses of corporations and 
businesses

Participate on a project team with significant exposure to senior leadership of 
the firm

Receive mentorship throughout the program

Participate in a week of training at the beginning of the summer

Receive broad exposure to a variety of industries including: Automotive, Aviation, 
Communications, Financial Services, Energy, Health & Life Sciences, Media, Retail, 
Surface Transportation and Technology.

Why join us?

Come aboard if you are excited by challenges and want to work across different 
cultures.

We want you to step out of your comfort zone and embrace your curiosity.

Our consultants learn on the job and receive formal training to develop their 
communication, presentation, analytical, and client management skills.

You’ll find genuine colleagues who stand by their beliefs and measure success by 
the lasting impact you create together.

We believe in flexibility, including the opportunity of hybrid working. You are 
also invited to join our employee resource groups and social activities.

Immediate impact, continuous challenge

You’ll work on challenging projects that have a significant impact on clients, 
industries, and societies from day one. No two weeks are ever the same.

We’ll ask you to be brave, challenging the status quo and constantly striving to 
build something new to shape our firm and the world around us. 

You’ll be a contributing team member from the start, building trust-based 
relationships with stakeholders and delivering breakthrough impact.

Your learning curve will be steep, with each project offering new opportunities 
to expand your toolkit and to team with specialists who have deep subject-matter 
and technical expertise.

Click here to learn even more.

Chart your course; we support the journey

Various colleagues will guide and coach you throughout your career, including a 
dedicated buddy, a career adviser, and your talent manager.

We care deeply about sustainable work-life quality and provide for career 
flexibility with a variety of programs including sabbaticals, non-profit fellowships, 
and externships.

We hire you to be you

Our open, inclusive, and down-to-earth culture will enable you to bring your 
best authentic self to work.

You’ll work alongside down-to-earth colleagues who do serious work, but don’t 
take themselves too seriously.

There’s no corporate mold to fit and hierarchy doesn’t get in the way.

We do not let artificial barriers stand in the way of your personal career 
progression.

Qualifications

We look for initiative, intuition and creativity with a strong background in 
problem solving and analytics. We do not require a specific academic major or 
industry experience and we value extracurricular activities and evidence of 
leading an interesting and impactful life outside of studies/work. One of the 
best things we can do for our clients and ourselves is to recruit a diverse group 
of people who bring a broad range of strengths and backgrounds to their roles.
"""

response = get_full_resume_review(resume_text, job_description)
print(response)
