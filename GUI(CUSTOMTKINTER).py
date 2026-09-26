import customtkinter as ctk
from tkinter import messagebox

from alg_FCFS import FCFS
from alg_Priority import PriorityScheduler
from alg_RoundRobin import RoundRobin
from alg_SJF import SJF


class VistaPlanificacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos de Planificación")
        self.geometry("1100x680")
        self.minsize(900, 600)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.filas_entradas = []
        self._datos_guardados = []

        self._configurar_ui()

    def _configurar_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        self.frame_config = ctk.CTkFrame(self, corner_radius=12)
        self.frame_config.grid(row=0, column=0, padx=18, pady=(18, 10), sticky="ew")
        self.frame_config.grid_columnconfigure(1, weight=1)

        self.label_total = ctk.CTkLabel(
            self.frame_config,
            text="Número de procesos:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_total.grid(row=0, column=0, padx=(18, 10), pady=(18, 8), sticky="w")

        self.entry_total = ctk.CTkEntry(self.frame_config, width=120)
        self.entry_total.insert(0, "5")
        self.entry_total.grid(row=0, column=1, padx=(0, 12), pady=(18, 8), sticky="ew")

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
            text="Quantum:",
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.label_quantum.grid(row=0, column=4, padx=(10, 8), pady=(18, 8), sticky="w")

        self.entry_quantum = ctk.CTkEntry(self.frame_config, width=90)
        self.entry_quantum.insert(0, "2")
        self.entry_quantum.grid(row=0, column=5, padx=(0, 12), pady=(18, 8), sticky="ew")

        self.btn_generar = ctk.CTkButton(
            self.frame_config,
            text="Generar matriz",
            command=self.generar_matriz,
            width=160,
            height=36,
        )
        self.btn_generar.grid(row=1, column=0, columnspan=2, padx=(18, 8), pady=(8, 18), sticky="ew")

        self.btn_simular = ctk.CTkButton(
            self.frame_config,
            text="Simular algoritmo",
            command=self.simular,
            width=180,
            height=36,
        )
        self.btn_simular.grid(row=1, column=2, columnspan=2, padx=(8, 18), pady=(8, 18), sticky="ew")

        self._actualizar_quantum(self.algoritmo_var.get())

        self.frame_tabla = ctk.CTkScrollableFrame(self, corner_radius=12)
        self.frame_tabla.grid(row=1, column=0, padx=18, pady=(0, 18), sticky="nsew")

        self.gantt_window = None

    def _obtener_columnas(self):
        algoritmo = self.algoritmo_var.get()
        if algoritmo == "Priority":
            return ["Process", "Arrival Time", "Burst Time", "Priority"]
        return ["Process", "Arrival Time", "Burst Time"]

    def generar_matriz(self):
        try:
            cantidad = int(self.entry_total.get())
        except ValueError:
            messagebox.showerror("Entrada inválida", "Debes ingresar un número entero válido.")
            return

        if cantidad <= 0:
            messagebox.showwarning("Cantidad inválida", "El número de procesos debe ser mayor que 0.")
            return

        for widget in self.frame_tabla.winfo_children():
            widget.destroy()
        self.filas_entradas = []
        self._datos_guardados = []

        columnas = self._obtener_columnas()
        for col_index, titulo in enumerate(columnas):
            label = ctk.CTkLabel(
                self.frame_tabla,
                text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=18,
                height=2,
            )
            label.grid(row=0, column=col_index, padx=8, pady=8, sticky="nsew")

        for i in range(cantidad):
            nombre = ctk.CTkLabel(self.frame_tabla, text=f"P{i + 1}", width=12)
            nombre.grid(row=i + 1, column=0, padx=8, pady=8, sticky="ew")

            arrival = ctk.CTkEntry(self.frame_tabla, width=16)
            burst = ctk.CTkEntry(self.frame_tabla, width=16)
            fila = {
                "process": nombre,
                "arrival": arrival,
                "burst": burst,
            }

            arrival.grid(row=i + 1, column=1, padx=8, pady=8, sticky="ew")
            burst.grid(row=i + 1, column=2, padx=8, pady=8, sticky="ew")

            if "Priority" in columnas:
                priority = ctk.CTkEntry(self.frame_tabla, width=16)
                priority.grid(row=i + 1, column=3, padx=8, pady=8, sticky="ew")
                fila["priority"] = priority

            self.filas_entradas.append(fila)

        for col in range(len(columnas)):
            self.frame_tabla.grid_columnconfigure(col, weight=1)

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
                    mensaje = "Ingresa enteros en Arrival Time, Burst Time y Priority."
                else:
                    mensaje = "Ingresa enteros en Arrival Time y Burst Time."
                messagebox.showerror(
                    "Datos incompletos",
                    f"El proceso P{index} tiene valores inválidos. {mensaje}",
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

        for col_index, titulo in enumerate(columnas):
            label = ctk.CTkLabel(
                self.frame_tabla,
                text=titulo,
                font=ctk.CTkFont(size=12, weight="bold"),
                width=18,
                height=2,
            )
            label.grid(row=0, column=col_index, padx=8, pady=8, sticky="nsew")

        for i, datos in enumerate(self._datos_guardados if self._datos_guardados else datos_previos):
            nombre = ctk.CTkLabel(self.frame_tabla, text=f"P{i + 1}", width=12)
            nombre.grid(row=i + 1, column=0, padx=8, pady=8, sticky="ew")

            arrival = ctk.CTkEntry(self.frame_tabla, width=16)
            burst = ctk.CTkEntry(self.frame_tabla, width=16)
            arrival.insert(0, datos.get("arrival", ""))
            burst.insert(0, datos.get("burst", ""))

            arrival.grid(row=i + 1, column=1, padx=8, pady=8, sticky="ew")
            burst.grid(row=i + 1, column=2, padx=8, pady=8, sticky="ew")

            fila = {
                "process": nombre,
                "arrival": arrival,
                "burst": burst,
            }

            if "Priority" in columnas:
                priority = ctk.CTkEntry(self.frame_tabla, width=16)
                priority.insert(0, datos.get("priority", ""))
                priority.grid(row=i + 1, column=3, padx=8, pady=8, sticky="ew")
                fila["priority"] = priority

            self.filas_entradas.append(fila)

        for col in range(len(columnas)):
            self.frame_tabla.grid_columnconfigure(col, weight=1)

    def mostrar_resultado(self, texto):
        if self.gantt_window is not None and self.gantt_window.winfo_exists():
            texto_widget = self.gantt_window._resultado_widget
            texto_widget.configure(state="normal")
            texto_widget.delete("1.0", "end")
            texto_widget.insert("end", texto)
            texto_widget.configure(state="disabled")
        else:
            return

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

    def _dibujar_diagrama_gantt(self, timeline, parent):
        for widget in parent.winfo_children():
            widget.destroy()

        if not timeline:
            label = ctk.CTkLabel(parent, text="No hay diagrama Gantt para mostrar.")
            label.grid(row=0, column=0, padx=12, pady=12)
            return

        procesos = sorted({item["process"] for item in timeline})
        total_tiempo = max(item["finish"] for item in timeline)
        colores = {
            "P1": "#CFE2F3",
            "P2": "#D9EAD3",
            "P3": "#FCE5CD",
            "P4": "#D9D2E9",
            "P5": "#F4CCCC",
            "P6": "#F3F3F3",
            "P7": "#EAD1DC",
            "P8": "#D0E0E3",
        }

        titulo = ctk.CTkLabel(parent, text="Diagrama de Gantt", font=ctk.CTkFont(size=16, weight="bold"))
        titulo.grid(row=0, column=0, columnspan=len(procesos) + 2, padx=12, pady=(12, 8), sticky="w")

        leyenda = ctk.CTkLabel(
            parent,
            text="Llegada  •  Espera  •  Procesando  •  Finalizado",
            font=ctk.CTkFont(size=12),
        )
        leyenda.grid(row=1, column=0, columnspan=len(procesos) + 2, padx=12, pady=(0, 8), sticky="w")

        encabezado = ctk.CTkLabel(parent, text="", width=6)
        encabezado.grid(row=2, column=0, padx=2, pady=2, sticky="nsew")

        for col_idx, proceso in enumerate(procesos, start=1):
            etiqueta = ctk.CTkLabel(parent, text=proceso, width=12, font=ctk.CTkFont(size=12, weight="bold"))
            etiqueta.grid(row=2, column=col_idx, padx=2, pady=2, sticky="nsew")

        for tiempo in range(total_tiempo + 1):
            tiempo_label = ctk.CTkLabel(parent, text=str(tiempo), width=6, font=ctk.CTkFont(size=11))
            tiempo_label.grid(row=tiempo + 3, column=0, padx=2, pady=2, sticky="nsew")

            for col_idx, proceso in enumerate(procesos, start=1):
                item = next((p for p in timeline if p["process"] == proceso and p["start"] <= tiempo < p["finish"]), None)
                fg = "#E5E7EB"
                txt = ""
                if item is not None:
                    fg = colores.get(proceso, "#D9EAF7")
                    txt = str(item["finish"] - tiempo)

                celda = ctk.CTkLabel(
                    parent,
                    text=txt,
                    width=12,
                    height=2,
                    fg_color=fg,
                    corner_radius=0,
                )
                celda.grid(row=tiempo + 3, column=col_idx, padx=1, pady=1, sticky="nsew")

        resumen = ctk.CTkFrame(parent, corner_radius=10)
        resumen.grid(row=total_tiempo + 5, column=0, columnspan=len(procesos) + 1, padx=12, pady=(16, 12), sticky="ew")

        resumen_titulo = ctk.CTkLabel(resumen, text="Resumen de estados", font=ctk.CTkFont(size=14, weight="bold"))
        resumen_titulo.grid(row=0, column=0, padx=12, pady=(10, 8), sticky="w")

        for idx, item in enumerate(timeline):
            estado = ctk.CTkLabel(
                resumen,
                text=(
                    f"{item['process']}: Llegada={item['arrival']} | "
                    f"Espera={item['waiting']} | "
                    f"Procesando={item['start']}-{item['finish']} | "
                    f"Finalizado={item['finish']}"
                ),
                anchor="w",
            )
            estado.grid(row=idx + 1, column=0, padx=12, pady=4, sticky="ew")

    def _abrir_gantt(self, timeline, texto_resultado=""):
        if self.gantt_window is not None and self.gantt_window.winfo_exists():
            self.gantt_window.destroy()

        self.gantt_window = ctk.CTkToplevel(self)
        self.gantt_window.title("Diagrama de Gantt")
        self.gantt_window.geometry("1200x700")
        self.gantt_window.minsize(980, 560)
        self.gantt_window.grab_set()

        contenedor = ctk.CTkScrollableFrame(self.gantt_window, corner_radius=12)
        contenedor.pack(fill="both", expand=True, padx=16, pady=16)
        self._dibujar_diagrama_gantt(timeline, contenedor)

        resultado_box = ctk.CTkTextbox(self.gantt_window, height=180, wrap="word")
        resultado_box.pack(fill="x", padx=16, pady=(0, 16))
        resultado_box.insert("end", texto_resultado)
        resultado_box.configure(state="disabled")
        self.gantt_window._resultado_widget = resultado_box

    def simular(self):
        procesos = self.leer_procesos()
        if not procesos:
            return

        algoritmo = self.algoritmo_var.get()
        quantum = None

        if algoritmo == "Round Robin":
            try:
                quantum = int(self.entry_quantum.get())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Quantum inválido", "El quantum debe ser un entero mayor que 0.")
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

        gantt = self._timeline_por_algoritmo(procesos, algoritmo, quantum)
        self._abrir_gantt(gantt, resultado)


if __name__ == "__main__":
    app = VistaPlanificacion()
    app.mainloop()

