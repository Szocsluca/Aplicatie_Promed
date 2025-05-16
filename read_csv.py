import csv
from typing import List
from Promed import Doctor, Assistant, Appointment 


import os
import sys

def resource_path(relative_path):
    try:

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)



def read_doctors(file_path: str) -> List[Doctor]:
    doctors = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            doctor_id = int(row['ID'])
            name = row['Nume']
            specialty1 = row['Specialitate 1']
            specialty2 = row['Specialitate 2']
            specialties = {specialty for specialty in [specialty1, specialty2] if specialty}
            doctors.append(Doctor(id=doctor_id, name=name, specialties=specialties, start_slot=0, end_slot=0))
    return doctors

def write_doctors(file_path: str, doctors: List[Doctor]) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Scriem antetul
        writer.writerow(["ID", "Nume", "Specialitate 1", "Specialitate 2"])
        for doctor in doctors:
            specialties = list(doctor.specialties)
            writer.writerow([
                doctor.id,
                doctor.name,
                specialties[0] if len(specialties) > 0 else "",
                specialties[1] if len(specialties) > 1 else ""
            ])

def read_assistants(file_path: str) -> List[Assistant]:
    assistants = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            name = row['Nume Asistent']
            specialty1 = row['Specializare 1']
            specialty2 = row['Specializare 2']
            specialty3 = row['Specializare 3']
            specialties = {specialty for specialty in [specialty1, specialty2, specialty3] if specialty}
            assistants.append(Assistant(name=name, specialties=specialties))
    return assistants

def read_appointments(file_path: str) -> List[Appointment]:
    appointments = []
    with open(file_path, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            doctor_id = int(row['ID'])
            date = row['Data']
            time_interval = row['Interval Orar']
            appointments.append(Appointment(doctor_id=doctor_id, date=date, time_interval=time_interval))
    return appointments

def write_appointments(file_path: str, appointments: List[Appointment]) -> None:
    with open(file_path, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        # Scriem antetul
        writer.writerow(["ID", "Data", "Interval Orar"])
        for appointment in appointments:
            writer.writerow([
                appointment.doctor_id,
                appointment.date,
                appointment.time_interval
            ])


if __name__ == "__main__":
    doctors_file = resource_path("data/Medici.csv")
    assistants_file = resource_path("data/Asistente.csv")
    appointments_file = resource_path("data/Program.csv")


    doctors = read_doctors(doctors_file)
    assistants = read_assistants(assistants_file)
    appointments = read_appointments(appointments_file)

    print("Doctors:")
    for doctor in doctors:
        print(doctor)

    print("\nAssistants:")
    for assistant in assistants:
        print(assistant)

    print("\nAppointments:")
    for appointment in appointments:
        print(appointment)
