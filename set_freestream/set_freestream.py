#!/usr/bin/env python3

# Script to calculate isentropic relations
# Author: Y.Takahashi, Hokkaido University
# Date; 2023/11/15

import numpy as np

def read_config_yaml(file_control):
  import yaml as yaml
  import sys as sys

  print("Reading control file...:", file_control)

  try:
    with open(file_control) as file:
      config = yaml.safe_load(file)
      print(config)
  except Exception as e:
    print('Exception occurred while loading YAML...', file=sys.stderr)
    print(e, file=sys.stderr)
    sys.exit(1)

  return config


def isentropic_relation(gamma, mach):
  
  # To calculate pressure, density velocity, and temperature ratios between stagnation and certain point
  # from Mach number based on isentropic relations

  # T/T0, p/p0, rho/rho0

  var_tmp = (1.0+(gamma-1.0)/2.0*mach**2)
  tempeature_ratio = var_tmp**(-1.0)
  pressure_ratio   = var_tmp**(-gamma/(gamma-1.0))
  density_ratio    = var_tmp**(-1.0/(gamma-1.0))

  return tempeature_ratio, pressure_ratio, density_ratio 


if __name__ == '__main__':

  # Read and set controlfile
  file_control="set_freestream.yml"
  config = read_config_yaml(file_control)

  # Set parameters
  gamma            = config['gas_properties']['gamma']
  gas_const        = config['gas_properties']['gas_const']
  #gas_const_univ   = config['gas_properties']['gas_const_univ']
  #molecular_weight = config['gas_properties']['molecular_weight']
  #gas_const = gas_const_univ/molecular_weight

  mach_number      = config['freestream']['mach_number']
  temperature_stag = config['freestream']['temperature']
  pressure_stag    = config['freestream']['pressure_dyn']

  # Density at stagnation 
  density_stag = pressure_stag/(gas_const*temperature_stag)

  # Isentropic relation
  tempeature_ratio, pressure_ratio, density_ratio = isentropic_relation(gamma, mach_number)

  # Freestream valuies
  temperature = tempeature_ratio*temperature_stag
  pressure    = pressure_ratio*pressure_stag
  density     = density_ratio*density_stag

  # Speed of sound
  speed_of_sound = np.sqrt(gamma*gas_const*temperature)

  # Local velocity
  velocity = speed_of_sound*mach_number

  # Density (from dynamic pressure)
  #density = 2.0*pressure_dyn/(velocity**2)

  # Static pressure
  #pressure = density*gas_const*temperature

  # Viscosity
  kind_visc = config['viscosity']['kind_visc']
  if kind_visc == 'constant' :
    viscosity = config['viscosity']['mu_const']
  elif kind_visc == 'sutherland' :
    mu0    = config['viscosity']['mu0_sut']
    t0_sut = config['viscosity']['t0_sut']
    c_sut  = config['viscosity']['c_sut']
    viscosity = mu0*( (temperature/t0_sut)**1.5 ) * ( (t0_sut+c_sut)/(temperature+c_sut) )
  else :
    viscosity = config['viscosity']['mu_const']

  length_ref = config['references']['length_ref']

  # Reynolds number
  reynolds_number = density*velocity*length_ref/viscosity


  # Output
  print( 'Stagnation paraneters')
  print( 'Temperature at stagnation,K (given) :', temperature_stag  )
  print( 'Pressure at stagnation, Pa (given)  :', pressure_stag )
  print( 'Density at stagnation, kg/m3        :', density_stag)

  print( 'Freestream paraneters')
  print( 'Temperature, K :', temperature )
  print( 'pressure, Pa   :', pressure )
  print( 'Density, kg/m3 :', density  )
  print( 'Velocity, m/s  :', velocity )
  print( 'Viscosity, Pa.s :', viscosity ) 
  print( 'Mach number (given)   :', mach_number  )
  print( 'Reynold num.   :', reynolds_number )

