#pragma once
#include "body.h"
#include "spacecraft.h"

struct MissionParameters {
    double mars_phase;
    double launch_dv_factor;
    double launch_normal_factor;
};

struct MissionResult {
    double closest_mars;
    double closest_mars_time;
    double mars_relative_speed;
    double max_sun_distance;

    double launch_dv_estimate;
    double launch_dv_applied;

    double capture_dv_estimate;
    double capture_dv_applied;
    double capture_time;
    double capture_distance;

    double initial_mass;
    double final_mass;
    double fuel_used;
    double initial_available_delta_v;

    bool captured;

    double hohmann_time;
};

Vector3 gravity(Vector3 r, Body b);

Body earth_position(double t);
Body mars_position(double t, double phase);

Vector3 acceleration(Vector3 r, double t, double mars_phase);

MissionResult simulate_mission(MissionParameters p, bool save_trajectory);