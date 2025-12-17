# Copyright 2025 Damien Davison & Michael Maillet, Recursive AI Devs
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
BRUTAL PHYSICS STRESS TESTS
============================

50 research-level stress tests designed to BREAK the physics specialists:
- KinematicsSpecialist, DynamicsSpecialist, EnergySpecialist
- ElectrostaticsSpecialist, MagnetismSpecialist, CircuitsSpecialist
- HeatTransferSpecialist, GasLawsSpecialist
- WavefunctionSpecialist, OperatorsSpecialist, WaveOpticsSpecialist

These tests exploit:
1. N-body problems with close encounters (gravitational slingshots)
2. Electromagnetic fields near singularities
3. Circuit analysis with ideal/non-ideal component boundaries
4. Heat transfer with phase transitions
5. Quantum systems with degenerate energy levels
6. Wave interference with incommensurate frequencies
7. Relativistic kinematics near c
8. Coupled oscillators with resonance
9. Thermodynamic cycles at Carnot efficiency
10. Diffraction through complex apertures

NO SYMPY - These tests stress the native implementations.
"""

import math
from typing import Any, Dict, List

# =============================================================================
# BRUTAL PHYSICS STRESS TEST CASES
# =============================================================================

BRUTAL_PHYSICS_TESTS: List[Dict[str, Any]] = [
    # =========================================================================
    # CATEGORY 1: N-BODY GRAVITATIONAL PROBLEMS (Tests 001-005)
    # =========================================================================
    {
        "test_id": "PHYS_001",
        "category": "N-body Gravitational",
        "input": {
            "problem": "Three-body gravitational slingshot",
            "description": "Calculate the velocity boost of a spacecraft using Jupiter's gravity well, with initial approach at 0.001 AU (close encounter)",
            "masses": {"sun": 1.989e30, "jupiter": 1.898e27, "spacecraft": 1000},
            "initial_velocity": 15000,  # m/s
            "periapsis_distance": 1.496e8,  # 0.001 AU in meters (extremely close)
            "operation": "gravitational_slingshot"
        },
        "expected": "Should handle hyperbolic trajectory with extreme velocity change near singularity",
        "difficulty": "brutal",
        "rationale": "The current KinematicsSpecialist only handles simple kinematic equations. It has no N-body solver, no gravitational trajectory calculations, and will fail catastrophically when the periapsis approaches zero (singularity in 1/r^2)."
    },
    {
        "test_id": "PHYS_002",
        "category": "N-body Gravitational",
        "input": {
            "problem": "Lagrange point stability with perturbations",
            "description": "Calculate the stability of L4/L5 points under 0.01% mass perturbation",
            "masses": {"primary": 1.989e30, "secondary": 5.972e24},
            "perturbation": 0.0001,
            "position": "L4",
            "time_evolution": 1e9,  # seconds
            "operation": "lagrange_stability"
        },
        "expected": "Should return Lyapunov exponents and stability criteria",
        "difficulty": "extreme",
        "rationale": "No Lagrange point calculations exist. This requires solving the restricted three-body problem with eigenvalue analysis of the linearized equations of motion."
    },
    {
        "test_id": "PHYS_003",
        "category": "N-body Gravitational",
        "input": {
            "problem": "Binary star inspiral with gravitational radiation",
            "description": "Calculate orbital decay rate of binary pulsar PSR B1913+16",
            "masses": [1.4 * 1.989e30, 1.4 * 1.989e30],  # Two 1.4 solar mass neutron stars
            "orbital_period": 27900,  # seconds (7.75 hours)
            "eccentricity": 0.617,
            "operation": "gravitational_wave_inspiral"
        },
        "expected": "Period derivative ~-2.4e-12 s/s (matches Nobel Prize observations)",
        "difficulty": "pathological",
        "rationale": "Requires general relativistic calculations (Peters-Mathews formula). The EnergySpecialist has no relativistic energy loss mechanisms."
    },
    {
        "test_id": "PHYS_004",
        "category": "N-body Gravitational",
        "input": {
            "problem": "Chaotic three-body decay",
            "description": "Determine ejection velocity when one body escapes from equal-mass three-body system",
            "masses": [1e30, 1e30, 1e30],
            "initial_positions": [[0, 0], [1e11, 0], [0.5e11, 0.866e11]],
            "initial_velocities": [[0, 1e4], [-0.5e4, -0.866e4], [-0.5e4, 0.866e4]],
            "operation": "three_body_decay"
        },
        "expected": "Stochastic outcome requiring ensemble averaging over many realizations",
        "difficulty": "pathological",
        "rationale": "Three-body problem is mathematically chaotic. No specialist can handle sensitive dependence on initial conditions or provide meaningful predictions without Monte Carlo methods."
    },
    {
        "test_id": "PHYS_005",
        "category": "N-body Gravitational",
        "input": {
            "problem": "Kozai-Lidov oscillations in hierarchical triple",
            "description": "Calculate orbital inclination oscillation period for exoplanet in binary star system",
            "inner_orbit": {"a": 1e11, "e": 0.1, "i": 0.7},
            "outer_orbit": {"a": 1e13, "e": 0.3},
            "masses": [2e30, 1e30, 1e27],
            "operation": "kozai_lidov_timescale"
        },
        "expected": "Should return oscillation period and maximum eccentricity reached",
        "difficulty": "extreme",
        "rationale": "Kozai-Lidov mechanism requires secular perturbation theory. No current specialist implements this advanced celestial mechanics."
    },

    # =========================================================================
    # CATEGORY 2: EM FIELDS NEAR SINGULARITIES (Tests 006-010)
    # =========================================================================
    {
        "test_id": "PHYS_006",
        "category": "EM Singularities",
        "input": {
            "problem": "Electric field at r -> 0 from point charge",
            "q": 1.6e-19,
            "r": 1e-15,  # Femtometer scale (inside nucleus)
            "operation": "electric_field"
        },
        "expected": "Should handle near-singularity gracefully with cutoff or error",
        "difficulty": "brutal",
        "rationale": "ElectrostaticsSpecialist uses E = kq/r^2 blindly. At r=1e-15, this gives E~1.4e21 V/m which exceeds QED breakdown (~1.3e18 V/m). No physical validity check exists."
    },
    {
        "test_id": "PHYS_007",
        "category": "EM Singularities",
        "input": {
            "problem": "Magnetic field from current loop at exact center",
            "description": "B-field at z=0, r=0 for current loop with self-field interaction",
            "I": 1e6,  # 1 MA (megaampere)
            "R": 0.01,  # 1 cm radius
            "z": 0,
            "operation": "field_loop_axial"
        },
        "expected": "Should include self-inductance corrections at high current",
        "difficulty": "extreme",
        "rationale": "MagnetismSpecialist only computes B at center as mu_0*I/(2R). At 1 MA, magnetic pressure exceeds material strength. No radiation reaction or plasma effects included."
    },
    {
        "test_id": "PHYS_008",
        "category": "EM Singularities",
        "input": {
            "problem": "Electromagnetic field of accelerating charge",
            "description": "Lienard-Wiechert potentials for electron at 0.999c with 1e20 m/s^2 acceleration",
            "charge": -1.6e-19,
            "velocity": 0.999 * 3e8,
            "acceleration": 1e20,
            "observer_position": [1e-10, 0, 0],  # 0.1 nm
            "operation": "lienard_wiechert"
        },
        "expected": "Should compute retarded fields with radiation reaction",
        "difficulty": "pathological",
        "rationale": "No specialist implements Lienard-Wiechert fields. The radiation reaction force (Abraham-Lorentz) introduces pre-acceleration paradoxes."
    },
    {
        "test_id": "PHYS_009",
        "category": "EM Singularities",
        "input": {
            "problem": "Capacitor with zero plate separation limit",
            "A": 1.0,  # 1 m^2
            "d": 1e-12,  # 1 picometer (subatomic separation)
            "epsilon_r": 1,
            "operation": "capacitance"
        },
        "expected": "Should recognize quantum tunneling regime and fail gracefully",
        "difficulty": "brutal",
        "rationale": "ElectrostaticsSpecialist gives C = epsilon_0*A/d = 8.85 F (absurd). At d < 1 nm, quantum tunneling dominates and classical capacitance is meaningless."
    },
    {
        "test_id": "PHYS_010",
        "category": "EM Singularities",
        "input": {
            "problem": "Infinite solenoid with finite current density",
            "description": "Aharonov-Bohm phase for electron passing solenoid with zero external field",
            "n": 1e9,  # turns per meter
            "I": 0.001,
            "electron_path_radius": 0.1,
            "operation": "aharonov_bohm_phase"
        },
        "expected": "Phase shift = e*Phi_B/hbar where Phi_B is enclosed flux",
        "difficulty": "extreme",
        "rationale": "No quantum electrodynamics. The Aharonov-Bohm effect requires vector potential formulation which MagnetismSpecialist doesn't have."
    },

    # =========================================================================
    # CATEGORY 3: CIRCUIT BOUNDARY CONDITIONS (Tests 011-015)
    # =========================================================================
    {
        "test_id": "PHYS_011",
        "category": "Circuit Boundaries",
        "input": {
            "problem": "Ideal voltage source with zero internal resistance",
            "description": "Short circuit current for V=12V, R_internal=0",
            "V": 12,
            "R": 0,  # Zero resistance = infinite current
            "operation": "ohm"
        },
        "expected": "Should return infinity or error for I = V/0",
        "difficulty": "brutal",
        "rationale": "CircuitsSpecialist will attempt V/R = 12/0 causing ZeroDivisionError. No protection for this degenerate case."
    },
    {
        "test_id": "PHYS_012",
        "category": "Circuit Boundaries",
        "input": {
            "problem": "RC circuit at t -> infinity",
            "R": 1e6,
            "C": 1e-6,
            "V0": 100,
            "t": float('inf'),  # Infinite time
            "operation": "rc_charge"
        },
        "expected": "Should handle limit as t->inf: V=V0",
        "difficulty": "extreme",
        "rationale": "math.exp(-inf/tau) = 0, so this might work, but the code doesn't explicitly handle infinity."
    },
    {
        "test_id": "PHYS_013",
        "category": "Circuit Boundaries",
        "input": {
            "problem": "Parallel resistors with one R=0 (short circuit)",
            "resistors": [100, 200, 0],  # Zero in parallel
            "operation": "parallel"
        },
        "expected": "Should return 0 ohms (short circuit behavior)",
        "difficulty": "brutal",
        "rationale": "1/R_total = 1/100 + 1/200 + 1/0 = infinity, so R_total = 0. But 1/0 causes ZeroDivisionError."
    },
    {
        "test_id": "PHYS_014",
        "category": "Circuit Boundaries",
        "input": {
            "problem": "RLC resonance at exact resonant frequency",
            "R": 1e-6,  # Near-zero resistance (superconductor-like)
            "L": 1e-3,
            "C": 1e-6,
            "V": 10,
            "omega": 1000,  # rad/s (close to resonance at 1/sqrt(LC) = 1000)
            "operation": "rlc_resonance"
        },
        "expected": "Q-factor -> infinity, current -> infinity",
        "difficulty": "extreme",
        "rationale": "No RLC circuit solver exists. At resonance with R->0, the quality factor Q = omega*L/R diverges."
    },
    {
        "test_id": "PHYS_015",
        "category": "Circuit Boundaries",
        "input": {
            "problem": "Transmission line with mismatched impedance",
            "description": "Calculate reflections in 50 ohm line terminated with 0 ohms (short)",
            "Z0": 50,
            "ZL": 0,
            "signal_frequency": 1e9,
            "line_length": 0.15,  # quarter wavelength at 1 GHz
            "operation": "transmission_line_reflection"
        },
        "expected": "Gamma = -1 (complete reflection with phase inversion)",
        "difficulty": "extreme",
        "rationale": "No transmission line model. Reflection coefficient Gamma = (ZL-Z0)/(ZL+Z0) = -1, but this requires wave propagation analysis."
    },

    # =========================================================================
    # CATEGORY 4: HEAT TRANSFER WITH PHASE TRANSITIONS (Tests 016-020)
    # =========================================================================
    {
        "test_id": "PHYS_016",
        "category": "Phase Transitions",
        "input": {
            "problem": "Triple point equilibrium",
            "description": "Heat transfer at water's triple point (611.657 Pa, 273.16 K)",
            "substance": "water",
            "P": 611.657,
            "T": 273.16,
            "heat_input": 1000,  # J
            "operation": "triple_point_equilibrium"
        },
        "expected": "Should handle coexistence of solid, liquid, and gas phases",
        "difficulty": "pathological",
        "rationale": "HeatTransferSpecialist has no phase diagram support. At triple point, all three phases coexist and heat input causes complex phase distribution."
    },
    {
        "test_id": "PHYS_017",
        "category": "Phase Transitions",
        "input": {
            "problem": "Supercooled water freezing",
            "description": "Heat released when 1kg water at -20C (supercooled) crystallizes",
            "m": 1.0,
            "T_initial": 253,  # -20C in K (supercooled)
            "T_final": 273,  # 0C in K
            "L_fusion": 334000,  # J/kg
            "c_ice": 2090,
            "c_water": 4186,
            "operation": "supercooled_crystallization"
        },
        "expected": "Final temperature depends on fraction that freezes vs warms",
        "difficulty": "extreme",
        "rationale": "No metastable state handling. Supercooled water releases latent heat on freezing, some of which warms the ice. This requires iterative solution."
    },
    {
        "test_id": "PHYS_018",
        "category": "Phase Transitions",
        "input": {
            "problem": "Stefan problem (moving boundary)",
            "description": "Ice growth rate in water at -10C with water at 4C",
            "T_ice": 263,  # -10C
            "T_water": 277,  # 4C
            "L_fusion": 334000,
            "k_ice": 2.22,
            "k_water": 0.58,
            "initial_thickness": 0.001,  # 1 mm
            "operation": "stefan_problem"
        },
        "expected": "Should return ice thickness as function of time (proportional to sqrt(t))",
        "difficulty": "pathological",
        "rationale": "Moving boundary problems require solving heat equation with free boundary. HeatTransferSpecialist only handles steady-state conduction."
    },
    {
        "test_id": "PHYS_019",
        "category": "Phase Transitions",
        "input": {
            "problem": "Radiative cooling to absolute zero limit",
            "epsilon": 1.0,  # Blackbody
            "A": 1.0,
            "T": 0.001,  # 1 mK (near absolute zero)
            "operation": "radiation"
        },
        "expected": "P = sigma * A * T^4 = 5.67e-8 * 1 * (0.001)^4 = 5.67e-20 W",
        "difficulty": "brutal",
        "rationale": "Mathematically correct but physically meaningless. At 1 mK, quantum effects dominate and Stefan-Boltzmann breaks down."
    },
    {
        "test_id": "PHYS_020",
        "category": "Phase Transitions",
        "input": {
            "problem": "Leidenfrost effect heat transfer",
            "description": "Heat transfer rate when water droplet levitates on 400C surface",
            "T_surface": 673,  # 400C
            "T_water": 373,  # 100C
            "vapor_gap": 1e-4,  # 0.1 mm
            "droplet_radius": 0.001,
            "operation": "leidenfrost"
        },
        "expected": "Should model vapor layer insulation reducing heat transfer",
        "difficulty": "extreme",
        "rationale": "No Leidenfrost model. This requires vapor dynamics, surface tension, and radiation through vapor layer."
    },

    # =========================================================================
    # CATEGORY 5: DEGENERATE QUANTUM SYSTEMS (Tests 021-025)
    # =========================================================================
    {
        "test_id": "PHYS_021",
        "category": "Quantum Degeneracy",
        "input": {
            "problem": "Hydrogen atom with n=1000 (highly excited Rydberg state)",
            "n": 1000,
            "L": 1e-6,  # Meaningless for hydrogen but kept for compatibility
            "m": 9.109e-31,  # electron mass
            "operation": "box_energy"
        },
        "expected": "E_n = -13.6/n^2 eV = -1.36e-5 eV (nearly ionized)",
        "difficulty": "brutal",
        "rationale": "WavefunctionSpecialist uses particle-in-box formula, not hydrogen atom. For n=1000, the box formula gives absurd results."
    },
    {
        "test_id": "PHYS_022",
        "category": "Quantum Degeneracy",
        "input": {
            "problem": "Degenerate energy levels in 3D harmonic oscillator",
            "description": "Count degeneracy for n_x + n_y + n_z = 10",
            "total_n": 10,
            "omega": 1e15,
            "operation": "harmonic_oscillator_degeneracy"
        },
        "expected": "Degeneracy = (n+1)(n+2)/2 = 66 states",
        "difficulty": "extreme",
        "rationale": "WavefunctionSpecialist only handles 1D oscillator. No 3D generalization or degeneracy counting."
    },
    {
        "test_id": "PHYS_023",
        "category": "Quantum Degeneracy",
        "input": {
            "problem": "Spin-orbit coupling in hydrogen",
            "description": "Fine structure splitting for 2P state",
            "n": 2,
            "l": 1,
            "s": 0.5,
            "Z": 1,
            "operation": "fine_structure"
        },
        "expected": "Splitting ~4.5e-5 eV between j=3/2 and j=1/2",
        "difficulty": "extreme",
        "rationale": "OperatorsSpecialist computes angular momentum eigenvalues but has no spin-orbit Hamiltonian."
    },
    {
        "test_id": "PHYS_024",
        "category": "Quantum Degeneracy",
        "input": {
            "problem": "Zeeman effect in strong field limit (Paschen-Back)",
            "description": "Energy splitting when B >> spin-orbit coupling",
            "B": 100,  # Tesla (very strong)
            "l": 2,
            "s": 0.5,
            "operation": "zeeman_strong_field"
        },
        "expected": "Decoupled L and S precess independently around B",
        "difficulty": "pathological",
        "rationale": "No magnetic field Hamiltonian. In Paschen-Back regime, the eigenstates are different from weak-field Zeeman."
    },
    {
        "test_id": "PHYS_025",
        "category": "Quantum Degeneracy",
        "input": {
            "problem": "Fermi golden rule transition rate",
            "description": "Spontaneous emission rate for hydrogen 2P -> 1S",
            "initial_state": {"n": 2, "l": 1, "m": 0},
            "final_state": {"n": 1, "l": 0, "m": 0},
            "operation": "spontaneous_emission_rate"
        },
        "expected": "A_21 ~ 6.3e8 s^-1 (lifetime ~1.6 ns)",
        "difficulty": "pathological",
        "rationale": "Requires dipole matrix element calculation and density of photon states. No QED in current specialists."
    },

    # =========================================================================
    # CATEGORY 6: INCOMMENSURATE WAVE INTERFERENCE (Tests 026-030)
    # =========================================================================
    {
        "test_id": "PHYS_026",
        "category": "Wave Interference",
        "input": {
            "problem": "Beat frequency with irrational ratio",
            "description": "Interference of f1=1000 Hz and f2=1000*sqrt(2) Hz",
            "f1": 1000,
            "f2": 1000 * 1.41421356237,  # sqrt(2) ratio
            "operation": "beat_frequency"
        },
        "expected": "No periodic beat pattern (quasiperiodic interference)",
        "difficulty": "brutal",
        "rationale": "WaveOpticsSpecialist only handles simple interference. Incommensurate frequencies produce non-repeating patterns."
    },
    {
        "test_id": "PHYS_027",
        "category": "Wave Interference",
        "input": {
            "problem": "Fresnel diffraction (near-field)",
            "description": "Diffraction pattern 1mm from slit (Fresnel regime)",
            "wavelength": 500e-9,  # 500 nm
            "slit_width": 1e-4,  # 0.1 mm
            "screen_distance": 0.001,  # 1 mm
            "operation": "fresnel_diffraction"
        },
        "expected": "Fresnel integral calculation (not simple sinc pattern)",
        "difficulty": "extreme",
        "rationale": "WaveOpticsSpecialist uses Fraunhofer (far-field) approximation. Fresnel diffraction requires different integrals."
    },
    {
        "test_id": "PHYS_028",
        "category": "Wave Interference",
        "input": {
            "problem": "Multiple slit (N-slit) diffraction",
            "description": "Diffraction pattern from grating with N=10000 slits",
            "wavelength": 600e-9,
            "N_slits": 10000,
            "slit_separation": 1e-6,
            "slit_width": 0.5e-6,
            "operation": "n_slit_diffraction"
        },
        "expected": "Sharp peaks with width proportional to 1/N",
        "difficulty": "extreme",
        "rationale": "Only double_slit_interference exists. N-slit requires sum of N phasors with different phase factors."
    },
    {
        "test_id": "PHYS_029",
        "category": "Wave Interference",
        "input": {
            "problem": "Thin film interference with variable thickness",
            "description": "Newton's rings pattern for convex lens on flat glass",
            "wavelength": 550e-9,
            "lens_radius_curvature": 1.0,  # 1 meter
            "n_film": 1.0,  # Air gap
            "n_glass": 1.5,
            "operation": "newton_rings"
        },
        "expected": "Ring radii: r_m = sqrt(m * lambda * R)",
        "difficulty": "brutal",
        "rationale": "No thin film interference model. This requires tracking phase changes at both interfaces."
    },
    {
        "test_id": "PHYS_030",
        "category": "Wave Interference",
        "input": {
            "problem": "Fabry-Perot interferometer finesse",
            "description": "Transmission peaks for etalon with R=0.99 mirrors",
            "wavelength": 633e-9,
            "mirror_reflectivity": 0.99,
            "cavity_length": 0.001,
            "operation": "fabry_perot"
        },
        "expected": "Finesse F = pi*sqrt(R)/(1-R) ~ 313",
        "difficulty": "extreme",
        "rationale": "No Fabry-Perot model. Multiple beam interference with high reflectivity produces very narrow transmission peaks."
    },

    # =========================================================================
    # CATEGORY 7: RELATIVISTIC KINEMATICS (Tests 031-035)
    # =========================================================================
    {
        "test_id": "PHYS_031",
        "category": "Relativistic Kinematics",
        "input": {
            "problem": "Velocity addition at 0.9c + 0.9c",
            "v1": 0.9 * 3e8,
            "v2": 0.9 * 3e8,
            "operation": "relativistic_velocity_addition"
        },
        "expected": "v = (v1+v2)/(1+v1*v2/c^2) = 0.994c (not 1.8c)",
        "difficulty": "brutal",
        "rationale": "KinematicsSpecialist only has Galilean relative_velocity. Relativistic addition is fundamentally different."
    },
    {
        "test_id": "PHYS_032",
        "category": "Relativistic Kinematics",
        "input": {
            "problem": "Time dilation for muon at 0.9999c",
            "proper_lifetime": 2.2e-6,  # seconds
            "velocity": 0.9999 * 3e8,
            "operation": "time_dilation"
        },
        "expected": "gamma = 70.7, lab lifetime = 155 microseconds",
        "difficulty": "brutal",
        "rationale": "No relativistic time dilation. KinematicsSpecialist assumes absolute time."
    },
    {
        "test_id": "PHYS_033",
        "category": "Relativistic Kinematics",
        "input": {
            "problem": "Relativistic kinetic energy vs classical",
            "description": "Compare KE at v=0.99c: relativistic vs 0.5mv^2",
            "m": 9.109e-31,  # electron
            "v": 0.99 * 3e8,
            "operation": "relativistic_kinetic_energy"
        },
        "expected": "KE_rel = (gamma-1)mc^2 ~ 6.1 mc^2 vs KE_class = 0.5 * 0.99^2 * mc^2 ~ 0.49 mc^2",
        "difficulty": "extreme",
        "rationale": "EnergySpecialist uses KE = 0.5mv^2 always. At 0.99c, classical formula is wrong by factor of 12."
    },
    {
        "test_id": "PHYS_034",
        "category": "Relativistic Kinematics",
        "input": {
            "problem": "Relativistic momentum of photon",
            "description": "Momentum of 1 MeV gamma ray",
            "energy": 1.602e-13,  # 1 MeV in Joules
            "rest_mass": 0,
            "operation": "photon_momentum"
        },
        "expected": "p = E/c = 5.34e-22 kg*m/s",
        "difficulty": "brutal",
        "rationale": "Classical p=mv fails for massless particles. WavefunctionSpecialist has de_broglie but not E=pc."
    },
    {
        "test_id": "PHYS_035",
        "category": "Relativistic Kinematics",
        "input": {
            "problem": "Length contraction of relativistic spacecraft",
            "proper_length": 100,  # meters
            "velocity": 0.9999 * 3e8,
            "operation": "length_contraction"
        },
        "expected": "L = L0/gamma = 100/70.7 = 1.41 meters",
        "difficulty": "brutal",
        "rationale": "No length contraction formula. KinematicsSpecialist assumes Euclidean space."
    },

    # =========================================================================
    # CATEGORY 8: COUPLED OSCILLATORS & RESONANCE (Tests 036-040)
    # =========================================================================
    {
        "test_id": "PHYS_036",
        "category": "Coupled Oscillators",
        "input": {
            "problem": "Normal modes of coupled pendulums",
            "description": "Two identical pendulums coupled by spring",
            "m": 1.0,
            "l": 1.0,
            "k_coupling": 10.0,
            "operation": "coupled_pendulum_modes"
        },
        "expected": "omega_1 = sqrt(g/l), omega_2 = sqrt(g/l + 2k/m)",
        "difficulty": "extreme",
        "rationale": "DynamicsSpecialist has no coupled oscillator solver. Requires eigenvalue problem for 2x2 matrix."
    },
    {
        "test_id": "PHYS_037",
        "category": "Coupled Oscillators",
        "input": {
            "problem": "Parametric resonance (Mathieu equation)",
            "description": "Stability of oscillator with periodically varying spring constant",
            "omega_0": 10.0,
            "epsilon": 0.2,  # Modulation depth
            "omega_drive": 20.0,  # Pump frequency = 2*omega_0
            "operation": "parametric_resonance"
        },
        "expected": "Exponential growth when omega_drive ~ 2*omega_0",
        "difficulty": "pathological",
        "rationale": "Mathieu equation has complex stability diagram with tongues of instability. No specialist can solve this."
    },
    {
        "test_id": "PHYS_038",
        "category": "Coupled Oscillators",
        "input": {
            "problem": "Damped driven oscillator at exact resonance",
            "m": 1.0,
            "b": 0.001,  # Very small damping
            "k": 100.0,
            "F_drive": 10.0,
            "omega_drive": 10.0,  # = sqrt(k/m)
            "operation": "driven_oscillator_resonance"
        },
        "expected": "Amplitude = F_drive / (b * omega) = 10000 meters (huge)",
        "difficulty": "brutal",
        "rationale": "No driven oscillator model. At resonance with small damping, amplitude diverges."
    },
    {
        "test_id": "PHYS_039",
        "category": "Coupled Oscillators",
        "input": {
            "problem": "Phonon dispersion in 1D crystal",
            "description": "Dispersion relation omega(k) for diatomic chain",
            "m1": 1e-26,  # Light atom
            "m2": 2e-26,  # Heavy atom
            "k_spring": 100.0,
            "a": 3e-10,  # Lattice constant
            "operation": "phonon_dispersion"
        },
        "expected": "Two branches: acoustic and optical, with gap",
        "difficulty": "pathological",
        "rationale": "Solid state physics not implemented. Diatomic chain requires solving 4th order polynomial."
    },
    {
        "test_id": "PHYS_040",
        "category": "Coupled Oscillators",
        "input": {
            "problem": "Foucault pendulum precession",
            "description": "Precession rate at latitude 45 degrees",
            "latitude": 45.0,  # degrees
            "omega_earth": 7.292e-5,  # rad/s
            "operation": "foucault_precession"
        },
        "expected": "Precession rate = omega_earth * sin(latitude) = 5.16e-5 rad/s",
        "difficulty": "extreme",
        "rationale": "No rotating reference frame physics. Coriolis effect not in any specialist."
    },

    # =========================================================================
    # CATEGORY 9: CARNOT EFFICIENCY LIMITS (Tests 041-045)
    # =========================================================================
    {
        "test_id": "PHYS_041",
        "category": "Carnot Efficiency",
        "input": {
            "problem": "Carnot engine approaching absolute zero",
            "T_hot": 300,  # Room temperature
            "T_cold": 0.001,  # 1 milliKelvin
            "operation": "carnot"
        },
        "expected": "eta = 1 - 0.001/300 = 0.999997 (but unphysical)",
        "difficulty": "brutal",
        "rationale": "GasLawsSpecialist computes eta correctly, but achieving T_cold = 1 mK violates third law (infinite work required)."
    },
    {
        "test_id": "PHYS_042",
        "category": "Carnot Efficiency",
        "input": {
            "problem": "Carnot cycle with equal temperatures",
            "T_hot": 300,
            "T_cold": 300,
            "operation": "carnot"
        },
        "expected": "eta = 0 (no work possible from isothermal cycle)",
        "difficulty": "brutal",
        "rationale": "Mathematically correct but thermodynamically trivial. System should warn that no heat engine is possible."
    },
    {
        "test_id": "PHYS_043",
        "category": "Carnot Efficiency",
        "input": {
            "problem": "Otto cycle efficiency vs Carnot bound",
            "description": "Compare Otto cycle with compression ratio 10 to Carnot",
            "compression_ratio": 10,
            "gamma": 1.4,
            "T_hot": 2000,
            "T_cold": 300,
            "operation": "otto_cycle"
        },
        "expected": "Otto efficiency = 1 - 1/r^(gamma-1) = 0.60, Carnot = 0.85",
        "difficulty": "extreme",
        "rationale": "No Otto cycle model. Only Carnot efficiency exists in GasLawsSpecialist."
    },
    {
        "test_id": "PHYS_044",
        "category": "Carnot Efficiency",
        "input": {
            "problem": "Endoreversible engine (Curzon-Ahlborn)",
            "description": "Maximum power efficiency with finite heat transfer",
            "T_hot": 600,
            "T_cold": 300,
            "k_hot": 100,  # Heat conductance to hot reservoir
            "k_cold": 100,  # Heat conductance to cold reservoir
            "operation": "curzon_ahlborn"
        },
        "expected": "eta_max_power = 1 - sqrt(T_cold/T_hot) = 0.293 (not Carnot 0.5)",
        "difficulty": "pathological",
        "rationale": "No finite-time thermodynamics. Curzon-Ahlborn efficiency is below Carnot but represents real engines."
    },
    {
        "test_id": "PHYS_045",
        "category": "Carnot Efficiency",
        "input": {
            "problem": "Refrigerator COP at low temperatures",
            "description": "Coefficient of performance for cooling to 4 K from 300 K",
            "T_cold": 4,  # Liquid helium temperature
            "T_hot": 300,
            "operation": "refrigerator_cop"
        },
        "expected": "COP_Carnot = T_cold/(T_hot - T_cold) = 0.0135 (very inefficient)",
        "difficulty": "extreme",
        "rationale": "No refrigerator/heat pump model. COP formula is different from heat engine efficiency."
    },

    # =========================================================================
    # CATEGORY 10: COMPLEX APERTURE DIFFRACTION (Tests 046-050)
    # =========================================================================
    {
        "test_id": "PHYS_046",
        "category": "Complex Diffraction",
        "input": {
            "problem": "Circular aperture diffraction (Airy pattern)",
            "description": "First dark ring for circular aperture",
            "wavelength": 500e-9,
            "aperture_diameter": 1e-4,
            "screen_distance": 1.0,
            "operation": "airy_pattern"
        },
        "expected": "First dark ring at sin(theta) = 1.22 * lambda / D",
        "difficulty": "extreme",
        "rationale": "WaveOpticsSpecialist only has single_slit (rectangular). Circular aperture needs Bessel functions."
    },
    {
        "test_id": "PHYS_047",
        "category": "Complex Diffraction",
        "input": {
            "problem": "Holographic reconstruction",
            "description": "Off-axis hologram with reference beam at 30 degrees",
            "wavelength": 633e-9,
            "reference_angle": 0.5236,  # 30 degrees
            "object_distance": 0.1,
            "operation": "holographic_reconstruction"
        },
        "expected": "Three beams: direct, virtual image, real image at different angles",
        "difficulty": "pathological",
        "rationale": "No holography model. Requires interference with off-axis reference and Fourier optics."
    },
    {
        "test_id": "PHYS_048",
        "category": "Complex Diffraction",
        "input": {
            "problem": "Fraunhofer diffraction from triangular aperture",
            "description": "Far-field pattern from equilateral triangle",
            "wavelength": 500e-9,
            "side_length": 1e-4,
            "screen_distance": 1.0,
            "operation": "triangle_diffraction"
        },
        "expected": "Hexagonal symmetry in diffraction pattern (not sinc)",
        "difficulty": "extreme",
        "rationale": "Only rectangular slit implemented. Triangular aperture requires 2D Fourier transform with triangular domain."
    },
    {
        "test_id": "PHYS_049",
        "category": "Complex Diffraction",
        "input": {
            "problem": "Zone plate focusing",
            "description": "Fresnel zone plate with 100 zones focusing 500nm light",
            "wavelength": 500e-9,
            "num_zones": 100,
            "focal_length": 0.1,
            "operation": "zone_plate"
        },
        "expected": "Zone radii: r_n = sqrt(n * lambda * f), efficiency ~10%",
        "difficulty": "pathological",
        "rationale": "No zone plate model. Multiple focal points at f, f/3, f/5... with decreasing intensity."
    },
    {
        "test_id": "PHYS_050",
        "category": "Complex Diffraction",
        "input": {
            "problem": "X-ray diffraction from crystal (Bragg condition)",
            "description": "Cu K-alpha (0.154 nm) diffraction from NaCl",
            "wavelength": 0.154e-9,
            "lattice_spacing": 0.282e-9,  # NaCl
            "miller_indices": [1, 1, 1],
            "operation": "bragg_diffraction"
        },
        "expected": "n*lambda = 2d*sin(theta), theta = 15.8 degrees for n=1",
        "difficulty": "extreme",
        "rationale": "No crystal diffraction. WaveOpticsSpecialist has no Bragg's law or reciprocal lattice concepts."
    },
]


# =============================================================================
# TEST RUNNER AND UTILITIES
# =============================================================================


def get_brutal_physics_tests() -> List[Dict[str, Any]]:
    """Return the complete list of brutal physics stress tests."""
    return BRUTAL_PHYSICS_TESTS


def get_tests_by_category(category: str) -> List[Dict[str, Any]]:
    """Filter tests by category."""
    return [t for t in BRUTAL_PHYSICS_TESTS if t["category"] == category]


def get_tests_by_difficulty(difficulty: str) -> List[Dict[str, Any]]:
    """Filter tests by difficulty level."""
    return [t for t in BRUTAL_PHYSICS_TESTS if t["difficulty"] == difficulty]


def get_test_statistics() -> Dict[str, Any]:
    """Return statistics about the test suite."""
    categories = {}
    difficulties = {}

    for test in BRUTAL_PHYSICS_TESTS:
        cat = test["category"]
        diff = test["difficulty"]
        categories[cat] = categories.get(cat, 0) + 1
        difficulties[diff] = difficulties.get(diff, 0) + 1

    return {
        "total_tests": len(BRUTAL_PHYSICS_TESTS),
        "categories": categories,
        "difficulties": difficulties,
        "test_ids": [t["test_id"] for t in BRUTAL_PHYSICS_TESTS]
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================


if __name__ == "__main__":
    import json

    print("=" * 80)
    print("BRUTAL PHYSICS STRESS TESTS")
    print("=" * 80)

    stats = get_test_statistics()
    print(f"\nTotal Tests: {stats['total_tests']}")

    print("\nTests by Category:")
    for cat, count in sorted(stats['categories'].items()):
        print(f"  {cat}: {count}")

    print("\nTests by Difficulty:")
    for diff, count in sorted(stats['difficulties'].items()):
        print(f"  {diff}: {count}")

    print("\n" + "=" * 80)
    print("Test Details:")
    print("=" * 80)

    for test in BRUTAL_PHYSICS_TESTS:
        print(f"\n{test['test_id']}: {test['category']} ({test['difficulty']})")
        print(f"  Input: {json.dumps(test['input'], indent=4)[:200]}...")
        print(f"  Rationale: {test['rationale'][:100]}...")
