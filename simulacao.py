import pandas as pd
import re
from rocketpy import Environment, SolidMotor, Rocket, Flight

# 1. CURVA DE ARRASTO DO RASAERO II (.CSV) COM TRATAMENTO DE VÍRGULA DECIMAL

df = pd.read_csv("arrasto_rasaero.csv")
df_zero = df[df["Alpha"] == 0].sort_values("Mach")
cd_off = list(zip(df_zero["Mach"], df_zero["CD Power-Off"]))
cd_on = list(zip(df_zero["Mach"], df_zero["CD Power-On"]))


# 2. AMBIENTE: IREC 2026 - MIDLAND, TEXAS (.NC)

env = Environment(
    latitude=31.9425,
    longitude=-102.2019,
    elevation=875.4,
)
env.set_date((2026, 6, 18, 15))  
env.set_atmospheric_model(
    type="Reanalysis",
    file="irec_2026_midland.nc",
    dictionary="ECMWF",
)


# 3. MOTOR: AEROTECH M685W-P (75 mm)

motor = SolidMotor(
    thrust_source="AeroTech_M685W.eng",  
    dry_mass=2.765,
    dry_inertia=(0.133, 0.133, 0.0019),
    nozzle_radius=0.025,
    grain_number=5,
    grain_density=1750,
    grain_outer_radius=0.0345,
    grain_initial_inner_radius=0.0115,
    grain_initial_height=0.140,
    grain_separation=0.003,
    grains_center_of_mass_position=0.38,
    center_of_dry_mass_position=0.38,
    nozzle_position=0,
    throat_radius=0.011,
    coordinate_system_orientation="nozzle_to_combustion_chamber",
)


# 4. FOGUETE 

foguete = Rocket(
    radius=0.06,                        # Diâmetro máximo 12 cm -> raio 0,06 m
    mass=14.9411,                       # Massa sem motor: 14941,1 g
    inertia=(5.79, 5.79, 0.029),        # Inércia sem motor (Iyy, Izz, Ixx) em kg*m²
    power_off_drag=cd_off,              # Curva do RASAero II
    power_on_drag=cd_on,                # Curva do RASAero II
    center_of_mass_without_motor=1.6319,# CG sem motor: 163,19 cm
    coordinate_system_orientation="nose_to_tail",
)

# Motor na base do foguete (comprimento total = 2,55 m)
foguete.add_motor(motor, position=2.55)

# Ogiva tangente (0.55 m)
foguete.add_nose(length=0.55, kind="tangent", position=0)

# Conjunto de 4 aletas trapezoidais 
foguete.add_trapezoidal_fins(
    n=4,
    root_chord=0.26,   # Corda da raiz (m)
    tip_chord=0.12,    # Corda da ponta (m)
    span=0.12,         # Envergadura / altura da aleta (m)
    position=2.29,     # Posição do início da raiz a partir da ponta da ogiva (m)
)

# Paraquedas (Drogue no apogeu e Principal a 450 m do solo)
foguete.add_parachute(
    name="Drogue",
    cd_s=0.9,
    trigger="apogee",
    sampling_rate=105,
    lag=1.5,
)
foguete.add_parachute(
    name="Main",
    cd_s=8.5,
    trigger=450,
    sampling_rate=105,
    lag=1.5,
)


# 5. SIMULAÇÃO DE VOO E GRÁFICOS

voo = Flight(
    rocket=foguete,
    environment=env,
    rail_length=5.2,
    inclination=85,
    heading=90,
)

voo.info()
voo.plots.trajectory_3d()
voo.all_info()