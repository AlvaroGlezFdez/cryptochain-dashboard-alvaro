# CryptoChain Insights Dashboard

**Estudiante:** Álvaro González Fernández  
**GitHub User:** TU_USUARIO  
**Asignatura:** Criptografía  
**Institución:** Universidad Alfonso X el Sabio (UAX)  
**Profesor:** Jorge Calvo  

---

## Descripción del Proyecto

**CryptoChain Insights Dashboard** es un panel de control interactivo desarrollado en Python con Streamlit para visualizar y analizar métricas criptográficas de la red Bitcoin en tiempo real. El proyecto aplica conceptos teóricos como SHA-256, Proof of Work y ajuste de dificultad sobre datos reales obtenidos de APIs públicas (Blockstream, Mempool.space).

---

## Enfoque de IA — Módulo M4

**Tipo:** Detector de Anomalías  
**Objetivo:** Identificar bloques cuyo tiempo de llegada (inter-arrival time) sea estadísticamente anormal respecto al comportamiento esperado de la red.  
**Metodología:** Se modela el tiempo entre bloques mediante una distribución exponencial con media 600 s (baseline teórico de Bitcoin). Los bloques que superen el umbral del percentil 95 o estén por debajo del percentil 5 se clasifican como anomalías y se resaltan visualmente en el dashboard.

---

## Estado de los Módulos

| Módulo | Descripción | Estado |
| :--- | :--- | :--- |
| **M1** | Monitor de Proof of Work (dificultad, hash rate, tiempos entre bloques) | 🚧 En desarrollo |
| **M2** | Analizador de Header de Bloque (6 campos, verificación SHA-256², bits a cero) | 🚧 En desarrollo |
| **M3** | Historial de Dificultad (periodos de 2016 bloques, ratio tiempo_real/600 s) | 🚧 En desarrollo |
| **M4** | IA — Detector de Anomalías (distribución exponencial) | 🚧 En desarrollo |

---

## Progreso Actual

- [x] Repositorio de GitHub Classroom aceptado y clonado localmente
- [x] Estructura de carpetas configurada (`api/`, `modules/`, `report/`)
- [x] Cliente API funcional en `api/blockchain_client.py` — recupera el último bloque en tiempo real (altura, hash, dificultad, nonce)
- [x] README completo con información del estudiante y enfoque de IA
- [ ] Implementación de módulos M1–M4
- [ ] Tests de integración y validación de la verificación local del PoW

---

## Próximo Paso

Implementar **M1** (Monitor de Proof of Work) y **M2** (Analizador de Header): añadir las funciones `get_block()` y `get_difficulty_history()` al cliente API y conectarlas a los tabs del dashboard.

---

## Bloqueadores

Ninguno actualmente.

---

## Instrucciones de Ejecución

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Lanzar el dashboard
streamlit run app.py
```

<!-- student-repo-auditor:teacher-feedback:start -->
## Teacher Feedback

### Kick-off Review

Review time: 2026-04-29 20:44 CEST
Status: Green

Strength:
- I can see the dashboard structure integrating the checkpoint modules.

Improve now:
- The README should now reflect the checkpoint more explicitly, including progress, blockers, and updated module status.

Next step:
- Update the README so progress, blockers, module status, and next step match the checkpoint format exactly.
<!-- student-repo-auditor:teacher-feedback:end -->
