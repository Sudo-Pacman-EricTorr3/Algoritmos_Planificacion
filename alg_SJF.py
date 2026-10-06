from alg_preemptive import (
    generar_resumen,
    generar_timeline,
    generar_timeline_no_apropiativo,
)


class SJF:
    @staticmethod
    def generar_timeline(procesos, apropiativo=True):
        generador = generar_timeline if apropiativo else generar_timeline_no_apropiativo
        return generador(procesos, criterio=lambda _, restante: restante)

    @staticmethod
    def simular(procesos, apropiativo=True):
        timeline = SJF.generar_timeline(procesos, apropiativo)
        tipo = "Apropiativo - SRTF" if apropiativo else "No apropiativo"
        return generar_resumen(
            procesos,
            timeline,
            f"SJF ({tipo})",
        )
