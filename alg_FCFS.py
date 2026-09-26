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

        promedio_espera = total_espera / len(orden)
        promedio_retorno = total_retorno / len(orden)
        orden_texto = " -> ".join(item["process"] for item in orden_ejecucion)

        resumen = [
            "Algoritmo: FCFS (No Apropiativo)",
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
                # Si el proceso se está ejecutando en este segundo
                if item["start"] <= t < item["finish"]:
                    restante = item["finish"] - t
                    ejecutando_str = f"{item['process']} (restan {restante})"
                
                # Si el proceso ya llegó, pero aún no inicia (está en cola)
                elif item["arrival"] <= t < item["start"]:
                    esperando_list.append(item["process"])
            
            esperando_str = ", ".join(esperando_list) if esperando_list else "(Ninguno)"
            resumen.append(f"T={t:02d} | Ejecutando: {ejecutando_str:<16} | En cola: {esperando_str}")
        
        return "\n".join(resumen)