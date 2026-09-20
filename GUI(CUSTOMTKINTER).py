import customtkinter as ctk
from tkinter import messagebox


class VistaPlanificacion(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Algoritmos de Planificación")
        self.geometry("1100x680")
        self.minsize(900, 600)
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self.filas_entradas = []

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
            command=self._actualizar_quantum,
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

        self.resultado = ctk.CTkTextbox(self, height=150, wrap="word")
        self.resultado.grid(row=2, column=0, padx=18, pady=(0, 18), sticky="ew")
        self.resultado.insert("end", "Resultado de la simulación aparecerá aquí.\n")
        self.resultado.configure(state="disabled")

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

        columnas = ["Process", "Arrival Time", "Burst Time", "Priority"]
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
            priority = ctk.CTkEntry(self.frame_tabla, width=16)

            arrival.grid(row=i + 1, column=1, padx=8, pady=8, sticky="ew")
            burst.grid(row=i + 1, column=2, padx=8, pady=8, sticky="ew")
            priority.grid(row=i + 1, column=3, padx=8, pady=8, sticky="ew")

            self.filas_entradas.append(
                {
                    "process": nombre,
                    "arrival": arrival,
                    "burst": burst,
                    "priority": priority,
                }
            )

        for col in range(4):
            self.frame_tabla.grid_columnconfigure(col, weight=1)

    def leer_procesos(self):
        procesos = []

        for index, fila in enumerate(self.filas_entradas, start=1):
            try:
                arrival_time = int(fila["arrival"].get())
                burst_time = int(fila["burst"].get())
                priority = int(fila["priority"].get())
            except ValueError:
                messagebox.showerror(
                    "Datos incompletos",
                    f"El proceso P{index} tiene valores inválidos. Ingresa enteros en Arrival Time, Burst Time y Priority.",
                )
                return []

            procesos.append(
                {
                    "process": f"P{index}",
                    "arrival_time": arrival_time,
                    "burst_time": burst_time,
                    "priority": priority,
                }
            )

        return procesos

    def _actualizar_quantum(self, algoritmo):
        if algoritmo == "Round Robin":
            self.label_quantum.grid()
            self.entry_quantum.grid()
        else:
            self.label_quantum.grid_remove()
            self.entry_quantum.grid_remove()

    def mostrar_resultado(self, texto):
        self.resultado.configure(state="normal")
        self.resultado.delete("1.0", "end")
        self.resultado.insert("end", texto)
        self.resultado.configure(state="disabled")

    def simular(self):
        procesos = self.leer_procesos()
        if not procesos:
            return

        algoritmo = self.algoritmo_var.get()

        if algoritmo == "Round Robin":
            try:
                quantum = int(self.entry_quantum.get())
                if quantum <= 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Quantum inválido", "El quantum debe ser un entero mayor que 0.")
                return
            encabezado = f"Simulando Round Robin con quantum = {quantum}\n"
        else:
            encabezado = f"Simulando {algoritmo}\n"

        resumen = encabezado + "\nProcesos capturados:\n"
        for proceso in procesos:
            resumen += (
                f"{proceso['process']} -> Arrival: {proceso['arrival_time']}, "
                f"Burst: {proceso['burst_time']}, Priority: {proceso['priority']}\n"
            )

        self.mostrar_resultado(resumen)


if __name__ == "__main__":
    app = VistaPlanificacion()
    app.mainloop()

