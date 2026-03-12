import re
import numpy as np
import yaml

# Constants
Boltzmann_constant = 1.380649e-23 #[J/K]
diameter_molecular = 4.0e-10 # [m] （N2: 3.7e-10, O2: 3.5e-10, Air: 3.7e-10, CO2: 4.0e-10 程度らしい）

def load_config(yaml_file):
    with open(yaml_file, "r") as f:
        config = yaml.safe_load(f)
    return config

def calc_specific_heats(species_list, R_list, dof_dict):
    """自由度に基づいて比熱を計算する関数"""
    cp_list = []
    cv_list = []
    
    for sp, R in zip(species_list, R_list):
        f = dof_dict[sp]  # 自由度
        cv = 0.5 * f * R
        cp = cv + R
        cv_list.append(cv)
        cp_list.append(cp)
    
    return cp_list, cv_list

# Convert mass fractions to mole fractions.
def mass_to_mole_fraction(mass_fractions, molar_masses):
    """
    Convert mass fractions to mole fractions.
    Parameters
    ----------
    mass_fractions : list[float]
        Y_i (must sum approximately to 1)
    molar_masses : list[float]
        M_i [kg/mol]
    Returns
    -------
    list[float]
        mole fractions X_i
    """

    if len(mass_fractions) != len(molar_masses):
        raise ValueError("mass_fractions and molar_masses must have same length")

    # Σ(Y_i / M_i)
    denom = sum(Y / M for Y, M in zip(mass_fractions, molar_masses))

    if denom == 0.0:
        raise ValueError("Invalid input: denominator becomes zero.")

    mole_fractions = [(Y / M) / denom for Y, M in zip(mass_fractions, molar_masses)]

    return mole_fractions

# Mass fraction
def mole_to_mass_fraction(molar_mass_list, molefraction_list, species_list):
    # 平均分子量
    M_mix = sum(x * M for x, M in zip(molefraction_list, molar_mass_list))
    # 各成分の質量分率
    massfractions = [x * M / M_mix for x, M in zip(molefraction_list, molar_mass_list)]    
    # リスト形式
    massfractions_list = massfractions
    # 辞書形式
    massfractions_dict = {name: w for name, w in zip(species_list, massfractions)}    
    return M_mix, massfractions_list, massfractions_dict

# Mixture gas properties
def compute_mixture_properties(species_list, mole_frac_list, molar_mass_list, dof_dict, R_universal):
    # 比気体定数（各成分） [J/kg.K]
    R_spec_list = [R_universal / M for M in molar_mass_list]

    # 各成分の cv, cp（単位 J/kg.K）: cv = f/2 * R_spec, cp = cv + R_spec
    cv_list = [0.5 * dof_dict[sp] * R for sp, R in zip(species_list, R_spec_list)]
    cp_list = [cv + R for cv, R in zip(cv_list, R_spec_list)]

    # モル分率 -> 質量分率
    # 平均モル質量（kg/mol）
    M_mix = sum(x * M for x, M in zip(mole_frac_list, molar_mass_list))
    mass_frac_list = [x * M / M_mix for x, M in zip(mole_frac_list, molar_mass_list)]

    # 混合気体（質量基準） cp, cv（質量分率で重み付け）
    cp_mix_mass = sum(w * cp for w, cp in zip(mass_frac_list, cp_list))
    cv_mix_mass = sum(w * cv for w, cv in zip(mass_frac_list, cv_list))
    gamma_mix_mass = cp_mix_mass / cv_mix_mass

    # 混合比気体定数（質量基準）
    R_mix_mass = cp_mix_mass - cv_mix_mass  # R = cp - cv
    # または R_mix_mass = sum(w_i * R_i) でも同じ

    # モル基準（J/mol.K）での各成分と混合
    # cp_i (J/mol.K) = cp_i (J/kg.K) * M_i (kg/mol)
    cp_molar_list = [cp * M for cp, M in zip(cp_list, molar_mass_list)]
    cv_molar_list = [cv * M for cv, M in zip(cv_list, molar_mass_list)]
    cp_mix_molar = sum(x * cpm for x, cpm in zip(mole_frac_list, cp_molar_list))
    cv_mix_molar = sum(x * cvm for x, cvm in zip(mole_frac_list, cv_molar_list))
    gamma_mix_molar = cp_mix_molar / cv_mix_molar

    # 返却
    return {
        "R_spec_list": R_spec_list,
        "cp_list_J_per_kgK": cp_list,
        "cv_list_J_per_kgK": cv_list,
        "mass_fraction_list": mass_frac_list,
        "cp_mix_mass_J_per_kgK": cp_mix_mass,
        "cv_mix_mass_J_per_kgK": cv_mix_mass,
        "gamma_mix_mass": gamma_mix_mass,
        "R_mix_mass": R_mix_mass,
        "cp_molar_list_J_per_molK": cp_molar_list,
        "cv_molar_list_J_per_molK": cv_molar_list,
        "cp_mix_molar_J_per_molK": cp_mix_molar,
        "cv_mix_molar_J_per_molK": cv_mix_molar,
        "gamma_mix_molar": gamma_mix_molar,
        "M_mix_kg_per_mol": M_mix
    }

def viscosity_sutherland(T, mu0=1.37e-5, T0=293.0, S=240.0):
    mu = mu0 * (T/T0)**1.5 * (T0+S)/(T+S)
    return mu

# Knudsen number
def calculate_knudsen_number( length, temperature, pressure ):
    lamb = Boltzmann_constant*temperature/(np.sqrt(2.0)*np.pi*diameter_molecular**2 * pressure)
    kn = lamb/length
    return kn

# Trajectory data 
def read_simulation_file(filepath):
    variables = []
    data = []

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            # 変数名の取得
            if line.startswith("variables="):
                variables = [v.strip() for v in line.replace("variables=", "").split(",")]
                # 最初の "step" もカラムに含める
                #variables = ["step"] + variables
            elif line.lower().startswith("zone"):
                continue
            elif line:
                # データ部分（空白区切り）
                values = re.split(r"\s+", line)
                # 数値に変換
                values = [float(v) for v in values]
                data.append(values)

    # 結果を {列名: データのリスト} にまとめる
    print('Variables of the data:', variables)
    columns = {var: [] for var in variables}
    for row in data:
        for var, val in zip(variables, row):
            columns[var].append(val)

    return columns

def write_tecplot(filename, header, time, altitude, density, temperature, velocity, mach, reynolds, knudsen, heatflux, fmt=".6e"):
    """Tecplot ASCII 出力"""
    with open(filename, "w") as f:
        # ヘッダー
        f.write(header+'\n')
        for t, a, rho, temp, v, m, r, kn, h in zip(time, altitude, density, temperature, velocity, mach, reynolds, knudsen, heatflux):
            f.write(f"{t:{fmt}} {a:{fmt}} {rho:{fmt}} {temp:{fmt}} {v:{fmt}} {m:{fmt}} {r:{fmt}} {kn:{fmt}} {h:{fmt}}\n")


def main():


    # YAML 読み込み
    config = load_config("compute_thermodynamics_property.yaml")

    gas_constant_universal = config["gas_constant_universal"]

    # Species
    species_name_list = [sp["name"] for sp in config["species"]]
    molar_mass_list   = [sp["molar_mass"] for sp in config["species"]]
    degrees_of_freedom = {sp["name"]: sp["dof"] for sp in config["species"]}
    #molefraction_list = [sp["mole_fraction"] for sp in config["species"]]
    # --- fraction の自動判定 ---
    if "mole_fraction" in config["species"][0]:
        fraction_type = "mole_fraction"
    elif "mass_fraction" in config["species"][0]:
        fraction_type = "mass_fraction"
    else:
        raise ValueError("Neither mole_fraction nor mass_fraction is defined in YAML.")
    fraction_list = [sp[fraction_type] for sp in config["species"]]

    if fraction_type == "mole_fraction":
        molefraction_list = fraction_list
    elif fraction_type == "mass_fraction":
        massfraction_list = fraction_list
        molefraction_list = mass_to_mole_fraction(massfraction_list,molar_mass_list)

    # Sutherland
    mu0 = config["sutherland_constant"]["mu0"]
    T0  = config["sutherland_constant"]["T0"]
    S   = config["sutherland_constant"]["S"]

    # Gas properties
    gas_constant_list = [gas_constant_universal / M for M in molar_mass_list]

    specific_heat_press_list, specific_heat_volum_list = calc_specific_heats(
        species_name_list, gas_constant_list, degrees_of_freedom
    )
    #for sp, cp, cv in zip(species_name_list, specific_heat_press_list, specific_heat_volum_list):
    #    print(f"{sp}: cp={cp:.2f} J/kg.K, cv={cv:.2f} J/kg.K")

    # Mixture gas
    M_mix, massfractions_list, massfractions_dict = mole_to_mass_fraction( molar_mass_list, molefraction_list, species_name_list )

    # 実行例
    res = compute_mixture_properties(species_name_list,
                                    molefraction_list,
                                    molar_mass_list,
                                    degrees_of_freedom,
                                    gas_constant_universal)

    # 表示
    print("各成分の比気体定数 R_i [J/kg.K]:")
    for sp, R in zip(species_name_list, res["R_spec_list"]):
        print(f"  {sp}: {R:.2f}")

    print("\n各成分の cp, cv [J/kg.K]:")
    for sp, cp, cv in zip(species_name_list, res["cp_list_J_per_kgK"], res["cv_list_J_per_kgK"]):
        print(f"  {sp}: cp={cp:.2f}, cv={cv:.2f}")

    print("\n質量分率 (mass fractions):")
    for sp, w in zip(species_name_list, res["mass_fraction_list"]):
        print(f"  {sp}: {w:.6f}")
    print(f"  (sum) = {sum(res['mass_fraction_list']):.12f}")

    print("\n混合気体（質量基準）:")
    print(f"  cp_mix = {res['cp_mix_mass_J_per_kgK']:.6f} J/kg.K")
    print(f"  cv_mix = {res['cv_mix_mass_J_per_kgK']:.6f} J/kg.K")
    print(f"  gamma  = {res['gamma_mix_mass']:.6f}")

    print("\n混合気体（モル基準）:")
    print(f"  cp_mix = {res['cp_mix_molar_J_per_molK']:.6f} J/mol.K")
    print(f"  cv_mix = {res['cv_mix_molar_J_per_molK']:.6f} J/mol.K")
    print(f"  gamma  = {res['gamma_mix_molar']:.6f}")

    print(f"\n混合気体の比気体定数 R_mix = {res['R_mix_mass']:.6f} J/kg.K")

    print("\n混合気体の分子質量 M_mix [Kg/mole]:")
    print(f"  {M_mix:.6f}")

    gamma_mixture = res['gamma_mix_mass']
    gas_constant_mixture = res['R_mix_mass']


    # Read trajectory data
    #file_path = config['filename_trajectory']
    #data = read_simulation_file(file_path)

    #step = data['step']
    #time = data['time[s]']
    #altitude = data['altitude[km]']
    #vel_long = data['vel_long[m/s]']
    #velo_lat = data['velo_lati[m/s]']
    #velo_alt = data['velo_alt[m/s]']
    velocity = config["velocity"]
    density  = config["density"]
    temperature = config["temperature"]

    #num_step = len(step)

    #nose_radius = 500.e-3 # meter
    #lenght_character = 1000.e-3

    # Geometry
    nose_radius = config["geometry"]["nose_radius"]
    length_character = config["geometry"]["length_character"]

    # Flow property profile along altitude
    #time_out        = []
    #altitude_out    = []
    #density_out     = []
    #temperature_out = []
    #velocity_out    = []
    #mach_out        = []
    #reynolds_out    = []
    #knudsen_out     = []
    #heatflux_out    = []

    #for n in range(0, num_step):
    # Speed of sound
    speed_of_sound = np.sqrt( gamma_mixture * gas_constant_mixture * temperature)
    # Mach number
    machnumber = velocity/speed_of_sound
    # Heating rate (Tauber)
    heatflux_stag = 1.35e-7 * (density/nose_radius)**0.5 * velocity**3.04
    # Viscosity
    #print(temperature,density)
    mu = viscosity_sutherland(temperature, mu0, T0, S)
    # Reynolds number
    reynolds_number = density*velocity*length_character/mu
    # Knudsen number
    pressure = density*gas_constant_mixture * temperature
    knudsen_number = calculate_knudsen_number(length_character, temperature, pressure)

    #print(velocity, machnumber, heatflux_stag, reynolds_number)

    print("\nFlow field:")
    print(f"  Velocity        = {velocity:.6f} m/2")
    print(f"  Density         = {density:.6e} kg/m^3")
    print(f"  Temperature     = {temperature:.6f} K")
    print(f"  Pressure        = {pressure:.6f} Pa")
    print(f"  Viscosity       = {mu:.6e} Pa.s")
    print(f"  Mach number     = {machnumber:.6f}")
    print(f"  Reynolds number = {reynolds_number:.6e}")
    print(f"  Knudsen number  = {knudsen_number:.6f}")

        ## 結果を保存
        #time_out.append(time[n])
        #altitude_out.append(altitude[n])
        #density_out.append(density[n])
        #temperature_out.append(temperature[n])
        #velocity_out.append(velocity[n])
        #mach_out.append(machnumber)
        #reynolds_out.append(reynolds_number)
        #knudsen_out.append(knudsen_number)
        #heatflux_out.append(heatflux_stag)

    # ndarray に変換したい場合
    #time_out        = np.array(time_out)
    #altitude_out    = np.array(altitude_out)
    #density_out     = np.array(density_out)
    #temperature_out = np.array(temperature_out)
    #velocity_out    = np.array(velocity_out)
    #mach_out        = np.array(mach_out)
    #reynolds_out    = np.array(reynolds_out)
    #knudsen_out    = np.array(knudsen_out)
    #heatflux_out    = np.array(heatflux_out)

    # Tecplot形式でまとめて出力
    #filename_output = config['filename_tecplot_output']
    #fmt_output = config['format_tecplot_output']
    #header_output = config['header_tecplot_output']
    #write_tecplot(filename_output, header_output, time_out, altitude_out, density_out, temperature_out, velocity_out, mach_out, reynolds_out, knudsen_out, heatflux_out, fmt=fmt_output)

            # ファイル出力
    #        f.write(f"{time[n]:.6e} {altitude[n]:.6e} {velocity[n]:.6e} {density[n]:.6e} {temperature[n]:.6e} {machnumber:.6e} {reynolds_number:.6e} {heatflux_stag:.6e}\n")
    
    #print(f"[INFO] Tecplot format file written: {filename_output}")

  
if __name__ == '__main__':
    main()