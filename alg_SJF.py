class SJF:
    @staticmethod
    def simular(procesos):
        if not procesos:
            return "No hay procesos para ejecutar."

        # Ordenar por tiempo de llegada (1), ráfaga (2) y nombre (3)
        procesos_ordenados = sorted(
            procesos, key=lambda p: (p["arrival_time"], p["burst_time"], p["process"])
        )

        tiempo_actual = 0
        cola = []
        indice = 0
        total_espera = 0
        total_retorno = 0
        orden_ejecucion = []

        while indice < len(procesos_ordenados) or cola:
            # 1. Encolar los procesos que ya llegaron al tiempo_actual
            while indice < len(procesos_ordenados) and procesos_ordenados[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos_ordenados[indice])
                indice += 1

            # 2. Si no hay procesos en cola, el procesador está inactivo (Idle)
            if not cola:
                tiempo_actual = procesos_ordenados[indice]["arrival_time"]
                continue

            # 3. SJF Core: elegir el proceso con la ráfaga más corta.
            #    Se busca el índice (no el objeto) para evitar borrar un
            #    duplicado incorrecto con list.remove().
            idx_min = min(
                range(len(cola)),
                key=lambda i: (cola[i]["burst_time"], cola[i]["arrival_time"], cola[i]["process"])
            )
            proceso = cola.pop(idx_min)

            llegada = proceso["arrival_time"]
            burst = max(0, proceso["burst_time"])  # protege contra datos inválidos
            inicio = tiempo_actual
            fin = tiempo_actual + burst

            # 4. Métricas
            espera = inicio - llegada       # inicio siempre >= llegada
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

        # 5. Formateo de salida
        cantidad_procesos = len(procesos_ordenados)
        promedio_espera = total_espera / cantidad_procesos
        promedio_retorno = total_retorno / cantidad_procesos

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

        return "\n".join(resumen)