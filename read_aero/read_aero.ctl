#---File names---
./          # Input data directory
history_00102.dat               # Input data file
./results_aero   # Result directory name
tecplot_aero              # Output file name
#---CFD information-
1.e-4                     # time step, s
0                         # Start step of free oscillation
16                        # Mass, kg
6.07e-4                   # Moment of inertia, kg.m2
#---Freestream condition----
342.8                     # Freestream velocity, m/s
1.013                     # Freestream density, kg/m3
241.3                     # Freestream temperature, K
#---Viscosity(Sutherland)---
1.716e-5      # mu0
273.15        # T0
110.4         # C
#---Gas properties---
1.4           # gamma
8.3144598     # Gas constant
28.8e-3       # Molecular weight of air
#---Reference---
0.1           # Characteristic length, m
0.00785398163 # Characteristic area m^2
#---Data process-
0                         # Reference AoA, deg.
#---Probe--------
false
../hayabusa_m1.1/probe     # Input data directory (probe)
8                         # Number of probe file
probe_output_0006.dat     # Input data file
probe_output_0007.dat 
probe_output_0008.dat 
probe_output_0009.dat
probe_output_0010.dat
probe_output_0011.dat
probe_output_0012.dat 
probe_output_0013.dat 
