# school-pickup
A full-stack application for text-in school pickup scheduling and automation during COVID

Steps for usage:
- Create a heroku app w/ postgres db linked to this repo (the `heroku` branch)
- Add config vars for a twilio account sid and auth token as ACCOUNT_SID and AUTH_TOKEN
- Use the included `pickup_cli.py` script for adding students to the system, getting logs, removing students, etc.
