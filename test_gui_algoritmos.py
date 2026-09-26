import importlib.util
import unittest
from pathlib import Path


FILE_PATH = Path(__file__).parent / "GUI(CUSTOMTKINTER).py"

spec = importlib.util.spec_from_file_location("gui_customtkinter", FILE_PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VistaPlanificacion = module.VistaPlanificacion


class TestVistaPlanificacion(unittest.TestCase):
    def test_fcfs_omits_priority_column_and_reads_without_priority(self):
        app = VistaPlanificacion()
        app.algoritmo_var.set("FCFS")
        app.entry_total.delete(0, "end")
        app.entry_total.insert(0, "2")

        app.generar_matriz()

        headers = [
            widget.cget("text")
            for widget in app.frame_tabla.winfo_children()
            if type(widget).__name__ == "CTkLabel" and widget.cget("text") in {"Process", "Arrival Time", "Burst Time", "Priority"}
        ]
        self.assertNotIn("Priority", headers)
        self.assertIn("Arrival Time", headers)
        self.assertIn("Burst Time", headers)

        app.filas_entradas[0]["arrival"].insert(0, "1")
        app.filas_entradas[0]["burst"].insert(0, "3")
        app.filas_entradas[1]["arrival"].insert(0, "2")
        app.filas_entradas[1]["burst"].insert(0, "4")

        procesos = app.leer_procesos()

        self.assertEqual(
            procesos,
            [
                {"process": "P1", "arrival_time": 1, "burst_time": 3},
                {"process": "P2", "arrival_time": 2, "burst_time": 4},
            ],
        )

        app.destroy()

    def test_priority_algorithm_keeps_priority_column(self):
        app = VistaPlanificacion()
        app.algoritmo_var.set("Priority")
        app.entry_total.delete(0, "end")
        app.entry_total.insert(0, "1")

        app.generar_matriz()

        headers = [
            widget.cget("text")
            for widget in app.frame_tabla.winfo_children()
            if type(widget).__name__ == "CTkLabel" and widget.cget("text") in {"Process", "Arrival Time", "Burst Time", "Priority"}
        ]
        self.assertIn("Priority", headers)

        app.filas_entradas[0]["arrival"].insert(0, "1")
        app.filas_entradas[0]["burst"].insert(0, "2")
        app.filas_entradas[0]["priority"].insert(0, "5")

        procesos = app.leer_procesos()
        self.assertEqual(procesos[0]["priority"], 5)
        app.destroy()

    def test_round_robin_omits_priority_column(self):
        app = VistaPlanificacion()
        app.algoritmo_var.set("Round Robin")
        app.entry_total.delete(0, "end")
        app.entry_total.insert(0, "1")

        app.generar_matriz()

        headers = [
            widget.cget("text")
            for widget in app.frame_tabla.winfo_children()
            if type(widget).__name__ == "CTkLabel" and widget.cget("text") in {"Process", "Arrival Time", "Burst Time", "Priority"}
        ]
        self.assertNotIn("Priority", headers)
        app.destroy()

    def test_changing_algorithm_rebuilds_priority_column(self):
        app = VistaPlanificacion()
        app.entry_total.delete(0, "end")
        app.entry_total.insert(0, "2")
        app.algoritmo_var.set("Priority")
        app.generar_matriz()

        app.filas_entradas[0]["arrival"].insert(0, "1")
        app.filas_entradas[0]["burst"].insert(0, "3")
        app.filas_entradas[0]["priority"].insert(0, "7")
        app.filas_entradas[1]["arrival"].insert(0, "2")
        app.filas_entradas[1]["burst"].insert(0, "4")
        app.filas_entradas[1]["priority"].insert(0, "2")

        app.algoritmo_var.set("FCFS")
        app._on_algoritmo_cambiado("FCFS")
        headers = [
            widget.cget("text")
            for widget in app.frame_tabla.winfo_children()
            if type(widget).__name__ == "CTkLabel" and widget.cget("text") in {"Process", "Arrival Time", "Burst Time", "Priority"}
        ]
        self.assertNotIn("Priority", headers)
        self.assertEqual(app.filas_entradas[0]["arrival"].get(), "1")
        self.assertEqual(app.filas_entradas[0]["burst"].get(), "3")

        app.algoritmo_var.set("Priority")
        app._on_algoritmo_cambiado("Priority")
        headers = [
            widget.cget("text")
            for widget in app.frame_tabla.winfo_children()
            if type(widget).__name__ == "CTkLabel" and widget.cget("text") in {"Process", "Arrival Time", "Burst Time", "Priority"}
        ]
        self.assertIn("Priority", headers)
        self.assertEqual(app.filas_entradas[0]["priority"].get(), "7")
        app.destroy()

    def test_round_robin_ejecuta_por_quantum_y_reencola(self):
        app = VistaPlanificacion()
        procesos = [
            {"process": "P1", "arrival_time": 0, "burst_time": 5},
            {"process": "P2", "arrival_time": 1, "burst_time": 2},
            {"process": "P3", "arrival_time": 2, "burst_time": 3},
        ]

        timeline = app._timeline_por_algoritmo(procesos, "Round Robin", quantum=2)

        self.assertEqual(len(timeline), 6)
        self.assertEqual([item["process"] for item in timeline], ["P1", "P2", "P3", "P1", "P3", "P1"])
        app.destroy()

    def test_simulacion_usa_el_algoritmo_seleccionado(self):
        app = VistaPlanificacion()
        app.algoritmo_var.set("FCFS")
        app.entry_total.delete(0, "end")
        app.entry_total.insert(0, "2")
        app.generar_matriz()

        app.filas_entradas[0]["arrival"].insert(0, "0")
        app.filas_entradas[0]["burst"].insert(0, "3")
        app.filas_entradas[1]["arrival"].insert(0, "1")
        app.filas_entradas[1]["burst"].insert(0, "2")

        app.simular()
        self.assertIsNotNone(app.gantt_window)
        self.assertIn("FCFS", app.gantt_window._resultado_widget.get("1.0", "end"))
        self.assertIn("P1", app.gantt_window._resultado_widget.get("1.0", "end"))
        app.destroy()


if __name__ == "__main__":
    unittest.main()
