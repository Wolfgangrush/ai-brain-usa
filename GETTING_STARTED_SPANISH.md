# Bienvenido, abogado — su AI Brain comienza aquí

No necesita ser programador. Necesita una laptop (Mac o Windows), conexión a internet para la instalación, y 30 minutos. Si puede copiar y pegar, puede usar esto.

> **English:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## Qué es esto, en un párrafo

Una herramienta gratuita que convierte su laptop en un asistente legal privado. Recuerda sus casos (cada expediente, cada parte, cada orden, cada fecha de audiencia). Valida citas legales en formato Bluebook. Le dice qué tribunal federal tiene jurisdicción. Señala riesgos bajo la Regla Modelo 7 de la ABA y problemas de cumplimiento con CCPA. Funciona **en su propia computadora** — sin nube, sin cargas, sin que terceros lean los datos de sus clientes. Licencia MIT. Todo lo que ponga le pertenece.

## Por qué un abogado independiente en EE.UU. debería interesarse

Los grandes bufetes tienen equipos de asociados para verificar citas, gestionar casos y redactar documentos. Usted se tiene a sí mismo y a su laptop. Esta es su segunda memoria.

- **Olvida menos.** El contexto de casos de meses atrás vuelve al instante.
- **Pierde menos plazos.** Se rastrean fechas de audiencias, plazos de presentación y prescripción.
- **Se mantiene en cumplimiento con la ABA.** El firewall incorporado señala riesgos de publicidad (Regla 7), práctica multijurisdiccional (Regla 5.5) y confidencialidad (Regla 1.6).
- **Ahorra dinero.** Westlaw, PACER y LexisNexis cuestan miles al año. Esto cuesta $0.
- **Sus datos permanecen privados.** Los casos de sus clientes NUNCA salen de su laptop.
- **Puede crecer.** Cuando contrate a su primer asociado, cambie de modo individual a modo firma — misma herramienta, mismos datos.

## Qué incluye

7 especialistas dentro de su terminal:

1. **El Recepcionista** — interpreta lo que necesita y lo dirige al especialista correcto.
2. **El Auxiliar de Citas** — valida citas Bluebook (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.).
3. **El Secretario Judicial** — conoce los tribunales federales: SCOTUS, 13 circuitos, 94 distritos, quiebras, tribunal fiscal.
4. **El Gestor de Casos** — mantiene sus expedientes activos (partes, audiencias, órdenes, plazos).
5. **El Asistente de Redacción** — se conecta a los complementos de redacción wolfgang_rush (v0.2+).
6. **El Oficial de Cumplimiento** — Reglas ABA 7, 5.5, 1.6, Opinión Formal 512 (ética de IA), CCPA/CPRA, FinCEN CTA.
7. **El Rastreador de Plazos** — prescripción, plazos de presentación, fechas de audiencia (cómputo de tiempo según FRCP Regla 6).

## Instalación rápida

```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
ailawfirm_usa
```

## Probar

```bash
ailawfirm_usa court "scotus"
ailawfirm_usa cite "347 U.S. 483 (1954)"
ailawfirm_usa cite "42 U.S.C. § 1983"
```

## Nota de alcance

v0.1 está **enfocado en lo federal.** Cubre SCOTUS, tribunales federales de circuito/distrito, FRCP/FRCrP/FRE, Reglas Modelo de la ABA y citas Bluebook. Los módulos específicos por estado (CA CRC, NY CPLR, reglas estatales de la barra) llegan en v0.2+. Todos los 50 estados están enumerados como marcadores de posición.

## Privacidad

Todo funciona localmente. Los casos de sus clientes, archivos y datos del calendario permanecen en su laptop. Sin carga a la nube. Sin acceso de terceros. Sin telemetría.
