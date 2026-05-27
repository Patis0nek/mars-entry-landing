#include "constants.h"
#include "physics.h"
#include <cmath>
#include <fstream>
#include <iostream>

using namespace std;

struct BestResult {
    double score;
    double distance;
    double phase;
    double factor;
    double normal;
    double time;
    double relative_speed;
    double max_sun_distance;
    double final_mass;
    bool reached_entry;
};

double normalize_search_angle(double x)
{
    while (x < 0.0) {
        x += 2.0 * pi;
    }

    while (x >= 2.0 * pi) {
        x -= 2.0 * pi;
    }

    return x;
}

double mission_score(MissionResult r)
{
    double entry_error_km = fabs(r.closest_mars - mars_entry_radius) / 1000.0;
    double speed_error_kms = fabs(r.mars_relative_speed - mars_entry_speed_target) / 1000.0;

    double score = 0.0;

    score += 200.0 * entry_error_km;
    score += 1000.0 * speed_error_kms;

    if (r.closest_mars < rmars) {
        score += 100000000.0;
    }

    if (r.captured) {
        score -= 100000000.0;
    }

    return score;
}

void test_range(ofstream& file, BestResult& best, int& missions, double phase_min, double phase_max, double factor_min, double factor_max, double normal_min, double normal_max, int phase_steps,
    int factor_steps, int normal_steps)
{
    for (int i = 0; i < phase_steps; i++) {
        double raw_phase = phase_min + (phase_max - phase_min) * i / (phase_steps - 1.0);
        double phase = normalize_search_angle(raw_phase);

        for (int j = 0; j < factor_steps; j++) {
            double factor = factor_min + (factor_max - factor_min) * j / (factor_steps - 1.0);

            for (int k = 0; k < normal_steps; k++) {
                double normal = normal_min + (normal_max - normal_min) * k / (normal_steps - 1.0);

                MissionParameters p;
                p.mars_phase = phase;
                p.launch_dv_factor = factor;
                p.launch_normal_factor = normal;

                MissionResult r = simulate_mission(p, false);

                double score = mission_score(r);
                double entry_error_km = fabs(r.closest_mars - mars_entry_radius) / 1000.0;
                double speed_error_kms = fabs(r.mars_relative_speed - mars_entry_speed_target) / 1000.0;

                file << missions << " " << phase << " " << factor << " " << normal << " " << r.closest_mars / 1000.0 << " " << mars_entry_radius / 1000.0 << " " << entry_error_km << " "
                     << r.closest_mars_time / day << " " << r.mars_relative_speed / 1000.0 << " " << speed_error_kms << " " << r.max_sun_distance / 1000.0 << " " << r.launch_dv_estimate << " "
                     << r.launch_dv_applied << " " << r.final_mass << " " << r.captured << " " << score << endl;

                if (score < best.score) {
                    best.score = score;
                    best.distance = r.closest_mars;
                    best.phase = phase;
                    best.factor = factor;
                    best.normal = normal;
                    best.time = r.closest_mars_time;
                    best.relative_speed = r.mars_relative_speed;
                    best.max_sun_distance = r.max_sun_distance;
                    best.final_mass = r.final_mass;
                    best.reached_entry = r.captured;

                    cout << "new best: "
                         << "distance = " << best.distance / 1000.0 << " km, "
                         << "entry error = " << fabs(best.distance - mars_entry_radius) / 1000.0 << " km, "
                         << "time = " << best.time / day << " days, "
                         << "v_rel = " << best.relative_speed / 1000.0 << " km/s, "
                         << "speed error = " << fabs(best.relative_speed - mars_entry_speed_target) / 1000.0 << " km/s, "
                         << "phase = " << best.phase << ", "
                         << "factor = " << best.factor << ", "
                         << "normal = " << best.normal << ", "
                         << "entry = " << best.reached_entry << ", "
                         << "score = " << best.score << endl;
                }

                missions++;
            }
        }
    }
}

int main()
{
    ofstream file("results/search_entry_local.txt");

    BestResult best;
    best.score = 1.0e100;
    best.distance = 1.0e100;
    best.phase = 0.0;
    best.factor = 0.0;
    best.normal = 0.0;
    best.time = 0.0;
    best.relative_speed = 0.0;
    best.max_sun_distance = 0.0;
    best.final_mass = 0.0;
    best.reached_entry = false;

    int missions = 0;

    test_range(file, best, missions, 2.798, 2.812, 1.024, 1.037, -0.125, -0.070, 14, 7, 7);

    double phase_center = best.phase;
    double factor_center = best.factor;
    double normal_center = best.normal;

    test_range(file, best, missions, phase_center - 0.0035, phase_center + 0.0035, factor_center - 0.0030, factor_center + 0.0030, normal_center - 0.0080, normal_center + 0.0080, 9, 5, 5);

    cout << endl;
    cout << "missions tested = " << missions << endl;
    cout << "best Mars phase = " << best.phase << endl;
    cout << "best launch factor = " << best.factor << endl;
    cout << "best launch normal factor = " << best.normal << endl;
    cout << "closest Mars approach = " << best.distance / 1000.0 << " km" << endl;
    cout << "Mars entry target radius = " << mars_entry_radius / 1000.0 << " km" << endl;
    cout << "entry radius error = " << fabs(best.distance - mars_entry_radius) / 1000.0 << " km" << endl;
    cout << "time = " << best.time / day << " days" << endl;
    cout << "Mars relative speed = " << best.relative_speed / 1000.0 << " km/s" << endl;
    cout << "entry speed target = " << mars_entry_speed_target / 1000.0 << " km/s" << endl;
    cout << "entry speed error = " << fabs(best.relative_speed - mars_entry_speed_target) / 1000.0 << " km/s" << endl;
    cout << "maximum Sun distance = " << best.max_sun_distance / 1000.0 << " km" << endl;
    cout << "final mass = " << best.final_mass << " kg" << endl;
    cout << "reached entry interface = " << best.reached_entry << endl;

    return 0;
}