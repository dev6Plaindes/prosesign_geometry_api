import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import time

def conectar_google_sheets(ruta_json, nombre_sheet):
    """Establece la conexión con la cuenta de servicio."""
    scopes = [
        'https://www.googleapis.com/auth/spreadsheets',
        'https://www.googleapis.com/auth/drive'
    ]
    creds = Credentials.from_service_account_file(ruta_json, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open(nombre_sheet)

def procesar_y_extraer_sheets(datos, nombre_archivo_google):
    """
    Escribe los datos en las hojas correspondientes y extrae
    el resultado de la hoja CALCULOS.
    """
    ruta_json = './hip-service-491917-s6-4e534bb75127.json'

    try:
        sh = conectar_google_sheets(ruta_json, nombre_archivo_google)

        try:
            aforo_inicial = int(datos[0]["aforo_grado"])
        except (IndexError, KeyError):
            aforo_inicial = 0

        try:
            aforo_primaria = int(datos[1]["aforo_grado"])
        except (IndexError, KeyError):
            aforo_primaria = 0

        try:
            aforo_sec = int(datos[2]["aforo_grado"])
        except (IndexError, KeyError):
            aforo_sec = 0

        ws_inicial = sh.worksheet("INICIAL")
        ws_inicial.update_acell('D5', aforo_inicial)
        ws_inicial.update_acell('D6', aforo_inicial)
        ws_inicial.update_acell('E3', aforo_inicial)
        ws_inicial.update_acell('C2', aforo_inicial)

        ws_primaria = sh.worksheet("PRIM")
        ws_primaria.update_acell('E3', aforo_primaria)
        # Actualizar rango D5:D10 (6 filas)
        valores_prim = [[aforo_primaria]] * 6
        ws_primaria.update('D5:D10', valores_prim)

        ws_sec = sh.worksheet("SEC")
        ws_sec.update_acell('E3', aforo_sec)
        # Actualizar rango D5:D9 (5 filas)
        valores_sec = [[aforo_sec]] * 5
        ws_sec.update('D5:D9', valores_sec)

        print("⏳ Esperando recalculo de Google Sheets...")
        time.sleep(3)

        ws_calculos = sh.worksheet("CALCULOS")

        data = ws_calculos.get_all_values()
        df_calculos = pd.DataFrame(data[1:], columns=data[0])

        def limpiar_numero_peruano(valor):
            if not valor or str(valor).strip() == "":
                return 0.0

            s_valor = str(valor).strip()

            if "," in s_valor:
                s_valor = s_valor.replace('.', '')
                s_valor = s_valor.replace(',', '.')

            try:
                return float(s_valor)
            except ValueError:
                return valor

        df_calculos = df_calculos.map(limpiar_numero_peruano)

        df_calculos.dropna(how="all", inplace=True)
        df_calculos = df_calculos.loc[:, df_calculos.columns != '']

        print(f"✅ Proceso completado. {len(df_calculos)} filas extraídas de CALCULOS.")
        return df_calculos

    except Exception as e:
        print(f"❌ Error en el flujo de Google Sheets: {e}")
        return None
    
# df_excel = procesar_y_extraer_sheets(df_aforo.to_dict(orient="records"), "MARIATEGUI")
# df_excel