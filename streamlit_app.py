import math
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st
import io
import numpy as np

# -----------------------------
# Física del EV (modelo simple)
# -----------------------------
def slope_trig_from_percent(grade_percent: float):
    """
    Convierte pendiente % a sin/cos sin usar ángulo.
    grade_percent = 6 significa 6% (6m de subida por 100m horizontales aprox)
    """
    tan_t = grade_percent / 100.0
    cos_t = 1.0 / math.sqrt(1.0 + tan_t**2)
    sin_t = tan_t * cos_t
    return sin_t, cos_t

def ev_segment(m_kg: float,
               v_kmh: float,
               grade_percent: float,
               L_km: float,
               eta: float,
               Crr: float,
               regen_eff: float):
    """
    Calcula fuerzas, potencia y energía consumida en un tramo.
    Si grade_percent < 0, aplica regeneración de forma simplificada.
    """
    g = 9.81
    v = v_kmh / 3.6          # m/s
    L = L_km * 1000.0        # m

    sin_t, cos_t = slope_trig_from_percent(grade_percent)

    # Fuerzas
    F_pend = m_kg * g * sin_t
    F_roz  = Crr * m_kg * g * cos_t
    F_tot  = F_pend + F_roz

    # Potencia (en ruedas) y desde batería
    P_mec = F_tot * v                 # W
    P_bat = P_mec / eta               # W

    # Energía consumida (J -> kWh)
    E_j = (F_tot * L) / eta
    E_kwh = E_j / 3.6e6

    # Regeneración simplificada en bajadas
    E_regen_kwh = 0.0
    if grade_percent < 0:
        # Cambio de altura (positivo si bajas): -L*sin_t (porque sin_t es negativo)
        dh_down = -L * sin_t
        # Energía potencial recuperable ~ m g dh
        E_regen_j = regen_eff * m_kg * g * dh_down
        E_regen_kwh = E_regen_j / 3.6e6
        E_kwh = max(0.0, E_kwh - E_regen_kwh)

    return {
        "F_pend_N": F_pend,
        "F_roz_N": F_roz,
        "F_tot_N": F_tot,
        "P_mec_kW": P_mec / 1000.0,
        "P_bat_kW": P_bat / 1000.0,
        "E_tramo_kWh": E_kwh,
        "E_regen_kWh": E_regen_kwh
    }

def compute_sweep(m_kg, eta, Crr, regen_eff,
                  L_km, v_kmh_list, grade_list):
    rows = []
    for v in v_kmh_list:
        for gr in grade_list:
            out = ev_segment(m_kg, v, gr, L_km, eta, Crr, regen_eff)
            kwh_per_km = out["E_tramo_kWh"] / L_km
            rows.append({
                "Velocidad (km/h)": v,
                "Pendiente (%)": gr,
                "F_total (N)": out["F_tot_N"],
                "P_bateria (kW)": out["P_bat_kW"],
                "E_tramo (kWh)": out["E_tramo_kWh"],
                "Consumo (kWh/100km)": kwh_per_km * 100.0
            })
    return pd.DataFrame(rows)

# -----------------------------
# Función auxiliar para exportar gráficos
# -----------------------------
def fig_to_bytes(fig):
    """Convierte una figura de matplotlib a bytes PNG para descarga"""
    buf = io.BytesIO()
    fig.savefig(buf, format='png', dpi=150, bbox_inches='tight')
    buf.seek(0)
    return buf.read()

def draw_vehicle_on_slope(grade_percent, F_pend, F_roz, F_tot, v_kmh):
    """Dibuja una visualización realista del vehículo en la pendiente con las fuerzas"""
    fig, ax = plt.subplots(figsize=(14, 8))
    
    # Calcular ángulo en radianes
    angle_rad = math.atan(grade_percent / 100.0)
    angle_deg = math.degrees(angle_rad)
    
    # Fondo - cielo y suelo
    ax.fill_between([0, 15], [-3, -3], [10, 10], color='#87CEEB', alpha=0.3, zorder=0)
    ax.fill_between([0, 15], [-3, -3], [0, 0], color='#8B7355', alpha=0.2, zorder=0)
    
    # Dibujar la carretera más realista
    road_length = 12
    road_width = 1.2
    x_road_center = np.array([0, road_length * math.cos(angle_rad)])
    y_road_center = np.array([0, road_length * math.sin(angle_rad)])
    
    # Bordes de la carretera
    perp_x = -math.sin(angle_rad) * road_width / 2
    perp_y = math.cos(angle_rad) * road_width / 2
    
    x_road_top = x_road_center + perp_x
    y_road_top = y_road_center + perp_y
    x_road_bottom = x_road_center - perp_x
    y_road_bottom = y_road_center - perp_y
    
    # Carretera (asfalto)
    road_vertices = np.array([
        [x_road_bottom[0], y_road_bottom[0]],
        [x_road_bottom[1], y_road_bottom[1]],
        [x_road_top[1], y_road_top[1]],
        [x_road_top[0], y_road_top[0]]
    ])
    road_poly = plt.Polygon(road_vertices, facecolor='#404040', edgecolor='#606060', linewidth=2, zorder=1)
    ax.add_patch(road_poly)
    
    # Líneas centrales de la carretera (discontinuas)
    num_dashes = 8
    for i in range(num_dashes):
        if i % 2 == 0:
            t1 = i / num_dashes
            t2 = (i + 0.6) / num_dashes
            x_dash = [x_road_center[0] + t1 * (x_road_center[1] - x_road_center[0]),
                     x_road_center[0] + t2 * (x_road_center[1] - x_road_center[0])]
            y_dash = [y_road_center[0] + t1 * (y_road_center[1] - y_road_center[0]),
                     y_road_center[0] + t2 * (y_road_center[1] - y_road_center[0])]
            ax.plot(x_dash, y_dash, 'yellow', linewidth=2.5, zorder=2)
    
    # Posición del vehículo
    car_pos_x = 6 * math.cos(angle_rad)
    car_pos_y = 6 * math.sin(angle_rad)
    
    # Dimensiones del auto realista
    car_length = 2.2
    car_height = 1.0
    car_roof_height = 0.6
    
    # Crear matriz de rotación
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    def rotate_point(x, y, cx, cy):
        """Rotar punto alrededor del centro del auto"""
        x_rot = cos_a * (x - cx) - sin_a * (y - cy) + cx
        y_rot = sin_a * (x - cx) + cos_a * (y - cy) + cy
        return x_rot, y_rot
    
    # Carrocería principal (cuerpo del auto)
    body_vertices = [
        (-car_length/2, -car_height/2),
        (car_length/2, -car_height/2),
        (car_length/2, car_height/2),
        (-car_length/2, car_height/2)
    ]
    body_rotated = [rotate_point(x + car_pos_x, y + car_pos_y, car_pos_x, car_pos_y) 
                    for x, y in body_vertices]
    body_poly = plt.Polygon(body_rotated, facecolor='#E74C3C', edgecolor='#C0392B', 
                            linewidth=2.5, zorder=5)
    ax.add_patch(body_poly)
    
    # Techo/cabina del auto
    roof_vertices = [
        (-car_length/3, car_height/2),
        (car_length/3, car_height/2),
        (car_length/4, car_height/2 + car_roof_height),
        (-car_length/4, car_height/2 + car_roof_height)
    ]
    roof_rotated = [rotate_point(x + car_pos_x, y + car_pos_y, car_pos_x, car_pos_y) 
                    for x, y in roof_vertices]
    roof_poly = plt.Polygon(roof_rotated, facecolor='#C0392B', edgecolor='#922B21', 
                           linewidth=2, zorder=6)
    ax.add_patch(roof_poly)
    
    # Ventanas
    window_vertices = [
        (-car_length/4 + 0.1, car_height/2 + 0.05),
        (car_length/4 - 0.1, car_height/2 + 0.05),
        (car_length/5 - 0.1, car_height/2 + car_roof_height - 0.1),
        (-car_length/5 + 0.1, car_height/2 + car_roof_height - 0.1)
    ]
    window_rotated = [rotate_point(x + car_pos_x, y + car_pos_y, car_pos_x, car_pos_y) 
                      for x, y in window_vertices]
    window_poly = plt.Polygon(window_rotated, facecolor='#AED6F1', edgecolor='#5DADE2', 
                             linewidth=1.5, zorder=7, alpha=0.7)
    ax.add_patch(window_poly)
    
    # Ruedas realistas
    wheel_radius = 0.25
    wheel_y_offset = -car_height/2 - wheel_radius * 0.3
    
    # Rueda trasera
    wheel1_x, wheel1_y = rotate_point(car_pos_x - car_length/3, car_pos_y + wheel_y_offset, 
                                      car_pos_x, car_pos_y)
    wheel1_outer = plt.Circle((wheel1_x, wheel1_y), wheel_radius, color='#2C3E50', zorder=8)
    wheel1_inner = plt.Circle((wheel1_x, wheel1_y), wheel_radius * 0.5, color='#34495E', zorder=9)
    wheel1_center = plt.Circle((wheel1_x, wheel1_y), wheel_radius * 0.2, color='#95A5A6', zorder=10)
    ax.add_patch(wheel1_outer)
    ax.add_patch(wheel1_inner)
    ax.add_patch(wheel1_center)
    
    # Rueda delantera
    wheel2_x, wheel2_y = rotate_point(car_pos_x + car_length/3, car_pos_y + wheel_y_offset, 
                                      car_pos_x, car_pos_y)
    wheel2_outer = plt.Circle((wheel2_x, wheel2_y), wheel_radius, color='#2C3E50', zorder=8)
    wheel2_inner = plt.Circle((wheel2_x, wheel2_y), wheel_radius * 0.5, color='#34495E', zorder=9)
    wheel2_center = plt.Circle((wheel2_x, wheel2_y), wheel_radius * 0.2, color='#95A5A6', zorder=10)
    ax.add_patch(wheel2_outer)
    ax.add_patch(wheel2_inner)
    ax.add_patch(wheel2_center)
    
    # Faros delanteros
    headlight_x, headlight_y = rotate_point(car_pos_x + car_length/2 - 0.1, 
                                           car_pos_y - car_height/4, 
                                           car_pos_x, car_pos_y)
    headlight = plt.Circle((headlight_x, headlight_y), 0.12, color='#F4D03F', 
                          edgecolor='#F39C12', linewidth=1.5, zorder=7)
    ax.add_patch(headlight)
    
    # Escala para las flechas de fuerza
    max_force = max(abs(F_pend), abs(F_roz), 100)
    scale = 2.5 / max_force
    
    # Vector de dirección paralela a la pendiente
    para_x = math.cos(angle_rad)
    para_y = math.sin(angle_rad)
    
    # Punto de inicio de las flechas (centro superior del auto)
    arrow_start_x = car_pos_x
    arrow_start_y = car_pos_y + car_height/2 + car_roof_height/2
    
    # Dibujar fuerza gravitacional (componente pendiente)
    if abs(F_pend) > 0.1:
        arrow_length = abs(F_pend) * scale
        if grade_percent > 0:  # subida
            ax.arrow(arrow_start_x, arrow_start_y, 
                    -para_x * arrow_length, -para_y * arrow_length,
                    head_width=0.35, head_length=0.25, fc='#E74C3C', ec='#C0392B', 
                    linewidth=3, zorder=11, alpha=0.9,
                    label=f'F_gravedad = {F_pend:.0f} N')
        else:  # bajada
            ax.arrow(arrow_start_x, arrow_start_y, 
                    para_x * arrow_length, para_y * arrow_length,
                    head_width=0.35, head_length=0.25, fc='#E74C3C', ec='#C0392B', 
                    linewidth=3, zorder=11, alpha=0.9,
                    label=f'F_gravedad = {F_pend:.0f} N')
    
    # Dibujar fuerza de rozamiento
    if abs(F_roz) > 0.1:
        arrow_length = abs(F_roz) * scale
        offset_y = 0.4
        ax.arrow(arrow_start_x, arrow_start_y + offset_y, 
                -para_x * arrow_length * 0.8, -para_y * arrow_length * 0.8,
                head_width=0.3, head_length=0.2, fc='#E67E22', ec='#D35400', 
                linewidth=3, zorder=11, alpha=0.9,
                label=f'F_rozamiento = {F_roz:.0f} N')
    
    # Dibujar velocidad (flecha verde al frente del auto)
    velocity_length = 2.0
    vel_start_x, vel_start_y = rotate_point(car_pos_x + car_length/2, car_pos_y, 
                                            car_pos_x, car_pos_y)
    ax.arrow(vel_start_x, vel_start_y, 
            para_x * velocity_length, para_y * velocity_length,
            head_width=0.35, head_length=0.3, fc='#27AE60', ec='#1E8449', 
            linewidth=3.5, zorder=11, alpha=0.9,
            label=f'Velocidad = {v_kmh} km/h')
    
    # Indicador de pendiente con arco
    if abs(grade_percent) > 0.1:
        arc_radius = 1.5
        arc = plt.Circle((0, 0), arc_radius, fill=False, edgecolor='gray', 
                        linewidth=1.5, linestyle='--', alpha=0.5, zorder=1)
        ax.add_patch(arc)
        
        # Texto del ángulo
        text_angle_x = arc_radius * 0.7 * math.cos(angle_rad/2)
        text_angle_y = arc_radius * 0.7 * math.sin(angle_rad/2)
        ax.text(text_angle_x, text_angle_y, f'{angle_deg:.1f}°', 
               fontsize=11, fontweight='bold', color='#555',
               bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8))
    
    # Información de la pendiente
    info_text = f'Pendiente: {grade_percent}% ({angle_deg:.1f}°)\nFuerza Total: {F_tot:.0f} N'
    ax.text(0.5, -1.8, info_text, 
            fontsize=12, fontweight='bold', 
            bbox=dict(boxstyle='round,pad=0.5', facecolor='#FFF9C4', 
                     edgecolor='#F57F17', linewidth=2, alpha=0.9),
            verticalalignment='top')
    
    # Configurar ejes
    ax.set_xlim(-1, 13)
    ax.set_ylim(-2.5, max(7, y_road_center[-1] + 2))
    ax.set_aspect('equal')
    ax.grid(True, alpha=0.2, linestyle=':', color='gray')
    ax.legend(loc='upper right', fontsize=10, framealpha=0.9)
    ax.set_xlabel('Distancia horizontal (m)', fontsize=11, fontweight='bold')
    ax.set_ylabel('Altura (m)', fontsize=11, fontweight='bold')
    ax.set_title('🚗 Análisis de Fuerzas sobre el Vehículo Eléctrico', 
                fontsize=15, fontweight='bold', pad=15)
    
    # Quitar bordes superiores y derecho para apariencia más limpia
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    
    plt.tight_layout()
    return fig

def draw_energy_consumption_journey(grade_percent, m_kg, v_kmh, L_km, eta, Crr, E_bat_kwh):
    """Dibuja la simulación del vehículo subiendo la pendiente con consumo energético"""
    fig = plt.figure(figsize=(20, 15))
    gs = fig.add_gridspec(3, 2, height_ratios=[3, 1.2, 0.8], hspace=0.6, wspace=0.5)
    
    # Panel principal: Trayectoria completa
    ax_main = fig.add_subplot(gs[0, :])
    
    # Calcular ángulo
    angle_rad = math.atan(grade_percent / 100.0)
    angle_deg = math.degrees(angle_rad)
    
    # Distancia total en metros
    L_total = L_km * 1000
    
    # Fondo mejorado con gradiente
    ax_main.fill_between([0, L_total * 1.15], [L_total * 0.15, L_total * 0.15], [L_total * 0.4, L_total * 0.4], 
                         color='#E3F2FD', alpha=0.6, zorder=0)
    ax_main.fill_between([0, L_total * 1.15], [-80, -80], [L_total * 0.15, L_total * 0.15], 
                         color='#D7CCC8', alpha=0.4, zorder=0)
    
    # Dibujar carretera más ancha y visible
    road_width = 70
    x_road = [0, L_total * math.cos(angle_rad)]
    y_road = [0, L_total * math.sin(angle_rad)]
    
    perp_x = -math.sin(angle_rad) * road_width / 2
    perp_y = math.cos(angle_rad) * road_width / 2
    
    road_vertices = [
        [0 - perp_x, 0 - perp_y],
        [x_road[1] - perp_x, y_road[1] - perp_y],
        [x_road[1] + perp_x, y_road[1] + perp_y],
        [0 + perp_x, 0 + perp_y]
    ]
    
    # Sombra de la carretera
    shadow_offset = 15
    shadow_vertices = [[v[0] - shadow_offset, v[1] - shadow_offset] for v in road_vertices]
    shadow_poly = plt.Polygon(shadow_vertices, facecolor='#424242', alpha=0.15, zorder=1)
    ax_main.add_patch(shadow_poly)
    
    # Carretera principal
    road_poly = plt.Polygon(road_vertices, facecolor='#37474F', edgecolor='#263238', 
                           linewidth=3, zorder=2)
    ax_main.add_patch(road_poly)
    
    # Bordes blancos de carretera
    border_width = 4
    for side in [-1, 1]:
        border_x = [perp_x * side, x_road[1] + perp_x * side]
        border_y = [perp_y * side, y_road[1] + perp_y * side]
        ax_main.plot(border_x, border_y, 'white', linewidth=border_width, zorder=3, alpha=0.8)
    
    # Líneas centrales amarillas más gruesas y visibles
    num_dashes = max(12, int(L_km * 2.5))
    for i in range(num_dashes):
        if i % 2 == 0:
            t1 = i / num_dashes
            t2 = (i + 0.55) / num_dashes
            x_dash = [t1 * x_road[1], t2 * x_road[1]]
            y_dash = [t1 * y_road[1], t2 * y_road[1]]
            ax_main.plot(x_dash, y_dash, color='#FDD835', linewidth=5, zorder=3, solid_capstyle='round')
    
    # Posiciones del vehículo (5 puntos)
    positions = [0, 0.25, 0.5, 0.75, 1.0]
    energies = []
    heights = []
    
    # Colores progresivos para los autos (de azul a rojo = frío a caliente = inicio a final)
    car_colors = ['#42A5F5', '#66BB6A', '#FFA726', '#FF7043', '#EF5350']
    
    cos_a = math.cos(angle_rad)
    sin_a = math.sin(angle_rad)
    
    for i, t in enumerate(positions):
        # Posición del auto
        car_x = t * x_road[1]
        car_y = t * y_road[1]
        
        # Calcular energía consumida hasta este punto
        distance_km = t * L_km
        seg_out = ev_segment(m_kg, v_kmh, grade_percent, distance_km, 
                            eta, Crr, 0.0)
        energy_kwh = seg_out["E_tramo_kWh"]
        energies.append(energy_kwh)
        heights.append(car_y)
        
        # Auto más grande y visible
        car_size = min(120, L_total * 0.055)
        
        # Cuerpo del auto con color progresivo
        car_length = car_size
        car_height = car_size * 0.5
        car_roof = car_size * 0.3
        
        def rotate_point(x, y, cx, cy, angle):
            x_rot = math.cos(angle) * (x - cx) - math.sin(angle) * (y - cy) + cx
            y_rot = math.sin(angle) * (x - cx) + math.cos(angle) * (y - cy) + cy
            return x_rot, y_rot
        
        # Sombra del auto
        shadow_vertices = [
            (-car_length/2 - 10, -car_height/2 - 15),
            (car_length/2 - 10, -car_height/2 - 15),
            (car_length/2 - 10, car_height/2 - 15),
            (-car_length/2 - 10, car_height/2 - 15)
        ]
        shadow_rotated = [rotate_point(x + car_x, y + car_y, car_x, car_y, angle_rad) 
                         for x, y in shadow_vertices]
        shadow_poly = plt.Polygon(shadow_rotated, facecolor='black', alpha=0.15, zorder=4)
        ax_main.add_patch(shadow_poly)
        
        # Carrocería principal
        body_vertices = [
            (-car_length/2, -car_height/2),
            (car_length/2, -car_height/2),
            (car_length/2, car_height/2),
            (-car_length/2, car_height/2)
        ]
        body_rotated = [rotate_point(x + car_x, y + car_y, car_x, car_y, angle_rad) 
                       for x, y in body_vertices]
        
        body_poly = plt.Polygon(body_rotated, facecolor=car_colors[i], 
                               edgecolor='#263238', linewidth=3, zorder=5)
        ax_main.add_patch(body_poly)
        
        # Techo
        roof_vertices = [
            (-car_length/3.5, car_height/2),
            (car_length/3.5, car_height/2),
            (car_length/4, car_height/2 + car_roof),
            (-car_length/4, car_height/2 + car_roof)
        ]
        roof_rotated = [rotate_point(x + car_x, y + car_y, car_x, car_y, angle_rad) 
                       for x, y in roof_vertices]
        roof_poly = plt.Polygon(roof_rotated, 
                               facecolor=car_colors[i], 
                               edgecolor='#263238', linewidth=2.5, zorder=6,
                               alpha=0.9)
        ax_main.add_patch(roof_poly)
        
        # Ventanas
        window_vertices = [
            (-car_length/4.5, car_height/2 + car_roof * 0.15),
            (car_length/4.5, car_height/2 + car_roof * 0.15),
            (car_length/5, car_height/2 + car_roof * 0.85),
            (-car_length/5, car_height/2 + car_roof * 0.85)
        ]
        window_rotated = [rotate_point(x + car_x, y + car_y, car_x, car_y, angle_rad) 
                         for x, y in window_vertices]
        window_poly = plt.Polygon(window_rotated, facecolor='#B3E5FC', 
                                 edgecolor='#0277BD', linewidth=2, zorder=7, alpha=0.7)
        ax_main.add_patch(window_poly)
        
        # Ruedas más grandes y detalladas
        wheel_r = car_size * 0.15
        wheel_offset = car_height/2 + wheel_r * 0.4
        
        for wheel_pos in [-car_length/3, car_length/3]:
            w_x, w_y = rotate_point(car_x + wheel_pos, car_y - wheel_offset, 
                                    car_x, car_y, angle_rad)
            
            # Rueda exterior
            wheel = plt.Circle((w_x, w_y), wheel_r, color='#212121', zorder=8, linewidth=2, edgecolor='#000')
            ax_main.add_patch(wheel)
            # Llanta
            rim = plt.Circle((w_x, w_y), wheel_r * 0.6, color='#424242', zorder=9)
            ax_main.add_patch(rim)
            # Centro
            center = plt.Circle((w_x, w_y), wheel_r * 0.25, color='#9E9E9E', zorder=10)
            ax_main.add_patch(center)
        
        # Faros delanteros brillantes
        if t == 1.0:  # Solo el auto final tiene faros encendidos
            headlight_x, headlight_y = rotate_point(car_x + car_length/2 - 8, 
                                                   car_y - car_height/3.5, 
                                                   car_x, car_y, angle_rad)
            headlight = plt.Circle((headlight_x, headlight_y), wheel_r * 0.5, 
                                  color='#FFF59D', edgecolor='#F57F17', 
                                  linewidth=2, zorder=7)
            ax_main.add_patch(headlight)
        
        # Etiquetas mejoradas con mejor distribución vertical
        if t > 0:
            # Alternar posición vertical para evitar solapamiento
            if i == 1:
                label_y_offset = 180
            elif i == 2:
                label_y_offset = 240
            elif i == 3:
                label_y_offset = 180
            else:  # i == 4
                label_y_offset = 140
            
            label_text = f'  {int(t*100)}%  \n {energy_kwh:.2f} kWh \n ↑ {car_y:.0f} m  '
            
            # Línea de conexión más visible
            ax_main.plot([car_x, car_x], [car_y + car_height/2 + car_roof, car_y + label_y_offset - 25],
                        'k--', linewidth=1.5, alpha=0.5, zorder=4)
            
            ax_main.annotate(label_text,
                           xy=(car_x, car_y + car_height/2 + car_roof), 
                           xytext=(car_x, car_y + label_y_offset),
                           fontsize=11, fontweight='bold',
                           bbox=dict(boxstyle='round,pad=0.7', 
                                   facecolor='white',
                                   edgecolor=car_colors[i], 
                                   linewidth=3,
                                   alpha=0.95),
                           ha='center', va='center',
                           zorder=12)
    
    # Línea punteada en la base para referencia
    ax_main.plot([0, L_total * 1.1], [0, 0], 'brown', linewidth=2, 
                linestyle=':', alpha=0.4, zorder=1, label='Nivel del suelo')
    
    ax_main.set_xlim(-L_total * 0.08, L_total * 1.12)
    ax_main.set_ylim(-120, max(y_road[1] * 1.4, 280))
    ax_main.set_aspect('equal')
    ax_main.grid(True, alpha=0.15, linestyle=':', color='gray', linewidth=0.8)
    ax_main.set_xlabel('Distancia horizontal (m)', fontsize=14, fontweight='bold', color='#424242')
    ax_main.set_ylabel('Altura (m)', fontsize=14, fontweight='bold', color='#424242')
    ax_main.set_title(f'🚗 Simulación: Vehículo ascendiendo pendiente de {grade_percent}% ({angle_deg:.1f}°) a {v_kmh} km/h',
                     fontsize=16, fontweight='bold', pad=20, color='#1565C0')
    ax_main.set_facecolor('#FAFAFA')
    
    # Panel inferior izquierdo: Energía vs Distancia
    ax_energy = fig.add_subplot(gs[1, 0])
    distances_plot = [t * L_km for t in positions]
    
    # Línea con marcadores más grandes
    ax_energy.plot(distances_plot, energies, 'o-', color='#D32F2F', linewidth=4, 
                  markersize=12, markeredgecolor='#B71C1C', markeredgewidth=2)
    ax_energy.fill_between(distances_plot, energies, alpha=0.25, color='#EF5350')
    
    ax_energy.set_xlabel('Distancia recorrida (km)', fontsize=13, fontweight='bold')
    ax_energy.set_ylabel('Energía consumida (kWh)', fontsize=13, fontweight='bold')
    ax_energy.set_title('📊 Consumo energético acumulado', fontsize=14, fontweight='bold', color='#D32F2F', pad=12)
    ax_energy.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax_energy.set_facecolor('#FFFEF7')
    
    # Línea de capacidad de batería
    ax_energy.axhline(E_bat_kwh, color='#2E7D32', linestyle='--', linewidth=3, 
                     label=f'Capacidad batería: {E_bat_kwh} kWh', alpha=0.8)
    ax_energy.legend(fontsize=11, loc='upper left', framealpha=0.95)
    
    # Panel inferior derecho: Altura vs Distancia
    ax_height = fig.add_subplot(gs[1, 1])
    ax_height.plot(distances_plot, heights, 's-', color='#1976D2', linewidth=4, 
                  markersize=12, markeredgecolor='#0D47A1', markeredgewidth=2)
    ax_height.fill_between(distances_plot, heights, alpha=0.25, color='#42A5F5')
    
    ax_height.set_xlabel('Distancia recorrida (km)', fontsize=13, fontweight='bold')
    ax_height.set_ylabel('Altura alcanzada (m)', fontsize=13, fontweight='bold')
    ax_height.set_title('📈 Elevación del trayecto', fontsize=14, fontweight='bold', color='#1976D2', pad=12)
    ax_height.grid(True, alpha=0.3, linestyle='--', linewidth=1)
    ax_height.set_facecolor('#FFFEF7')
    
    # Panel resumen mejorado
    ax_summary = fig.add_subplot(gs[2, :])
    ax_summary.axis('off')
    
    total_energy = energies[-1]
    total_height = heights[-1]
    battery_used_pct = (total_energy / E_bat_kwh) * 100
    remaining_range = (E_bat_kwh - total_energy) / (total_energy / L_km) if total_energy > 0 else float('inf')
    potential_energy = m_kg * 9.81 * total_height / 3.6e6
    
    summary_text = f"""
    ╔══════════════════════════════════════════════════════════════════════════════════════════════════════════════╗
    ║                              📋  RESUMEN DEL ANÁLISIS DE CONSUMO ENERGÉTICO                                   ║
    ╠══════════════════════════════════════════════════════════════════════════════════════════════════════════════╣
    ║                                                                                                                  ║
    ║  🛣️  Distancia: {L_km:.2f} km     📐 Pendiente: {grade_percent}% ({angle_deg:.1f}°)     🚗 Velocidad: {v_kmh} km/h     ⬆️  Elevación: {total_height:.1f} m   ║
    ║                                                                                                                  ║
    ║  ⚡ Energía consumida: {total_energy:.2f} kWh     🔋 Batería usada: {battery_used_pct:.1f}%     📏 Autonomía restante: {remaining_range:.0f} km        ║
    ║                                                                                                                  ║
    ║  💡 Consumo específico: {(total_energy/L_km)*100:.1f} kWh/100km     🏔️  Energía potencial: {potential_energy:.2f} kWh ({potential_energy/total_energy*100:.1f}% del total)   ║
    ║                                                                                                                  ║
    ╚══════════════════════════════════════════════════════════════════════════════════════════════════════════════╝
    """
    
    ax_summary.text(0.5, 0.5, summary_text, 
                   transform=ax_summary.transAxes,
                   fontsize=12, 
                   verticalalignment='center',
                   horizontalalignment='center',
                   bbox=dict(boxstyle='round,pad=1.5', facecolor='#E8F5E9', 
                            edgecolor='#388E3C', linewidth=4, alpha=0.95),
                   family='monospace',
                   weight='bold')
    
    plt.suptitle('Análisis del Consumo Energético de un Vehículo Eléctrico al Ascender Pendientes',
                fontsize=18, fontweight='bold', y=0.99, color='#1A237E')
    
    fig.patch.set_facecolor('#FAFAFA')
    
    return fig

# -----------------------------
# UI Streamlit
# -----------------------------
st.set_page_config(page_title="Simulador EV en Pendientes (Mecánica Clásica)", layout="wide")
st.title("🚗⚡ Simulador: Autonomía de Autos Eléctricos en Pendientes (Mecánica Clásica)")

st.markdown("""
**Análisis del consumo energético de un vehículo eléctrico al ascender pendientes usando modelos de mecánica clásica.**
""")

# Sección teórica expandible
with st.expander("📚 Fundamento teórico y ayuda", expanded=False):
    st.markdown(r"""
    ### Fundamento de Mecánica Clásica
    
    Este simulador aplica principios fundamentales de **dinámica, trabajo, energía y potencia** para modelar el consumo energético
    de un vehículo eléctrico en diferentes condiciones de pendiente y velocidad.
    
    #### 1. Fuerzas sobre el vehículo
    
    **Componente gravitacional (pendiente):**
    $$F_{pend} = mg\sin\theta$$
    
    **Fuerza de rozamiento:**
    $$F_{roz} = C_{rr} \cdot mg\cos\theta$$
    
    **Fuerza total:**
    $$F_{total} = F_{pend} + F_{roz}$$
    
    #### 2. Trabajo y energía
    
    El trabajo realizado para recorrer una distancia $L$ es:
    $$W = F_{total} \cdot L$$
    
    Considerando la eficiencia del tren motriz $\eta$:
    $$E_{batería} = \frac{W}{\eta}$$
    
    #### 3. Potencia
    
    La potencia instantánea requerida es:
    $$P = F_{total} \cdot v$$
    
    #### 4. Regeneración en bajadas
    
    En descensos, se recupera parte de la energía potencial gravitacional:
    $$E_{regen} = \eta_{regen} \cdot mg\Delta h$$
    
    ---
    
    **Parámetros típicos:**
    - $m$: masa del vehículo (kg)
    - $\eta$: eficiencia del motor (0.85-0.95)
    - $C_{rr}$: coeficiente de rodadura (0.008-0.015)
    - $C_d$: coeficiente aerodinámico (0.25-0.35)
    - $A$: área frontal (2.0-2.5 m²)
    - $\rho$: densidad del aire (≈1.2 kg/m³)
    """)

# Casos de ejemplo predefinidos
with st.expander("🎯 Casos de ejemplo"):
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🏙️ Urbano (plano)"):
            st.session_state.example = "urbano"
    with col2:
        if st.button("⛰️ Montaña (6% subida)"):
            st.session_state.example = "montana"
    with col3:
        if st.button("🛣️ Autopista (plano)"):
            st.session_state.example = "autopista"

# Sidebar inputs
st.sidebar.header("🔧 Parámetros del vehículo")

# Aplicar casos de ejemplo si se seleccionaron
if 'example' in st.session_state:
    if st.session_state.example == "urbano":
        default_v, default_grade = 50, 0
    elif st.session_state.example == "montana":
        default_v, default_grade = 60, 6
    elif st.session_state.example == "autopista":
        default_v, default_grade = 110, 0
    st.session_state.pop('example')
else:
    default_v, default_grade = 70, 6

m_kg = st.sidebar.number_input("Masa total m (kg)", min_value=500.0, max_value=4000.0, value=1700.0, step=10.0,
                                 help="Incluye vehículo + pasajeros + carga")
E_bat_kwh = st.sidebar.number_input("Capacidad batería (kWh)", min_value=10.0, max_value=200.0, value=60.0, step=1.0,
                                      help="Capacidad útil de la batería")
eta = st.sidebar.slider("Eficiencia tren motriz η", min_value=0.70, max_value=0.98, value=0.90, step=0.01,
                        help="Eficiencia de motor eléctrico (típico: 0.85-0.95)")
Crr = st.sidebar.slider("Coef. rozamiento Crr", min_value=0.005, max_value=0.030, value=0.010, step=0.001,
                        help="Coeficiente de rozamiento entre neumáticos y superficie")

st.sidebar.header("🛣️ Tramo a simular")
L_km = st.sidebar.number_input("Distancia del tramo L (km)", min_value=0.1, max_value=50.0, value=2.0, step=0.1)
v_kmh = st.sidebar.slider("Velocidad v (km/h)", min_value=10, max_value=130, value=default_v, step=5)
grade_percent = st.sidebar.slider("Pendiente (%) (subida + / bajada -)", min_value=-15, max_value=15, value=default_grade, step=1)

st.sidebar.header("♻️ Regeneración (solo bajadas)")
regen_on = st.sidebar.checkbox("Aplicar regeneración en bajadas", value=True)
regen_eff = st.sidebar.slider("Eficiencia regen η_regen", min_value=0.0, max_value=0.8, value=0.6, step=0.05)
if not regen_on:
    regen_eff = 0.0

# Cálculo para el caso puntual
out = ev_segment(m_kg, v_kmh, grade_percent, L_km, eta, Crr, regen_eff)
kwh_per_km = out["E_tramo_kWh"] / L_km
kwh_per_100km = kwh_per_km * 100.0
range_km = (E_bat_kwh / kwh_per_km) if kwh_per_km > 0 else float("inf")

# Resultados principales
c1, c2, c3, c4 = st.columns(4)
c1.metric("Consumo (kWh/100 km)", f"{kwh_per_100km:.2f}")
c2.metric("Energía tramo (kWh)", f"{out['E_tramo_kWh']:.3f}")
c3.metric("Potencia desde batería (kW)", f"{out['P_bat_kW']:.2f}")
c4.metric("Autonomía estimada (km)", f"{range_km:.0f}")

st.divider()

# Interpretación automática de resultados
if kwh_per_100km > 25:
    st.warning(f"⚠️ Consumo alto ({kwh_per_100km:.1f} kWh/100km). La pendiente de {grade_percent}% y/o la velocidad de {v_kmh} km/h aumentan significativamente el consumo.")
elif kwh_per_100km < 10:
    st.success(f"✅ Consumo excelente ({kwh_per_100km:.1f} kWh/100km). Condiciones favorables para maximizar autonomía.")
else:
    st.info(f"ℹ️ Consumo normal ({kwh_per_100km:.1f} kWh/100km). Dentro del rango esperado para estas condiciones.")

st.divider()

# Simulación completa del recorrido
st.subheader("🎬 Simulación completa: Ascendiendo la pendiente")
st.markdown("""
Esta visualización muestra el vehículo en diferentes momentos del ascenso (0%, 25%, 50%, 75%, 100%),
con la **energía consumida acumulada** y la **altura alcanzada** en cada punto.
""")

fig_journey = draw_energy_consumption_journey(grade_percent, m_kg, v_kmh, L_km, eta, Crr, E_bat_kwh)
st.pyplot(fig_journey)

col_download_journey = st.columns([1, 2])
with col_download_journey[0]:
    st.download_button(
        label="📥 Descargar simulación completa (PNG)",
        data=fig_to_bytes(fig_journey),
        file_name=f"simulacion_completa_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )
with col_download_journey[1]:
    st.info("💡 Esta visualización es ideal para tu informe: muestra claramente el problema de consumo energético al ascender pendientes.")

st.divider()

# Visualización gráfica del vehículo en la pendiente
st.subheader("🎨 Diagrama de cuerpo libre: Análisis de fuerzas")
st.markdown("Visualización detallada de todas las fuerzas que actúan sobre el vehículo en un instante.")

fig_vehicle = draw_vehicle_on_slope(grade_percent, out['F_pend_N'], out['F_roz_N'], 
                                     out['F_tot_N'], v_kmh)
st.pyplot(fig_vehicle)

col_download_viz, col_explain_viz = st.columns([1, 2])
with col_download_viz:
    st.download_button(
        label="📥 Descargar visualización (PNG)",
        data=fig_to_bytes(fig_vehicle),
        file_name=f"visualizacion_vehiculo_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
        mime="image/png"
    )
with col_explain_viz:
    st.caption("🔴 Rojo: Fuerza gravitacional (componente en pendiente) | 🟠 Naranja: Fuerza de rozamiento |  Verde: Dirección de movimiento")

st.divider()

# Detalle de fuerzas/potencias
left, right = st.columns([1, 1])

with left:
    st.subheader("📌 Detalle de fuerzas")
    st.write(f"- **F_pend (N)** = {out['F_pend_N']:.1f}")
    st.write(f"- **F_rozamiento (N)** = {out['F_roz_N']:.1f}")
    st.write(f"- **F_total (N)** = {out['F_tot_N']:.1f}")
    if grade_percent < 0 and regen_on:
        st.write(f"- **E_regen (kWh)** ≈ {out['E_regen_kWh']:.3f} (modelo simple)")

with right:
    st.subheader("📌 Detalle de potencia")
    st.write(f"- **P_mec (kW)** = {out['P_mec_kW']:.2f}")
    st.write(f"- **P_bat (kW)** = {out['P_bat_kW']:.2f}")
    st.caption("P_bat = P_mec / η")

st.divider()

# Simulación: barrido y gráficos
st.subheader("📈 Simulación: barrido por pendiente y velocidad")

colA, colB = st.columns(2)
with colA:
    st.markdown("**Rango de pendientes (para gráfico)**")
    min_g = st.number_input("Pendiente mínima (%)", value=-10, step=1)
    max_g = st.number_input("Pendiente máxima (%)", value=12, step=1)
    step_g = st.number_input("Paso pendiente (%)", value=2, step=1, min_value=1)

with colB:
    st.markdown("**Rango de velocidades (para gráfico)**")
    v_min = st.number_input("Velocidad mínima (km/h)", value=30, step=5)
    v_max = st.number_input("Velocidad máxima (km/h)", value=110, step=5)
    v_step = st.number_input("Paso velocidad (km/h)", value=20, step=5, min_value=5)

grade_list = list(range(int(min_g), int(max_g) + 1, int(step_g)))
v_list = list(range(int(v_min), int(v_max) + 1, int(v_step)))

df = compute_sweep(m_kg, eta, Crr, regen_eff, L_km, v_list, grade_list)

st.dataframe(df, width='stretch')

# Botón de descarga de datos
csv_data = df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="📥 Descargar tabla de resultados (CSV)",
    data=csv_data,
    file_name=f"resultados_ev_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
    mime="text/csv",
    help="Descarga los datos en formato CSV para análisis posterior"
)

# Gráfico 1: Consumo vs pendiente para cada velocidad
fig1, ax1 = plt.subplots(figsize=(10, 6))
for v in v_list:
    d = df[df["Velocidad (km/h)"] == v].sort_values("Pendiente (%)")
    ax1.plot(d["Pendiente (%)"], d["Consumo (kWh/100km)"], marker="o", label=f"{v} km/h", linewidth=2)
ax1.set_xlabel("Pendiente (%)", fontsize=12)
ax1.set_ylabel("Consumo (kWh/100 km)", fontsize=12)
ax1.set_title("Consumo energético vs Pendiente (varias velocidades)", fontsize=14, fontweight='bold')
ax1.legend(fontsize=10)
ax1.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig1)

# Botón de descarga del gráfico 1
st.download_button(
    label="📥 Descargar Gráfico 1 (PNG)",
    data=fig_to_bytes(fig1),
    file_name=f"consumo_vs_pendiente_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
    mime="image/png"
)

# Gráfico 2: Consumo vs velocidad para una pendiente seleccionada
st.markdown("### Consumo vs velocidad (pendiente fija)")
grade_for_vplot = st.selectbox("Elige la pendiente (%) para este gráfico", grade_list, index=min(len(grade_list)-1, 0))

d2 = df[df["Pendiente (%)"] == grade_for_vplot].sort_values("Velocidad (km/h)")

fig2, ax2 = plt.subplots(figsize=(10, 6))
ax2.plot(d2["Velocidad (km/h)"], d2["Consumo (kWh/100km)"], marker="o", linewidth=2, markersize=8, color='#FF6B6B')
ax2.set_xlabel("Velocidad (km/h)", fontsize=12)
ax2.set_ylabel("Consumo (kWh/100 km)", fontsize=12)
ax2.set_title(f"Consumo energético vs Velocidad (pendiente = {grade_for_vplot}%)", fontsize=14, fontweight='bold')
ax2.grid(True, alpha=0.3)
plt.tight_layout()
st.pyplot(fig2)

# Botón de descarga del gráfico 2
st.download_button(
    label="📥 Descargar Gráfico 2 (PNG)",
    data=fig_to_bytes(fig2),
    file_name=f"consumo_vs_velocidad_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.png",
    mime="image/png"
)

st.divider()

# Conclusiones y observaciones
st.subheader("📝 Conclusiones y observaciones")

col_a, col_b = st.columns(2)

with col_a:
    st.markdown("""
    **Relación con la teoría:**
    - Las pendientes positivas incrementan significativamente el consumo por la componente $mg\sin\theta$
    - La fuerza de rozamiento es proporcional a la normal: $F_{roz} = C_{rr} \cdot mg\cos\theta$
    - La regeneración en bajadas puede recuperar hasta 60-70% de la energía potencial
    - El trabajo realizado contra las fuerzas es $W = F_{total} \cdot d$
    """)

with col_b:
    st.markdown("""
    **Aplicaciones prácticas:**
    - Planificación de rutas para maximizar autonomía
    - Estimación de tiempos de carga necesarios
    - Análisis de viabilidad de vehículos eléctricos en zonas montañosas
    - Optimización de velocidad para eficiencia energética
    """)

st.info(
    "💡 **Tip académico:** Este simulador demuestra la aplicación práctica de conceptos fundamentales de mecánica clásica "
    "(dinámica, trabajo, energía y potencia) en problemas de ingeniería moderna."
)

# Footer
st.divider()
st.caption("🔬 Simulador de Consumo Energético de Vehículos Eléctricos | Curso de Mecánica Clásica | 2026")