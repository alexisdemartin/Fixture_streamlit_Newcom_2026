import streamlit as st

def generar_fixture(equipos):
    """Genera un fixture donde cada equipo juega exactamente 3 partidos,
    sin que un equipo juegue dos veces en la misma fecha.
    Prioriza a los primeros equipos en las primeras fechas."""
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # Construir enfrentamientos de forma equilibrada:
    # cada equipo i juega contra i+1, i+2, i+3 (circular)
    enfrentamientos = set()
    for i in range(n):
        for offset in [1, 2, 3]:
            j = (i + offset) % n
            if i != j:
                par = tuple(sorted([equipos[i], equipos[j]]))
                enfrentamientos.add(par)

    partidos = list(enfrentamientos)
    # Ordenar para que los primeros equipos aparezcan primero
    partidos.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # Asignar fechas y canchas evitando que un equipo juegue dos veces en la misma fecha
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    fecha_num = 1
    equipos_en_fecha = set()
    partidos_en_fecha = 0

    for par in partidos:
        eq1, eq2 = par
        # Si alguno de los equipos ya juega en esta fecha, o la fecha ya tiene 3 partidos,
        # pasamos a la siguiente fecha
        if eq1 in equipos_en_fecha or eq2 in equipos_en_fecha or partidos_en_fecha >= 3:
            fecha_num += 1
            equipos_en_fecha = set()
            partidos_en_fecha = 0

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
