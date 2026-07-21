# YouMRI · Gestión de Desarrollo — Guía

**MRIPlanexpert | YouMRI** · Autor: Francesc Torres Giménez — CSO de MRIPlanexpert

App web para gestionar el flujo **DEV → PROD** de las historias del backlog:
seguimiento de estado, persona asignada y fechas automáticas de cada cambio.

---

## 1. Qué hace

- Subes tu **Backlog** y tu **Priorización** (los .xlsx que ya tienes).
- Cada historia (US-xxx) avanza por estos estados, y en **cada cambio se guarda la fecha automáticamente**:

  `Backlog → En desarrollo → Revisión DEV → OK DEV / KO DEV(correctivas) → En producción → Revisión PROD → OK definitivo ✅`

- Asignas cada tarea a: **Francesc (CSO), Ferran Illa, Javier Nájera o Pablo Zaragüeta**.
- Si una tarea es **KO en DEV**, escribes las tareas correctivas; quedan ligadas a esa US.
- Cuando subes una **versión nueva** del backlog, la app conserva el estado, asignado y
  el histórico de fechas de las historias que ya existían (solo actualiza el contenido).
- Puedes **eliminar** versiones de documento desde la barra lateral.
- Exportas el estado actual a Excel cuando quieras.

---

## 2. Ejecutar en tu ordenador (prueba rápida, sin nube)

Con Python instalado:

```bash
pip install -r requirements.txt
streamlit run app.py
```

Se abre en el navegador. Sin credenciales de Google usa una base local (`data.db`).
Ideal para probar. Para uso real y multi-dispositivo → configura Google Sheets (paso 3).

---

## 3. Conectar Google Sheets (para que los datos vivan en la nube)

1. Crea una hoja de cálculo nueva en Google Sheets (vacía). Copia su URL.
2. En [Google Cloud Console](https://console.cloud.google.com):
   - Crea un proyecto → habilita **Google Sheets API**.
   - Crea una **cuenta de servicio** → genera una **clave JSON**.
   - Copia el email de la cuenta de servicio (algo como `xxx@xxx.iam.gserviceaccount.com`).
3. **Comparte tu Google Sheet** con ese email (permiso Editor).
4. Guarda las credenciales en los *secrets* de Streamlit (ver paso 4).

La app crea sola dos pestañas en la hoja: **Tareas** y **Docs**.
Puedes abrir la hoja en cualquier momento y ver/editar los datos a mano.

---

## 4. Desplegar gratis en Streamlit Community Cloud (URL accesible desde cualquier sitio)

1. Crea una cuenta en [share.streamlit.io](https://share.streamlit.io) con tu GitHub.
2. Sube esta carpeta a un repositorio de GitHub (privado si quieres).
3. En Streamlit Cloud: **New app** → elige el repo → archivo principal `app.py` → Deploy.
4. En **Settings → Secrets** de la app, pega esto (rellena con tu JSON y tu URL):

```toml
sheet_url = "https://docs.google.com/spreadsheets/d/TU_ID/edit"

[gcp_service_account]
type = "service_account"
project_id = "..."
private_key_id = "..."
private_key = "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n"
client_email = "xxx@xxx.iam.gserviceaccount.com"
client_id = "..."
auth_uri = "https://accounts.google.com/o/oauth2/auth"
token_uri = "https://oauth2.googleapis.com/token"
auth_provider_x509_cert_url = "https://www.googleapis.com/oauth2/v1/certs"
client_x509_cert_url = "..."
```

5. Guarda. La app se reinicia y ya usa Google Sheets. Tienes una URL fija tipo
   `https://youmri-dev.streamlit.app` — la abres desde móvil o portátil, donde sea.

---

## 5. Tu rutina diaria (muy simple)

1. Abre la URL.
2. Filtra por persona o fase si quieres.
3. Abre una historia, cambia su **Estado** y/o **Asignado**, pulsa **Guardar**.
   → la fecha del cambio queda registrada sola en el histórico.
4. Si es KO, escribe las correctivas.
5. Cuando saques una versión nueva del Backlog/Priorización, súbela en la barra lateral;
   el resto se conserva.

---

## 6. Personalizar

- **Cambiar personas:** edita la lista `PERSONAS` al inicio de `app.py`.
- **Cambiar estados del flujo:** edita la lista `ESTADOS` (y `ESTADO_COLOR`) en `app.py`.
- Nada más hay que tocar.
