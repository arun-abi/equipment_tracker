# Electrical Maintenance Tracker (Django)

Tracks building electrical equipment, PPM schedules, last PM dates and fault history.

## Run it

```bash
python -m venv venv
venv\Scripts\activate          # Windows   (Mac/Linux: source venv/bin/activate)
pip install -r requirements.txt

python manage.py makemigrations equipment
python manage.py migrate
python manage.py setup_demo          # roles, demo users, sample equipment
python manage.py createsuperuser     # your own admin login
python manage.py runserver
```

Open http://127.0.0.1:8000/

## Roles
| User | Password | Can do |
|------|----------|--------|
| engineer | demo12345 | view, add, edit equipment; log PM and faults |
| manager  | demo12345 | view only |

Change these passwords (or delete the demo users) before real use.
Add real users in the admin panel (/admin/) and put them in the Engineer or Manager group.
Users need "Staff status" ticked only if they should enter the admin panel.

## How the due date works
`next_pm_due = last_pm_date + PPM period` (or installation date if never serviced).
Adding a PM record updates `last_pm_date` automatically.
"Due soon" = within 14 days (`PM_DUE_SOON_DAYS` in `config/settings.py`).

## Files
- `equipment/models.py`  Equipment, PMRecord, FaultRecord + due-date logic
- `equipment/views.py`   dashboard, list/search, detail, add/edit pages
- `equipment/admin.py`   admin panel setup
- `templates/`, `equipment/templates/`  HTML pages
