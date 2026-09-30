import customtkinter as ctk
from tkinter import Canvas, messagebox

from alg_FCFS import FCFS
from alg_Priority import PriorityScheduler
from alg_RoundRobin import RoundRobin
from alg_SJF import SJF

MAX_PROCESOS = 15
MAX_TIEMPO_LLEGADA = 20
MAX_RAFAGA = 20
MAX_PRIORIDAD = 10
MAX_QUANTUM = 10
MAX_DURACION_DIAGRAMA = 170


class VistaPlanificacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos de Planificación")
        self.geometry("1400x900")
        self.minsize(1000, 700)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.filas_entradas = []
        self._datos_guardados = []

        self._configurar_ui()

    def _configurar_ui(self):
        self.grid_columnconfigure(0, weight=0)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self.frame_config = ctk.CTkFrame(self, corner_radius=12)
        self.frame_config.grid(row=0, column=0, columnspan=2, padx=18, pady=(18, 10), sticky="ew")
        self.frame_config.grid_columnconfigure(1, weight=0)

        self.label_total = ctk.CTkLabel(
            self.frame_config,
            text="Número de procesos (MAX 15 PROCESOS):",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_total.grid(row=0, column=0, padx=(18, 10), pady=(18, 8), sticky="w")

        self.entry_total = ctk.CTkEntry(self.frame_config, width=76, height=30)
        self.entry_total.insert(0, "5")
        self.entry_total.grid(row=0, column=1, padx=(0, 12), pady=(18, 8), sticky="w")

        self.label_algoritmo = ctk.CTkLabel(
            self.frame_config,
            text="Algoritmo:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_algoritmo.grid(row=0, column=2, padx=(10, 8), pady=(18, 8), sticky="w")

        self.algoritmo_var = ctk.StringVar(value="FCFS")
        self.op_algoritmo = ctk.CTkOptionMenu(
            self.frame_config,
            values=["FCFS", "SJF", "Priority", "Round Robin"],
            variable=self.algoritmo_var,
            command=self._on_algoritmo_cambiado,
            width=160,
        )
        self.op_algoritmo.grid(row=0, column=3, padx=(0, 10), pady=(18, 8), sticky="ew")

        self.label_quantum = ctk.CTkLabel(
            self.frame_config,
            text="Quantum (1-10):",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_quantum.grid(row=0, column=4, padx=(10, 8), pady=(18, 8), sticky="w")

        self.entry_quantum = ctk.CTkEntry(self.frame_config, width=90)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=0, column=5, padx=(0, 12), pady=(18, 8), sticky="ew")

        self.frame_acciones_procesos = ctk.CTkFrame(self.frame_config, fg_color="transparent")
        self.frame_acciones_procesos.grid(row=1, column=0, columnspan=2, padx=(18, 0), pady=(4, 14), sticky="w")

        self.btn_generar = ctk.CTkButton(
            self.frame_acciones_procesos,
            text="Generar matriz",
            command=self.generar_matriz,
            width=132,
            height=32,
        )
        self.btn_generar.grid(row=0, column=0, padx=(0, 6), sticky="w")

        self.btn_limpiar = ctk.CTkButton(
            self.frame_acciones_procesos,
            text="Limpiar",
            command=self.limpiar,
            width=88,
            height=32,
            fg_color="#6B7280",
            hover_color="#4B5563",
        )
        self.btn_limpiar.grid(row=0, column=1, sticky="w")

        self.btn_simular = ctk.CTkButton(
            self.frame_config,
            text="Simular algoritmo",
            command=self.simular,
            width=180,
            height=32,
        )
        self.btn_simular.grid(row=1, column=2, columnspan=2, padx=(8, 18), pady=(4, 14), sticky="w")

        self._actualizar_quantum(self.algoritmo_var.get())

        self.frame_tabla = ctk.CTkScrollableFrame(self, corner_radius=12, width=540, height=210)
        self.frame_tabla.grid(row=1, column=0, padx=18, pady=(0, 8), sticky="nw")

        self.frame_gantt = ctk.CTkFrame(self, corner_radius=12)
        self.frame_gantt.grid(row=1, column=1, padx=(0, 18), pady=(0, 8), sticky="nsew")
        self.frame_gantt.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            self.frame_gantt,
            text="El diagrama de Gantt aparecerá aquí.",
            font=ctk.CTkFont(size=14),
        ).grid(row=0, column=0, padx=16, pady=16, sticky="nw")

        self.frame_resultados = ctk.CTkFrame(self, corner_radius=12)
        self.frame_resultados.grid(row=2, column=0, columnspan=2, padx=18, pady=(0, 18), sticky="nsew")
        self.frame_resultados.grid_columnconfigure(0, weight=1)
        self.frame_resultados.grid_rowconfigure(0, weight=1)
        self._resultado_widget = None
        ctk.CTkLabel(
            self.frame_resultados,
            text="La tabla de estados y el resumen aparecerán aquí.",
            font=ctk.CTkFont(size=14),
        ).grid(row=0, column=0, padx=16, pady=16, sticky="nw")

    def _obtener_columnas(self):
        algoritmo = self.algoritmo_var.get()
        if algoritmo == "Priority":
            return ["Process", "Arrival Time (0-20)", "Burst Time (1-20)", "Priority (1-10)"]
        return ["Process", "Arrival Time (0-20)", "Burst Time (1-20)"]

    def _validar_cantidad_procesos(self):
        try:
            cantidad = int(self.entry_total.get())
        except ValueError:
            messagebox.showerror("Entrada inválida", "Debes ingresar un número entero válido.")
            return None

        if cantidad <= 0:
            messagebox.showwarning("Cantidad inválida", "El número de procesos debe ser mayor que 0.")
            return None

        if cantidad > MAX_PROCESOS:
            messagebox.showwarning(
                "Límite de procesos",
            f"El máximo permitido es {MAX_PROCESOS} procesos. No se generará la matriz ni se ejecutará la simulación.",
            )
            return None

        return cantidad

    def generar_matriz(self):
        cantidad = self._validar_cantidad_procesos()
        if cantidad is None:
            return

       

        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        self.filas_entradas = []
        self._datos_guardados = []

        columnas = self._obtener_columnas()
        self.frame_tabla.configure(width=720 if self.algoritmo_var.get() == "Priority" else 540)
        for col_index, titulo in enumerate(columnas):
            label = ctk.CTkLabel(
                self.frame_tabla,
                text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=18,
                height=2,
            )
            label.grid(row=0, column=col_index, padx=8, pady=4, sticky="nsew")

        for i in range(cantidad):
            nombre = ctk.CTkLabel(self.frame_tabla, text=f"P{i + 1}", width=12, height=26)
            nombre.grid(row=i + 1, column=0, padx=8, pady=3, sticky="ew")

            arrival = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
            burst = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
            fila = {
                "process": nombre,
                "arrival": arrival,
                "burst": burst,
            }

            arrival.grid(row=i + 1, column=1, padx=8, pady=3, sticky="ew")
            burst.grid(row=i + 1, column=2, padx=8, pady=3, sticky="ew")

            if self.algoritmo_var.get() == "Priority":
                priority = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
                priority.grid(row=i + 1, column=3, padx=8, pady=3, sticky="ew")
                fila["priority"] = priority

            self.filas_entradas.append(fila)

        self.frame_tabla.grid_columnconfigure(0, weight=0, minsize=80)
        for col in range(1, len(columnas)):
            self.frame_tabla.grid_columnconfigure(col, weight=0, minsize=180)

    def limpiar(self):
        self.entry_total.delete(0, "end")
        self.entry_quantum.delete(0, "end")
        self.filas_entradas.clear()
        self._datos_guardados.clear()

        for contenedor in (self.frame_tabla, self.frame_gantt, self.frame_resultados):
            for widget in contenedor.winfo_children():
                widget.destroy()

        self.frame_tabla.configure(width=540)
        ctk.CTkLabel(
            self.frame_gantt,
            text="El diagrama de Gantt aparecerá aquí.",
            font=ctk.CTkFont(size=14),
        ).grid(row=0, column=0, padx=16, pady=16, sticky="nw")
        ctk.CTkLabel(
            self.frame_resultados,
            text="La tabla de estados y el resumen aparecerán aquí.",
            font=ctk.CTkFont(size=14),
        ).grid(row=0, column=0, padx=16, pady=16, sticky="nw")
        self._resultado_widget = None

    def leer_procesos(self):
        procesos = []
        algoritmo = self.algoritmo_var.get()

        for index, fila in enumerate(self.filas_entradas, start=1):
            try:
                arrival_time = int(fila["arrival"].get())
                burst_time = int(fila["burst"].get())
                priority = None
                if algoritmo == "Priority":
                    if "priority" not in fila or fila["priority"] is None:
                        raise ValueError
                    priority = int(fila["priority"].get())
            except ValueError:
                if algoritmo == "Priority":
                    mensaje = "Ingresa enteros válidos en Arrival Time, Burst Time y Priority."
                else:
                    mensaje = "Ingresa enteros válidos en Arrival Time y Burst Time."
                messagebox.showerror(
                    "Datos incompletos",
                    f"El proceso P{index} tiene valores inválidos. {mensaje}",
                )
                return []

            if not 0 <= arrival_time <= MAX_TIEMPO_LLEGADA or not 1 <= burst_time <= MAX_RAFAGA:
                messagebox.showerror(
                    "Valor fuera de rango",
                    f"P{index}: Arrival Time debe estar entre 0 y {MAX_TIEMPO_LLEGADA}, y Burst Time entre 1 y {MAX_RAFAGA}.",
                )
                return []

            if algoritmo == "Priority" and not 1 <= priority <= MAX_PRIORIDAD:
                messagebox.showerror(
                    "Prioridad fuera de rango",
                    f"P{index}: Priority debe estar entre 1 y {MAX_PRIORIDAD}.",
                )
                return []

            proceso = {
                "process": f"P{index}",
                "arrival_time": arrival_time,
                "burst_time": burst_time,
            }
            if algoritmo == "Priority":
                proceso["priority"] = priority

            procesos.append(proceso)

        return procesos

    def _actualizar_quantum(self, algoritmo):
        if algoritmo == "Round Robin":
            self.label_quantum.grid()
            self.entry_quantum.grid()
        else:
            self.label_quantum.grid_remove()
            self.entry_quantum.grid_remove()

    def _on_algoritmo_cambiado(self, algoritmo):
        self._actualizar_quantum(algoritmo)

        if not self.filas_entradas:
            return

        datos_previos = []
        for i, fila in enumerate(self.filas_entradas):
            valor = {
                "arrival": fila["arrival"].get(),
                "burst": fila["burst"].get(),
            }
            if "priority" in fila:
                valor["priority"] = fila["priority"].get()
            elif i < len(self._datos_guardados) and "priority" in self._datos_guardados[i]:
                valor["priority"] = self._datos_guardados[i]["priority"]
            datos_previos.append(valor)
        self._datos_guardados = datos_previos

        for widget in self.frame_tabla.winfo_children():
            widget.destroy()

        self.filas_entradas = []
        columnas = self._obtener_columnas()
        self.frame_tabla.configure(width=720 if self.algoritmo_var.get() == "Priority" else 540)

        for col_index, titulo in enumerate(columnas):
            label = ctk.CTkLabel(
                self.frame_tabla,
                text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=18,
                height=2,
            )
            label.grid(row=0, column=col_index, padx=8, pady=4, sticky="nsew")

        for i, datos in enumerate(self._datos_guardados if self._datos_guardados else datos_previos):
            nombre = ctk.CTkLabel(self.frame_tabla, text=f"P{i + 1}", width=12, height=26)
            nombre.grid(row=i + 1, column=0, padx=8, pady=3, sticky="ew")

            arrival = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
            burst = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
            arrival.insert(0, datos.get("arrival", ""))
            burst.insert(0, datos.get("burst", ""))

            arrival.grid(row=i + 1, column=1, padx=8, pady=3, sticky="ew")
            burst.grid(row=i + 1, column=2, padx=8, pady=3, sticky="ew")

            fila = {
                "process": nombre,
                "arrival": arrival,
                "burst": burst,
            }

            if self.algoritmo_var.get() == "Priority":
                priority = ctk.CTkEntry(self.frame_tabla, width=120, height=28)
                priority.insert(0, datos.get("priority", ""))
                priority.grid(row=i + 1, column=3, padx=8, pady=3, sticky="ew")
                fila["priority"] = priority

            self.filas_entradas.append(fila)

        self.frame_tabla.grid_columnconfigure(0, weight=0, minsize=80)
        for col in range(1, len(columnas)):
            self.frame_tabla.grid_columnconfigure(col, weight=0, minsize=180)

    def mostrar_resultado(self, texto):
        if self._resultado_widget is None or not self._resultado_widget.winfo_exists():
            return
        self._resultado_widget.configure(state="normal")
        self._resultado_widget.delete("1.0", "end")
        self._resultado_widget.insert("end", texto)
        self._resultado_widget.configure(state="disabled")

    def _timeline_por_algoritmo(self, procesos, algoritmo, quantum=None):
        if algoritmo == "FCFS":
            orden = sorted(procesos, key=lambda p: (p["arrival_time"], p["process"]))
            actual = 0
            timeline = []
            for proceso in orden:
                inicio = max(actual, proceso["arrival_time"])
                fin = inicio + proceso["burst_time"]
                timeline.append(
                    {
                        "process": proceso["process"],
                        "arrival": proceso["arrival_time"],
                        "burst": proceso["burst_time"],
                        "start": inicio,
                        "finish": fin,
                        "waiting": max(0, inicio - proceso["arrival_time"]),
                        "turnaround": fin - proceso["arrival_time"],
                    }
                )
                actual = fin
            return timeline

        if algoritmo == "SJF":
            orden = sorted(procesos, key=lambda p: (p["arrival_time"], p["burst_time"], p["process"]))
            actual = 0
            cola = []
            timeline = []
            indice = 0
            while indice < len(orden) or cola:
                while indice < len(orden) and orden[indice]["arrival_time"] <= actual:
                    cola.append(orden[indice])
                    indice += 1
                if not cola:
                    actual = orden[indice]["arrival_time"]
                    continue
                proceso = min(cola, key=lambda p: (p["burst_time"], p["arrival_time"], p["process"]))
                cola.remove(proceso)
                inicio = actual
                fin = actual + proceso["burst_time"]
                timeline.append(
                    {
                        "process": proceso["process"],
                        "arrival": proceso["arrival_time"],
                        "burst": proceso["burst_time"],
                        "start": inicio,
                        "finish": fin,
                        "waiting": max(0, inicio - proceso["arrival_time"]),
                        "turnaround": fin - proceso["arrival_time"],
                    }
                )
                actual = fin
            return timeline

        if algoritmo == "Priority":
            orden = sorted(procesos, key=lambda p: (p["arrival_time"], p["priority"], p["process"]))
            actual = 0
            cola = []
            timeline = []
            indice = 0
            while indice < len(orden) or cola:
                while indice < len(orden) and orden[indice]["arrival_time"] <= actual:
                    cola.append(orden[indice])
                    indice += 1
                if not cola:
                    actual = orden[indice]["arrival_time"]
                    continue
                proceso = min(cola, key=lambda p: (p["priority"], p["arrival_time"], p["process"]))
                cola.remove(proceso)
                inicio = actual
                fin = actual + proceso["burst_time"]
                timeline.append(
                    {
                        "process": proceso["process"],
                        "arrival": proceso["arrival_time"],
                        "burst": proceso["burst_time"],
                        "priority": proceso["priority"],
                        "start": inicio,
                        "finish": fin,
                        "waiting": max(0, inicio - proceso["arrival_time"]),
                        "turnaround": fin - proceso["arrival_time"],
                    }
                )
                actual = fin
            return timeline

        if algoritmo == "Round Robin":
            from collections import deque
            if quantum is None:
                quantum = int(self.entry_quantum.get())
            cola = deque()
            procesos_rr = [
                {"process": p["process"], "arrival_time": p["arrival_time"], "burst_time": p["burst_time"], "remaining": p["burst_time"]}
                for p in procesos
            ]
            procesos_rr.sort(key=lambda proceso: (proceso["arrival_time"], proceso["process"]))
            indice = 0
            tiempo_actual = 0
            timeline = []
            resultados = []
            while indice < len(procesos_rr) or cola:
                while indice < len(procesos_rr) and procesos_rr[indice]["arrival_time"] <= tiempo_actual:
                    cola.append(procesos_rr[indice])
                    indice += 1
                if not cola:
                    tiempo_actual = procesos_rr[indice]["arrival_time"]
                    continue
                proceso = cola.popleft()
                inicio = tiempo_actual
                slice_t = min(quantum, proceso["remaining"])
                tiempo_actual += slice_t
                proceso["remaining"] -= slice_t

                while indice < len(procesos_rr) and procesos_rr[indice]["arrival_time"] <= tiempo_actual:
                    cola.append(procesos_rr[indice])
                    indice += 1

                if proceso["remaining"] > 0:
                    cola.append(proceso)
                else:
                    resultados.append(
                        {
                            "process": proceso["process"],
                            "arrival": proceso["arrival_time"],
                            "burst": proceso["burst_time"],
                            "start": inicio,
                            "finish": tiempo_actual,
                            "waiting": tiempo_actual - proceso["arrival_time"] - proceso["burst_time"],
                            "turnaround": tiempo_actual - proceso["arrival_time"],
                        }
                    )

                timeline.append(
                    {
                        "process": proceso["process"],
                        "arrival": proceso["arrival_time"],
                        "burst": proceso["burst_time"],
                        "start": inicio,
                        "finish": tiempo_actual,
                        "waiting": max(0, tiempo_actual - proceso["arrival_time"] - proceso["burst_time"]),
                        "turnaround": tiempo_actual - proceso["arrival_time"],
                    }
                )
            return timeline

        return []

    @staticmethod
    def _estado_proceso_en_tiempo(datos_proceso, tiempo):
        llegada = datos_proceso["arrival"]
        rafaga = datos_proceso["burst"]
        segmentos = datos_proceso["segments"]

        if tiempo < llegada:
            return None, None
        if tiempo == llegada:
            return "arrival", rafaga

        finalizacion = max(segmento["finish"] for segmento in segmentos)
        if tiempo > finalizacion:
            return None, None
        if tiempo == finalizacion:
            return "finished", 0

        ejecutado = sum(
            max(0, min(tiempo, segmento["finish"]) - segmento["start"])
            for segmento in segmentos
        )
        restante = max(0, rafaga - ejecutado)
        en_ejecucion = any(
            segmento["start"] < tiempo <= segmento["finish"]
            for segmento in segmentos
        )

        if en_ejecucion:
            return "running", restante
        return "waiting", restante

    def _dibujar_gantt_horizontal(self, timeline, parent):
        total_tiempo = max(item["finish"] for item in timeline)
        ancho_unidad = 44
        margen_izquierdo = 48
        alto_canvas = 122
        colores_proceso = [
            "#B9D7EA", "#F7DFA4", "#C5E1C5", "#E8C1CE", "#CFC6E8",
            "#F4C7A1", "#BFE3E0", "#E7D6A5", "#C7D4F0", "#D8C8B7",
            "#BFD8C2", "#EBC4B5", "#C4D6D2", "#E3CBE8", "#D6D6A8",
        ]
        color_por_proceso = {
            proceso: colores_proceso[indice % len(colores_proceso)]
            for indice, proceso in enumerate(
                sorted({item["process"] for item in timeline}, key=lambda nombre: int(nombre[1:]))
            )
        }

        titulo = ctk.CTkLabel(
            parent,
            text="Diagrama de Gantt · intervalos de ejecución",
            font=ctk.CTkFont(size=16, weight="bold"),
        )
        titulo.grid(row=0, column=0, sticky="w", padx=4, pady=(0, 4))

        lienzo = Canvas(parent, height=alto_canvas, background="#FFFFFF", highlightthickness=0)
        lienzo.grid(row=1, column=0, sticky="ew")
        barra = ctk.CTkScrollbar(parent, orientation="horizontal", command=lienzo.xview)
        barra.grid(row=2, column=0, sticky="ew")
        lienzo.configure(xscrollcommand=barra.set)

        def dibujar(evento=None):
            ancho_total = margen_izquierdo + total_tiempo * ancho_unidad + 24
            lienzo.configure(scrollregion=(0, 0, ancho_total, alto_canvas))
            lienzo.delete("all")
            lienzo.create_text(
                8,
                56,
                text="CPU",
                anchor="w",
                fill="#202020",
                font=("Segoe UI", 10, "bold"),
            )

            limites = {0, total_tiempo}
            cursor = 0
            for segmento in sorted(timeline, key=lambda item: (item["start"], item["finish"])):
                inicio = segmento["start"]
                fin = segmento["finish"]
                if inicio > cursor:
                    x1 = margen_izquierdo + cursor * ancho_unidad
                    x2 = margen_izquierdo + inicio * ancho_unidad
                    lienzo.create_rectangle(x1, 37, x2, 75, fill="#E5E7EB", outline="#444444")
                    lienzo.create_text((x1 + x2) / 2, 56, text="Inactivo", fill="#202020", font=("Segoe UI", 9))

                x1 = margen_izquierdo + inicio * ancho_unidad
                x2 = margen_izquierdo + fin * ancho_unidad
                lienzo.create_rectangle(
                    x1,
                    37,
                    x2,
                    75,
                    fill=color_por_proceso[segmento["process"]],
                    outline="#444444",
                    width=1,
                )
                lienzo.create_text(
                    (x1 + x2) / 2,
                    56,
                    text=segmento["process"],
                    fill="#111111",
                    font=("Segoe UI", 10, "bold"),
                )
                limites.update((inicio, fin))
                cursor = fin

            for tiempo in sorted(limites):
                x = margen_izquierdo + tiempo * ancho_unidad
                lienzo.create_line(x, 75, x, 88, fill="#333333")
                lienzo.create_text(x, 103, text=str(tiempo), fill="#111111", font=("Segoe UI", 9))

        lienzo.bind("<Configure>", dibujar)
        dibujar()

    def _dibujar_diagrama_gantt(self, timeline, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        if not timeline:
            label = ctk.CTkLabel(parent, text="No hay diagrama Gantt para mostrar.")
            label.grid(row=0, column=0, padx=12, pady=12)
            return

        procesos = sorted({item["process"] for item in timeline}, key=lambda proceso: int(proceso[1:]))
        total_tiempo = max(item["finish"] for item in timeline)
        colores_estado = {
            "arrival": "#D9EAF7",
            "waiting": "#FFF2CC",
            "running": "#D9EAD3",
            "finished": "#EAD5DF",
        }
        datos_por_proceso = {}
        for segmento in timeline:
            proceso = segmento["process"]
            if proceso not in datos_por_proceso:
                datos_por_proceso[proceso] = {
                    "arrival": segmento["arrival"],
                    "burst": segmento["burst"],
                    "segments": [],
                }
            datos_por_proceso[proceso]["segments"].append(segmento)

        titulo = ctk.CTkLabel(parent, text="Tabla de estados", font=ctk.CTkFont(size=14, weight="bold"))
        titulo.grid(row=0, column=0, columnspan=len(procesos) + 2, padx=12, pady=(12, 8), sticky="w")

        parent.grid_columnconfigure(0, weight=0, minsize=48)
        for col_idx in range(1, len(procesos) + 1):
            parent.grid_columnconfigure(
                col_idx,
                weight=1,
                uniform="columnas_proceso",
                minsize=44,
            )

        for indice, (estado, texto) in enumerate(
            [("arrival", "Llegada"), ("waiting", "Espera"), ("running", "En proceso"), ("finished", "Finalizado")]
        ):
            leyenda = ctk.CTkLabel(
                parent,
                text=texto,
                fg_color=colores_estado[estado],
                text_color="#000000",
                corner_radius=4,
            )
            leyenda.grid(row=1, column=indice, padx=4, pady=(0, 8), sticky="w")

        encabezado = ctk.CTkLabel(parent, text="", width=6)
        encabezado.grid(row=2, column=0, padx=2, pady=2, sticky="nsew")

        for col_idx, proceso in enumerate(procesos, start=1):
            etiqueta = ctk.CTkLabel(parent, text=proceso, width=12, font=ctk.CTkFont(size=11, weight="bold"))
            etiqueta.grid(row=2, column=col_idx, padx=2, pady=2, sticky="nsew")

        for tiempo in range(total_tiempo + 1):
            fila_tiempo = tiempo + 3
            parent.grid_rowconfigure(
                fila_tiempo,
                weight=1,
                uniform="filas_tiempo",
                minsize=26,
            )
            tiempo_label = ctk.CTkLabel(parent, text=str(tiempo), width=6, font=ctk.CTkFont(size=10))
            tiempo_label.grid(row=fila_tiempo, column=0, padx=2, pady=2, sticky="nsew")

            for col_idx, proceso in enumerate(procesos, start=1):
                estado, restante = self._estado_proceso_en_tiempo(datos_por_proceso[proceso], tiempo)
                fg = colores_estado.get(estado, "#FFFFFF")
                txt = "" if restante is None else str(restante)

                celda = ctk.CTkLabel(
                    parent,
                    text=txt,
                    width=12,
                    height=2,
                    fg_color=fg,
                    text_color="#000000",
                    corner_radius=0,
                )
                celda.grid(row=fila_tiempo, column=col_idx, padx=1, pady=1, sticky="nsew")
        
        # Aquí eliminamos todo el bloque de código que dibujaba el "resumen = ctk.CTkFrame..."

    def _mostrar_gantt(self, timeline, texto_resultado=""):
        for widget in self.frame_gantt.winfo_children():
            widget.destroy()
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        self.frame_gantt.grid_columnconfigure(0, weight=1)
        self.frame_resultados.grid_columnconfigure(0, weight=3)
        self.frame_resultados.grid_columnconfigure(1, weight=2)
        self.frame_resultados.grid_rowconfigure(0, weight=1)

        self._dibujar_gantt_horizontal(timeline, self.frame_gantt)

        tabla_estados = ctk.CTkScrollableFrame(self.frame_resultados, corner_radius=8)
        tabla_estados.grid(row=0, column=0, sticky="nsew", padx=(12, 6), pady=12)
        self._dibujar_diagrama_gantt(timeline, tabla_estados)

        fuente_mono = ctk.CTkFont(family="Consolas", size=13)
        resultado_box = ctk.CTkTextbox(self.frame_resultados, wrap="none", font=fuente_mono, corner_radius=8)
        resultado_box.grid(row=0, column=1, sticky="nsew", padx=(6, 12), pady=12)
        resultado_box.insert("end", texto_resultado)
        resultado_box.configure(state="disabled")
        self._resultado_widget = resultado_box

    def simular(self):
        if self._validar_cantidad_procesos() is None:
            return

        procesos = self.leer_procesos()
        if not procesos:
            return

        algoritmo = self.algoritmo_var.get()
        quantum = None

        if algoritmo == "Round Robin":
            try:
                quantum = int(self.entry_quantum.get())
                if not 1 <= quantum <= MAX_QUANTUM:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Quantum inválido",
                    f"El quantum debe ser un entero entre 1 y {MAX_QUANTUM}.",
                )
                return

        gantt = self._timeline_por_algoritmo(procesos, algoritmo, quantum)
        if gantt and max(item["finish"] for item in gantt) > MAX_DURACION_DIAGRAMA:
            messagebox.showwarning(
                "Diagrama demasiado largo",
                f"La duración total no puede superar {MAX_DURACION_DIAGRAMA} unidades de tiempo.",
            )
            return
        if algoritmo == "FCFS":
            resultado = FCFS.simular(procesos)
        elif algoritmo == "SJF":
            resultado = SJF.simular(procesos)
        elif algoritmo == "Priority":
            resultado = PriorityScheduler.simular(procesos)
        elif algoritmo == "Round Robin":
            resultado = RoundRobin.simular(procesos, quantum)
        else:
            resultado = f"No se encontró un algoritmo para: {algoritmo}"

        self._mostrar_gantt(gantt, resultado)


if __name__ == "__main__":
    app = VistaPlanificacion()
    app.mainloop()

