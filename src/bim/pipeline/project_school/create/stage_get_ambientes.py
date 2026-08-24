import json
from src.bim.adapters.google_sheets_adapter import procesar_y_extraer_sheets
from src.bim.pipeline.project_school.create.pipeline_context import PipelineContext
from src.utils.logger import logger


def normalizar_nombre(nombre: str) -> str:
    """Normaliza nombres eliminando tildes, caracteres especiales y paréntesis"""
    if not nombre:
        return ""
    replacements = {
        "Á": "A", "É": "E", "Í": "I", "Ó": "O", "Ú": "U", "Ü": "U",
        "á": "a", "é": "e", "í": "i", "ó": "o", "ú": "u", "ü": "u"
    }
    result = nombre.strip().upper()
    for old, new in replacements.items():
        result = result.replace(old, new)
        
    # Eliminar puntuaciones comunes, espacios y paréntesis para evitar fallos de formato
    for char in [".", ",", "-", "_", "(", ")", " "]:
        result = result.replace(char, "")
        
    return result


def stage_get_ambientes(ctx: PipelineContext):
    
    logger.info("PROCESANDO AMBIENTES...")
    
    df_excel_ambientes = procesar_y_extraer_sheets(
        datos=ctx.request.aforo, 
        nombre_archivo_google="MARIATEGUI"
    )
    
    ctx.ambientes = df_excel_ambientes.to_dict(orient="records")
    
    with open('ambientes_original.json', 'w', encoding='utf-8') as f:
        json.dump(ctx.ambientes, f, indent=4, ensure_ascii=False)

    # ==================== LÓGICA PARA EXCLUIR GRADOS CON AFORO CERO ====================
    aforo_data = ctx.request.aforo
    grados_a_excluir = {
        item.get("grado", "").upper()
        for item in aforo_data
        if item.get("aforo_por_grado", 0) == 0 or item.get("cantidad_aulas", 0) == 0
    }
    
    if grados_a_excluir:
        logger.info(f"Grados a excluir por aforo/aulas cero: {grados_a_excluir}")

        pabellon_map = {
            "INICIAL": "Inferior",
            "PRIMARIA": "Izquierda",
            "SECUNDARIA": "Derecha"
        }
        pabellones_a_excluir = {pabellon_map[g] for g in grados_a_excluir if g in pabellon_map}
        
        if pabellones_a_excluir:
            logger.info(f"Pabellones a excluir: {pabellones_a_excluir}")
            ctx.ambientes = [row for row in ctx.ambientes if row.get("Pabellon") not in pabellones_a_excluir]

    # ==================== LISTA OFICIAL DE AMBIENTES COMPLEMENTARIOS ====================
    complementarios_posibles = {
        "SALA DE USOS MÚLTIPLES (SUM)",
        "COCINA ESCOLAR",
        "DIRECCIÓN ADMINISTRATIVA",
        "PATIO INICIAL",
        "AUDITORIO MULTIUSOS",
        "SALA DE REUNIONES",
        "LACTARIO",
        "TOPICO",
        "SALA DE PSICOMOTRICIDAD",
        "SALA DE MAESTROS",
        "BIBLIOTECA",
        "TALLER CREATIVO",
        "AREA DE ESPERA",
        "AULA DE INNOVACION SEC",
        "TALLER CREATIVO SEC",
        "LABORATORIO",
        "ESCALERA SEC",
        "SSHH SEC - HOMBRES",
        "SSHH SEC - MUJERES",
        "AULA DE INNOVACION PRIM",
        "TALLER CREATIVO PRIM",
        "ESCALERA PRIM",
        "SSHH PRIM - HOMBRES",
        "SSHH PRIM - MUJERES",
        "SSHH INICIAL - HOMBRES",
        "SSHH INICIAL - MUJERES",
        "COCINA INICIAL",
        "DIRECCION ADM.",
        "ÁREA DE ESPERA",
        "AREA DE INGRESO",
        "SALA DE PROFESORES",
        "SSHH ADM. - HOMBRES",
        "SSHH ADM. - MUJERES",
        "LOSA DEPORTIVA",
        "TALLER EPT",
        "SUM",
        "COCINA PRIM - SEC",
    }

    solicitud_ambientes = getattr(ctx.request, 'ambientes', None) or []
    
    seleccionados = {
        normalizar_nombre(amb["ambienteComplementario"]) 
        for amb in solicitud_ambientes 
        if "ambienteComplementario" in amb
    }

    if not seleccionados:
        logger.info("No se recibieron ambientes complementarios. Se removerán todos los complementarios.")
    else:
        logger.info(f"Ambientes complementarios seleccionados: {seleccionados}")

    ambientes_filtrados = []
    eliminados = 0

    for row in ctx.ambientes:
        nombre_ambiente = row.get("Ambientes", "")
        nombre_norm = normalizar_nombre(nombre_ambiente)

        # ¿Es un ambiente complementario?
        es_complementario = False
        for comp in complementarios_posibles:
            comp_norm = normalizar_nombre(comp)
            # Validación bidireccional (si uno contiene al otro) o si son iguales
            if comp_norm in nombre_norm or nombre_norm in comp_norm:
                es_complementario = True
                break

        if not es_complementario:
            # Ambientes fijos / principales → siempre se mantienen
            ambientes_filtrados.append(row)
        else:
            # Ambiente complementario → filtrar según selección
            # Buscamos si el nombre del Excel coincide o se cruza con los seleccionados por el usuario
            match_encontrado = False
            for sel in seleccionados:
                # Caso especial para "SUM" si en el Excel viene acortado
                if sel == "SALADEUSOSMULTIPLESSUM" and ("SUM" in nombre_norm or "SALADEUSOS" in nombre_norm):
                    match_encontrado = True
                    break
                if sel in nombre_norm or nombre_norm in sel:
                    match_encontrado = True
                    break

            if match_encontrado:
                # Mantener
                try:
                    if int(float(str(row.get("Cantidad", 0)))) == 0:
                        row["Cantidad"] = 1
                except:
                    row["Cantidad"] = 1
                ambientes_filtrados.append(row)
                logger.info(f"[OK] Mantenido complementario: {nombre_ambiente}")
            else:
                # Eliminar
                logger.info(f"[REMOVIDO] Complementario no seleccionado: {nombre_ambiente}")
                eliminados += 1

    ctx.ambientes = ambientes_filtrados

    # Guardado final
    with open('ambientes_filtrados.json', 'w', encoding='utf-8') as f:
        json.dump(ctx.ambientes, f, indent=4, ensure_ascii=False)

    logger.info(f"Filtrado completado. Ambientes finales: {len(ctx.ambientes)} | Eliminados: {eliminados}")
    
def stage_get_ambientes_test(ctx: PipelineContext):
    
    logger.info("PROCESANDO AMBIENTES...")
    
    with open('ambientes_original.json', 'w', encoding='utf-8') as f:
        json.dump(ctx.ambientes, f, indent=4, ensure_ascii=False)

    # ==================== LÓGICA PARA EXCLUIR GRADOS CON AFORO CERO ====================
    aforo_data = ctx.request.aforo
    grados_a_excluir = {
        item.get("grado", "").upper()
        for item in aforo_data
        if item.get("aforo_por_grado", 0) == 0 or item.get("cantidad_aulas", 0) == 0
    }
    
    if grados_a_excluir:
        logger.info(f"Grados a excluir por aforo/aulas cero: {grados_a_excluir}")

        pabellon_map = {
            "INICIAL": "Inferior",
            "PRIMARIA": "Izquierda",
            "SECUNDARIA": "Derecha"
        }
        pabellones_a_excluir = {pabellon_map[g] for g in grados_a_excluir if g in pabellon_map}
        
        if pabellones_a_excluir:
            logger.info(f"Pabellones a excluir: {pabellones_a_excluir}")
            ctx.ambientes = [row for row in ctx.ambientes if row.get("Pabellon") not in pabellones_a_excluir]

    # ==================== LISTA OFICIAL DE AMBIENTES COMPLEMENTARIOS ====================
    complementarios_posibles = {
        "SALA DE USOS MÚLTIPLES (SUM)",
        "COCINA ESCOLAR",
        "DIRECCIÓN ADMINISTRATIVA",
        "PATIO INICIAL",
        "AUDITORIO MULTIUSOS",
        "SALA DE REUNIONES",
        "LACTARIO",
        "TOPICO",
        "SALA DE PSICOMOTRICIDAD",
        "SALA DE MAESTROS",
        "BIBLIOTECA",
        "TALLER CREATIVO",
        "AREA DE ESPERA",
        "AULA DE INNOVACION SEC",
        "TALLER CREATIVO SEC",
        "LABORATORIO",
        "ESCALERA SEC",
        "SSHH SEC - HOMBRES",
        "SSHH SEC - MUJERES",
        "AULA DE INNOVACION PRIM",
        "TALLER CREATIVO PRIM",
        "ESCALERA PRIM",
        "SSHH PRIM - HOMBRES",
        "SSHH PRIM - MUJERES",
        "SSHH INICIAL - HOMBRES",
        "SSHH INICIAL - MUJERES",
        "COCINA INICIAL",
        "DIRECCION ADM.",
        "ÁREA DE ESPERA",
        "AREA DE INGRESO",
        "SALA DE PROFESORES",
        "SSHH ADM. - HOMBRES",
        "SSHH ADM. - MUJERES",
        "LOSA DEPORTIVA",
        "TALLER EPT",
        "SUM",
        "COCINA PRIM - SEC",
    }

    if not getattr(ctx.request, 'ambientes', None):
        logger.info("No se recibieron ambientes complementarios del usuario.")
        return

    # Selección del usuario normalizada
    seleccionados = {normalizar_nombre(amb["ambienteComplementario"]) 
                     for amb in ctx.request.ambientes}

    logger.info(f"Ambientes complementarios seleccionados: {seleccionados}")

    ambientes_filtrados = []
    eliminados = 0

    for row in ctx.ambientes:
        nombre_ambiente = row.get("Ambientes", "")
        nombre_norm = normalizar_nombre(nombre_ambiente)

        # ¿Es un ambiente complementario?
        es_complementario = False
        for comp in complementarios_posibles:
            comp_norm = normalizar_nombre(comp)
            # Validación bidireccional (si uno contiene al otro) o si son iguales
            if comp_norm in nombre_norm or nombre_norm in comp_norm:
                es_complementario = True
                break

        if not es_complementario:
            # Ambientes fijos / principales → siempre se mantienen
            ambientes_filtrados.append(row)
        else:
            # Ambiente complementario → filtrar según selección
            # Buscamos si el nombre del Excel coincide o se cruza con los seleccionados por el usuario
            match_encontrado = False
            for sel in seleccionados:
                # Caso especial para "SUM" si en el Excel viene acortado
                if sel == "SALADEUSOSMULTIPLESSUM" and ("SUM" in nombre_norm or "SALADEUSOS" in nombre_norm):
                    match_encontrado = True
                    break
                if sel in nombre_norm or nombre_norm in sel:
                    match_encontrado = True
                    break

            if match_encontrado:
                # Mantener
                try:
                    if int(float(str(row.get("Cantidad", 0)))) == 0:
                        row["Cantidad"] = 1
                except:
                    row["Cantidad"] = 1
                ambientes_filtrados.append(row)
                logger.info(f"[OK] Mantenido complementario: {nombre_ambiente}")
            else:
                # Eliminar
                logger.info(f"[REMOVIDO] Complementario no seleccionado: {nombre_ambiente}")
                eliminados += 1

    ctx.ambientes = ambientes_filtrados

    # Guardado final
    with open('ambientes_filtrados.json', 'w', encoding='utf-8') as f:
        json.dump(ctx.ambientes, f, indent=4, ensure_ascii=False)

    logger.info(f"Filtrado completado. Ambientes finales: {len(ctx.ambientes)} | Eliminados: {eliminados}")
    