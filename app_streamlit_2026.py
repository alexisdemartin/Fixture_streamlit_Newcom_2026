import streamlit as st
from itertools import combinations

def generar_fixture_por_zonas(equipos):
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos."

    # 1. Agrupar en zonas de 4 (respetando orden de inscripción)
    zonas = []
    equipos_restantes = equipos.copy()

    while len(equipos_restantes) >= 4:
        zonas.append(equipos_restantes[:4])
        equipos_restantes = equipos_restantes[4:]

    # 2. Si quedan equipos sueltos (1, 2 o 3), redistribuir
    if equipos_restantes:
        # Desarmar la última zona y mezclar con los sobrantes
        if zonas:
            ultima_zona = zonas.pop()
            sobrantes = ultima_zona + equipos_restantes
        else:
            sobrantes = equipos_restantes

        # Redistribuir en zonas de 4 (o lo más cercano posible)
        # Estrategia simple: llenar zonas existentes hasta 4, luego crear nuevas
        for eq in sobrantes:
            colocado = False
            for zona in zonas:
                if len(zona) < 4:
                    zona.append(eq)
                    colocado = True
                    break
            if not colocado:
                zonas.append([eq])

    # 3. Generar partidos dentro de cada zona (round-robin completo)
    #    Cada zona de 4 genera 6 partidos (3 fechas x 2 partidos)
    todos_los_partidos = []
    for idx_zona, zona in enumerate(zonas, start=1):
        partidos_zona = list(combinations(zona, 2))
        # Ordenar para priorizar a los primeros equipos de la zona
        partidos_zona.sort(key=lambda par: (zona.index(par[0]), zona.index(par[1])))
        for par in partidos_zona:
            todos_los_partidos.append((f"Zona {idx_zona}", par))

    # 4. Asignar rondas y canchas
    #    Cada ronda puede tener hasta 3 partidos (3 canchas).
    #    Ningún equipo juega dos veces en la misma ronda.
    #    Se priorizan los partidos de las primeras zonas y primeros equipos.
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    ronda_num = 1
    partidos_restantes = todos_los_partidos.copy()

    while partidos_restantes:
        equipos_en_ronda = set()
        partidos_en_ronda = []
        nuevos_restantes = []

        for partido in partidos_restantes:
            zona_nombre, (eq1, eq2) = partido
            if eq1 not in equipos_en_ronda and eq2 not in equipos_en_ronda:
                partidos_en_ronda.append(partido)
                equipos_en_ronda.add(eq1)
                equipos_en_ronda.add(eq2)
                if len(partidos_en_ronda) == 3:
                    idx = partidos_restantes.index(partido)
                    nuevos_restantes.extend(partidos_restantes[idx + 1:])
                    break
            else:
                nuevos_restantes.append(partido)

        if partidos_en_ronda:
            fixture[f"Ronda {ronda_num}"] = {}
            for j in range(3):
                if j < len(partidos_en_ronda):
                    zona_nombre, (eq1, eq2) = partidos_en_ronda[j]
                    fixture[f"Ronda {ronda_num}"][canchas[j]] = f"[{zona_nombre}] {eq1} vs {eq2}"
                else:
                    fixture[f"Ronda {ronda_num}"][canchas[j]] = "— (sin partido) —"
            ronda_num += 1
        else:
            break

        partidos_restantes = nuevos_restantes

    # 5. Verificación: cada equipo debe tener exactamente 3 partidos
    conteo = {eq: 0 for eq in equipos}
    for ronda, canchas_dict in fixture.items():
        if ronda == "Nota":
            continue
        for cancha, texto in canchas_dict.items():
            if " vs " in texto:
                # Extraer equipos del texto
                equipos_partido = texto.split("] ")[1].split(" vs ")
                for eq in equipos_partido:
                    if eq in conteo:
                        conteo[eq] += 1

    equipos_incompletos = [eq for eq, c in conteo.items() if c != 3]
    if equipos_incompletos:
        fixture["Nota"] = {
            "Cancha 1": f"Equipos con partidos distintos de 3: {', '.join(equipos_incompletos)}",
            "Cancha 2": "",
            "Cancha 3": ""
        }

    return fixture, None


# --- Interfaz de Streamlit ---
st.title("⚽ Generador de Fixture por Zonas de 4")
st.markdown("""
- **Zonas de 4 equipos** (round-robin completo: cada equipo juega 3 partidos)
- Si el número de equipos no es múltiplo de 4, se **desarma una zona** y se redistribuyen los equipos
- **3 canchas** por ronda
- Ningún equipo juega dos veces en la misma ronda
- Los primeros equipos en anotarse juegan primero en las canchas
""")

equipos_input = st.text_area(
    "Ingresa los equipos separados por coma (el orden es el de inscripción):",
    "Equipo 1, Equipo 2, Equipo 3, Equipo 4, Equipo 5, Equipo 6, Equipo 7, Equipo 8, Equipo 9",
    height=100
)

if st.button("Generar Fixture"):
    equipos = [e.strip() for e in equipos_input.split(",") if e.strip()]
    fixture, error = generar_fixture_por_zonas(equipos)

    if error:
        st.error(error)
    else:
        st.success("¡Fixture generado!")
        for ronda, partidos in fixture.items():
            if ronda == "Nota":
                st.warning(partidos["Cancha 1"])
            else:
                st.subheader(ronda)
                for cancha, partido in partidos.items():
                    st.write(f"**{cancha}:** {partido}")
