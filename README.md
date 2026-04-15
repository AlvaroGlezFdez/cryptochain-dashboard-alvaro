# ₿ CryptoChain Insights: Bitcoin Dashboard

**Estudiante:** Álvaro González Fernández  
**Asignatura:** Criptografía y Seguridad  
**Institución:** Universidad Alfonso X el Sabio (UAX)

---

## 🚀 Descripción del Proyecto
**CryptoChain Insights** es un dashboard interactivo desarrollado en Python para la monitorización en tiempo real de la red Bitcoin. El objetivo es analizar métricas críticas de la cadena de bloques, como el Proof of Work (PoW), la evolución de la dificultad y la seguridad de los hashes.

## 🧠 Componente de IA (Módulo M4)
* **Enfoque seleccionado:** Detector de Anomalías.
* **Objetivo:** Identificar variaciones estadísticas inusuales en el tiempo de minado de bloques (inter-arrival time) para detectar posibles picos de hash rate o retrasos en la red.
* **Metodología:** Análisis de la distribución exponencial de los tiempos de bloque.

## 📊 Estado del Desarrollo
| Módulo | Descripción | Estado |
| :--- | :--- | :--- |
| **M1** | Monitor de Proof of Work (Hash & Target) | ⏳ En desarrollo |
| **M2** | Analizador de Header de Bloque | ⏳ Pendiente |
| **M3** | Historial de Dificultad | ⏳ Pendiente |
| **M4** | IA: Detector de Anomalías | ⏳ Pendiente |

---

## ✅ Hitos Completados (Sesión 1)
1.  **Configuración del Entorno:** Clonación del repositorio y verificación de la estructura de carpetas.
2.  **Llamada a la API:** Implementación funcional del cliente en `api/blockchain_client.py` que recupera datos en vivo (Altura, Hash, Dificultad, Nonce).
3.  **Documentación inicial:** Definición del alcance del proyecto y selección del componente de IA.

## ⏭️ Próximos Pasos
* Instalación y configuración de **Streamlit** para la interfaz visual.
* Mapeo de los datos de la API hacia los widgets del dashboard en `app.py`.