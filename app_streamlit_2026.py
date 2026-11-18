import streamlit as st

def generar_fixture(equipos):
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # 1. Generar todos los pares posibles (i < j) y ordenarlos por orden de inscripción
    todos_los_pares = []
    for i in range(n):
        for j in range(i + 1, n):
            todos_los_pares.append((equipos[i], equipos[j]))
    todos_los_pares.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # 2. Contador de partidos por equipo
    partidos_por_equipo = {eq: 0 for eq in equipos}
    seleccionados = []

    # 3. Asignar partidos de forma equilibrada (misma lógica que antes)
    for par in todos_los_pares:
        eq1, eq2 = par
        if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
            seleccionados.append(par)
            partidos_por_equipo[eq1] += 1
            partidos_por_equipo[eq2] += 1

    # Segunda pasada para completar equipos incompletos
    equipos_incompletos = [eq for eq in equipos if partidos_por_equipo[eq] < 3]
    if equipos_incompletos:
        for par in todos_los_pares:
            if par in seleccionados:
                continue
            eq1, eq2 = par
            if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
                seleccionados.append(par)
                partidos_por_equipo[eq1] += 1
                partidos_por_equipo[eq2] += 1
                equipos_incompletos = [eq for eq in equipos if partidos_por_equipo[eq] < 3]
                if not equipos_incompletos:
                    break

    # 4. Asignar rondas: cada ronda es una "pasada" por todos los equipos
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    ronda_num = 1
    partidos_restantes = seleccionados.copy()

    while partidos_restantes:
        equipos_en_ronda = set()
        partidos_en_ronda = []
        nuevos_restantes = []

        # Recorrer los equipos en orden de inscripción
        # Para cada equipo, si aún no jugó en esta ronda y necesita partidos,
        # buscarle un rival disponible que tampoco haya jugado en esta ronda.
        for equipo in equipos:
            if equipo in equipos_en_ronda:
                continue
            if partidos_por_equipo[equipo] <= 0:  # ya no necesita más partidos
                continue

            # Buscar un rival para este equipo entre los partidos restantes
            rival_encontrado = None
            for par in partidos_restantes:
                if par in partidos_en_ronda:
                    continue
                eq1, eq2 = par
                if eq1 == equipo and eq2 not in equipos_en_ronda:
                    rival_encontrado = par
                    break
                elif eq2 == equipo and eq1 not in equipos_en_ronda:
                    rival_encontrado = par
                    break

            if rival_encontrado:
                partidos_en_ronda.append(rival_encontrado)
                equipos_en_ronda.add(rival_encontrado[0])
                equipos_en_ronda.add(rival_encontrado[1])
                partidos_por_equipo[rival_encontrado[0]] -= 1
                partidos_por_equipo[rival_encontrado[1]] -= 1
                partidos_restantes.remove(rival_encontrado)

        # Si no se asignó ningún partido en esta pasada, salir para evitar bucle infinito
        if not partidos_en_ronda:
            break

        # Asignar los partidos de esta ronda a las canchas
        fixture[f"Ronda {ronda_num}"] = {}
        for j in range(3):
            if j < len(partidos_en_ronda):
                eq1, eq2 = partidos_en_ronda[j]
                fixture[f"Ronda {ronda_num}"][canchas[j]] = f"{eq1} vs {eq2}"
            else:
                fixture[f"Ronda {ronda_num}"][canchas[j]] = "— (sin partido) —"
        ronda_num += 1

    # 5. Nota si quedaron equipos con partidos pendientes
    equipos_sin_completar = [eq for eq in equipos if partidos_por_equipo[eq] > 0]
    if equipos_sin_completar:
        fixture["Nota"] = {
            "Cancha 1": f"Equipos con partidos pendientes: {', '.join(equipos_sin_completar)}",
            "Cancha 2": "",
            "Cancha 3": ""
        }

    return fixture, None

# --- Interfaz de Streamlit ---
st.title("⚽ Generador de Fixture")
st.markdown("""
- **Equipos ilimitados** (mínimo 4)
- Cada equipo juega **exactamente 3 partidos** (o los que se puedan)
- **3 canchas** por ronda
- Ningún equipo juega dos veces en la misma ronda
- **Un equipo no vuelve a jugar hasta que todos los demás hayan tenido su turno en la ronda**
- Si no se completan todos los partidos, se dejan **espacios vacíos**
""")

equipos_input = st.text_area(
    "Ingresa los equipos separados por coma (el orden es el de inscripción):",
    "Equipo 1, Equipo 2, Equipo 3, Equipo 4, Equipo 5, Equipo 6",
    height=100
)

if st.button("Generar Fixture"):
    equipos = [e.strip() for e in equipos_input.split(",") if e.strip()]
    fixture, error = generar_fixture(equipos)

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
