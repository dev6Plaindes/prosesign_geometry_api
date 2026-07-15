from typing import Literal

RegionPeru = Literal[
    "LIMA METROPOLITANA Y PROVINCIA CONSTITUCIONAL DEL CALLAO",
    "COSTA (EXCEPTO LIMA METROPOLITANA Y CALLAO)",
    "SIERRA",
    "SELVA"
]

def region_classifier(departamento: str, provincia: str = "") -> RegionPeru:
    dep = departamento.strip().upper()
    prov = provincia.strip().upper()

    # 🌆 Caso especial: Lima + Callao
    if dep == "LIMA" or dep == "CALLAO":
        return "LIMA METROPOLITANA Y PROVINCIA CONSTITUCIONAL DEL CALLAO"
    
    # 🌴 SELVA
    selva = {
        "LORETO",
        "UCAYALI",
        "MADRE DE DIOS",
        "SAN MARTIN",
        "AMAZONAS"
    }

    # 🏔 SIERRA
    sierra = {
        "CAJAMARCA",
        "CUSCO",
        "PUNO",
        "AYACUCHO",
        "HUANCAVELICA",
        "HUANUCO",
        "PASCO",
        "APURIMAC",
        "JUNIN"
    }

    # 🌊 COSTA (resto)
    costa_excepciones = {"LIMA", "CALLAO"}

    if dep in selva:
        return "SELVA"

    if dep in sierra:
        return "SIERRA"

    if dep not in costa_excepciones:
        return "COSTA (EXCEPTO LIMA METROPOLITANA Y CALLAO)"

    # fallback (por seguridad)
    return "COSTA (EXCEPTO LIMA METROPOLITANA Y CALLAO)"