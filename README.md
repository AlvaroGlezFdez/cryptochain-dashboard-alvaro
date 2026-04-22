#  CryptoChain Analyzer Dashboard

**Asignatura:** Cryptography | [cite_start]Universidad Alfonso X el Sabio [cite: 1]
[cite_start]**Profesor:** Prof. Jorge Calvo [cite: 2]
**Estudiante:** Álvaro González Fernández
**GitHub User:** (TU_USUARIO_AQUÍ)

---

##  Descripción del Proyecto
[cite_start]Este proyecto consiste en el desarrollo de un panel de control interactivo (dashboard) en tiempo real utilizando Python para visualizar y analizar métricas criptográficas de la red Bitcoin. [cite: 12] [cite_start]El objetivo es aplicar conceptos teóricos como SHA-256, Proof of Work y dificultad a datos reales obtenidos de una API pública. [cite: 75]

##  Enfoque de IA (M4)
[cite_start]Para el módulo de Inteligencia Artificial [cite: 104][cite_start], he seleccionado el **Detector de Anomalías**. [cite: 107]
* [cite_start]**Objetivo:** Identificar bloques cuyo tiempo de llegada (inter-arrival time) sea estadísticamente anormal. [cite: 107]
* [cite_start]**Justificación:** Se utilizará la distribución exponencial como base (baseline) para detectar desviaciones que puedan indicar comportamientos específicos de minería. [cite: 108]

##  Estado de los Módulos
| Módulo | Descripción | Estado |
| :--- | :--- | :--- |
| **M1** | Proof of Work Monitor | ⏳ Pendiente |
| **M2** | Block Header Analyzer | ⏳ Pendiente |
| **M3** | Difficulty History | ⏳ Pendiente |
| **M4** | AI Component (Anomaly Detector) | ⏳ Pendiente |

##  Progreso Actual
* [cite_start][x] Repositorio de GitHub Classroom aceptado. [cite: 33, 34]
* [cite_start][x] Estructura inicial del proyecto configurada (carpetas api/, modules/, report/). [cite: 149, 164]
* [cite_start][x] README inicial completado con información del estudiante y enfoque de IA. [cite: 36, 40]
* [cite_start][ ] Primera llamada a la API y script de prueba (Milestone 2). [cite: 46]

##  Next Step
[cite_start]Escribir un script de Python de máximo 10 líneas en `api/blockchain_client.py` que conecte con la API de Blockstream para recuperar datos del último bloque. [cite: 49, 64]

##  Bloqueadores (Blockers)
* Ninguno actualmente.

---

### Instrucciones de Ejecución
[cite_start]El dashboard se ejecutará mediante los siguientes pasos: [cite: 205]
1. Instalar dependencias: `pip install -r requirements.txt`
2. Ejecutar aplicación: `streamlit run app.py`


<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-22 12:25 CEST
Status: Amber

Strength:
- Your repository keeps the expected classroom structure.

Improve now:
- The README is present but still misses part of the required kickoff information.

Next step:
- Complete the README fields for student information, AI approach, module status, and next step.
<!-- student-repo-auditor:teacher-feedback:end -->
