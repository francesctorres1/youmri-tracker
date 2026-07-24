# -*- coding: utf-8 -*-
"""
YouMRI \u00b7 Gesti\u00f3n de Desarrollo
MRIPlanexpert | YouMRI
Autor: Francesc Torres Gim\u00e9nez \u2014 CSO de MRIPlanexpert
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import io

from storage import load_state, save_task, load_docs_meta, save_doc_meta, delete_doc_meta
from backlog_io import parse_backlog, parse_priorizacion
from logic import merge_backlog, apply_priorizacion

st.set_page_config(page_title="YouMRI \u00b7 Gesti\u00f3n de Desarrollo",
                   page_icon="\U0001F9E0", layout="wide")

NOCTURN = "#0E0F28"
ESPURNA = "#00F1CE"
GROC    = "#F8FF00"
CREMA   = "#E7E7E7"

PERSONAS = ["\u2014 Sin asignar \u2014", "Francesc Torres (CSO)",
            "Ferran Illa", "Javier N\u00e1jera", "Pablo Zarag\u00fceta"]

ESTADOS = [
    "Backlog",
    "En desarrollo",
    "Revisi\u00f3n DEV",
    "OK DEV",
    "KO DEV \u2014 correctivas",
    "En producci\u00f3n",
    "Revisi\u00f3n PROD",
    "OK definitivo \u2705",
]

ESTADO_COLOR = {
    "Backlog": "#6B7280",
    "En desarrollo": "#D97706",
    "Revisi\u00f3n DEV": "#2563EB",
    "OK DEV": "#16A34A",
    "KO DEV \u2014 correctivas": "#DC2626",
    "En producci\u00f3n": "#7C3AED",
    "Revisi\u00f3n PROD": "#0891B2",
    "OK definitivo \u2705": "#16A34A",
}

st.markdown(f"""
<style>
    .stApp {{ background-color: {NOCTURN}; }}
    .stApp, .stApp p, .stApp span, .stApp label, .stApp div,
    .stMarkdown, [data-testid="stMarkdownContainer"] {{ color: {CREMA}; }}
    h1,h2,h3,h4 {{ color: #FFFFFF !important; font-family: 'DM Sans', sans-serif; }}
    .marca {{ color:{ESPURNA}; font-weight:700; letter-spacing:1px; }}
    .stMetric {{ background:#181A3A; border-radius:12px; padding:12px; }}
    [data-testid="stMetricLabel"] {{ color:#C7C9E0 !important; }}
    div[data-testid="stMetricValue"] {{ color:{ESPURNA} !important; }}
    [data-testid="stCaptionContainer"], .stCaption, small {{ color:#AEB1CC !important; }}
   [data-testid="stExpander"] summary {{ color:{NOCTURN} !important; }}
    [data-testid="stExpander"] summary p {{ color:{NOCTURN} !important; }}
    [data-testid="stExpander"] summary span {{ color:{NOCTURN} !important; }}
    details summary, details summary * {{ color:{NOCTURN} !important; }}
    .stTabs [data-baseweb="tab"] {{ color:{CREMA} !important; }}
    .badge {{ display:inline-block; padding:3px 10px; border-radius:20px;
             color:white; font-size:12px; font-weight:600; }}
    .prio {{ display:inline-block; padding:2px 10px; border-radius:20px;
             background:{GROC}; color:{NOCTURN}; font-weight:700; font-size:12px; }}
    section[data-testid="stSidebar"] {{ background-color:#F4F5FA; }}
    section[data-testid="stSidebar"] * {{ color:{NOCTURN} !important; }}
    section[data-testid="stSidebar"] [data-testid="stCaptionContainer"],
    section[data-testid="stSidebar"] small {{ color:#4A4C66 !important; }}
    [data-testid="stPopover"] button p {{ color:{NOCTURN} !important; }}
    [data-baseweb="popover"] {{ background:#FFFFFF !important; }}
    [data-baseweb="popover"], [data-baseweb="popover"] * {{ color:{NOCTURN} !important; }}
    [data-testid="stPopoverBody"], [data-testid="stPopoverBody"] * {{ color:{NOCTURN} !important; }}
    div[data-baseweb="popover"] [data-testid="stMarkdownContainer"], div[data-baseweb="popover"] [data-testid="stMarkdownContainer"] * {{ color:{NOCTURN} !important; }}
    [data-baseweb="select"] div {{ color:{NOCTURN} !important; }}
    [data-baseweb="select"] span {{ color:{NOCTURN} !important; }}
    [data-testid="stMultiSelect"] div, [data-testid="stMultiSelect"] span {{ color:{NOCTURN} !important; }}
    .stButton button p, .stButton button span, .stButton button div {{ color:{NOCTURN} !important; }}
</style>
""", unsafe_allow_html=True)

st.markdown("<h1><span class='marca'>MRIPlanexpert | YouMRI</span> \u00b7 Gesti\u00f3n de Desarrollo</h1>",
            unsafe_allow_html=True)

@st.cache_data(ttl=30)
def get_state():
    return load_state()

def refresh():
    st.cache_data.clear()

# ---------------- SIDEBAR ----------------
with st.sidebar:
    st.markdown("### \U0001F4C4 Documentos fuente")
    st.caption("Sube tu Backlog y tu Priorizaci\u00f3n. Al reimportar una versi\u00f3n "
               "nueva se conservan los estados de las historias existentes.")

    docs = load_docs_meta()

    up_backlog = st.file_uploader("Backlog (.xlsx)", type=["xlsx"], key="up_bl")
    if up_backlog is not None:
        if st.button("\u2B06\uFE0F Importar / actualizar Backlog", use_container_width=True):
            df_new = parse_backlog(up_backlog)
            merge_backlog(df_new, up_backlog.name)
            save_doc_meta("backlog", up_backlog.name, len(df_new))
            refresh()
            st.success(f"Backlog \u00ab{up_backlog.name}\u00bb importado ({len(df_new)} historias).")
            st.rerun()

    up_prio = st.file_uploader("Priorizaci\u00f3n (.xlsx)", type=["xlsx"], key="up_pr")
    if up_prio is not None:
        if st.button("\u2B06\uFE0F Importar / actualizar Priorizaci\u00f3n", use_container_width=True):
            df_p = parse_priorizacion(up_prio)
            apply_priorizacion(df_p)
            save_doc_meta("priorizacion", up_prio.name, len(df_p))
            refresh()
            st.success(f"Priorizaci\u00f3n \u00ab{up_prio.name}\u00bb aplicada ({len(df_p)} filas).")
            st.rerun()

    st.divider()
    st.markdown("#### Versiones cargadas")
    if docs:
        for d in docs:
            c1, c2 = st.columns([4,1])
            c1.markdown(f"**{d['tipo']}** \u00b7 {d['nombre']}  \n"
                        f"<small>{d['n']} filas \u00b7 {d['fecha']}</small>",
                        unsafe_allow_html=True)
            if c2.button("\U0001F5D1\uFE0F", key=f"del_{d['tipo']}_{d['nombre']}"):
                delete_doc_meta(d['tipo'], d['nombre'])
                refresh(); st.rerun()
    else:
        st.caption("A\u00fan no hay documentos cargados.")

# ---------------- CUERPO ----------------
state = get_state()

if not state:
    st.info("\U0001F448 Empieza subiendo tu **Backlog** en la barra lateral.")
    st.stop()

df = pd.DataFrame(state)
if "Grupo" not in df.columns:
    df["Grupo"] = ""

# lista de grupos existentes (una sola fuente de verdad)
GRUPOS = sorted({str(g).strip() for g in df["Grupo"].tolist() if str(g).strip()})

c1,c2,c3,c4,c5 = st.columns(5)
c1.metric("Historias", len(df))
c2.metric("En desarrollo", (df["Estado"]=="En desarrollo").sum())
c3.metric("En producci\u00f3n", (df["Estado"]=="En producci\u00f3n").sum())
c4.metric("Correctivas", (df["Estado"]=="KO DEV \u2014 correctivas").sum())
c5.metric("OK definitivo", (df["Estado"]=="OK definitivo \u2705").sum())

st.divider()

# --- Filtros (fila 1) ---
f1,f2,f3,f4 = st.columns(4)
fase_f   = f1.multiselect("Fase", sorted(df["Fase"].dropna().unique()))
estado_f = f2.multiselect("Estado", ESTADOS)
pers_f   = f3.multiselect("Asignado a", PERSONAS)
buscar   = f4.text_input("Buscar (ID o texto)")

# --- Filtros (fila 2): prioridad, GRUPO, orden ---
g1, gG, g2 = st.columns([1,1,2])
prio_vals = sorted([p for p in df.get("Prio_Francesc", pd.Series()).dropna().unique() if str(p).strip()])
prio_f = g1.multiselect("Tu prioridad (1\u20135)", prio_vals)
grupo_f = gG.multiselect("Grupo", GRUPOS)
orden = g2.radio("Ordenar por",
                 ["Avance del pipeline", "Tu prioridad (m\u00e1s alta primero)"],
                 horizontal=True)

view = df.copy()
if fase_f:   view = view[view["Fase"].isin(fase_f)]
if estado_f: view = view[view["Estado"].isin(estado_f)]
if pers_f:   view = view[view["Asignado"].isin(pers_f)]
if prio_f and "Prio_Francesc" in view.columns:
    view = view[view["Prio_Francesc"].isin(prio_f)]
if grupo_f:
    view = view[view["Grupo"].astype(str).str.strip().isin(grupo_f)]
if buscar:
    m = view["ID"].str.contains(buscar, case=False, na=False) | \
        view["Historia"].str.contains(buscar, case=False, na=False)
    view = view[m]

view["_ord"] = view["Estado"].map({e:i for i,e in enumerate(ESTADOS)})
if orden.startswith("Tu prioridad"):
    def _pnum(x):
        try: return int(float(x))
        except: return -1
    view["_prio"] = view.get("Prio_Francesc", pd.Series()).apply(_pnum)
    view = view.sort_values(["_prio","_ord","ID"], ascending=[False, True, True])
else:
    view = view.sort_values(["_ord","ID"])

tab1, tabG, tab2 = st.tabs(["\U0001F5C2\uFE0F Tablero de tareas",
                            "\U0001F517 Grupos",
                            "\U0001F4CA Vista global / export"])

# ============================ TAB 1: TABLERO ================================
with tab1:
    with st.container(border=True):
        st.markdown("**\U0001F517 Selecci\u00f3n m\u00faltiple y grupos**")
        gsel1, gsel2, gsel3 = st.columns([2,2,1])
        grupo_pick = gsel1.selectbox("Marcar historias de un grupo existente",
            ["\u2014 ninguno \u2014"] + GRUPOS, key="grupo_pick")
        ids_del_grupo = [str(r["ID"]) for _, r in df.iterrows()
                         if str(r.get("Grupo","")).strip() == grupo_pick] \
                        if grupo_pick != "\u2014 ninguno \u2014" else []
        if gsel2.button("\u2705 Marcar historias de este grupo", use_container_width=True,
                        disabled=(grupo_pick == "\u2014 ninguno \u2014")):
            for rid in ids_del_grupo:
                st.session_state[f"chk_{rid}"] = True
            st.rerun()
        if gsel3.button("\u2716\uFE0F Limpiar selecci\u00f3n", use_container_width=True):
            for k in list(st.session_state.keys()):
                if k.startswith("chk_"):
                    st.session_state[k] = False
            st.rerun()
        if grupo_pick != "\u2014 ninguno \u2014":
            st.caption(f"El grupo \u00ab{grupo_pick}\u00bb tiene {len(ids_del_grupo)} historias: "
                       f"{', '.join(ids_del_grupo)}")

    seleccionadas = [t for _, t in view.iterrows()
                     if st.session_state.get(f"chk_{t['ID']}", False)]

    if seleccionadas:
        ids_sel = [t["ID"] for t in seleccionadas]
        with st.container(border=True):
            st.markdown(f"**\u26A1 Acci\u00f3n masiva \u2014 {len(seleccionadas)} seleccionadas:** "
                        f"{', '.join(ids_sel)}")
            b1, b2 = st.columns(2)
            masa_estado = b1.selectbox("Nuevo estado (para todas)",
                ["\u2014 no cambiar \u2014"] + ESTADOS, key="masa_estado")
            masa_pers = b2.selectbox("Asignar a (todas)",
                ["\u2014 no cambiar \u2014"] + PERSONAS, key="masa_pers")
            masa_corr = st.text_area("Correctivas comunes (se aplican a todas)",
                key="masa_corr",
                placeholder="Texto de correctivas que comparten estas historias...")
            gg1, gg2 = st.columns([2,1])
            # elegir grupo existente o escribir uno nuevo
            grupo_opt = gg1.selectbox("Asignar a grupo existente",
                ["\u2014 no cambiar \u2014", "\u2795 nuevo grupo\u2026"] + GRUPOS,
                key="masa_grupo_sel")
            masa_grupo_new = ""
            if grupo_opt == "\u2795 nuevo grupo\u2026":
                masa_grupo_new = gg2.text_input("Nombre del nuevo grupo",
                    key="masa_grupo_new", placeholder="Ej.: Sem\u00e1foro")

            if st.button("\U0001F4BE Aplicar a las seleccionadas", type="primary"):
                stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                grupo_final = None
                if grupo_opt == "\u2795 nuevo grupo\u2026" and masa_grupo_new.strip():
                    grupo_final = masa_grupo_new.strip()
                elif grupo_opt not in ("\u2014 no cambiar \u2014", "\u2795 nuevo grupo\u2026"):
                    grupo_final = grupo_opt
                for t in seleccionadas:
                    rec = dict(t); rec.pop("_ord", None); rec.pop("_prio", None)
                    if masa_estado != "\u2014 no cambiar \u2014" and masa_estado != t["Estado"]:
                        linea = f"[{stamp}] {t['Estado']} \u2192 {masa_estado} (por Francesc \u00b7 masiva)"
                        rec["Historico"] = (t.get("Historico","") + "\n" + linea).strip()
                        rec["Estado"] = masa_estado
                    if masa_pers != "\u2014 no cambiar \u2014":
                        rec["Asignado"] = masa_pers
                    if masa_corr.strip():
                        rec["Correctivas"] = masa_corr.strip()
                    if grupo_final is not None:
                        rec["Grupo"] = grupo_final
                    save_task(rec)
                refresh()
                st.success(f"Aplicado a {len(seleccionadas)} historias."
                           + (f" Agrupadas como \u00ab{grupo_final}\u00bb." if grupo_final else ""))
                st.rerun()

    st.caption(f"{len(view)} historias \u00b7 orden: {orden.lower()}")

    for _, t in view.iterrows():
        color = ESTADO_COLOR.get(t["Estado"], "#6B7280")
        prio_lbl = ""
        if str(t.get("Prio_Francesc","")).strip():
            prio_lbl = f" \u00b7 \u2B50 Prio {t['Prio_Francesc']}"
        grupo_lbl = ""
        if str(t.get("Grupo","")).strip():
            grupo_lbl = f" \u00b7 \U0001F517 {t['Grupo']}"

        col_chk, col_exp = st.columns([1, 22])
        col_chk.checkbox(" ", key=f"chk_{t['ID']}", label_visibility="collapsed")
        with col_exp.expander(
            f"**{t['ID']}** \u00b7 {t['\u00c9pica']} \u00b7 {t['Fase']}  \u2014  "
            f"[{t['Estado']}] \u00b7 \U0001F464 {t['Asignado']}{prio_lbl}{grupo_lbl}"):

            st.markdown(f"<span class='badge' style='background:{color}'>"
                        f"{t['Estado']}</span>", unsafe_allow_html=True)
            st.markdown(f"**Historia:** {t['Historia']}")
            if t.get("Criterios"):
                with st.popover("Ver criterios de aceptaci\u00f3n"):
                    st.markdown(t["Criterios"])
            meta = f"Clasif: {t.get('Clasificaci\u00f3n','')} \u00b7 Prio: {t.get('Prioridad','')} \u00b7 " \
                   f"SP: {t.get('SP','')} \u00b7 Dep: {t.get('Dependencias','')} \u00b7 " \
                   f"Ref: {t.get('RefDoc','')}"
            if t.get("Prio_Francesc"):
                meta += f" \u00b7 Tu prio: {t['Prio_Francesc']}"
            if str(t.get("Grupo","")).strip():
                meta += f" \u00b7 Grupo: {t['Grupo']}"
            st.caption(meta)

            cc1, cc2 = st.columns(2)
            new_estado = cc1.selectbox("Estado", ESTADOS,
                index=ESTADOS.index(t["Estado"]) if t["Estado"] in ESTADOS else 0,
                key=f"est_{t['ID']}")
            new_pers = cc2.selectbox("Asignado a", PERSONAS,
                index=PERSONAS.index(t["Asignado"]) if t["Asignado"] in PERSONAS else 0,
                key=f"per_{t['ID']}")

            new_grupo = st.text_input("Grupo relacionado (opcional)",
                value=str(t.get("Grupo","")), key=f"grp_{t['ID']}",
                placeholder="Ej.: Sem\u00e1foro")

            correctivas = t.get("Correctivas","")
            if new_estado == "KO DEV \u2014 correctivas" or t["Estado"] == "KO DEV \u2014 correctivas":
                correctivas = st.text_area("Tareas correctivas identificadas",
                    value=t.get("Correctivas",""), key=f"cor_{t['ID']}",
                    placeholder="Ej.: falta validar id_estudio...")

            if st.button("\U0001F4BE Guardar cambios", key=f"save_{t['ID']}"):
                rec = dict(t); rec.pop("_ord", None); rec.pop("_prio", None)
                cambios = []
                if new_estado != t["Estado"]:
                    stamp = datetime.now().strftime("%Y-%m-%d %H:%M")
                    linea = f"[{stamp}] {t['Estado']} \u2192 {new_estado} (por Francesc)"
                    rec["Historico"] = (t.get("Historico","") + "\n" + linea).strip()
                    cambios.append("estado")
                rec["Estado"] = new_estado
                rec["Asignado"] = new_pers
                rec["Correctivas"] = correctivas
                rec["Grupo"] = new_grupo.strip()
                save_task(rec)
                refresh()
                st.success("Guardado." + (" Fecha de cambio de estado registrada."
                           if "estado" in cambios else ""))
                st.rerun()

            if t.get("Historico"):
                with st.popover("\U0001F552 Hist\u00f3rico de fechas"):
                    st.text(t["Historico"])

# ============================ TAB GRUPOS ================================
with tabG:
    if not GRUPOS:
        st.info("A\u00fan no has creado ning\u00fan grupo. En el Tablero, marca varias "
                "historias con las casillas y as\u00edgnalas a un grupo nuevo.")
    else:
        st.caption(f"{len(GRUPOS)} grupos creados. Cada grupo agrupa historias relacionadas.")
        for g in GRUPOS:
            miembros = df[df["Grupo"].astype(str).str.strip() == g]
            with st.expander(f"\U0001F517 **{g}** \u2014 {len(miembros)} historias", expanded=False):
                for _, m in miembros.iterrows():
                    prio = f" \u00b7 \u2B50 Prio {m['Prio_Francesc']}" if str(m.get("Prio_Francesc","")).strip() else ""
                    st.markdown(
                        f"- **{m['ID']}** \u00b7 {m['\u00c9pica']} \u00b7 {m['Fase']} "
                        f"\u2014 [{m['Estado']}] \u00b7 \U0001F464 {m['Asignado']}{prio}")
                # Deshacer grupo
                if st.button(f"\U0001F5D1\uFE0F Deshacer grupo \u00ab{g}\u00bb",
                             key=f"delgrp_{g}"):
                    for _, m in miembros.iterrows():
                        rec = dict(m); rec.pop("_ord", None); rec.pop("_prio", None)
                        rec["Grupo"] = ""
                        save_task(rec)
                    refresh()
                    st.success(f"Grupo \u00ab{g}\u00bb deshecho. Las historias vuelven al listado general.")
                    st.rerun()

# ====================== TAB VISTA GLOBAL / EXPORT ========================
with tab2:
    cols = ["ID","\u00c9pica","Fase","Estado","Asignado","Prioridad",
            "Prio_Francesc","Grupo","SP","Correctivas","Historico"]
    cols = [c for c in cols if c in df.columns]
    st.dataframe(df[cols], use_container_width=True, height=520)

    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as w:
        df.drop(columns=["_ord","_prio"], errors="ignore").to_excel(
            w, index=False, sheet_name="Estado")
    st.download_button("\u2B07\uFE0F Descargar estado actual (.xlsx)",
        data=buf.getvalue(), file_name="YouMRI_Estado_Desarrollo.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

st.caption("MRIPlanexpert | YouMRI \u00b7 Autor: Francesc Torres Gim\u00e9nez \u2014 CSO de MRIPlanexpert")
