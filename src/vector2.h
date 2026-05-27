#pragma once
#include <cmath>

struct Vector2 {
    double x;
    double y;

    Vector2()
    {
        x = 0.0;
        y = 0.0;
    }

    Vector2(double x0, double y0)
    {
        x = x0;
        y = y0;
    }

    Vector2 operator+(Vector2 b) const { return Vector2(x + b.x, y + b.y); }

    Vector2 operator-(Vector2 b) const { return Vector2(x - b.x, y - b.y); }

    Vector2 operator*(double a) const { return Vector2(a * x, a * y); }

    Vector2 operator/(double a) const { return Vector2(x / a, y / a); }
};

inline Vector2 operator*(double a, Vector2 b)
{
    return Vector2(a * b.x, a * b.y);
}

inline double norm(Vector2 a)
{
    return sqrt(a.x * a.x + a.y * a.y);
}

inline Vector2 unit(Vector2 a)
{
    double r = norm(a);

    if (r == 0.0) {
        return Vector2(0.0, 0.0);
    }

    return a / r;
}

inline double dot(Vector2 a, Vector2 b)
{
    return a.x * b.x + a.y * b.y;
}