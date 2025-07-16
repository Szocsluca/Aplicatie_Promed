from __future__ import annotations
from dataclasses import dataclass
from typing import List, Dict, Tuple, Optional

import matplotlib.pyplot as plt
from matplotlib.patches import Patch
from matplotlib import patheffects as pe


@dataclass
class Doctor:
    id: int
    name: str
    specialties: set[str]
    start_slot: int
    end_slot: int


@dataclass
class Assistant:
    name: str
    specialties: set[str]


@dataclass
class Cabinet:
    name: str
    specialties: set[str]

class Appointment:
    def __init__(self, doctor_id: int, date: str, time_interval: str):
        self.doctor_id = doctor_id
        self.date = date
        self.time_interval = time_interval

    def __repr__(self):
        return f"Appointment(ID={self.doctor_id}, Date={self.date}, Interval={self.time_interval})"


def schedule_day(
    doctors: List[Doctor],
    assistants: List[Assistant],
    cabinets: List[Cabinet],
    opening_hour: int = 8,
    closing_hour: int = 17,
    slot_minutes: int = 30,
) -> Dict[str, Dict[str, List[Tuple[str, int]]]]:
    """
    Returnează:
        { "doctors":    { doctor_name:    [(cabinet_name, slot), ...] },
          "assistants": { assistant_name: [(loc|general , slot), ...] } }
    """
    total_minutes = (closing_hour - opening_hour) * 60
    T = total_minutes // slot_minutes
    C, D, A = len(cabinets), len(doctors), len(assistants)

    # -1 = nealocat
    doc_alloc = [[-1] * T for _ in range(D)]
    asst_alloc = [[-1] * T for _ in range(A)]

    # Compatibilitate doctor-cabinet și asistent-cabinet
    doc_comp = [
        [k for k, cab in enumerate(cabinets) if not cab.specialties.isdisjoint(doc.specialties)]
        for doc in doctors
    ]
    asst_comp = [
        [k for k, cab in enumerate(cabinets) if not cab.specialties.isdisjoint(ast.specialties)]
        for ast in assistants
    ]

    for t in range(T):
        cab_free = [True] * C
        asst_free = [asst_alloc[a][t] == -1 for a in range(A)]

        # Plasăm doctorii (+asistentele) în acest slot
        for d, doc in enumerate(doctors):
            if not (doc.start_slot <= t < doc.end_slot):
                continue

            # Folosim prima specialitate a doctorului pentru alocare
            primary_specialty = next(iter(doc.specialties), None)
            if not primary_specialty:
                continue

            prev_cab = doc_alloc[d][t - 1] if t > 0 else -2
            cab_order = (
                [prev_cab] + [c for c in doc_comp[d] if c != prev_cab]
                if (prev_cab in doc_comp[d] and cab_free[prev_cab])
                else doc_comp[d]
            )

            placed = False
            for cab in cab_order:
                if not cab_free[cab]:
                    continue

                # Alegem asistenta compatibilă
                stick_same, stick_any, free_any = [], [], []
                for a, ast in enumerate(assistants):
                    if not asst_free[a] or cab not in asst_comp[a]:
                        continue
                    prev_a = asst_alloc[a][t - 1] if t > 0 else -2
                    if prev_a == cab:
                        stick_same.append(a)
                    elif prev_a >= 0:
                        stick_any.append(a)
                    else:
                        free_any.append(a)

                cand: Optional[int] = None
                for pool in (stick_same, stick_any, free_any):
                    if pool:
                        cand = pool[0]
                        break
                if cand is None:
                    continue  # încercăm alt cabinet

                # Alocăm doctorul și asistenta
                doc_alloc[d][t] = cab
                asst_alloc[cand][t] = cab
                cab_free[cab] = False
                asst_free[cand] = False
                placed = True
                break
            if not placed:
                raise ValueError(
                    f"Nu există combin. cab+asistentă pt {doc.name} la slot {t}"
                )

    out_docs: Dict[str, List[Tuple[str, int]]] = {}
    for d, doc in enumerate(doctors):
        out_docs[doc.name] = [
            (cabinets[doc_alloc[d][t]].name, t) for t in range(T) if doc_alloc[d][t] != -1
        ]

    out_asst: Dict[str, List[Tuple[str, int]]] = {}
    for a, ast in enumerate(assistants):
        lst = []
        for t in range(T):
            cab = asst_alloc[a][t]
            loc = "general" if cab == -1 else cabinets[cab].name
            lst.append((loc, t))
        out_asst[ast.name] = lst


    return {"doctors": out_docs, "assistants": out_asst}



