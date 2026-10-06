from collections import deque

class RoundRobin:
    @staticmethod
    def simular(procesos, quantum):
        if not procesos:
            return "No hay procesos para ejecutar."
        if quantum <= 0:
            raise ValueError("El quantum debe ser mayor que 0.")

        # Guardamos una copia original para la traza paso a paso
        procesos_orig = [
            {
                "process": p["process"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"]
            }
            for p in procesos
        ]

        procesos_rr = [
            {
                "process": p["process"],
                "arrival_time": p["arrival_time"],
                "burst_time": p["burst_time"],
                "remaining": p["burst_time"],
            }
            for p in procesos
        ]
        procesos_rr.sort(key=lambda proceso: (proceso["arrival_time"], proceso["process"]))

        cola = deque()
        indice = 0
        tiempo_actual = 0
        orden_ejecucion = []
        resultados = []
        estados_por_tiempo = {}
        
        # Lista extra para guardar los bloques exactos de ejecución
        intervalos_ejecucion = []

        while indice < len(procesos_rr) or cola:
            # 1. Encolar los que ya llegaron
            while indice < len(procesos_rr) and procesos_rr[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos_rr[indice])
                indice += 1

            # 2. Si la cola está vacía, saltar el tiempo de inactividad
            if not cola:
                tiempo_actual = procesos_rr[indice]["arrival_time"]
                while indice < len(procesos_rr) and procesos_rr[indice]["arrival_time"] <= tiempo_actual:
                    cola.append(procesos_rr[indice])
                    indice += 1
                continue

            # 3. Sacar proceso de la cola y ejecutar por el quantum
            proceso = cola.popleft()
            inicio = tiempo_actual
            quantum_aplicado = min(quantum, proceso["remaining"])
            tiempo_actual += quantum_aplicado
            proceso["remaining"] -= quantum_aplicado

            for tiempo in range(inicio, tiempo_actual):
                cola_en_tiempo = [
                    {"process": esperando["process"], "remaining": esperando["remaining"]}
                    for esperando in cola
                ]
                for pendiente in procesos_rr[indice:]:
                    if pendiente["arrival_time"] <= tiempo:
                        cola_en_tiempo.append(
                            {"process": pendiente["process"], "remaining": pendiente["remaining"]}
                        )
                estados_por_tiempo[tiempo] = {
                    "process": proceso["process"],
                    "remaining": proceso["remaining"] + quantum_aplicado - (tiempo - inicio),
                    "queue": cola_en_tiempo,
                }
            
            orden_ejecucion.append(proceso["process"])
            
            # Guardamos el bloque para la traza de escritorio
            intervalos_ejecucion.append({
                "process": proceso["process"],
                "start": inicio,
                "finish": tiempo_actual,
                "initial_remaining": proceso["remaining"] + quantum_aplicado
            })

            # 4. Verificar si llegaron nuevos procesos MIENTRAS se ejecutaba el actual
            while indice < len(procesos_rr) and procesos_rr[indice]["arrival_time"] <= tiempo_actual:
                cola.append(procesos_rr[indice])
                indice += 1

            # 5. Si el proceso no ha terminado, se vuelve a formar al FINAL de la cola
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
        formula_espera = " + ".join(str(item["waiting"]) for item in resultados)
        orden_texto = " -> ".join(orden_ejecucion)

        resumen = [
            "Algoritmo: Round Robin (Apropiativo)",
            f"Quantum: {quantum}",
            f"Orden: {orden_texto}",
            "-" * 60
        ]
        for item in resultados:
            resumen.append(
                f"[{item['process']:>2}] Fin: {item['completion']:2d} | "
                f"Espera: {item['waiting']:2d} | Retorno: {item['turnaround']:2d}"
            )
        resumen.append("-" * 60)
        resumen.append(
            f"Tiempo promedio de espera: ({formula_espera}) / {len(resultados)} = "
            f"{total_espera / len(resultados):.2f} ms"
        )

        # --- SECCIÓN: TRAZA PASO A PASO ---
        resumen.append("\n" + "=" * 60)
        resumen.append("=" * 60)
        
        tiempo_maximo = max(item["finish"] for item in intervalos_ejecucion) if intervalos_ejecucion else 0
        
        for t in range(tiempo_maximo):
            ejecutando_str = "[Inactivo]"
            estado = estados_por_tiempo.get(t)
            esperando_list = []
            if estado is not None:
                ejecutando_str = f"{estado['process']} (restan {estado['remaining']})"
                esperando_list = [
                    f"{proceso_cola['process']} (restan {proceso_cola['remaining']})"
                    for proceso_cola in estado["queue"]
                ]
            
            esperando_str = ", ".join(esperando_list) if esperando_list else "(Ninguno)"
            resumen.append(f"T={t:02d} | Ejecutando: {ejecutando_str:<18} | En cola: {esperando_str}")

        return "\n".join(resumen)