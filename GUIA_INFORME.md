# Guía para Informe Académico

## 📋 Estructura Sugerida del Informe

### 1. Introducción (1-2 páginas)

- Contexto: Importancia de los vehículos eléctricos
- Problema a resolver: Estimación de consumo energético en pendientes
- Objetivo del trabajo
- Justificación del uso de mecánica clásica

### 2. Marco Teórico (2-3 páginas)

#### 2.1 Fundamentos de Mecánica Clásica

- Segunda ley de Newton: F = ma
- Trabajo: W = F · d
- Energía cinética y potencial
- Potencia: P = F · v

#### 2.2 Fuerzas sobre el vehículo

**Incluir las ecuaciones:**

- Componente gravitacional: F_pend = mg·sin(θ)
- Resistencia por rodadura: F_rr = C_rr·mg·cos(θ)
- Resistencia aerodinámica: F_aero = ½·ρ·C_d·A·v²
- Fuerza total: F_total = F_pend + F_rr + F_aero

**Explicar cada parámetro:**

- m: masa del vehículo (kg)
- g: aceleración gravitacional (9.81 m/s²)
- θ: ángulo de la pendiente
- C_rr: coeficiente de rodadura (típico: 0.008-0.015)
- ρ: densidad del aire (≈1.2 kg/m³)
- C_d: coeficiente aerodinámico (típico: 0.25-0.35)
- A: área frontal del vehículo (m²)
- v: velocidad (m/s)

#### 2.3 Modelo energético

- Trabajo realizado: W = F_total · L
- Energía de batería: E_batería = W / η
- Potencia instantánea: P = F_total · v
- Regeneración en bajadas: E_regen = η_regen · mg·Δh

### 3. Metodología (1-2 páginas)

#### 3.1 Herramientas utilizadas

- Python 3.13
- Streamlit (interfaz web interactiva)
- Pandas (análisis de datos)
- Matplotlib (visualización)

#### 3.2 Implementación del simulador

Describir brevemente cómo se implementaron las ecuaciones en código.

#### 3.3 Parámetros de simulación

Tabla con los valores típicos utilizados:

| Parámetro         | Valor típico | Rango       | Unidad |
| ----------------- | ------------ | ----------- | ------ |
| Masa (m)          | 1700         | 500-4000    | kg     |
| Capacidad batería | 60           | 10-200      | kWh    |
| Eficiencia (η)    | 0.90         | 0.70-0.98   | -      |
| C_rr              | 0.010        | 0.005-0.030 | -      |
| C_d               | 0.28         | 0.20-0.50   | -      |
| Área frontal (A)  | 2.2          | 1.5-3.5     | m²     |
| Densidad aire (ρ) | 1.2          | 0.9-1.4     | kg/m³  |

### 4. Resultados y Análisis (3-4 páginas)

#### 4.1 Casos de estudio

**Incluir análisis de los 3 casos principales:**

1. **Caso Urbano (plano, 50 km/h)**
   - Consumo estimado: ~12-15 kWh/100km
   - Fuerza dominante: Resistencia por rodadura
   - Autonomía esperada: ~400 km con batería de 60 kWh

2. **Caso Montaña (6% subida, 60 km/h)**
   - Consumo estimado: ~25-30 kWh/100km
   - Fuerza dominante: Componente gravitacional
   - Autonomía reducida: ~200 km

3. **Caso Autopista (plano, 110 km/h)**
   - Consumo estimado: ~18-22 kWh/100km
   - Fuerza dominante: Resistencia aerodinámica (crece con v²)
   - Autonomía: ~300 km

#### 4.2 Gráficos y tablas

**IMPORTANTE:** Exporta e incluye:

- Gráfico 1: Consumo vs Pendiente (múltiples velocidades)
- Gráfico 2: Consumo vs Velocidad (pendiente fija)
- Tabla con valores numéricos para al menos 10 casos

#### 4.3 Análisis de sensibilidad

Discutir cómo varían los resultados al cambiar:

- La velocidad (efecto cuadrático de F_aero)
- La pendiente (efecto lineal de F_pend)
- La masa del vehículo
- Los coeficientes aerodinámicos

#### 4.4 Regeneración en bajadas

- Comparar consumo con y sin regeneración
- Eficiencia típica: 60-70% de recuperación
- Impacto en autonomía total

### 5. Discusión (1-2 páginas)

#### 5.1 Validación del modelo

Comparar resultados con datos reales de fabricantes (Tesla Model 3, Nissan Leaf, etc.)

#### 5.2 Limitaciones del modelo

- Simplificaciones asumidas
- Factores no considerados (temperatura, envejecimiento de batería, etc.)
- Condiciones ideales vs. mundo real

#### 5.3 Aplicaciones prácticas

- Planificación de rutas
- Diseño de infraestructura de carga
- Optimización de consumo energético
- Viabilidad de EVs en diferentes terrenos

### 6. Conclusiones (1 página)

#### Principales hallazgos:

1. La resistencia aerodinámica tiene un impacto cuadrático con la velocidad
2. Las pendientes aumentan significativamente el consumo
3. La regeneración puede recuperar hasta 60-70% de la energía en bajadas
4. La velocidad óptima para eficiencia está entre 50-70 km/h en terreno plano

#### Relación con el curso:

- Aplicación directa de la segunda ley de Newton
- Análisis de trabajo y energía
- Cálculo de potencia instantánea
- Conservación de energía en regeneración

#### Aprendizajes:

- Comprensión profunda de las fuerzas en movimiento
- Importancia de la modelación matemática
- Aplicación práctica de conceptos teóricos

### 7. Referencias

**Incluir al menos:**

- Bibliografía del curso de mecánica clásica
- Manuales técnicos de vehículos eléctricos
- Artículos sobre eficiencia energética
- Documentación de Python/Streamlit (opcional)

Ejemplos:

- Serway, R. A., & Jewett, J. W. (2018). Physics for Scientists and Engineers.
- Tesla Motors. (2024). Model 3 Technical Specifications.
- Ehsani, M., et al. (2018). Modern Electric, Hybrid Electric, and Fuel Cell Vehicles.

### 8. Anexos (opcionales)

#### Anexo A: Código fuente

Fragmentos relevantes del código con comentarios explicativos.

#### Anexo B: Capturas de pantalla

Imágenes del simulador en funcionamiento.

#### Anexo C: Datos adicionales

Tablas completas de resultados si no caben en el cuerpo principal.

---

## 📊 Recomendaciones para la Presentación

### Estructura de diapositivas (10-15 slides):

1. **Título** - Nombre del proyecto, curso, fecha
2. **Introducción** - Contexto y objetivo (1 slide)
3. **Marco teórico** - Ecuaciones principales (2-3 slides)
4. **Metodología** - Herramientas y modelo (1-2 slides)
5. **Demo del simulador** - Screenshots o demo en vivo (2-3 slides)
6. **Resultados** - Gráficos principales (3-4 slides)
7. **Análisis** - Interpretación de resultados (2 slides)
8. **Conclusiones** - Hallazgos principales (1 slide)
9. **Preguntas** - Slide final

### Tips para la presentación:

- Practica la demo del simulador antes
- Prepara 2-3 casos específicos para mostrar
- Explica las ecuaciones paso a paso
- Relaciona cada resultado con la teoría del curso
- Anticipa preguntas sobre limitaciones del modelo

---

## ✅ Checklist para el Informe

### Contenido:

- [ ] Todas las ecuaciones están correctamente escritas en LaTeX
- [ ] Los gráficos tienen títulos, ejes etiquetados y unidades
- [ ] Las tablas están numeradas y tienen títulos descriptivos
- [ ] Se citan todas las fuentes utilizadas
- [ ] Se explica la relación con conceptos del curso
- [ ] Se discuten limitaciones del modelo

### Formato:

- [ ] Páginas numeradas
- [ ] Índice de contenidos
- [ ] Lista de figuras y tablas
- [ ] Formato consistente (fuente, márgenes, espaciado)
- [ ] Revisión ortográfica y gramatical
- [ ] Referencias en formato correcto

### Anexos:

- [ ] Código fuente (comentado)
- [ ] Capturas de pantalla del simulador
- [ ] Archivo README.md del proyecto
- [ ] Datos exportados (CSV)

---

## 🎯 Criterios de Evaluación (según rúbrica típica)

### Fundamento teórico (30%):

- Correcta aplicación de leyes de la mecánica clásica
- Ecuaciones bien derivadas y explicadas
- Referencias bibliográficas apropiadas

### Metodología (20%):

- Descripción clara del modelo implementado
- Justificación de parámetros utilizados
- Herramientas apropiadas

### Resultados (25%):

- Gráficos claros y profesionales
- Análisis cuantitativo detallado
- Interpretación física correcta

### Análisis y discusión (15%):

- Comparación con datos reales
- Identificación de limitaciones
- Propuesta de mejoras

### Presentación (10%):

- Formato profesional
- Claridad en la redacción
- Organización lógica

---

**¡Mucho éxito con tu proyecto!** 🚀
