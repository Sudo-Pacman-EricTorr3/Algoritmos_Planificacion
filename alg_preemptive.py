def generar_timeline(procesos, criterio):
    procesos_ordenados = sorted(
        procesos,
        key=lambda proceso: (proceso["arrival_time"], proceso["process"]),
    )
    restante = {
        proceso["process"]: proceso["burst_time"]
        for proceso in procesos_ordenados
    }
    indice = 0
    tiempo = 0
    timeline = []

    while indice < len(procesos_ordenados) or any(restante.values()):
        while (
            indice < len(procesos_ordenados)
            and procesos_ordenados[indice]["arrival_time"] <= tiempo
        ):
            indice += 1

        listos = [
            proceso
            for proceso in procesos_ordenados[:indice]
            if restante[proceso["process"]] > 0
        ]
        if not listos:
            tiempo = procesos_ordenados[indice]["arrival_time"]
            continue

        proceso = min(
            listos,
            key=lambda item: (
                criterio(item, restante[item["process"]]),
                item["arrival_time"],
                item["process"],
            ),
        )
        nombre = proceso["process"]
        if timeline and timeline[-1]["process"] == nombre:
            timeline[-1]["finish"] = tiempo + 1
        else:
            segmento = {
                "process": nombre,
                "arrival": proceso["arrival_time"],
                "burst": proceso["burst_time"],
                "start": tiempo,
                "finish": tiempo + 1,
            }
            if "priority" in proceso:
                segmento["priority"] = proceso["priority"]
            timeline.append(segmento)

        restante[nombre] -= 1
        tiempo += 1

    return timeline


def generar_timeline_no_apropiativo(procesos, criterio):
    procesos_ordenados = sorted(
        procesos,
        key=lambda proceso: (proceso["arrival_time"], proceso["process"]),
    )
    restante = {
        proceso["process"]: proceso["burst_time"]
        for proceso in procesos_ordenados
    }
    indice = 0
    tiempo = 0
    timeline = []

    while indice < len(procesos_ordenados) or any(restante.values()):
        while (
            indice < len(procesos_ordenados)
            and procesos_ordenados[indice]["arrival_time"] <= tiempo
        ):
            indice += 1

        listos = [
            proceso
            for proceso in procesos_ordenados[:indice]
            if restante[proceso["process"]] > 0
        ]
        if not listos:
            tiempo = procesos_ordenados[indice]["arrival_time"]
            continue

        proceso = min(
            listos,
            key=lambda item: (
                criterio(item, restante[item["process"]]),
                item["arrival_time"],
                item["process"],
            ),
        )
        inicio = tiempo
        tiempo += restante[proceso["process"]]
        restante[proceso["process"]] = 0
        segmento = {
            "process": proceso["process"],
            "arrival": proceso["arrival_time"],
            "burst": proceso["burst_time"],
            "start": inicio,
            "finish": tiempo,
        }
        if "priority" in proceso:
            segmento["priority"] = proceso["priority"]
        timeline.append(segmento)

    return timeline


def generar_resumen(procesos, timeline, nombre_algoritmo, quantum=None):
    if not procesos:
        return "No hay procesos para ejecutar."

    estadisticas = {}
    for proceso in procesos:
        segmentos = [
            segmento
            for segmento in timeline
            if segmento["process"] == proceso["process"]
        ]
        fin = max(segmento["finish"] for segmento in segmentos)
        inicio = min(segmento["start"] for segmento in segmentos)
        estadisticas[proceso["process"]] = {
            "process": proceso["process"],
            "arrival": proceso["arrival_time"],
            "burst": proceso["burst_time"],
            "start": inicio,
            "finish": fin,
            "waiting": fin - proceso["arrival_time"] - proceso["burst_time"],
            "turnaround": fin - proceso["arrival_time"],
            "priority": proceso.get("priority"),
        }

    orden = sorted(
        estadisticas.values(),
        key=lambda item: (item["start"], item["process"]),
    )
    formula_espera = " + ".join(str(item["waiting"]) for item in orden)
    promedio_espera = sum(item["waiting"] for item in orden) / len(orden)
    orden_ejecucion = " -> ".join(
        segmento["process"] for segmento in timeline
    )
    resumen = [f"Algoritmo: {nombre_algoritmo}"]
    if quantum is not None:
        resumen.append(f"Quantum: {quantum}")
    resumen.extend((f"Orden: {orden_ejecucion}", "-" * 60))

    for item in orden:
        prioridad = (
            f"Prioridad: {item['priority']} | "
            if item["priority"] is not None
            else ""
        )
        resumen.append(
            f"[{item['process']:>2}] Llegada: {item['arrival']:2d} | "
            f"Burst: {item['burst']:2d} | {prioridad}"
            f"Inicio: {item['start']:2d} | Fin: {item['finish']:2d} | "
            f"Espera: {item['waiting']:2d} | Retorno: {item['turnaround']:2d}"
        )

    resumen.extend(
        (
            "-" * 60,
            f"Tiempo promedio de espera: ({formula_espera}) / {len(orden)} = "
            f"{promedio_espera:.2f} ms",
            "\n" + "=" * 60,
            "=" * 60,
        )
    )

    tiempo_maximo = max(segmento["finish"] for segmento in timeline)
    for tiempo in range(tiempo_maximo):
        segmento_activo = next(
            (
                segmento
                for segmento in timeline
                if segmento["start"] <= tiempo < segmento["finish"]
            ),
            None,
        )
        if segmento_activo is None:
            ejecutando = "[Inactivo]"
            proceso_activo = None
        else:
            proceso_activo = segmento_activo["process"]
            ejecutado = sum(
                max(0, min(tiempo + 1, segmento["finish"]) - segmento["start"])
                for segmento in timeline
                if segmento["process"] == proceso_activo
            )
            restante = max(
                0,
                estadisticas[proceso_activo]["burst"] - ejecutado,
            )
            ejecutando = f"{proceso_activo} (restan {restante})"

        esperando = []
        for item in orden:
            if (
                item["arrival"] <= tiempo < item["finish"]
                and item["process"] != proceso_activo
            ):
                ejecutado = sum(
                    max(
                        0,
                        min(tiempo, segmento["finish"]) - segmento["start"],
                    )
                    for segmento in timeline
                    if segmento["process"] == item["process"]
                )
                restante = item["burst"] - ejecutado
                dato = f"{item['process']} (restan {restante})"
                if item["priority"] is not None:
                    dato = f"{item['process']} (prio: {item['priority']}, restan {restante})"
                esperando.append(dato)

        cola = ", ".join(esperando) if esperando else "(Ninguno)"
        resumen.append(f"T={tiempo:02d} | Ejecutando: {ejecutando:<18} | En cola: {cola}")

    return "\n".join(resumen)
