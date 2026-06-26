"""
seed.py — Populate the database with demo data for development

Run:
    python seed.py

Creates:
  - 5 user accounts (admin, 2 dept heads, 2 faculty)
  - 5 sample job postings
  - 6 sample applications across different stages
  - Sample notices
"""

from database import SessionLocal, engine
import models
from security import hash_password
from datetime import date

models.Base.metadata.create_all(bind=engine)
db = SessionLocal()


def seed():
    # ── Clear existing data ───────────────────────────────────────────────────
    db.query(models.Notice).delete()
    db.query(models.Application).delete()
    db.query(models.Job).delete()
    db.query(models.User).delete()
    db.commit()
    print("Cleared existing data.")

    # ── Users ─────────────────────────────────────────────────────────────────
    users_data = [
        {"name":"HR Administrator",     "email":"admin@thd.de",     "password":"admin123",  "role":"admin",   "department":"Human Resources"},
        {"name":"Prof. Dr. Müller",      "email":"dept@thd.de",      "password":"dept123",   "role":"dept",    "department":"Computer Science"},
        {"name":"Prof. Dr. Schneider",   "email":"dept2@thd.de",     "password":"dept123",   "role":"dept",    "department":"Marketing"},
        {"name":"Prof. Dr. Wagner",      "email":"prof@thd.de",      "password":"prof123",   "role":"faculty", "department":"AI Research Lab"},
        {"name":"Dr. Fischer",           "email":"faculty2@thd.de",  "password":"prof123",   "role":"faculty", "department":"IT Services"},
    ]

    user_objs = {}
    for u in users_data:
        user = models.User(
            name=u["name"],
            email=u["email"],
            hashed_password=hash_password(u["password"]),
            role=u["role"],
            department=u["department"],
        )
        db.add(user)
        db.flush()
        user_objs[u["email"]] = user
        print(f"  Created user: {u['name']} ({u['role']})")

    db.commit()

    # ── Jobs ──────────────────────────────────────────────────────────────────
    jobs_data = [
        {"title":"Student Assistant – IT Support",    "dept":"IT Services",       "status":"Published","visibility":"internal","hours_per_week":10,"salary":"520","deadline":date(2025,6,20),"rv":"approved","description":"Support students and staff with hardware and software issues on campus.","requirements":"Basic IT knowledge; enrolled at THD."},
        {"title":"Research Assistant (AI/ML)",        "dept":"AI Research Lab",   "status":"Published","visibility":"internal","hours_per_week":12,"salary":"560","deadline":date(2025,6,15),"rv":"pending", "description":"Assist professors with AI/ML research, data collection and paper writing.","requirements":"Python, statistics knowledge."},
        {"title":"Marketing Student Worker",          "dept":"Marketing",         "status":"Published","visibility":"external","hours_per_week":8, "salary":"480","deadline":date(2025,6,30),"rv":"approved","description":"Create content for social media channels and support internal campaigns.","requirements":"Creativity, communication skills."},
        {"title":"Library Assistant",                 "dept":"University Library","status":"Draft",    "visibility":"internal","hours_per_week":8, "salary":"440","deadline":date(2025,7,1), "rv":"pending", "description":"Help students find academic resources and support catalogue management.","requirements":"Organized and reliable."},
        {"title":"Web Developer Student Worker",      "dept":"IT Services",       "status":"Published","visibility":"external","hours_per_week":15,"salary":"600","deadline":date(2025,6,25),"rv":"approved","description":"Maintain and improve the university web presence using modern frameworks.","requirements":"HTML, CSS, JavaScript. React is a plus."},
    ]

    job_objs = {}
    admin_user = user_objs["admin@thd.de"]
    for j in jobs_data:
        job = models.Job(
            title=j["title"], dept=j["dept"], status=j["status"],
            visibility=j["visibility"], hours_per_week=j["hours_per_week"],
            salary=j["salary"], deadline=j["deadline"], rv=j["rv"],
            description=j["description"], requirements=j["requirements"],
            created_by=admin_user.id,
        )
        db.add(job)
        db.flush()
        job_objs[j["title"]] = job
        print(f"  Created job: {j['title']}")

    db.commit()

    # ── Applications ──────────────────────────────────────────────────────────
    it_job     = job_objs["Student Assistant – IT Support"]
    mktg_job   = job_objs["Marketing Student Worker"]
    web_job    = job_objs["Web Developer Student Worker"]

    apps_data = [
        {"job":it_job,   "name":"Anna Schmidt",  "email":"a.schmidt@thd.de",  "sid":"20210001","prog":"Applied Informatics",  "sem":5,"stage":"review",    "score":82,"notes":"","mot":"Interested in IT support...","email_conf":True},
        {"job":it_job,   "name":"Max Huber",     "email":"m.huber@thd.de",    "sid":"20210042","prog":"Business Informatics", "sem":3,"stage":"new",       "score":70,"notes":"","mot":"This role matches my studies...","email_conf":True},
        {"job":mktg_job, "name":"Lisa Wagner",   "email":"l.wagner@thd.de",   "sid":"20200088","prog":"Communication Design", "sem":7,"stage":"interview", "score":90,"notes":"Strong portfolio.","mot":"Marketing is my passion...","email_conf":True,"email_inv":True},
        {"job":it_job,   "name":"David Brown",   "email":"d.brown@thd.de",    "sid":"20210066","prog":"Computer Science",     "sem":4,"stage":"contract",  "score":88,"notes":"Interview went very well.","mot":"IT troubleshooting experience...","email_conf":True,"email_inv":True,"email_ctr":True},
        {"job":web_job,  "name":"Emma Fischer",  "email":"e.fischer@thd.de",  "sid":"20190055","prog":"Media Informatics",    "sem":9,"stage":"hired",     "score":95,"notes":"Excellent candidate.","mot":"5 semesters React experience...","email_conf":True,"email_inv":True,"email_ctr":True},
        {"job":mktg_job, "name":"John Miller",   "email":"j.miller@thd.de",   "sid":"20220012","prog":"International Business","sem":2,"stage":"new",      "score":75,"notes":"","mot":"I love content creation...","email_conf":True},
    ]

    for a in apps_data:
        app = models.Application(
            job_id=a["job"].id,
            applicant_name=a["name"],
            applicant_email=a["email"],
            student_id=a.get("sid",""),
            university="Technische Hochschule Deggendorf",
            program=a.get("prog",""),
            semester=a.get("sem",1),
            motivation=a.get("mot",""),
            stage=a["stage"],
            score=a["score"],
            notes=a.get("notes",""),
            email_confirmation_sent=a.get("email_conf",False),
            email_interview_sent=a.get("email_inv",False),
            email_contract_sent=a.get("email_ctr",False),
        )
        db.add(app)
        # Update job applicant count
        a["job"].applicants = (a["job"].applicants or 0) + 1
        print(f"  Created application: {a['name']} → {a['job'].title}")

    db.commit()

    # ── Notices ───────────────────────────────────────────────────────────────
    notices = [
        {"title":"New application received",    "description":"Anna Schmidt applied for Student Assistant – IT Support.", "color":"#1B3A6B"},
        {"title":"Interview invitation sent",   "description":"Email triggered for Lisa Wagner — Marketing Student Worker.", "color":"#5B2D8E"},
        {"title":"Contract notification sent",  "description":"Contract-ready email sent to David Brown.",                  "color":"#00A3D9"},
        {"title":"Candidate hired",             "description":"Emma Fischer successfully hired as Web Developer.",           "color":"#1E7E4A"},
    ]
    for n in notices:
        notice = models.Notice(**n)
        db.add(notice)
    db.commit()

    print("\n✅ Seed complete! Demo credentials:")
    print("   Admin:   admin@thd.de  / admin123")
    print("   Dept:    dept@thd.de   / dept123")
    print("   Faculty: prof@thd.de   / prof123")
    print("\nSwagger UI: http://localhost:8000/docs")


if __name__ == "__main__":
    seed()
    db.close()
