from read_csv import read_doctors, read_assistants, read_appointments
from Promed import Doctor, Assistant, Cabinet, schedule_day
from gui_schedule import run_gui


import os
import sys

def resource_path(relative_path):
    try:

        base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    except AttributeError:
        base_path = os.path.dirname(os.path.abspath(__file__))

    return os.path.join(base_path, relative_path)


if __name__ == "__main__":
    doctors_file = resource_path("data/Medici.csv")
    assistants_file = resource_path("data/Asistente.csv")
    appointments_file = resource_path("data/Program.csv")

    doctors = read_doctors(doctors_file)
    assistants = read_assistants(assistants_file)
    appointments = read_appointments(appointments_file)


    target_date = "2025-04-25"
    opening_hour = 8
    for doctor in doctors:
        doctor.start_slot = 0
        doctor.end_slot = 0
    for appointment in appointments:
        if appointment.date == target_date:
            for doctor in doctors:
                if doctor.id == appointment.doctor_id:
                    start_hour, start_minute = map(int, appointment.time_interval.split('-')[0].split(':'))
                    end_hour, end_minute = map(int, appointment.time_interval.split('-')[1].split(':'))

                    # Calculăm sloturile relative la opening_hour
                    start_slot = (start_hour - opening_hour) * 2 + (start_minute // 30)
                    end_slot = (end_hour - opening_hour) * 2 + (end_minute // 30)

                    # Actualizăm sloturile doctorului
                    doctor.start_slot = min(doctor.start_slot, start_slot) if doctor.start_slot else start_slot
                    doctor.end_slot = max(doctor.end_slot, end_slot)

    # Filtrarea doctorilor care lucrează în ziua respectivă
    active_doctors = [doctor for doctor in doctors if doctor.start_slot != 0 or doctor.end_slot != 0]


    cabinets = [
        Cabinet("P1", {"Cardiologie"}),
        Cabinet("P2", {"Neurologie"}),
        Cabinet("P3", {"ORL"}),
        Cabinet("P4", {"Dermatologie"}),
        Cabinet("P5", {"Pediatrie", "Reabilitare Medicala"}),
        Cabinet("P6", {"Chirurgie Generala"}),
        Cabinet("P7", {"Urologie si Sexologie", "Explorari Functionale", "Obstetrica si Ginecologie"}),
        Cabinet("P8", {"Obstetrica si Ginecologie", "Urologie si Sexologie", "Explorari Functionale"}),
        Cabinet("P9", {"Reabilitare Medicala"}),
        Cabinet("P10", {"Endocrinologie"}),
        Cabinet("P11", {"Psihiatrie"}),
        Cabinet("P12", {"Hematologie", "Cardiologie"}),
        Cabinet("P13", {"Medicina Generala", "Medicina Interna"}),
        Cabinet("P14", {"Medicina Generala", "Medicina Interna"}),
        Cabinet("P15", {"Diabet"}),
        Cabinet("Gastroenterologie", {"Gastroenterologie"}),
        Cabinet("Ortopedie", {"Ortopedie", "Ortopedie pedriatica"}),
        Cabinet("Alergologie", {"Alergologie", "Oftalmologie"}),
        Cabinet("Neurochirurgie", {"Neurochirurgie", "Neurologie"}),
        Cabinet("Pneumologie", {"Pneumologie"}),
        Cabinet("Oftalmologie", {"Oftalmologie"}),
    ]

    initial = schedule_day(active_doctors, assistants, cabinets, 8, 17, 30)
    run_gui(
    active_doctors,
    assistants,
    cabinets,
    initial,
    opening_hour=8,
    closing_hour=17,
    slot_minutes=30,
    program_csv=appointments_file,
    doctors_csv=doctors_file
)
