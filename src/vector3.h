#pragma once
#include <cmath>

struct Vector3 {
    double x;
    double y;
    double z;

    Vector3()
    {
        x = 0.0;
        y = 0.0;
        z = 0.0;
    }

    Vector3(double x0, double y0, double z0)
    {
        x = x0;
        y = y0;
        z = z0;
    }

    Vector3 operator+(Vector3 b) const { return Vector3(x + b.x, y + b.y, z + b.z); }

    Vector3 operator-(Vector3 b) const { return Vector3(x - b.x, y - b.y, z - b.z); }

    Vector3 operator*(double a) const { return Vector3(a * x, a * y, a * z); }

    Vector3 operator/(double a) const { return Vector3(x / a, y / a, z / a); }
};

inline Vector3 operator*(double a, Vector3 b)
{
    return Vector3(a * b.x, a * b.y, a * b.z);
}

inline double dot(Vector3 a, Vector3 b)
{
    return a.x * b.x + a.y * b.y + a.z * b.z;
}

inline Vector3 cross(Vector3 a, Vector3 b)
{
    return Vector3(a.y * b.z - a.z * b.y, a.z * b.x - a.x * b.z, a.x * b.y - a.y * b.x);
}

inline double norm(Vector3 a)
{
    return sqrt(dot(a, a));
}

inline Vector3 unit(Vector3 a)
{
    double r = norm(a);

    if (r == 0.0) {
        return Vector3(0.0, 0.0, 0.0);
    }

    return a / r;
}