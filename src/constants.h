#pragma once
#include <cmath>

const double pi = 3.141592653589793;
const double deg = pi / 180.0;

const double G = 6.67430e-11;
const double day = 24.0 * 3600.0;
const double au = 1.495978707e11;

const double msun = 1.9885e30;
const double mearth = 5.9722e24;
const double mmars = 6.4171e23;

const double rearth = 6371000.0;
const double rmars = 3389500.0;

const double earth_a = 1.00000011 * au;
const double earth_e = 0.01671022;
const double earth_i = 0.00005 * deg;
const double earth_Omega = -11.26064 * deg;
const double earth_varpi = 102.94719 * deg;
const double earth_omega_arg = earth_varpi - earth_Omega;
const double earth_L0 = 100.46435 * deg;
const double earth_M0 = earth_L0 - earth_varpi;

const double mars_a = 1.52366231 * au;
const double mars_e = 0.09341233;
const double mars_i = 1.85061 * deg;
const double mars_Omega = 49.57854 * deg;
const double mars_varpi = 336.04084 * deg;
const double mars_omega_arg = mars_varpi - mars_Omega;
const double mars_L0 = 355.45332 * deg;
const double mars_M0 = mars_L0 - mars_varpi;

const double earth_period = 365.25 * day;
const double mars_period = 686.98 * day;

const double g0 = 9.80665;

const double starship_initial_mass = 1420000.0;
const double starship_dry_mass = 220000.0;
const double starship_exhaust_velocity = 380.0 * g0;

const double launch_burn_time = 1800.0;

const double mars_entry_altitude = 125000.0;
const double mars_entry_radius = rmars + mars_entry_altitude;
const double mars_entry_speed_target = 7500.0;

const double mars_atmosphere_height = 125000.0;
const double mars_scale_height = 11100.0;
const double mars_surface_density = 0.020;

const double starship_drag_coefficient = 2.7;
const double starship_drag_area = 3400.0;

const double mars_landing_burn_altitude = 30000.0;
const double mars_landing_burn_acceleration = 80.0;
const double mars_touchdown_speed_limit = 40.0;

const double mars_correction_distance = 3000000.0 * 1000.0;
const double mars_correction_max_dv = 500.0;