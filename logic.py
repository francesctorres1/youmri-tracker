# -*- coding: utf-8 -*-
"""Logica de reconciliacion al importar Backlog / Priorizacion."""
import pandas as pd
from storage import load_state, save_tasks_bulk


def merge_backlog(df_new: pd.DataFrame, fname: str):
    """Anade historias nuevas; conserva estado/asignado/historico de las existentes.
    Escribe todo en un solo lote (evita rate limit de Google Sheets)."""
    state = load_state()
    by_id = {t["ID"]: t for t in state}
    result = []
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
        if rid in by_id:
            t = dict(by_id[rid])
            t.update(base)
            result.append(t)
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
            result.append(base)
    save_tasks_bulk(result)


def apply_priorizacion(df_p: pd.DataFrame):
    """Vuelca la columna 'Tu prioridad' de la priorizacion sobre las historias.
    Escribe en un solo lote."""
    state = load_state()
    idx = {t["ID"]: dict(t) for t in state}
    cambiadas = []
    for _, row in df_p.iterrows():
        rid = row["ID"]
        if rid in idx:
            t = idx[rid]
            changed = False
            if pd.notna(row.get("Prio_Francesc")):
                t["Prio_Francesc"] = str(row["Prio_Francesc"]); changed = True
            if pd.notna(row.get("Notas")) and str(row["Notas"]).strip():
                t["Notas"] = str(row["Notas"]); changed = True
            if changed:
                cambiadas.append(t)
    if cambiadas:
        save_tasks_bulk(cambiadas)
