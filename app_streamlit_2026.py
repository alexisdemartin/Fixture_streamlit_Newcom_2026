import streamlit as st

def generar_fixture(equipos):
    """
    Genera un fixture con:
    - Número indefinido de equipos (mínimo 4)
    - Cada equipo juega exactamente 3 partidos
    - 3 canchas por ronda
    - Ningún equipo juega dos veces en la misma ronda
    - Los primeros equipos en anotarse juegan primero en las 3 canchas
    """
    n = len(equipos)
    if n < 4:
        return None, "Se necesitan al menos 4 equipos para que cada uno juegue 3 partidos."

    # 1. Generar todos los pares posibles (i < j) y ordenarlos por orden de inscripción
    todos_los_pares = []
    for i in range(n):
        for j in range(i + 1, n):
            todos_los_pares.append((equipos[i], equipos[j]))

    # Ordenar para priorizar a los primeros equipos (por índice del primer equipo, luego del segundo)
    todos_los_pares.sort(key=lambda par: (equipos.index(par[0]), equipos.index(par[1])))

    # 2. Asignar partidos de forma equilibrada: cada equipo debe tener exactamente 3
    partidos_por_equipo = {eq: 0 for eq in equipos}
    seleccionados = []

    # Estrategia: recorrer los pares en orden, pero solo aceptar si ambos equipos
    # aún no han alcanzado los 3 partidos. Si al final algún equipo queda con menos,
    # se corrige con una segunda pasada.
    for par in todos_los_pares:
        eq1, eq2 = par
        if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
            seleccionados.append(par)
            partidos_por_equipo[eq1] += 1
            partidos_por_equipo[eq2] += 1

    # 3. Si algún equipo no llegó a 3 partidos, intentar completar con pares no seleccionados
    equipos_incompletos = [eq for eq in equipos if partidos_por_equipo[eq] < 3]
    if equipos_incompletos:
        # Buscar pares no seleccionados que involucren a equipos incompletos
        for par in todos_los_pares:
            if par in seleccionados:
                continue
            eq1, eq2 = par
            if partidos_por_equipo[eq1] < 3 and partidos_por_equipo[eq2] < 3:
                seleccionados.append(par)
                partidos_por_equipo[eq1] += 1
                partidos_por_equipo[eq2] += 1
                # Actualizar lista de incompletos
                equipos_incompletos = [eq for eq in equipos if partidos_por_equipo[eq] < 3]
                if not equipos_incompletos:
                    break

    # Verificación final
    if any(partidos_por_equipo[eq] != 3 for eq in equipos):
        return None, "No se pudo generar un fixture válido con exactamente 3 partidos por equipo. Intenta con más equipos."

    # 4. Asignar rondas y canchas respetando el orden de inscripción
    #    y evitando que un equipo juegue dos veces en la misma ronda.
    fixture = {}
    canchas = ["Cancha 1", "Cancha 2", "Cancha 3"]
    ronda_num = 1
    partidos_restantes = seleccionados.copy()

    while partidos_restantes:
        equipos_en_ronda = set()
        partidos_en_ronda = []
        nuevos_restantes = []

        # Recorrer los partidos en orden (ya están ordenados por inscripción)
        for par in partidos_restantes:
            eq1, eq2 = par
            if eq1 not in equipos_en_ronda and eq2 not in equipos_en_ronda:
                partidos_en_ronda.append(par)
                equipos_en_ronda.add(eq1)
                equipos_en_ronda.add(eq2)
                if len(partidos_en_ronda) == 3:
                    # Ronda completa
                    idx = partidos_restantes.index(par)
                    nuevos_restantes.extend(partidos_restantes[idx + 1:])
                    break
            else:
                nuevos_restantes.append(par)

        if partidos_en_ronda:
            fixture[f"Ronda {ronda_num}"] = {}
            for j, (eq1, eq2) in enumerate(partidos_en_ronda):
                fixture[f"Ronda {ronda_num}"][canchas[j]] = f"{eq1} vs {eq2}"
            ronda_num += 1
        else:
            break

        partidos_restantes = nuevos_restantes

    return fixture, None

# --- Interfaz de Streamlit ---
st.title("⚽ Generador de Fixture")
st.markdown("""
- **Equipos ilimitados** (mínimo 4)
- Cada equipo juega **exactamente 3 partidos**
- **3 canchas** por ronda
- Ningún equipo juega dos veces en la misma ronda
- Los primeros equipos en anotarse juegan primero en las 3 canchas
""")

equipos_input = st.text_area(
    "Ingresa los equipos separados por coma (el orden es el de inscripción):",
    "Equipo 1, Equipo 2, Equipo 3, Equipo 4, Equipo 5, Equipo 6, Equipo 7, Equipo 8",
    height=100
)

if st.button("Generar Fixture"):
    equipos = [e.strip() for e in equipos_input.split(",") if e.strip()]
    fixture, error = generar_fixture(equipos)

    if error:
        st.error(error)
    else:
        st.success("¡Fixture generado con éxito!")
        for ronda, partidos in fixture.items():
            st.subheader(ronda)
            for cancha, partido in partidos.items():
                st.write(f"**{cancha}:** {partido}")
