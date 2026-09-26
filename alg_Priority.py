class PriorityScheduler:
    @staticmethod
    def simular(procesos):
        if not procesos:
            return "No hay procesos para ejecutar."

        procesos_ordenados = sorted(procesos, key=lambda p: (p["arrival_time"], p["priority"], p["process"]))
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

            proceso = min(cola, key=lambda p: (p["priority"], p["arrival_time"], p["process"]))
            cola.remove(proceso)

            llegada = proceso["arrival_time"]
            burst = proceso["burst_time"]
            inicio = tiempo_actual
            fin = tiempo_actual + burst
            espera = max(0, inicio - llegada)
            retorno = fin - llegada

            total_espera += espera
            total_retorno += retorno
            tiempo_actual = fin
            orden_ejecucion.append(
                {
                    "process": proceso["process"],
                    "arrival": llegada,
                    "burst": burst,
                    "priority": proceso["priority"],
                    "start": inicio,
                    "finish": fin,
                    "waiting": espera,
                    "turnaround": retorno,
                }
            )

        promedio_espera = total_espera / len(procesos_ordenados)
        promedio_retorno = total_retorno / len(procesos_ordenados)
        orden_texto = " -> ".join(item["process"] for item in orden_ejecucion)

        resumen = [
            "Algoritmo: Priority",
            f"Orden: {orden_texto}",
        ]
        for item in orden_ejecucion:
            resumen.append(
                f"{item['process']} -> Llegada: {item['arrival']}, Burst: {item['burst']}, "
                f"Prioridad: {item['priority']}, Inicio: {item['start']}, Fin: {item['finish']}, "
                f"Espera: {item['waiting']}, Retorno: {item['turnaround']}"
            )
        resumen.append(f"Tiempo promedio de espera: {promedio_espera:.2f}")
        resumen.append(f"Tiempo promedio de retorno: {promedio_retorno:.2f}")
        return "\n".join(resumen)


