import gspread
import pandas as pd
from google.oauth2.service_account import Credentials
import time
from src.bim.rules.region_classifier import RegionPeru
from src.bim.schemas.schema_dto import DataFormCostosInfra


def conectar_google_sheets(ruta_json, nombre_sheet):
    """Establece la conexión con la cuenta de servicio."""
    scopes = [
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]
    creds = Credentials.from_service_account_file(ruta_json, scopes=scopes)
    gc = gspread.authorize(creds)
    return gc.open(nombre_sheet)


def procesar_y_extraer_sheets(datos, nombre_archivo_google):
    """
    Escribe los datos en las hojas correspondientes y extrae
    el resultado de la hoja CALCULOS.
    """
    ruta_json = "./hip-service-491917-s6-4e534bb75127.json"

    try:
        sh = conectar_google_sheets(ruta_json, nombre_archivo_google)

        try:
            aforo_inicial = int(datos[0]["aforo_por_grado"])
            aula_ciclo_i = int(datos[0]["aulas"]["aula_ciclo_i"])
            aula_ciclo_ii = int(datos[0]["aulas"]["aula_ciclo_ii"])

        except (IndexError, KeyError):
            aforo_inicial = 0

        try:
            aforo_primaria = int(datos[1]["aforo_por_grado"])

            aula_1_prim = int(datos[1]["aulas"]["aula_1_prim"])
            aula_2_prim = int(datos[1]["aulas"]["aula_2_prim"])
            aula_3_prim = int(datos[1]["aulas"]["aula_3_prim"])
            aula_4_prim = int(datos[1]["aulas"]["aula_4_prim"])
            aula_5_prim = int(datos[1]["aulas"]["aula_5_prim"])
            aula_6_prim = int(datos[1]["aulas"]["aula_6_prim"])

        except (IndexError, KeyError):
            aforo_primaria = 0

        try:
            aforo_sec = int(datos[2]["aforo_por_grado"])
            
            
            aula_1_sec = int(datos[2]["aulas"]["aula_1_sec"])
            aula_2_sec = int(datos[2]["aulas"]["aula_2_sec"])
            aula_3_sec = int(datos[2]["aulas"]["aula_3_sec"])
            aula_4_sec = int(datos[2]["aulas"]["aula_4_sec"])
            aula_5_sec = int(datos[2]["aulas"]["aula_5_sec"])
        except (IndexError, KeyError):
            aforo_sec = 0

        # INICIAL
        ws_inicial = sh.worksheet("INICIAL")
        ws_inicial.update_acell("E3", aforo_inicial)

        ws_inicial.update_acell("D5", aula_ciclo_i)
        ws_inicial.update_acell("D6", aula_ciclo_ii)

        # PRIMARIA
        ws_primaria = sh.worksheet("PRIM")
        ws_primaria.update_acell("E3", aforo_primaria)
        # Actualizar rango D5:D10 (6 filas)
        valores_prim = [
            [aula_1_prim],
            [aula_2_prim],
            [aula_3_prim],
            [aula_4_prim],
            [aula_5_prim],
            [aula_6_prim],
        ]
        ws_primaria.update("D5:D10", valores_prim)

        # SECUNDARIA
        ws_sec = sh.worksheet("SEC")
        ws_sec.update_acell("E3", aforo_sec)
        # Actualizar rango D5:D9 (5 filas)
        valores_sec = [
            [aula_1_sec],
            [aula_2_sec],
            [aula_3_sec],
            [aula_4_sec],
            [aula_5_sec]
        ]
        ws_sec.update("D5:D9", valores_sec)

        print("⏳ Esperando recalculo de Google Sheets...")
        time.sleep(3)

        ws_calculos = sh.worksheet("CALCULOS")

        data = ws_calculos.get_all_values()
        df_calculos = pd.DataFrame(data[1:], columns=data[0])

        def limpiar_numero_peruano(valor):
            if not valor or str(valor).strip() == "":
                return 0.0

            s_valor = str(valor).strip()

            # [DOCUMENTACIÓN] Si el valor es un error de división por cero u otro error de Excel, retornamos 0.0 para evitar caídas en el procesamiento
            if s_valor.startswith("#"):
                return 0.0

            if "," in s_valor:
                s_valor = s_valor.replace(".", "")
                s_valor = s_valor.replace(",", ".")

            try:
                return float(s_valor)
            except ValueError:
                return valor

        df_calculos = df_calculos.map(limpiar_numero_peruano)

        df_calculos.dropna(how="all", inplace=True)
        df_calculos = df_calculos.loc[:, df_calculos.columns != ""]

        print(f"✅ Proceso completado. {len(df_calculos)} filas extraídas de CALCULOS.")
        return df_calculos

    except Exception as e:
        print(f"❌ Error en el flujo de Google Sheets: {e}")
        return None


def get_name_sheet_costos_for_region(name_region: RegionPeru):
    if name_region == "COSTA (EXCEPTO LIMA METROPOLITANA Y CALLAO)":
        return "DATA COSTA (NO LIMA NI CALLAO)"
    elif name_region == "LIMA METROPOLITANA Y PROVINCIA CONSTITUCIONAL DEL CALLAO":
        return "DATA LIMA Y CALLAO"
    elif name_region == "SIERRA":
        return "DATA SIERRA"
    elif name_region == "LIMA METROPOLITANA Y PROVINCIA CONSTITUCIONAL DEL CALLAO":
        return "DATA SELVA"


def procesar_y_extraer_sheets_costos(
    datos,
    nombre_archivo_google,
    region: RegionPeru,
    data_form_costos: DataFormCostosInfra,
):
    """
    Escribe los datos en las hojas correspondientes y extrae
    el resultado de la hoja CALCULOS.
    """
    ruta_json = "./hip-service-491917-s6-4e534bb75127.json"

    name_sheet_region = get_name_sheet_costos_for_region(region)

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

        ws_inicial = sh.worksheet("UNIFICADO")
        ws_inicial.update_acell("I4", region)

        ws_inicial = sh.worksheet("INICIAL")
        ws_inicial.update_acell("D5", aforo_inicial)
        ws_inicial.update_acell("D6", aforo_inicial)
        ws_inicial.update_acell("E3", aforo_inicial)
        ws_inicial.update_acell("C2", aforo_inicial)

        ws_primaria = sh.worksheet("PRIM")
        ws_primaria.update_acell("E3", aforo_primaria)
        # Actualizar rango D5:D10 (6 filas)
        valores_prim = [[aforo_primaria]] * 6
        ws_primaria.update("D5:D10", valores_prim)

        ws_sec = sh.worksheet("SEC")
        ws_sec.update_acell("E3", aforo_sec)
        # Actualizar rango D5:D9 (5 filas)
        valores_sec = [[aforo_sec]] * 5
        ws_sec.update("D5:D9", valores_sec)

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
                s_valor = s_valor.replace(".", "")
                s_valor = s_valor.replace(",", ".")

            try:
                return float(s_valor)
            except ValueError:
                return valor

        df_calculos = df_calculos.map(limpiar_numero_peruano)

        df_calculos.dropna(how="all", inplace=True)
        df_calculos = df_calculos.loc[:, df_calculos.columns != ""]

        # =======================================================
        # HOJA DE COSTOS E INSERCCION DE CATEGORIA
        # Muros y columnas	Techos	Pisos	Puertas y ventanas	Revestimientos	Baños	Ins. eléctricas y sanitarias

        ws_costos_region = sh.worksheet(name_sheet_region)
        ws_costos_region.update_acell("C16", data_form_costos["muros_y_columnas"])
        ws_costos_region.update_acell("C17", data_form_costos["techos"])
        # ws_costos_region.update_acell('C18', data_form_costos["pisos"])
        ws_costos_region.update_acell("C19", data_form_costos["puertas_y_ventanas"])
        ws_costos_region.update_acell("C20", data_form_costos["revestimientos"])
        ws_costos_region.update_acell("C21", data_form_costos["banos"])
        ws_costos_region.update_acell("C22", data_form_costos["instalaciones"])

        print(f"✅ Proceso completado. {len(df_calculos)} filas extraídas de CALCULOS.")
        return df_calculos

    except Exception as e:
        print(f"❌ Error en el flujo de Google Sheets: {e}")
        return None
