# Simulador de Consumo Energético de Vehículos Eléctricos

## 📖 Descripción

Simulador interactivo que aplica principios de **mecánica clásica** para analizar el consumo energético de vehículos eléctricos al ascender y descender pendientes. Desarrollado como proyecto académico para el curso de Mecánica Clásica.

## 🎯 Objetivo

Demostrar la aplicación práctica de conceptos fundamentales de mecánica clásica (dinámica, trabajo, energía y potencia) en problemas de ingeniería moderna, específicamente en el análisis de eficiencia energética de vehículos eléctricos.

## 🔬 Fundamento Teórico

El simulador modela las fuerzas que actúan sobre un vehículo en movimiento:

### Fuerzas principales:

- **Fuerza gravitacional en pendiente**: F_pend = mg·sin(θ)
- **Resistencia por rodadura**: F_rr = C_rr·mg·cos(θ)
- **Resistencia aerodinámica**: F_aero = ½·ρ·C_d·A·v²

### Cálculos energéticos:

- **Trabajo**: W = F_total · L
- **Energía de batería**: E_batería = W / η
- **Potencia**: P = F_total · v
- **Regeneración**: E_regen = η_regen · mg·Δh

## ✨ Características

### Funcionalidades principales:

- ✅ Cálculo de fuerzas en tiempo real
- ✅ Análisis de consumo energético (kWh/100km)
- ✅ Estimación de autonomía
- ✅ Simulación con regeneración en bajadas
- ✅ Visualización gráfica interactiva
- ✅ Exportación de datos (CSV) y gráficos (PNG)
- ✅ Casos de ejemplo predefinidos (urbano, montaña, autopista)
- ✅ Tooltips de ayuda contextuales
- ✅ Sección teórica con ecuaciones matemáticas

### Parámetros configurables:

- Masa del vehículo
- Capacidad de batería
- Eficiencia del motor
- Coeficientes aerodinámicos
- Velocidad y pendiente
- Condiciones ambientales

## 🌐 Demo en Línea

🚀 **[Probar el simulador en línea](https://tu-app.streamlit.app)** (próximamente)

## 🚀 Instalación y Ejecución

### Requisitos previos:

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación:

```bash
# Clonar o descargar el proyecto
cd captcha-v3

# Crear entorno virtual (recomendado)
python3 -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt
```

### Ejecución:

```bash
# Activar el entorno virtual (si no está activado)
source .venv/bin/activate

# Ejecutar el simulador
streamlit run main.py
```

El simulador se abrirá automáticamente en tu navegador en http://localhost:8501

## 📊 Uso del Simulador

### Panel lateral (Parámetros):

1. **Parámetros del vehículo**: Configura masa, batería, eficiencia y coeficientes
2. **Tramo a simular**: Define distancia, velocidad y pendiente
3. **Regeneración**: Activa/desactiva y configura eficiencia de regeneración

### Sección principal:

- **Métricas principales**: Consumo, energía, potencia y autonomía estimada
- **Detalle de fuerzas**: Desglose de cada componente de fuerza
- **Tabla de resultados**: Barrido por velocidad y pendiente
- **Gráficos**: Visualización de consumo vs pendiente y velocidad

### Casos de ejemplo:

Usa los botones predefinidos para cargar configuraciones típicas:

- 🏙️ **Urbano**: Velocidad moderada en terreno plano
- ⛰️ **Montaña**: Ascenso de 6% a velocidad moderada
- 🛣️ **Autopista**: Alta velocidad en terreno plano

## 📥 Exportación de Resultados

El simulador permite exportar:

- **Tabla de resultados**: Botón "📥 Descargar tabla de resultados (CSV)"
- **Gráfico 1**: Consumo vs Pendiente para diferentes velocidades (PNG)
- **Gráfico 2**: Consumo vs Velocidad para pendiente fija (PNG)

## 🎓 Alineación con el Curso

Este proyecto integra:

- **Dinámica de partículas**: Análisis de fuerzas en sistemas en movimiento
- **Trabajo y energía**: Cálculo de trabajo realizado y energía consumida
- **Potencia**: Relación entre fuerza, velocidad y potencia
- **Conservación de energía**: Regeneración en bajadas

## 📚 Estructura del Código

```
captcha-v3/
├── main.py           # Aplicación Streamlit principal
├── doc/              # Documentación del curso
│   ├── silabus.pdf
│   └── rubrica.pdf
├── README.md         # Este archivo
├── MEJORAS.md        # Notas sobre mejoras implementadas
└── .venv/            # Entorno virtual (generado)
```

## 🔧 Tecnologías Utilizadas

- **Python 3.13**: Lenguaje de programación
- **Streamlit**: Framework para aplicaciones web interactivas
- **Pandas**: Manipulación y análisis de datos
- **Matplotlib**: Visualización de gráficos
- **NumPy** (implícito): Cálculos numéricos

## 📝 Conclusiones

### Observaciones teóricas:

- El consumo aumenta con la velocidad debido a que F_aero ∝ v²
- La potencia necesaria crece aproximadamente como P ∝ v³
- Las pendientes positivas incrementan significativamente el consumo
- La regeneración puede recuperar 60-70% de la energía potencial en bajadas

### Aplicaciones prácticas:

- Planificación de rutas para maximizar autonomía
- Estimación de tiempos de carga necesarios
- Análisis de viabilidad de EVs en zonas montañosas
- Optimización de velocidad para eficiencia energética

## 👤 Autor

Proyecto desarrollado para el curso de Mecánica Clásica - 2026

## 📄 Licencia

Proyecto académico - Todos los derechos reservados

---

**💡 Tip:** Para obtener los mejores resultados, experimenta con diferentes combinaciones de parámetros y observa cómo afectan al consumo energético. Utiliza los casos de ejemplo como punto de partida.
