#include "constants.h"
#include "physics.h"
#include <fstream>
#include <iostream>

using namespace std;

int main()
{
    MissionParameters p;

    p.mars_phase = 2.79733;
    p.launch_dv_factor = 1.03633;
    p.launch_normal_factor = -0.0751667;

    MissionResult r = simulate_mission(p, true);

    ofstream summary("results/summary.txt");

    summary << "Mars Mission Simulator - Mission Summary" << endl;
    summary << endl;

    summary << "transfer type = Starship-like Earth to Mars transfer" << endl;
    summary << "integration method = RK4" << endl;
    summary << "gravity sources = Sun, Earth, Mars" << endl;
    summary << "orbit model = 3D elliptical Kepler orbits" << endl;
    summary << "burn model = patched-conic Earth departure with mass loss" << endl;
    summary << "Mars arrival model = atmospheric entry interface" << endl;
    summary << endl;

    summary << "initial spacecraft mass = " << r.initial_mass << " kg" << endl;
    summary << "final spacecraft mass = " << r.final_mass << " kg" << endl;
    summary << "fuel used = " << r.fuel_used << " kg" << endl;
    summary << "initial available delta-v = " << r.initial_available_delta_v << " m/s" << endl;
    summary << endl;

    summary << "Mars phase = " << p.mars_phase << " rad" << endl;
    summary << "launch delta-v factor = " << p.launch_dv_factor << endl;
    summary << "launch normal factor = " << p.launch_normal_factor << endl;
    summary << endl;

    summary << "launch burn model = patched-conic departure" << endl;
    summary << "launch burn duration = simplified as impulsive escape burn" << endl;
    summary << "Mars capture burn duration = disabled" << endl;
    summary << "Mars entry altitude target = " << mars_entry_altitude / 1000.0 << " km" << endl;
    summary << "Mars entry radius target = " << mars_entry_radius / 1000.0 << " km from Mars center" << endl;
    summary << "Mars entry speed target = " << mars_entry_speed_target / 1000.0 << " km/s" << endl;
    summary << endl;

    summary << "launch delta-v estimate = " << r.launch_dv_estimate << " m/s" << endl;
    summary << "launch delta-v applied = " << r.launch_dv_applied << " m/s" << endl;
    summary << "Mars propulsive capture burn = disabled" << endl;
    summary << "Mars approach correction delta-v = " << r.capture_dv_applied << " m/s" << endl;
    summary << "total propulsive delta-v applied = " << r.launch_dv_applied + r.capture_dv_applied << " m/s" << endl;
    summary << endl;

    summary << "approximate Hohmann transfer time = " << r.hohmann_time / day << " days" << endl;
    summary << "closest Mars approach = " << r.closest_mars / 1000.0 << " km from Mars center" << endl;
    summary << "entry radius error = " << (r.closest_mars - mars_entry_radius) / 1000.0 << " km" << endl;
    summary << "time of closest Mars approach = " << r.closest_mars_time / day << " days" << endl;
    summary << "Mars relative speed at closest approach = " << r.mars_relative_speed << " m/s" << endl;
    summary << "Mars relative speed error = " << (r.mars_relative_speed - mars_entry_speed_target) / 1000.0 << " km/s" << endl;
    summary << "maximum Sun distance = " << r.max_sun_distance / 1000.0 << " km" << endl;
    summary << endl;

    if (r.captured) {
        summary << "entry interface time = " << r.capture_time / day << " days" << endl;
        summary << "entry interface distance = " << r.capture_distance / 1000.0 << " km from Mars center" << endl;
        summary << "Mars encounter status = reached atmospheric entry interface" << endl;
    } else {
        summary << "entry interface time = not reached" << endl;
        summary << "entry interface distance = not reached" << endl;
        summary << "Mars encounter status = missed atmospheric entry interface" << endl;
    }

    summary << endl;
    summary << "Starship-style interpretation:" << endl;
    summary << "The simulation does not model a propulsive Mars orbit insertion." << endl;
    summary << "Instead, the trajectory is evaluated as a direct Mars atmospheric arrival." << endl;
    summary << "At Mars, Starship-like deceleration would mainly be aerodynamic, with engines used later for the final landing phase." << endl;

    summary.close();

    cout << "Simulation finished." << endl;
    cout << "Summary saved to results/summary.txt" << endl;
    cout << "Trajectory saved to results/trajectory.txt" << endl;
    cout << "3D trajectory saved to results/trajectory3d.txt" << endl;
    cout << "Telemetry saved to results/telemetry.txt" << endl;

    return 0;
}