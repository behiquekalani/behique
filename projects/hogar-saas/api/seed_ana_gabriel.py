#!/usr/bin/env python3
"""
Seed Hogar Ana Gabriel — populate the database with real data.
Run once to set up the test hogar.
"""

from models import init_db, add_hogar, add_resident, add_medication, add_staff
from task_engine import TaskEngine

# Create hogar
hogar_id = add_hogar(
    name="Hogar Ana Gabriel",
    address="Carr. 633 Km 0.7 Calle J, Bo Campamento, Sector La Grama, Ciales, PR 00638",
    phone="7875014445",
    email="hogaranagabriel@gmail.com",
    owner_name="Ana Gabriel",
    max_capacity=25
)
print(f"Hogar created: ID {hogar_id}")

# Add staff (sample — replace with real names)
staff1 = add_staff(hogar_id, "Staff", "Uno", "nurse", "7871234567", "day")
staff2 = add_staff(hogar_id, "Staff", "Dos", "aide", "7871234568", "day")
staff3 = add_staff(hogar_id, "Staff", "Tres", "cook", "7871234569", "day")
staff4 = add_staff(hogar_id, "Staff", "Admin", "admin", "7875014445", "day")
print(f"Staff added: 4 members")

# Add sample residents (anonymized)
residents = [
    {"first": "Residente", "last": "1", "dob": "1940-03-15", "room": "1", "conditions": ["hipertension"], "mobility": "assisted"},
    {"first": "Residente", "last": "2", "dob": "1938-07-22", "room": "2", "conditions": ["diabetes tipo 2"], "mobility": "wheelchair"},
    {"first": "Residente", "last": "3", "dob": "1945-11-08", "room": "3", "conditions": ["artritis"], "mobility": "independent"},
    {"first": "Residente", "last": "4", "dob": "1935-01-30", "room": "4", "conditions": ["alzheimer leve"], "mobility": "assisted"},
    {"first": "Residente", "last": "5", "dob": "1942-06-14", "room": "5", "conditions": ["COPD"], "mobility": "assisted"},
]

resident_ids = []
for r in residents:
    rid = add_resident(
        hogar_id, r["first"], r["last"],
        date_of_birth=r["dob"], room_number=r["room"],
        conditions=r["conditions"], mobility_level=r["mobility"]
    )
    resident_ids.append(rid)

print(f"Residents added: {len(resident_ids)}")

# Add sample medications
add_medication(resident_ids[0], "Losartan", "50mg", "daily", ["08:00"], "Con comida")
add_medication(resident_ids[0], "Aspirina", "81mg", "daily", ["08:00"], "")
add_medication(resident_ids[1], "Metformina", "500mg", "twice_daily", ["08:00", "20:00"], "Con comida")
add_medication(resident_ids[1], "Insulina", "10 unidades", "daily", ["07:30"], "Subcutanea")
add_medication(resident_ids[2], "Acetaminofen", "500mg", "as_needed", ["08:00", "14:00", "20:00"], "Para dolor")
add_medication(resident_ids[3], "Donepezilo", "5mg", "daily", ["20:00"], "Antes de dormir")
add_medication(resident_ids[4], "Salbutamol", "2 puffs", "twice_daily", ["08:00", "20:00"], "Inhalador")
print(f"Medications added: 7")

# Generate today's tasks
tasks_created = TaskEngine.generate_daily_tasks(hogar_id)
print(f"Tasks generated for today: {tasks_created}")

print(f"\nHogar Ana Gabriel seeded successfully!")
print(f"Run the dashboard: python3 dashboard.py")
