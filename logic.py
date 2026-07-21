# -*- coding: utf-8 -*-
"""Lógica de reconciliación al importar Backlog / Priorización."""
import pandas as pd
from storage import load_state, save_task


def merge_backlog(df_new: pd.DataFrame, fname: str):
    """Añade historias nuevas; conserva estado/asignado/histórico de las existentes."""
    state = load_state()
    existing_ids = {t["ID"] for t in state}
    for _, row in df_new.iterrows():
        rid = row["ID"]
        base = {
            "ID": rid,
            "Épica": row.get("Épica", ""),
            "Fase": row.get("Fase", ""),
            "Clasificación": row.get("Clasificación", ""),
            "Prioridad": row.get("Prioridad", ""),
            "Historia": row.get("Historia", ""),
            "Criterios": row.get("Criterios", ""),
            "SP": row.get("SP", ""),
            "Dependencias": row.get("Dependencias", ""),
            "RefDoc": row.get("RefDoc", ""),
        }
        if rid in existing_ids:
            t = next(t for t in state if t["ID"] == rid)
            for k, v in base.items():
                t[k] = v
            save_task(t)
        else:
            base.update({
                "Asignado": "— Sin asignar —",
                "Estado": "Backlog",
                "Correctivas": "",
                "Prio_Francesc": "",
                "Notas": "",
                "Historico": "",
                "Grupo": "",
            })
            save_task(base)


def apply_priorizacion(df_p: pd.DataFrame):
    """Vuelca la columna 'Tu prioridad' de la priorización sobre las historias."""
    state = load_state()
    idx = {t["ID"]: t for t in state}
    for _, row in df_p.iterrows():
        rid = row["ID"]
        if rid in idx:
            t = idx[rid]
            if pd.notna(row.get("Prio_Francesc")):
                t["Prio_Francesc"] = str(row["Prio_Francesc"])
            if pd.notna(row.get("Notas")) and str(row["Notas"]).strip():
                t["Notas"] = str(row["Notas"])
            save_task(t)
