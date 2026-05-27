#pragma once
#include "spacecraft.h"

struct State {
    Vector3 r;
    Vector3 v;
};

State derivative(State s, double t, double mars_phase, Vector3 thrust_acceleration);
State add_state(State s, State k, double a);

void rk4_step(Spacecraft& s, double t, double dt, double mars_phase, Vector3 thrust_acceleration);