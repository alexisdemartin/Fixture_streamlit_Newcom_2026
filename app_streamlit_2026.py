import streamlit as st

def generar_fixture(equipos):
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # 1. Generar enfrentamientos: cada equipo i juega contra i+1, i+2, i+3 (circular)
    enfrentamientos = set()
    for i in range(n):
        for offset in [1, 2, 3]:
            j = (i + offset) % n
            if i != j:
                par = tuple(sorted([equipos[i], equipos[j]]))
                enfrentamientos.add(par)

    partidos = list(enfrentamientos)
    # Ordenar para priorizar a los primeros equipos
    partidos.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # 2. Asignar fechas: cada fecha tendrá hasta 3 partidos, sin repetir equipos
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    fecha_num = 1
    partidos_restantes = partidos.copy()

    while partidos_restantes:
        equipos_en_fecha = set()
        partidos_en_fecha = []
        nuevos_restantes = []

        for par in partidos_restantes:
            eq1, eq2 = par
            if eq1 not in equipos_en_fecha and eq2 not in equipos_en_fecha:
                # Se puede agregar a esta fecha
                partidos_en_fecha.append(par)
                equipos_en_fecha.add(eq1)
                equipos_en_fecha.add(eq2)
                if len(partidos_en_fecha) == 3:
                    # Ya tenemos 3 partidos para esta fecha
                    # El resto de partidos_restantes (incluyendo los que faltan recorrer)
                    # se agregarán a nuevos_restantes
                    nuevos_restantes.extend([p for p in partidos_restantes if p not in partidos_en_fecha and p not in nuevos_restantes])
                    break
            else:
                nuevos_restantes.append(par)

        # Asignar los partidos de esta fecha a las canchas
        if partidos_en_fecha:
            fixture[f"Fecha {fecha_num}"] = {}
            for j, (eq1, eq2) in enumerate(partidos_en_fecha):
                fixture[f"Fecha {fecha_num}"][canchas[j]] = f"{eq1} vs {eq2}"
            fecha_num += 1
        else:
            # No se pudo asignar ningún partido (no debería ocurrir)
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
