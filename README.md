# vision-haptic-auto

## Proyecto Personal del Curso de Investigación y Desarrollo de Instrumentos Inteligentes

### Diseño de un Sistema de Retroalimentación de Fuerza Háptica para Pantallas Táctiles de Vehículos Inteligentes Basado en Percepción Visotáctil

---

## Introducción del Proyecto

Este proyecto es el trabajo final del curso *Diseño y Fabricación de Instrumentos Inteligentes*, clasificado como **diseño innovador**.

Aborda el problema de que, en el contexto de la pantalla táctil integral en vehículos inteligentes, los conductores se ven obligados a depender de la confirmación visual debido a la falta de retroalimentación háptica, lo que provoca distracción al conducir y riesgos de seguridad. Se diseña un sistema de retroalimentación de fuerza háptica para pantallas táctiles de vehículos inteligentes basado en percepción visotáctil.

### Innovaciones del Diseño

1. **Innovación de escenario**: Transferencia de la tecnología de detección visotáctil desde la inspección industrial al escenario de interacción a bordo
2. **Innovación funcional**: La dimensión de percepción se expande de "posición" a información tetradimensional: "fuerza + área + velocidad + posición"
3. **Innovación del sistema**: Construcción de una arquitectura de retroalimentación completa de "capa de percepción → capa de decisión → capa de ejecución"

### Arquitectura del Sistema

```
Capa de percepción: Cámara microscópica bajo la pantalla + marcado de patrón de moteado en elastómero → Percepción háptica tetradimensional
       ↓
Capa de decisión: Algoritmo de mapeo fuerza-sensación háptica + estrategia adaptativa de escenario
       ↓
Capa de ejecución: Matriz de actuadores piezoeléctricos + control de retroalimentación → Retroalimentación de fuerza háptica diferenciada
```

---

## Estructura del Repositorio

```
vision-haptic-auto/
├── README.md                # Descripción del proyecto (este archivo)
├── .gitignore               # Reglas de ignorado de Git
├── paper/                   # Documento del artículo
│   └── main.md              # Documento principal en Markdown
├── figures/                 # Recursos gráficos
│   ├── fig0_architecture.png    # Diagrama de arquitectura del sistema
│   ├── fig1_force_haptic_mapping.png  # Mapa de mapeo fuerza-sensación háptica
│   ├── fig2_speckle_tracking.png      # Resultado del seguimiento de patrón de moteado
│   └── generate_all_figures.py  # Script de generación por lotes
├── simulation/              # Código de simulación
│   ├── matlab/              # Simulación en MATLAB
│   │   └── force_haptic_mapping.m
│   └── python/              # Simulación en Python
│       └── speckle_tracker.py
└── references/              # Referencias bibliográficas
    └── bibliography.bib     # Referencias en BibTeX
```

---

## Cuatro Por Qués

| Sección | Pregunta Clave |
|---------|----------------|
| I. Introducción | **Por qué hacerlo** — Contexto industrial, análisis de problemas, deficiencias actuales |
| II. Estado del Arte | **Nivel actual** — Estado de cuatro tecnologías: pantalla capacitiva/LRA/actuador piezoeléctrico/visotáctil |
| III. Diseño de la Solución | **Qué hacer** — Diseño de arquitectura de tres capas: percepción + decisión + ejecución |
| IV. Resultados Esperados | **Cómo será** — Indicadores de rendimiento, experiencia esperada, plan de validación |
| V. Conclusión | Revisión y perspectivas |

---

## Indicadores de Rendimiento Esperados

| Indicador | Valor Objetivo |
|-----------|----------------|
| Resolución de percepción de fuerza | ≤0.05 N |
| Rango de percepción de fuerza | 0.1 N ~ 10 N |
| Resolución del área de contacto | ≤1 mm² |
| Latencia de respuesta de retroalimentación | <10 ms |
| Efectos hápticos distinguibles | ≥8 tipos |
| Rango de temperatura de funcionamiento | -40 °C ~ +85 °C |

---

## Referencias

1. Asociación China de Fabricantes de Automóviles. *Informe de Investigación sobre la Industria de Cabinas Inteligentes en China*, 2024.
2. Lee J D, Young K L, Regan M A. Defining driver distraction. En *Driver Distraction: Theory, Effects, and Mitigation*, CRC Press, 2008.
3. Petermeijer S M, Abbink D A, Mulder M. Haptic feedback in automotive interfaces: A systematic review. *IEEE Trans. on Haptics*, 8(2), 2015.
4. TDK Corporation. *PowerHap: Piezoelectric Actuators for Haptic Applications*, 2020.
5. Cirrus Logic. *CS40L25: Piezo Haptic Driver Datasheet*, 2023.
6. Luo S, et al. Robotic tactile sensing for industrial applications. *IEEE Trans. on Industrial Informatics*, 14(2), 2017.
7. Li R, Adelson E H. A GelSight tactile sensor for robotic applications. *IEEE/RSJ IROS*, 2013.
8. Shimonomura K. Tactile image sensors employing camera: A review. *Sensors*, 19(19), 2019.

---

## Licencia

MIT License — Solo para fines académicos
