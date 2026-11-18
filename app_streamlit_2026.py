import streamlit as st

def generar_fixture(equipos):
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # 1. Generar todos los pares posibles (i < j) para evitar duplicados
    todos_los_pares = []
    for i in range(n):
        for j in range(i + 1, n):
            todos_los_pares.append((equipos[i], equipos[j]))

    # 2. Ordenar para priorizar a los primeros equipos
    todos_los_pares.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # 3. Seleccionar enfrentamientos asegurando que ningún equipo supere 3 partidos
    partidos_por_equipo = {eq: 0 for eq in equipos}
    seleccionados = []

    for par in todos_los_pares:
        eq1, eq2 = par
        if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
            seleccionados.append(par)
            partidos_por_equipo[eq1] += 1
            partidos_por_equipo[eq2] += 1

    # Verificar que todos los equipos tengan exactamente 3 partidos
    if any(partidos_por_equipo[eq] != 3 for eq in equipos):
        return None, "No se pudo generar un fixture válido con exactamente 3 partidos por equipo. Intenta con más equipos."

    # 4. Asignar fechas y canchas evitando que un equipo juegue dos veces en la misma fecha
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
                    # Esta fecha está completa; el resto va a nuevos_restantes
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
