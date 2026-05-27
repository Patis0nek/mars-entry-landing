#include "physics.h"
#include "constants.h"
#include <cmath>
#include <fstream>
#include <iomanip>

using namespace std;

double normalize_angle(double x)
{
    while (x < 0.0) {
        x += 2.0 * pi;
    }

    while (x >= 2.0 * pi) {
        x -= 2.0 * pi;
    }

    return x;
}

double solve_kepler(double M, double e)
{
    M = normalize_angle(M);

    double E = M;

    for (int i = 0; i < 20; i++) {
        double f = E - e * sin(E) - M;
        double df = 1.0 - e * cos(E);
        E = E - f / df;
    }

    return E;
}

Vector3 rotate_orbit(Vector3 r, double Omega, double inc, double omega)
{
    double cO = cos(Omega);
    double sO = sin(Omega);
    double ci = cos(inc);
    double si = sin(inc);
    double co = cos(omega);
    double so = sin(omega);

    double x1 = co * r.x - so * r.y;
    double y1 = so * r.x + co * r.y;
    double z1 = r.z;

    double x2 = x1;
    double y2 = ci * y1 - si * z1;
    double z2 = si * y1 + ci * z1;

    double x3 = cO * x2 - sO * y2;
    double y3 = sO * x2 + cO * y2;
    double z3 = z2;

    return Vector3(x3, y3, z3);
}

Vector3 orbit_position(double t, double a, double e, double inc, double Omega, double omega, double M0, double phase)
{
    double n = sqrt(G * msun / pow(a, 3.0));
    double M = M0 + n * t + phase;

    double E = solve_kepler(M, e);

    double x = a * (cos(E) - e);
    double y = a * sqrt(1.0 - e * e) * sin(E);

    return rotate_orbit(Vector3(x, y, 0.0), Omega, inc, omega);
}

Body earth_state(double t)
{
    Body earth;

    double h = 10.0;

    earth.r = orbit_position(t, earth_a, earth_e, earth_i, earth_Omega, earth_omega_arg, earth_M0, 0.0);

    Vector3 r2 = orbit_position(t + h, earth_a, earth_e, earth_i, earth_Omega, earth_omega_arg, earth_M0, 0.0);

    earth.v = (r2 - earth.r) / h;

    return earth;
}

Body mars_state(double t, double mars_phase)
{
    Body mars;

    double h = 10.0;

    mars.r = orbit_position(t, mars_a, mars_e, mars_i, mars_Omega, mars_omega_arg, mars_M0, mars_phase);

    Vector3 r2 = orbit_position(t + h, mars_a, mars_e, mars_i, mars_Omega, mars_omega_arg, mars_M0, mars_phase);

    mars.v = (r2 - mars.r) / h;

    return mars;
}

double consume_delta_v(Spacecraft& s, double dv)
{
    double possible_dv = available_delta_v(s);

    if (dv > possible_dv) {
        dv = possible_dv;
    }

    double m0 = s.mass;
    double mf = m0 * exp(-dv / s.exhaust_velocity);

    if (mf < s.dry_mass) {
        mf = s.dry_mass;
    }

    s.mass = mf;
    s.fuel_used += m0 - mf;

    return dv;
}

Vector3 gravity_acceleration(Vector3 r, Body earth, Body mars)
{
    Vector3 a(0.0, 0.0, 0.0);

    double rs = norm(r);
    Vector3 ds = Vector3(0.0, 0.0, 0.0) - r;
    a = a + ds * (G * msun / pow(rs, 3.0));

    Vector3 de = earth.r - r;
    double re = norm(de);
    a = a + de * (G * mearth / pow(re, 3.0));

    Vector3 dm = mars.r - r;
    double rm = norm(dm);
    a = a + dm * (G * mmars / pow(rm, 3.0));

    return a;
}

Vector3 mars_drag_acceleration(Vector3 r, Vector3 v, Body mars, Spacecraft s)
{
    Vector3 r_rel = r - mars.r;
    Vector3 v_rel = v - mars.v;

    double altitude = norm(r_rel) - rmars;

    if (altitude > mars_atmosphere_height || altitude < 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    double rho = mars_surface_density * exp(-altitude / mars_scale_height);
    double speed = norm(v_rel);

    if (speed == 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    double drag_force = 0.5 * rho * starship_drag_coefficient * starship_drag_area * speed * speed;
    Vector3 direction = unit(v_rel) * (-1.0);

    return direction * (drag_force / s.mass);
}

Vector3 landing_burn_acceleration(Vector3 r, Vector3 v, Body mars)
{
    Vector3 r_rel = r - mars.r;
    Vector3 v_rel = v - mars.v;

    double altitude = norm(r_rel) - rmars;
    double speed = norm(v_rel);

    if (altitude > mars_landing_burn_altitude || altitude < 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    if (speed == 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    double safe_altitude = altitude;

    if (safe_altitude < 50.0) {
        safe_altitude = 50.0;
    }

    double target_speed = 5.0 + 0.015 * safe_altitude;
    double speed_to_remove = speed - target_speed;

    if (speed_to_remove < 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    double required_acceleration = speed_to_remove * speed_to_remove / (2.0 * safe_altitude);
    double acceleration = required_acceleration;

    if (acceleration > mars_landing_burn_acceleration) {
        acceleration = mars_landing_burn_acceleration;
    }

    Vector3 direction = unit(v_rel) * (-1.0);

    return direction * acceleration;
}

Vector3 total_acceleration(Vector3 r, Vector3 v, double t, double mars_phase, Spacecraft s)
{
    Body earth = earth_state(t);
    Body mars = mars_state(t, mars_phase);

    Vector3 a = gravity_acceleration(r, earth, mars);
    a = a + mars_drag_acceleration(r, v, mars, s);
    a = a + landing_burn_acceleration(r, v, mars);

    return a;
}

void rk4_step(Spacecraft& s, double t, double dt, double mars_phase)
{
    Vector3 k1r = s.v;
    Vector3 k1v = total_acceleration(s.r, s.v, t, mars_phase, s);

    Vector3 k2r = s.v + k1v * (0.5 * dt);
    Vector3 k2v = total_acceleration(s.r + k1r * (0.5 * dt), s.v + k1v * (0.5 * dt), t + 0.5 * dt, mars_phase, s);

    Vector3 k3r = s.v + k2v * (0.5 * dt);
    Vector3 k3v = total_acceleration(s.r + k2r * (0.5 * dt), s.v + k2v * (0.5 * dt), t + 0.5 * dt, mars_phase, s);

    Vector3 k4r = s.v + k3v * dt;
    Vector3 k4v = total_acceleration(s.r + k3r * dt, s.v + k3v * dt, t + dt, mars_phase, s);

    s.r = s.r + (k1r + k2r * 2.0 + k3r * 2.0 + k4r) * (dt / 6.0);
    s.v = s.v + (k1v + k2v * 2.0 + k3v * 2.0 + k4v) * (dt / 6.0);
}

MissionResult simulate_mission(MissionParameters p, bool save_trajectory)
{
    MissionResult result;

    ofstream trajectory;
    ofstream trajectory3d;
    ofstream telemetry;

    if (save_trajectory) {
        trajectory.open("results/trajectory.txt");
        trajectory3d.open("results/trajectory3d.txt");
        telemetry.open("results/telemetry.txt");

        trajectory << scientific << setprecision(15);
        trajectory3d << scientific << setprecision(15);
        telemetry << scientific << setprecision(15);
    }

    double base_dt;
    double mission_time;

    if (save_trajectory) {
        base_dt = 60.0;
        mission_time = 300.0 * day;
    } else {
        base_dt = 600.0;
        mission_time = 430.0 * day;
    }

    Spacecraft s;
    s.mass = starship_initial_mass;
    s.dry_mass = starship_dry_mass;
    s.fuel_used = 0.0;
    s.exhaust_velocity = starship_exhaust_velocity;

    result.initial_mass = s.mass;
    result.initial_available_delta_v = available_delta_v(s);

    double parking_altitude = 300000.0;
    double parking_radius = rearth + parking_altitude;

    double parking_speed = sqrt(G * mearth / parking_radius);
    double escape_speed = sqrt(2.0 * G * mearth / parking_radius);

    double hohmann_a = 0.5 * (earth_a + mars_a);
    double hohmann_time = pi * sqrt(pow(hohmann_a, 3.0) / (G * msun));

    double earth_speed = sqrt(G * msun / earth_a);
    double transfer_perihelion_speed = sqrt(G * msun * (2.0 / earth_a - 1.0 / hohmann_a));
    double v_inf_required = transfer_perihelion_speed - earth_speed;

    double launch_dv_estimate = sqrt(v_inf_required * v_inf_required + escape_speed * escape_speed) - parking_speed;
    launch_dv_estimate *= p.launch_dv_factor;

    Body earth = earth_state(0.0);
    Body mars = mars_state(0.0, p.mars_phase);

    Vector3 radial = unit(earth.r);
    Vector3 tangential = unit(earth.v);
    Vector3 normal = unit(cross(earth.r, earth.v));

    Vector3 launch_direction = unit(tangential + normal * p.launch_normal_factor);

    double launch_dv_applied = consume_delta_v(s, launch_dv_estimate);

    double departure_speed = parking_speed + launch_dv_applied;
    double v_inf_applied = 0.0;

    if (departure_speed > escape_speed) {
        v_inf_applied = sqrt(departure_speed * departure_speed - escape_speed * escape_speed);
    }

    double earth_soi = earth_a * pow(mearth / msun, 2.0 / 5.0);

    s.r = earth.r + radial * earth_soi;
    s.v = earth.v + launch_direction * v_inf_applied;

    double closest_mars = 1.0e100;
    double closest_mars_time = 0.0;
    double closest_mars_speed = 0.0;

    double max_sun_distance = 0.0;
    double previous_mars_distance = 1.0e100;

    double entry_time = 0.0;
    double entry_distance = 0.0;
    bool reached_entry = false;

    bool landed = false;
    bool impact = false;

    bool surface_event_started = false;
    double surface_event_time = 0.0;
    double post_landing_duration = 0.002 * day;

    bool correction_done = false;
    double correction_time = 0.0;
    double correction_dv_applied = 0.0;

    double t = 0.0;

    while (t <= mission_time) {
        earth = earth_state(t);
        mars = mars_state(t, p.mars_phase);

        double distance_earth = norm(s.r - earth.r);
        double distance_mars = norm(s.r - mars.r);
        double distance_sun = norm(s.r);

        double mars_altitude = distance_mars - rmars;

        Vector3 r_rel_mars = s.r - mars.r;
        Vector3 v_rel_mars = s.v - mars.v;
        double mars_relative_speed = norm(v_rel_mars);

        double dt = base_dt;

        if (save_trajectory && distance_mars < 20000000.0 * 1000.0) {
            dt = 30.0;
        }

        if (save_trajectory && distance_mars < 2000000.0 * 1000.0) {
            dt = 5.0;
        }

        if (save_trajectory && distance_mars < 200000.0 * 1000.0) {
            dt = 0.5;
        }

        if (save_trajectory && mars_altitude < 300000.0) {
            dt = 0.1;
        }

        if (save_trajectory && mars_altitude < 80000.0) {
            dt = 0.02;
        }

        if (surface_event_started) {
            dt = 0.5;
        }

        if (!correction_done && t > 100.0 * day && distance_mars < mars_correction_distance && distance_mars < previous_mars_distance) {
            double v2 = dot(v_rel_mars, v_rel_mars);
            double t_closest = 0.0;

            if (v2 > 0.0) {
                t_closest = -dot(r_rel_mars, v_rel_mars) / v2;
            }

            if (t_closest > 0.0 && t_closest < 4.0 * day) {
                Vector3 predicted_closest = r_rel_mars + v_rel_mars * t_closest;
                double predicted_distance = norm(predicted_closest);

                Vector3 target_closest = unit(predicted_closest) * mars_entry_radius;
                Vector3 needed_shift = target_closest - predicted_closest;

                Vector3 correction_vector = needed_shift / t_closest;
                double correction_dv = norm(correction_vector);

                if (correction_dv > mars_correction_max_dv) {
                    correction_vector = unit(correction_vector) * mars_correction_max_dv;
                    correction_dv = mars_correction_max_dv;
                }

                double applied_dv = consume_delta_v(s, correction_dv);

                if (correction_dv > 0.0) {
                    s.v = s.v + unit(correction_vector) * applied_dv;
                }

                correction_dv_applied = applied_dv;
                correction_time = t;
                correction_done = true;
            }
        }

        if (distance_mars < closest_mars && t > 60.0 * day) {
            closest_mars = distance_mars;
            closest_mars_time = t;
            closest_mars_speed = mars_relative_speed;
        }

        if (distance_sun > max_sun_distance) {
            max_sun_distance = distance_sun;
        }

        if (!reached_entry && distance_mars < mars_entry_radius && previous_mars_distance > mars_entry_radius) {
            entry_time = t;
            entry_distance = distance_mars;
            reached_entry = true;
        }

        if (!surface_event_started && mars_altitude <= 0.0 && t > 60.0 * day) {
            surface_event_started = true;
            surface_event_time = t;

            if (mars_relative_speed <= mars_touchdown_speed_limit) {
                landed = true;
            } else {
                impact = true;
            }

            Vector3 surface_direction = unit(s.r - mars.r);
            s.r = mars.r + surface_direction * rmars;
            s.v = mars.v;

            distance_mars = rmars;
            mars_altitude = 0.0;
            v_rel_mars = s.v - mars.v;
            mars_relative_speed = 0.0;
        }

        if (surface_event_started) {
            Vector3 surface_direction = unit(s.r - mars.r);
            s.r = mars.r + surface_direction * rmars;
            s.v = mars.v;

            distance_mars = rmars;
            mars_altitude = 0.0;
            v_rel_mars = s.v - mars.v;
            mars_relative_speed = 0.0;
        }

        if (save_trajectory) {
            trajectory << t / day << " " << earth.r.x << " " << earth.r.y << " " << mars.r.x << " " << mars.r.y << " " << s.r.x << " " << s.r.y << " " << s.mass << endl;

            trajectory3d << t / day << " " << earth.r.x << " " << earth.r.y << " " << earth.r.z << " " << mars.r.x << " " << mars.r.y << " " << mars.r.z << " " << s.r.x << " " << s.r.y << " " << s.r.z
                         << " " << s.mass << endl;

            telemetry << t / day << " " << distance_earth / 1000.0 << " " << distance_mars / 1000.0 << " " << distance_sun / au << " " << norm(s.v) / 1000.0 << " " << mars_relative_speed / 1000.0
                      << " " << s.mass << " " << reached_entry << " " << mars_altitude / 1000.0 << " " << landed << " " << impact << " " << correction_done << endl;
        }

        previous_mars_distance = distance_mars;

        if (!reached_entry && closest_mars_time > 0.0 && t > closest_mars_time + 5.0 * day) {
            break;
        }

        if (surface_event_started) {
            if (t > surface_event_time + post_landing_duration) {
                break;
            }
        } else {
            rk4_step(s, t, dt, p.mars_phase);
        }

        t += dt;
    }

    result.final_mass = s.mass;
    result.fuel_used = s.fuel_used;

    result.launch_dv_estimate = launch_dv_estimate;
    result.launch_dv_applied = launch_dv_applied;

    result.capture_dv_estimate = correction_dv_applied;
    result.capture_dv_applied = correction_dv_applied;

    result.closest_mars = closest_mars;
    result.closest_mars_time = closest_mars_time;
    result.mars_relative_speed = closest_mars_speed;

    result.max_sun_distance = max_sun_distance;

    result.capture_time = entry_time;
    result.capture_distance = entry_distance;
    result.captured = reached_entry;

    result.hohmann_time = hohmann_time;

    return result;
}