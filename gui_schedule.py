import tkinter as tk
from tkinter import ttk, messagebox
import copy
from Promed import schedule_day, Doctor, Assistant, Cabinet, Appointment
from read_csv import write_doctors, write_appointments, read_appointments

# Data fixă pentru care lucrăm (in varianta finala se va putea selecta data )
TARGET_DATE = "2025-04-25"

def run_gui(
    doctors: list[Doctor],
    assistants: list[Assistant],
    cabinets: list[Cabinet],
    initial_schedule: dict,
    opening_hour: int = 8,
    closing_hour: int = 17,
    slot_minutes: int = 30,
    program_csv: str = "Program.csv",       
    doctors_csv: str = "Medici.csv"         
):
   
    schedule = copy.deepcopy(initial_schedule)
    previous_schedule = None
    populate_funcs = {}

    root = tk.Tk()
    root.title("Programul Doctorilor și Asistentelor")
    root.geometry("1000x650")
    root.columnconfigure(0, weight=1)
    root.rowconfigure(2, weight=1)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('Treeview', rowheight=35, font=('Segoe UI', 10))
    style.configure('Treeview.Heading',
                    background='#4A6984', foreground='white',
                    font=('Segoe UI', 11, 'bold'))
    style.map('Treeview',
              background=[('selected', '#347083')],
              foreground=[('selected', 'white')])

    ttk.Label(root,
              text="📅 Program Doctori & Asistente",
              font=('Segoe UI', 16, 'bold'),
              anchor='center')\
        .grid(row=0, column=0, pady=(10,0))

    ctrl = ttk.Frame(root, padding=5)
    ctrl.grid(row=1, column=0, sticky="ew", padx=10)
    for i in range(9): ctrl.columnconfigure(i, weight=0)
    ctrl.columnconfigure(8, weight=1)

    ttk.Label(ctrl, text="Doctor:").grid(row=0, column=0, padx=5)
    selected_doctor_var = tk.StringVar(value="Selectează un doctor")
    cb_doctors = ttk.Combobox(ctrl,
                              textvariable=selected_doctor_var,
                              values=[d.name for d in doctors],
                              state="readonly", width=25)
    cb_doctors.grid(row=0, column=1, padx=5)

    ttk.Label(ctrl, text="De la:").grid(row=0, column=2, padx=5)
    start_hour_var = tk.StringVar(value=str(opening_hour))
    sb_start = ttk.Spinbox(ctrl, from_=opening_hour, to=closing_hour-1,
                           textvariable=start_hour_var, width=5)
    sb_start.grid(row=0, column=3, padx=5)

    ttk.Label(ctrl, text="Până la:").grid(row=0, column=4, padx=5)
    end_hour_var = tk.StringVar(value=str(closing_hour))
    sb_end = ttk.Spinbox(ctrl, from_=opening_hour+1, to=closing_hour,
                         textvariable=end_hour_var, width=5)
    sb_end.grid(row=0, column=5, padx=5)

    btn_apply = ttk.Button(ctrl, text="Aplică modificările")
    btn_apply.grid(row=0, column=6, padx=5)
    btn_delete = ttk.Button(ctrl, text="Șterge programare")
    btn_delete.grid(row=0, column=7, padx=5)

    notebook = ttk.Notebook(root)
    notebook.grid(row=2, column=0, sticky="nsew", padx=10, pady=(0,10))

    filter_combo = None

    for kind in ("doctors", "assistants"):
        frame = ttk.Frame(notebook, padding=5)
        frame.columnconfigure(1, weight=1)
        frame.rowconfigure(2, weight=1)
        notebook.add(frame, text="Medici" if kind=="doctors" else "Asistente")

        ttk.Label(frame, text="Filtrează:").grid(row=0, column=0, sticky="w")
        names = sorted(schedule[kind].keys())
        combo = ttk.Combobox(frame, values=["Toți"] + names, state="readonly")
        combo.set("Toți")
        combo.grid(row=0, column=1, sticky="ew", padx=5)
        if kind == "doctors":
            filter_combo = combo

        if kind == "doctors":
            cols = ("Persoană","Loc/Cabinet","Începe","Se termină","Asistentă","Modificări")
        else:
            cols = ("Persoană","Loc/Cabinet","Începe","Se termină","Modificări")

        tree = ttk.Treeview(frame, columns=cols, show="headings")
        for c in cols:
            tree.heading(c, text=c)
            if c == "Modificări":
                tree.column(c, width=300, anchor="w", stretch=True)
            else:
                tree.column(c, width=100, anchor="center", stretch=True)
        tree.grid(row=2, column=0, columnspan=2, sticky="nsew")

        vsb = ttk.Scrollbar(frame, orient="vertical",   command=tree.yview)
        hsb = ttk.Scrollbar(frame, orient="horizontal", command=tree.xview)
        vsb.grid(row=2, column=2, sticky="ns")
        hsb.grid(row=3, column=0, columnspan=2, sticky="ew")
        tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        tree.tag_configure('oddrow',   background='#F9F9F9')
        tree.tag_configure('evenrow',  background='#FFFFFF')
        tree.tag_configure('modified', background='#FFE5E5')

        def make_populator(kind, combo, tree):
            def populate(selected):
                nonlocal previous_schedule, schedule
                for r in tree.get_children():
                    tree.delete(r)
                row_idx = 0

                old_map = {}
                if previous_schedule:
                    for nm, items in previous_schedule[kind].items():
                        old_map[nm] = {slot:loc for loc,slot in items}

                for name in sorted(schedule[kind].keys()):
                    if selected not in ("Toți", name):
                        continue
                    items = sorted(schedule[kind][name], key=lambda x: x[1])

                    if not items:
                        # fără slot-uri: afișăm linie goală
                        tag = 'evenrow' if row_idx%2==0 else 'oddrow'
                        if kind=="doctors":
                            tree.insert("", "end",
                                        values=(name,"","","","", ""),
                                        tags=(tag,))
                        else:
                            tree.insert("", "end",
                                        values=(name,"","","",""),
                                        tags=(tag,))
                        row_idx += 1
                        continue

                    # grupăm slot-contigu
                    blocks = []
                    loc0, s0 = items[0]; e0 = s0
                    for loc, sl in items[1:]:
                        if loc==loc0 and sl==e0+1:
                            e0 = sl
                        else:
                            blocks.append((loc0, s0, e0))
                            loc0, s0, e0 = loc, sl, sl
                    blocks.append((loc0, s0, e0))

                    for loc, s_slot, e_slot in blocks:
                        ts = opening_hour*60 + s_slot*slot_minutes
                        te = opening_hour*60 + (e_slot+1)*slot_minutes
                        sh, sm = divmod(ts, 60); eh, em = divmod(te, 60)
                        start_str = f"{sh:02d}:{sm:02d}"
                        end_str   = f"{eh:02d}:{em:02d}"

                        assistant = ""
                        if kind=="doctors":
                            for a, sched in schedule["assistants"].items():
                                if all((loc,sl) in sched for sl in range(s_slot, e_slot+1)):
                                    assistant = a
                                    break

                        desc = []
                        if previous_schedule:
                            old_loc = old_map.get(name, {}).get(s_slot)
                            if old_loc and old_loc!=loc:
                                desc.append(f"Cabinet: {old_loc}→{loc}")
                            if kind=="doctors":
                                old_asns = [
                                    a for a, sched in previous_schedule["assistants"].items()
                                    if old_loc and all((old_loc,sl) in sched for sl in range(s_slot, e_slot+1))
                                ]
                                old_a = old_asns[0] if old_asns else ""
                                if old_a and old_a!=assistant:
                                    desc.append(f"Asistentă: {old_a}→{assistant}")

                        note = "\n".join(desc)
                        is_mod = bool(desc)

                        if kind=="doctors":
                            vals = (name, loc, start_str, end_str, assistant, note)
                        else:
                            vals = (name, loc, start_str, end_str, note)

                        tag = 'modified' if is_mod else ('evenrow' if row_idx%2==0 else 'oddrow')
                        tree.insert("", "end", values=vals, tags=(tag,))
                        row_idx += 1

            combo.bind("<<ComboboxSelected>>",
                       lambda e, pop=populate, c=combo: pop(c.get()))
            return populate

        pop_fn = make_populator(kind, combo, tree)
        populate_funcs[kind] = pop_fn
        pop_fn("Toți")

    def on_apply():
        nonlocal schedule, previous_schedule
        previous_schedule = copy.deepcopy(schedule)

        name = selected_doctor_var.get()
        if name == "Selectează un doctor":
            messagebox.showerror("Eroare", "Alege întâi un doctor.")
            return
        try:
            ns = int(start_hour_var.get())
            ne = int(end_hour_var.get())
            assert opening_hour <= ns < ne <= closing_hour
        except:
            messagebox.showerror("Eroare", "Interval invalid.")
            return

        doc = next(d for d in doctors if d.name == name)
        doc.start_slot = (ns - opening_hour) * (60 // slot_minutes)
        doc.end_slot = (ne - opening_hour) * (60 // slot_minutes)

        schedule = schedule_day(doctors, assistants, cabinets,
                                opening_hour, closing_hour, slot_minutes)


        appts = read_appointments(program_csv)
        updated = False
        for ap in appts:
            if ap.doctor_id == doc.id and ap.date == TARGET_DATE:
                ap.time_interval = f"{ns:02d}:00-{ne:02d}:00"
                updated = True
                break
        if not updated:
            appts.append(Appointment(doc.id, TARGET_DATE, f"{ns:02d}:00-{ne:02d}:00"))
        write_appointments(program_csv, appts)
        write_doctors(doctors_csv, doctors)

        for p in populate_funcs.values():
            p("Toți")

    btn_apply.config(command=on_apply)
    def on_delete():
        nonlocal schedule, previous_schedule
        name = selected_doctor_var.get()
        if name == "Selectează un doctor":
            messagebox.showerror("Eroare", "Alege întâi un doctor.")
            return
        if not messagebox.askyesno("Confirmare",
                                   f"Ștergi programarea pentru {name}?"):
            return

        previous_schedule = copy.deepcopy(schedule)
        doc = next(d for d in doctors if d.name == name)
        doc.start_slot = doc.end_slot = 0

        schedule = schedule_day(doctors, assistants, cabinets,
                                opening_hour, closing_hour, slot_minutes)
        schedule["doctors"].pop(name, None)

        appts = [a for a in read_appointments(program_csv)
                 if not (a.doctor_id == doc.id and a.date == TARGET_DATE)]
        write_appointments(program_csv, appts)
        write_doctors(doctors_csv, doctors)

        if filter_combo is not None:
            vals = ["Toți"] + sorted(schedule["doctors"].keys())
            filter_combo['values'] = vals
            filter_combo.set("Toți")

        for p in populate_funcs.values():
            p("Toți")

    btn_delete.config(command=on_delete)

    ttk.Button(root, text="Închide", command=root.destroy)\
       .grid(row=3, column=0, pady=10)

    root.mainloop()
