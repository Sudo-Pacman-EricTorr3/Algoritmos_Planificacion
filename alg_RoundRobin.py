from collections import deque


class RoundRobin:
    @staticmethod
    def simular(procesos, quantum):
        if not procesos:
            return "No hay procesos para ejecutar."
        if quantum <= 0:
            raise ValueError("El quantum debe ser mayor que 0.")

        procesos = [
            {
                "process": p["process"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "remaining": p["burst_time"],
            }
            for p in procesos
        ]

        cola = deque()
        indice = 0
        tiempo_actual = 0
        orden_ejecucion = []
        resultados = []

        while indice < len(procesos) or cola:
            while indice < len(procesos) and procesos[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos[indice])
                indice += 1

            if not cola:
                tiempo_actual = procesos[indice]["arrival_time"]
                while indice < len(procesos) and procesos[indice]["arrival_time"] <= tiempo_actual:
                    cola.append(procesos[indice])
                    indice += 1
                continue

            proceso = cola.popleft()
            quantum_aplicado = min(quantum, proceso["remaining"])
            tiempo_actual += quantum_aplicado
            proceso["remaining"] -= quantum_aplicado
            orden_ejecucion.append(proceso["process"])

            while indice < len(procesos) and procesos[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos[indice])
                indice += 1

            if proceso["remaining"] > 0:
                cola.append(proceso)
            else:
                completion = tiempo_actual
                waiting = completion - proceso["arrival_time"] - proceso["burst_time"]
                turnaround = completion - proceso["arrival_time"]
                resultados.append(
                    {
                        "process": proceso["process"],
                        "completion": completion,
                        "waiting": waiting,
                        "turnaround": turnaround,
                    }
                )

        total_espera = sum(item["waiting"] for item in resultados)
        total_retorno = sum(item["turnaround"] for item in resultados)
        orden_texto = " -> ".join(orden_ejecucion)

        resumen = [
            "Algoritmo: Round Robin",
            f"Quantum: {quantum}",
            f"Orden: {orden_texto}",
        ]
        for item in resultados:
            resumen.append(
                f"{item['process']} -> Fin: {item['completion']}, "
                f"Espera: {item['waiting']}, Retorno: {item['turnaround']}"
            )
        resumen.append(f"Tiempo promedio de espera: {total_espera / len(resultados):.2f}")
        resumen.append(f"Tiempo promedio de retorno: {total_retorno / len(resultados):.2f}")
        return "\n".join(resumen)
 
