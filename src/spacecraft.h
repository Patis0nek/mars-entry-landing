#pragma once
#include "vector3.h"
#include <cmath>

struct Spacecraft {
    Vector3 r;
    Vector3 v;

    double mass;
    double dry_mass;
    double fuel_used;
    double exhaust_velocity;
};

inline double available_delta_v(Spacecraft s)
{
    return s.exhaust_velocity * log(s.mass / s.dry_mass);
}

inline double burn(Spacecraft& s, Vector3 direction, double dv)
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
    s.v = s.v + unit(direction) * dv;

    return dv;
}