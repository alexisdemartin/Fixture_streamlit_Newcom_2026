import streamlit as st

def generar_fixture(equipos):
    """Genera un fixture donde cada equipo juega exactamente 3 partidos,
    sin que un equipo juegue dos veces en la misma fecha.
    Prioriza a los primeros equipos en las primeras fechas."""
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # Generar todos los enfrentamientos posibles (pares únicos)
    todos_los_pares = []
    for i in range(n):
        for j in range(i + 1, n):
            todos_los_pares.append((equipos[i], equipos[j]))

    # Contador de partidos por equipo
    partidos_por_equipo = {eq: 0 for eq in equipos}
    # Lista de enfrentamientos seleccionados
    seleccionados = []

    # Ordenar los pares para priorizar a los primeros equipos:
    # primero los que involucran al equipo 1, luego al 2, etc.
    todos_los_pares.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # Seleccionar enfrentamientos asegurando que ningún equipo supere 3 partidos
    for par in todos_los_pares:
        eq1, eq2 = par
        if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
            seleccionados.append(par)
            partidos_por_equipo[eq1] += 1
            partidos_por_equipo[eq2] += 1
        if all(partidos_por_equipo[eq] == 3 for eq in equipos):
            break

    # Verificar que todos los equipos tengan exactamente 3 partidos
    if any(partidos_por_equipo[eq] != 3 for eq in equipos):
        return None, "No se pudo generar un fixture válido con 3 partidos por equipo. Intenta con más equipos."

    # Asignar fechas y canchas evitando que un equipo juegue dos veces en la misma fecha
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    fecha_num = 1
    equipos_en_fecha = set()  # Equipos que ya juegan en la fecha actual
    partidos_en_fecha = 0

    for par in seleccionados:
        eq1, eq2 = par
        # Si alguno de los equipos ya juega en esta fecha, o la fecha ya tiene 3 partidos,
        # pasamos a la siguiente fecha
        if eq1 in equipos_en_fecha or eq2 in equipos_en_fecha or partidos_en_fecha >= 3:
            fecha_num += 1
            equipos_en_fecha = set()
            partidos_en_fecha = 0

        # Asignar cancha (rotativa dentro de la fecha)
        cancha = canchas[partidos_en_fecha % 3]
        if fecha_num not in fixture:
            fixture[fecha_num] = {}
        fixture[fecha_num][cancha] = f"{eq1} vs {eq2}"
        equipos_en_fecha.add(eq1)
        equipos_en_fecha.add(eq2)
        partidos_en_fecha += 1

    # Convertir a formato legible
    fixture_legible = {f"Fecha {k}": v for k, v in fixture.items()}
    return fixture_legible, None

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
