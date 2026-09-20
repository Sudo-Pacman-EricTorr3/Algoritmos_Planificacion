class Controlador:
    def __init__(self, vista):
        self.vista = vista

    def obtener_procesos(self):
        return self.vista.leer_procesos()

    def enviar_datos_a_vista(self, datos):
        self.vista.mostrar_resultado(datos)

    def simular(self):
        procesos = self.obtener_procesos()
        if not procesos:
            return

        resumen = "Procesos capturados:\n"
        for proceso in procesos:
            resumen += (
                f"{proceso['process']} -> Arrival: {proceso['arrival_time']}, "
                f"Burst: {proceso['burst_time']}, Priority: {proceso['priority']}\n"
            )
        self.enviar_datos_a_vista(resumen)
