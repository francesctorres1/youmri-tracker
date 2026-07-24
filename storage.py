# -*- coding: utf-8 -*-
"""
Capa de almacenamiento.

Backend primario: Google Sheets (vía st.secrets["gcp_service_account"]).
Fallback: SQLite local (data.db) — permite probar la app sin credenciales.

El código detecta automáticamente si hay credenciales de Google configuradas.
"""
import json
import sqlite3
from datetime import datetime

import streamlit as st

# Campos de una tarea (columnas de la hoja "Tareas")
TASK_FIELDS = ["ID", "Épica", "Fase", "Clasificación", "Prioridad", "Historia",
               "Criterios", "SP", "Dependencias", "RefDoc", "Asignado",
               "Estado", "Correctivas", "Prio_Francesc", "Notas", "Historico", "Grupo"]

DOC_FIELDS = ["tipo", "nombre", "n", "fecha"]

# ---------------------------------------------------------------------------
# DETECCIÓN DE BACKEND
# ---------------------------------------------------------------------------
def _has_gsheets():
    try:
        return "gcp_service_account" in st.secrets and "sheet_url" in st.secrets
    except Exception:
        return False


# ===========================================================================
# BACKEND GOOGLE SHEETS
# ===========================================================================
@st.cache_resource
def _gs_spreadsheet():
    """Conexión cacheada: una sola vez por sesión, no en cada operación."""
    import gspread
    from google.oauth2.service_account import Credentials
    scopes = ["https://www.googleapis.com/auth/spreadsheets",
              "https://www.googleapis.com/auth/drive"]
    creds = Credentials.from_service_account_info(
        dict(st.secrets["gcp_service_account"]), scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open_by_url(st.secrets["sheet_url"])


def _gs_client():
    return _gs_spreadsheet()


def _gs_ws(sh, title, header):
    try:
        ws = sh.worksheet(title)
    except Exception:
        ws = sh.add_worksheet(title=title, rows=1000, cols=len(header))
        ws.append_row(header)
    return ws


def _gs_load_state():
    sh = _gs_client()
    ws = _gs_ws(sh, "Tareas", TASK_FIELDS)
    records = ws.get_all_records()
    return [dict(r) for r in records]


def _gs_save_task(task):
    sh = _gs_client()
    ws = _gs_ws(sh, "Tareas", TASK_FIELDS)
    ids = ws.col_values(1)  # columna ID
    row = [str(task.get(f, "")) for f in TASK_FIELDS]
    if task["ID"] in ids:
        r = ids.index(task["ID"]) + 1
        ws.update(f"A{r}:{chr(64+len(TASK_FIELDS))}{r}", [row])
    else:
        ws.append_row(row)


def _gs_save_tasks_bulk(tasks):
    """Escribe muchas tareas de una sola vez (evita rate limit al importar)."""
    sh = _gs_client()
    ws = _gs_ws(sh, "Tareas", TASK_FIELDS)
    existing = ws.get_all_records()
    by_id = {str(r.get("ID")): i + 2 for i, r in enumerate(existing)}  # fila real
    updates = []
    appends = []
    last_col = chr(64 + len(TASK_FIELDS))
    for task in tasks:
        row = [str(task.get(f, "")) for f in TASK_FIELDS]
        rid = str(task.get("ID"))
        if rid in by_id:
            r = by_id[rid]
            updates.append({"range": f"A{r}:{last_col}{r}", "values": [row]})
        else:
            appends.append(row)
    if updates:
        ws.batch_update(updates)
    if appends:
        ws.append_rows(appends)


def _gs_load_docs():
    sh = _gs_client()
    ws = _gs_ws(sh, "Docs", DOC_FIELDS)
    return [dict(r) for r in ws.get_all_records()]


def _gs_save_doc(tipo, nombre, n):
    sh = _gs_client()
    ws = _gs_ws(sh, "Docs", DOC_FIELDS)
    ws.append_row([tipo, nombre, str(n),
                   datetime.now().strftime("%Y-%m-%d %H:%M")])


def _gs_delete_doc(tipo, nombre):
    sh = _gs_client()
    ws = _gs_ws(sh, "Docs", DOC_FIELDS)
    vals = ws.get_all_values()
    for i, r in enumerate(vals[1:], start=2):
        if len(r) >= 2 and r[0] == tipo and r[1] == nombre:
            ws.delete_rows(i)
            break


# ===========================================================================
# BACKEND SQLITE (fallback local)
# ===========================================================================
DB = "data.db"

def _db():
    con = sqlite3.connect(DB)
    con.execute("""CREATE TABLE IF NOT EXISTS tareas (
        ID TEXT PRIMARY KEY, data TEXT)""")
    con.execute("""CREATE TABLE IF NOT EXISTS docs (
        tipo TEXT, nombre TEXT, n INTEGER, fecha TEXT)""")
    return con


def _sq_load_state():
    con = _db()
    rows = con.execute("SELECT data FROM tareas").fetchall()
    con.close()
    return [json.loads(r[0]) for r in rows]


def _sq_save_task(task):
    con = _db()
    con.execute("INSERT OR REPLACE INTO tareas (ID,data) VALUES (?,?)",
                (task["ID"], json.dumps(task, ensure_ascii=False)))
    con.commit(); con.close()


def _sq_load_docs():
    con = _db()
    rows = con.execute("SELECT tipo,nombre,n,fecha FROM docs").fetchall()
    con.close()
    return [{"tipo": r[0], "nombre": r[1], "n": r[2], "fecha": r[3]} for r in rows]


def _sq_save_doc(tipo, nombre, n):
    con = _db()
    con.execute("INSERT INTO docs VALUES (?,?,?,?)",
                (tipo, nombre, n, datetime.now().strftime("%Y-%m-%d %H:%M")))
    con.commit(); con.close()


def _sq_delete_doc(tipo, nombre):
    con = _db()
    con.execute("DELETE FROM docs WHERE tipo=? AND nombre=?", (tipo, nombre))
    con.commit(); con.close()


def _sq_save_tasks_bulk(tasks):
    con = _db()
    for task in tasks:
        con.execute("INSERT OR REPLACE INTO tareas (ID,data) VALUES (?,?)",
                    (task["ID"], json.dumps(task, ensure_ascii=False)))
    con.commit(); con.close()


# ===========================================================================
# API PÚBLICA (enruta al backend disponible)
# ===========================================================================
def load_state():
    return _gs_load_state() if _has_gsheets() else _sq_load_state()

def save_task(task):
    return _gs_save_task(task) if _has_gsheets() else _sq_save_task(task)

def save_tasks_bulk(tasks):
    return _gs_save_tasks_bulk(tasks) if _has_gsheets() else _sq_save_tasks_bulk(tasks)

def load_docs_meta():
    return _gs_load_docs() if _has_gsheets() else _sq_load_docs()

def save_doc_meta(tipo, nombre, n):
    return _gs_save_doc(tipo, nombre, n) if _has_gsheets() else _sq_save_doc(tipo, nombre, n)

def delete_doc_meta(tipo, nombre):
    return _gs_delete_doc(tipo, nombre) if _has_gsheets() else _sq_delete_doc(tipo, nombre)
