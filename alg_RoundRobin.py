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

        cola = deque()
        indice = 0
        tiempo_actual = 0
        orden_ejecucion = []
        resultados = []
        
        # Lista extra para guardar los bloques exactos de ejecución (nos servirá para la traza)
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
            
            orden_ejecucion.append(proceso["process"])
            
            # Guardamos el bloque para la traza de escritorio
            intervalos_ejecucion.append({
                "process": proceso["process"],
                "start": inicio,
                "finish": tiempo_actual,
                "initial_remaining": proceso["remaining"] + quantum_aplicado # Lo que tenía justo antes de entrar
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
        total_retorno = sum(item["turnaround"] for item in resultados)
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
        resumen.append(f"Tiempo promedio de espera: {total_espera / len(resultados):.2f}")
        resumen.append(f"Tiempo promedio de retorno: {total_retorno / len(resultados):.2f}")

        # --- SECCIÓN: TRAZA PASO A PASO (A PAPEL) ---
        resumen.append("\n" + "=" * 60)
        resumen.append("TRAZA PASO A PASO (Prueba de Escritorio)")
        resumen.append("=" * 60)
        
        tiempo_maximo = max(item["finish"] for item in intervalos_ejecucion) if intervalos_ejecucion else 0
        
        for t in range(tiempo_maximo):
            ejecutando_str = "[Inactivo]"
            ejecutando_proc = None
            
            # Buscar quién se ejecuta en el instante t
            for item in intervalos_ejecucion:
                if item["start"] <= t < item["finish"]:
                    ejecutando_proc = item["process"]
                    restante = item["initial_remaining"] - (t - item["start"])
                    ejecutando_str = f"{ejecutando_proc} (restan {restante})"
                    break
            
            # Buscar quiénes están en cola
            esperando_list = []
            for p_orig in procesos_orig:
                # Si el proceso ya llegó en este instante de tiempo
                if p_orig["arrival_time"] <= t:
                    
                    # Calculamos cuánto se ha ejecutado ANTES de este instante 't'
                    tiempo_ejecutado = 0
                    for inter in intervalos_ejecucion:
                        if inter["process"] == p_orig["process"] and inter["start"] <= t:
                            tiempo_ejecutado += min(t, inter["finish"]) - inter["start"]
                    
                    restante = p_orig["burst_time"] - tiempo_ejecutado
                    
                    # Si aún le queda ráfaga y NO es el proceso que está corriendo ahora mismo
                    if restante > 0 and p_orig["process"] != ejecutando_proc:
                        esperando_list.append(f"{p_orig['process']} (restan {restante})")
            
            esperando_str = ", ".join(esperando_list) if esperando_list else "(Ninguno)"
            resumen.append(f"T={t:02d} | Ejecutando: {ejecutando_str:<18} | En cola: {esperando_str}")

        return "\n".join(resumen)