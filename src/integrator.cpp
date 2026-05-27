#include "integrator.h"
#include "physics.h"

State derivative(State s, double t, double mars_phase, Vector3 thrust_acceleration)
{
    State ds;

    ds.r = s.v;
    ds.v = acceleration(s.r, t, mars_phase) + thrust_acceleration;

    return ds;
}

State add_state(State s, State k, double a)
{
    State result;

    result.r = s.r + k.r * a;
    result.v = s.v + k.v * a;

    return result;
}

void rk4_step(Spacecraft& s, double t, double dt, double mars_phase, Vector3 thrust_acceleration)
{
    State y;
    y.r = s.r;
    y.v = s.v;

    State k1 = derivative(y, t, mars_phase, thrust_acceleration);
    State k2 = derivative(add_state(y, k1, dt / 2.0), t + dt / 2.0, mars_phase, thrust_acceleration);
    State k3 = derivative(add_state(y, k2, dt / 2.0), t + dt / 2.0, mars_phase, thrust_acceleration);
    State k4 = derivative(add_state(y, k3, dt), t + dt, mars_phase, thrust_acceleration);

    s.r = s.r + (k1.r + 2.0 * k2.r + 2.0 * k3.r + k4.r) * (dt / 6.0);
    s.v = s.v + (k1.v + 2.0 * k2.v + 2.0 * k3.v + k4.v) * (dt / 6.0);
}