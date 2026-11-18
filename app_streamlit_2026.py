import streamlit as st

def generar_fixture(equipos):
    """Genera un fixture donde cada equipo juega exactamente 3 partidos."""
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # Generar enfrentamientos: cada equipo i juega contra i+1, i+2, i+3 (circular)
    enfrentamientos = set()
    for i in range(n):
        for offset in [1, 2, 3]:
            j = (i + offset) % n
            if i != j:
                par = tuple(sorted([equipos[i], equipos[j]]))
                enfrentamientos.add(par)

    partidos = list(enfrentamientos)
    partidos.sort()

    # Distribuir en fechas: 3 canchas por fecha (3 partidos por fecha)
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    fecha_num = 1
    for i in range(0, len(partidos), 3):
        bloque = partidos[i:i+3]
        fecha = f"Fecha {fecha_num}"
        fixture[fecha] = {}
        for j, (eq1, eq2) in enumerate(bloque):
            fixture[fecha][canchas[j]] = f"{eq1} vs {eq2}"
        fecha_num += 1

    return fixture, None

# --- Interfaz de Streamlit ---
st.title("⚽ Generador de Fixture")
st.markdown("Cada equipo jugará **exactamente 3 partidos**. Se usan **3 canchas** por fecha.")

# Entrada de equipos
equipos_input = st.text_area(
    "Ingresa los equipos separados por coma:",
    "A, B, C, D, E, F, G, H",
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
