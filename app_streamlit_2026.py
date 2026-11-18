import streamlit as st

def generar_fixture(equipos):
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # 1. Generar todos los pares posibles (i < j)
    todos_los_pares = []
    for i in range(n):
        for j in range(i + 1, n):
            todos_los_pares.append((equipos[i], equipos[j]))

    # 2. Contador de partidos por equipo
    partidos_por_equipo = {eq: 0 for eq in equipos}

    # 3. Selección equilibrada: mientras haya equipos con menos de 3 partidos
    seleccionados = []
    # Ordenar equipos por los que menos partidos tienen (para equilibrar)
    # pero también priorizar a los primeros equipos cuando hay empate
    while any(partidos_por_equipo[eq] < 3 for eq in equipos):
        # Ordenar equipos: primero los que menos partidos tienen,
        # y entre ellos, los que aparecen primero en la lista original
        equipos_ordenados = sorted(
            equipos,
            key=lambda eq: (partidos_por_equipo[eq], equipos.index(eq))
        )
        # Tomar el primer equipo que aún necesite partidos
        eq1 = next(eq for eq in equipos_ordenados if partidos_por_equipo[eq] < 3)

        # Buscar un rival que también necesite partidos y que no haya jugado ya contra eq1
        rival = None
        for candidato in equipos_ordenados:
            if candidato == eq1:
                continue
            if partidos_por_equipo[candidato] >= 3:
                continue
            # Verificar que no hayan jugado antes
            par = tuple(sorted([eq1, candidato]))
            if par not in seleccionados:
                rival = candidato
                break

        if rival is None:
            # No se encontró rival disponible (puede ocurrir en casos extremos)
            return None, "No se pudo generar un fixture válido con exactamente 3 partidos por equipo. Intenta con más equipos."

        # Agregar el partido
        par = tuple(sorted([eq1, rival]))
        seleccionados.append(par)
        partidos_por_equipo[eq1] += 1
        partidos_por_equipo[rival] += 1

    # 4. Ordenar los partidos para que los primeros equipos aparezcan primero
    seleccionados.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # 5. Asignar fechas y canchas evitando que un equipo juegue dos veces en la misma fecha
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    fecha_num = 1
    partidos_restantes = seleccionados.copy()

    while partidos_restantes:
        equipos_en_fecha = set()
        partidos_en_fecha = []
        nuevos_restantes = []

        for par in partidos_restantes:
            eq1, eq2 = par
            if eq1 not in equipos_en_fecha and eq2 not in equipos_en_fecha:
                partidos_en_fecha.append(par)
                equipos_en_fecha.add(eq1)
                equipos_en_fecha.add(eq2)
                if len(partidos_en_fecha) == 3:
                    idx = partidos_restantes.index(par)
                    nuevos_restantes.extend(partidos_restantes[idx + 1:])
                    break
            else:
                nuevos_restantes.append(par)

        if partidos_en_fecha:
            fixture[f"Fecha {fecha_num}"] = {}
            for j, (eq1, eq2) in enumerate(partidos_en_fecha):
                fixture[f"Fecha {fecha_num}"][canchas[j]] = f"{eq1} vs {eq2}"
            fecha_num += 1
        else:
            break

        partidos_restantes = nuevos_restantes

    return fixture, None

# --- Interfaz de Streamlit ---
st.title("⚽ Generador de Fixture")
st.markdown("Cada equipo jugará **exactamente 3 partidos**. Se usan **3 canchas** por fecha.")

equipos_input = st.text_area(
    "Ingresa los equipos separados por coma:",
    "Equipo 1, Equipo 2, Equipo 3, Equipo 4, Equipo 5, Equipo 6",
    height=100
)

if st.button("Generar Fixture"):
    equipos = [e.strip() for e in equipos_input.split(",") if e.strip()]
    fixture, error = generar_fixture(equipos)

    if error:
        st.error(error)
    else:
        st.success("¡Fixture generado con éxito!")
        for fecha, partidos in fixture.items():
            st.subheader(fecha)
            for cancha, partido in partidos.items():
                st.write(f"**{cancha}:** {partido}")
