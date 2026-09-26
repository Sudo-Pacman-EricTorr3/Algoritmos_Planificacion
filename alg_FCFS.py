class FCFS:
    @staticmethod
    def simular(procesos):
        if not procesos:
            return "No hay procesos para ejecutar."

        orden = sorted(procesos, key=lambda p: (p["arrival_time"], p["process"]))
        tiempo_actual = 0
        total_espera = 0
        total_retorno = 0
        orden_ejecucion = []

        for proceso in orden:
            llegada = proceso["arrival_time"]
            burst = proceso["burst_time"]

            if tiempo_actual < llegada:
                tiempo_actual = llegada

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
                    "start": inicio,
                    "finish": fin,
                    "waiting": espera,
                    "turnaround": retorno,
                }
            )

        promedio_espera = total_espera / len(orden)
        promedio_retorno = total_retorno / len(orden)
        orden_texto = " -> ".join(item["process"] for item in orden_ejecucion)

        resumen = [
            "Algoritmo: FCFS",
            f"Orden: {orden_texto}",
        ]
        for item in orden_ejecucion:
            resumen.append(
                f"{item['process']} -> Llegada: {item['arrival']}, Burst: {item['burst']}, "
                f"Inicio: {item['start']}, Fin: {item['finish']}, Espera: {item['waiting']}, "
                f"Retorno: {item['turnaround']}"
            )
        resumen.append(f"Tiempo promedio de espera: {promedio_espera:.2f}")
        resumen.append(f"Tiempo promedio de retorno: {promedio_retorno:.2f}")
        return "\n".join(resumen)

