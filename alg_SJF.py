class SJF:
    @staticmethod
    def simular(procesos):
        if not procesos:
            return "No hay procesos para ejecutar."

        procesos_ordenados = sorted(procesos, key=lambda p: (p["arrival_time"], p["burst_time"], p["process"]))
        tiempo_actual = 0
        cola = []
        indice = 0
        total_espera = 0
        total_retorno = 0
        orden_ejecucion = []

        while indice < len(procesos_ordenados) or cola:
            while indice < len(procesos_ordenados) and procesos_ordenados[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos_ordenados[indice])
                indice += 1

            if not cola:
                tiempo_actual = procesos_ordenados[indice]["arrival_time"]
                continue

            idx_min = min(
                range(len(cola)),
                key=lambda i: (cola[i]["burst_time"], cola[i]["arrival_time"], cola[i]["process"])
            )
            proceso = cola.pop(idx_min)

            llegada = proceso["arrival_time"]
            burst = proceso["burst_time"]
            inicio = tiempo_actual
            fin = tiempo_actual + burst

            espera = inicio - llegada
            retorno = fin - llegada

            total_espera += espera
            total_retorno += retorno
            tiempo_actual = fin 

            orden_ejecucion.append({
                "process": proceso["process"],
                "arrival": llegada,
                "burst": burst,
                "start": inicio,
                "finish": fin,
                "waiting": espera,
                "turnaround": retorno,
            })

        cantidad = len(procesos_ordenados)
        promedio_espera = total_espera / cantidad
        promedio_retorno = total_retorno / cantidad
        orden_texto = " -> ".join(item["process"] for item in orden_ejecucion)

        resumen = [
            "Algoritmo: SJF (No Apropiativo)",
            f"Orden: {orden_texto}",
            "-" * 60
        ]
        for item in orden_ejecucion:
            resumen.append(
                f"[{item['process']:>2}] Llegada: {item['arrival']:2d} | Burst: {item['burst']:2d} | "
                f"Inicio: {item['start']:2d} | Fin: {item['finish']:2d} | "
                f"Espera: {item['waiting']:2d} | Retorno: {item['turnaround']:2d}"
            )
        resumen.append("-" * 60)
        resumen.append(f"Tiempo promedio de espera: {promedio_espera:.2f}")
        resumen.append(f"Tiempo promedio de retorno: {promedio_retorno:.2f}")

        # --- SECCIÓN: TRAZA PASO A PASO (A PAPEL) ---
        resumen.append("\n" + "=" * 60)
        resumen.append("TRAZA PASO A PASO (Prueba de Escritorio)")
        resumen.append("=" * 60)
        
        tiempo_maximo = max(item["finish"] for item in orden_ejecucion) if orden_ejecucion else 0
        
        for t in range(tiempo_maximo):
            ejecutando_str = "[Inactivo]"
            esperando_list = []
            
            for item in orden_ejecucion:
                if item["start"] <= t < item["finish"]:
                    restante = item["finish"] - t
                    ejecutando_str = f"{item['process']} (restan {restante})"
                elif item["arrival"] <= t < item["start"]:
                    # Aquí el profe verá por qué se quedó esperando (SJF elige al más corto primero)
                    esperando_list.append(f"{item['process']} (burst: {item['burst']})")
            
            esperando_str = ", ".join(esperando_list) if esperando_list else "(Ninguno)"
            resumen.append(f"T={t:02d} | Ejecutando: {ejecutando_str:<16} | En cola: {esperando_str}")
        
        return "\n".join(resumen)