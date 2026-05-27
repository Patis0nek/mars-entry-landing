import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
results_dir = base_dir / "results"
figures_dir = base_dir / "figures"

figures_dir.mkdir(parents=True, exist_ok=True)

au = 1.495978707e11
mars_radius_km = 3389.5
mars_entry_altitude_km = 125.0
mars_entry_radius_km = mars_radius_km + mars_entry_altitude_km

trajectory = np.loadtxt(results_dir / "trajectory.txt")
trajectory3d = np.loadtxt(results_dir / "trajectory3d.txt")
telemetry = np.loadtxt(results_dir / "telemetry.txt")

t = trajectory[:, 0]

earth = trajectory[:, 1:3] / au
mars = trajectory[:, 3:5] / au
ship = trajectory[:, 5:7] / au

earth3d = trajectory3d[:, 1:4] / au
mars3d = trajectory3d[:, 4:7] / au
ship3d = trajectory3d[:, 7:10] / au

time_tel = telemetry[:, 0]
distance_earth_km = telemetry[:, 1]
distance_mars_km = telemetry[:, 2]
distance_sun_au = telemetry[:, 3]
speed_heliocentric_kms = telemetry[:, 4]
speed_mars_relative_kms = telemetry[:, 5]
mass_kg = telemetry[:, 6]

entry_flag = telemetry[:, 7]
altitude_km = telemetry[:, 8] if telemetry.shape[1] > 8 else distance_mars_km - mars_radius_km
landed_flag = telemetry[:, 9] if telemetry.shape[1] > 9 else np.zeros_like(time_tel)
impact_flag = telemetry[:, 10] if telemetry.shape[1] > 10 else np.zeros_like(time_tel)
correction_flag = telemetry[:, 11] if telemetry.shape[1] > 11 else np.zeros_like(time_tel)

valid = time_tel > 120.0
i_close = np.argmin(np.where(valid, distance_mars_km, np.inf))

entry_indices = np.where(entry_flag > 0.5)[0]
landed_indices = np.where(landed_flag > 0.5)[0]
impact_indices = np.where(impact_flag > 0.5)[0]
correction_indices = np.where(correction_flag > 0.5)[0]

i_entry = entry_indices[0] if len(entry_indices) > 0 else None
i_landed = landed_indices[0] if len(landed_indices) > 0 else None
i_impact = impact_indices[0] if len(impact_indices) > 0 else None
i_correction = correction_indices[0] if len(correction_indices) > 0 else None

i_surface = i_landed if i_landed is not None else i_impact

closest_km = distance_mars_km[i_close]
closest_altitude_km = altitude_km[i_close]
closest_day = time_tel[i_close]

bg = "#05070d"
panel = "#080b12"
grid = "#263241"
text = "#e6edf3"
muted = "#9da7b3"

sun_color = "#ffd166"
earth_color = "#4dabf7"
mars_color = "#ff6b35"
ship_color = "#80ffdb"
correction_color = "#ffb703"
entry_color = "#06d6a0"
landing_color = "#90ee90"
impact_color = "#ff4d6d"
close_color = "#c77dff"

plt.rcParams["figure.facecolor"] = bg
plt.rcParams["axes.facecolor"] = panel
plt.rcParams["savefig.facecolor"] = bg
plt.rcParams["text.color"] = text
plt.rcParams["axes.labelcolor"] = text
plt.rcParams["xtick.color"] = muted
plt.rcParams["ytick.color"] = muted
plt.rcParams["axes.edgecolor"] = muted
plt.rcParams["font.size"] = 11


def style_axis(ax):
    ax.grid(color=grid, linewidth=0.8, alpha=0.55)
    ax.tick_params(colors=muted)
    ax.xaxis.label.set_color(text)
    ax.yaxis.label.set_color(text)
    ax.title.set_color(text)


def legend(ax, loc="best"):
    ax.legend(loc=loc, facecolor="#0c111b", edgecolor="#30363d")


def savefig(name):
    plt.tight_layout()
    plt.savefig(figures_dir / name, dpi=240, facecolor=bg)
    plt.close()


def event_inside(i, xmin=None, xmax=None):
    if i is None:
        return False
    if xmin is None or xmax is None:
        return True
    return xmin <= time_tel[i] <= xmax


def add_event_lines(ax, xmin=None, xmax=None, include_correction=True):
    if include_correction and event_inside(i_correction, xmin, xmax):
        ax.axvline(time_tel[i_correction], linestyle="--", linewidth=1.5, color=correction_color, label="Correction burn")

    if event_inside(i_entry, xmin, xmax):
        ax.axvline(time_tel[i_entry], linestyle="--", linewidth=1.5, color=entry_color, label="Atmospheric entry")

    if event_inside(i_landed, xmin, xmax):
        ax.axvline(time_tel[i_landed], linestyle="--", linewidth=1.5, color=landing_color, label="Landing")

    if event_inside(i_impact, xmin, xmax):
        ax.axvline(time_tel[i_impact], linestyle="--", linewidth=1.5, color=impact_color, label="Impact")


# =========================================================
# Entry time axes
# =========================================================

entry_reference_day = time_tel[i_entry] if i_entry is not None else time_tel[i_close]
entry_time_min = (time_tel - entry_reference_day) * 24.0 * 60.0

surface_day = time_tel[i_surface] if i_surface is not None else entry_reference_day
surface_time_min = (surface_day - entry_reference_day) * 24.0 * 60.0

entry_start_min = -6.0
entry_end_min = surface_time_min + 3.0

if entry_end_min < 4.0:
    entry_end_min = 4.0

mask_entry = (entry_time_min >= entry_start_min) & (entry_time_min <= entry_end_min)

if np.sum(mask_entry) < 20:
    entry_start_min = -12.0
    entry_end_min = surface_time_min + 6.0
    mask_entry = (entry_time_min >= entry_start_min) & (entry_time_min <= entry_end_min)

entry_xmin = entry_start_min
entry_xmax = entry_end_min

one_min_start = -0.15
one_min_end = surface_time_min + 0.25

if one_min_end < 1.0:
    one_min_end = 1.0

if one_min_end > 2.0:
    one_min_end = 2.0

mask_1min = (entry_time_min >= one_min_start) & (entry_time_min <= one_min_end)

if np.sum(mask_1min) < 20:
    one_min_start = -0.5
    one_min_end = 1.5
    mask_1min = (entry_time_min >= one_min_start) & (entry_time_min <= one_min_end)


def add_entry_event_lines(ax):
    if i_entry is not None:
        ax.axvline(0.0, linestyle="--", linewidth=1.5, color=entry_color, label="Atmospheric entry")

    if i_landed is not None:
        x = (time_tel[i_landed] - entry_reference_day) * 24.0 * 60.0
        ax.axvline(x, linestyle="--", linewidth=1.5, color=landing_color, label="Landing")

    if i_impact is not None:
        x = (time_tel[i_impact] - entry_reference_day) * 24.0 * 60.0
        ax.axvline(x, linestyle="--", linewidth=1.5, color=impact_color, label="Impact")


if i_correction is not None:
    correction_center = time_tel[i_correction]
    correction_window = 0.15
    mask_correction = (time_tel >= correction_center - correction_window) & (time_tel <= correction_center + correction_window)

    if np.sum(mask_correction) < 10:
        correction_window = 0.4
        mask_correction = (time_tel >= correction_center - correction_window) & (time_tel <= correction_center + correction_window)

    correction_xmin = time_tel[mask_correction][0]
    correction_xmax = time_tel[mask_correction][-1]


# =========================================================
# 1. Full 2D trajectory
# =========================================================

plt.figure(figsize=(10, 10))
plt.plot(earth[:, 0], earth[:, 1], label="Earth", linewidth=1.8, color=earth_color)
plt.plot(mars[:, 0], mars[:, 1], label="Mars", linewidth=1.8, color=mars_color)
plt.plot(ship[:, 0], ship[:, 1], label="Starship", linewidth=2.2, color=ship_color)

plt.scatter([0], [0], s=180, label="Sun", color=sun_color)
plt.scatter([earth[0, 0]], [earth[0, 1]], s=45, label="Earth start", color=earth_color)
plt.scatter([mars[0, 0]], [mars[0, 1]], s=45, label="Mars start", color=mars_color)
plt.scatter([ship[0, 0]], [ship[0, 1]], s=45, label="Earth departure", color="white")
plt.scatter([ship[i_close, 0]], [ship[i_close, 1]], s=65, label="Closest approach", color=close_color)

if i_correction is not None:
    plt.scatter([ship[i_correction, 0]], [ship[i_correction, 1]], s=65, label="Correction burn", color=correction_color)
if i_entry is not None:
    plt.scatter([ship[i_entry, 0]], [ship[i_entry, 1]], s=70, label="Atmospheric entry", color=entry_color)
if i_landed is not None:
    plt.scatter([ship[i_landed, 0]], [ship[i_landed, 1]], s=80, label="Landing", color=landing_color)
if i_impact is not None:
    plt.scatter([ship[i_impact, 0]], [ship[i_impact, 1]], s=80, label="Impact", color=impact_color)

plt.xlabel("x [AU]")
plt.ylabel("y [AU]")
plt.title("Starship-like Mars Mission - Full Trajectory")
plt.axis("equal")
style_axis(plt.gca())
legend(plt.gca())
savefig("trajectory_full.png")


# =========================================================
# 2. Full 3D trajectory
# =========================================================

fig = plt.figure(figsize=(11, 9), facecolor=bg)
ax = fig.add_subplot(111, projection="3d", facecolor=panel)

ax.plot(earth3d[:, 0], earth3d[:, 1], earth3d[:, 2], label="Earth", linewidth=1.5, color=earth_color)
ax.plot(mars3d[:, 0], mars3d[:, 1], mars3d[:, 2], label="Mars", linewidth=1.5, color=mars_color)
ax.plot(ship3d[:, 0], ship3d[:, 1], ship3d[:, 2], label="Starship", linewidth=2.0, color=ship_color)

ax.scatter([0], [0], [0], s=160, label="Sun", color=sun_color)
ax.scatter([ship3d[0, 0]], [ship3d[0, 1]], [ship3d[0, 2]], s=45, label="Earth departure", color="white")
ax.scatter([ship3d[i_close, 0]], [ship3d[i_close, 1]], [ship3d[i_close, 2]], s=65, label="Closest approach", color=close_color)

if i_correction is not None:
    ax.scatter([ship3d[i_correction, 0]], [ship3d[i_correction, 1]], [ship3d[i_correction, 2]], s=70, label="Correction burn", color=correction_color)
if i_entry is not None:
    ax.scatter([ship3d[i_entry, 0]], [ship3d[i_entry, 1]], [ship3d[i_entry, 2]], s=70, label="Atmospheric entry", color=entry_color)
if i_landed is not None:
    ax.scatter([ship3d[i_landed, 0]], [ship3d[i_landed, 1]], [ship3d[i_landed, 2]], s=80, label="Landing", color=landing_color)
if i_impact is not None:
    ax.scatter([ship3d[i_impact, 0]], [ship3d[i_impact, 1]], [ship3d[i_impact, 2]], s=80, label="Impact", color=impact_color)

ax.set_xlabel("x [AU]")
ax.set_ylabel("y [AU]")
ax.set_zlabel("z [AU]")
ax.set_title("Starship-like Mars Mission - 3D Trajectory", color=text)

limit = 1.8
ax.set_xlim(-limit, limit)
ax.set_ylim(-limit, limit)
ax.set_zlim(-0.12, 0.12)

ax.view_init(elev=22, azim=42)
ax.grid(color=grid, alpha=0.45)
ax.tick_params(colors=muted)
legend(ax)
plt.tight_layout()
plt.savefig(figures_dir / "trajectory_3d.png", dpi=240, facecolor=bg)
plt.close()


# =========================================================
# 3. Mars reentry 1-minute zoom
# =========================================================

fig, ax1 = plt.subplots(figsize=(11, 6), facecolor=bg)
ax1.set_facecolor(panel)
ax2 = ax1.twinx()

ax1.plot(
    entry_time_min[mask_1min],
    altitude_km[mask_1min],
    label="Altitude above Mars",
    color=entry_color,
    linewidth=2.2
)

ax2.plot(
    entry_time_min[mask_1min],
    speed_mars_relative_kms[mask_1min],
    label="Mars-relative speed",
    color=ship_color,
    linewidth=2.2
)

ax1.axhline(mars_entry_altitude_km, linestyle=":", linewidth=1.5, label="Entry altitude", color=entry_color)
ax1.axhline(0.0, linestyle=":", linewidth=1.5, label="Mars surface", color=impact_color)

add_entry_event_lines(ax1)

ax1.set_xlim(one_min_start, one_min_end)

ax1.set_xlabel("Time from atmospheric entry [min]")
ax1.set_ylabel("Altitude [km]", color=text)
ax2.set_ylabel("Speed [km/s]", color=text)
ax1.set_title("Mars Reentry - Close Zoom")

style_axis(ax1)
ax2.tick_params(colors=muted)
ax2.yaxis.label.set_color(text)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, facecolor="#0c111b", edgecolor="#30363d")

plt.tight_layout()
plt.savefig(figures_dir / "mars_reentry_1min_zoom.png", dpi=240, facecolor=bg)
plt.close()


# =========================================================
# 4. Mission distances
# =========================================================

plt.figure(figsize=(11, 6))
plt.semilogy(time_tel, distance_earth_km, label="Distance to Earth", color=earth_color)
plt.semilogy(time_tel, distance_mars_km, label="Distance to Mars", color=mars_color)

plt.axhline(mars_entry_radius_km, linestyle=":", linewidth=1.5, label="Entry interface", color=entry_color)
plt.axhline(mars_radius_km, linestyle=":", linewidth=1.5, label="Mars surface", color=impact_color)
plt.axvline(time_tel[i_close], linestyle="--", linewidth=1.3, label="Closest approach", color=close_color)

add_event_lines(plt.gca())
plt.xlabel("Time [days]")
plt.ylabel("Distance [km]")
plt.title("Mission Distances")
style_axis(plt.gca())
legend(plt.gca())
savefig("distance_profile.png")


# =========================================================
# 5. Correction burn zoom
# =========================================================

if i_correction is not None:
    fig, ax1 = plt.subplots(figsize=(11, 6), facecolor=bg)
    ax1.set_facecolor(panel)
    ax2 = ax1.twinx()

    ax1.plot(time_tel[mask_correction], distance_mars_km[mask_correction], label="Distance to Mars", color=mars_color, linewidth=2.0)
    ax2.plot(time_tel[mask_correction], mass_kg[mask_correction], label="Spacecraft mass", color=ship_color, linewidth=2.0)

    ax1.axvline(time_tel[i_correction], linestyle="--", color=correction_color, label="Correction burn")
    ax1.set_xlim(correction_xmin, correction_xmax)

    ax1.set_xlabel("Time [days]")
    ax1.set_ylabel("Distance to Mars [km]", color=text)
    ax2.set_ylabel("Mass [kg]", color=text)
    ax1.set_title("Mars Approach Correction Burn Zoom")

    style_axis(ax1)
    ax2.tick_params(colors=muted)
    ax2.yaxis.label.set_color(text)

    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, facecolor="#0c111b", edgecolor="#30363d")

    plt.tight_layout()
    plt.savefig(figures_dir / "correction_burn_zoom.png", dpi=240, facecolor=bg)
    plt.close()


# =========================================================
# 6. Entry altitude zoom
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(entry_time_min[mask_entry], altitude_km[mask_entry], label="Altitude above Mars", color=ship_color, linewidth=2.0)

plt.axhline(mars_entry_altitude_km, linestyle=":", linewidth=1.5, label="Entry altitude", color=entry_color)
plt.axhline(0.0, linestyle=":", linewidth=1.5, label="Mars surface", color=impact_color)

add_entry_event_lines(plt.gca())

plt.xlim(entry_xmin, entry_xmax)
plt.xlabel("Time from atmospheric entry [min]")
plt.ylabel("Altitude [km]")
plt.title("Mars Entry and Landing Altitude Zoom")
style_axis(plt.gca())
legend(plt.gca())
savefig("mars_entry_altitude_zoom.png")


# =========================================================
# 7. Entry speed zoom
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(entry_time_min[mask_entry], speed_mars_relative_kms[mask_entry], label="Speed relative to Mars", color=ship_color, linewidth=2.0)

add_entry_event_lines(plt.gca())

plt.xlim(entry_xmin, entry_xmax)
plt.xlabel("Time from atmospheric entry [min]")
plt.ylabel("Speed [km/s]")
plt.title("Mars Entry and Landing Speed Zoom")
style_axis(plt.gca())
legend(plt.gca())
savefig("mars_entry_speed_zoom.png")


# =========================================================
# 8. Entry distance zoom
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(entry_time_min[mask_entry], distance_mars_km[mask_entry], label="Distance to Mars center", color=ship_color, linewidth=2.0)

plt.axhline(mars_entry_radius_km, linestyle=":", linewidth=1.5, label="Entry interface", color=entry_color)
plt.axhline(mars_radius_km, linestyle=":", linewidth=1.5, label="Mars surface", color=impact_color)

add_entry_event_lines(plt.gca())

plt.xlim(entry_xmin, entry_xmax)
plt.xlabel("Time from atmospheric entry [min]")
plt.ylabel("Distance from Mars center [km]")
plt.title("Mars Entry and Landing Distance Zoom")
style_axis(plt.gca())
legend(plt.gca())
savefig("mars_entry_distance_zoom.png")


# =========================================================
# 9. Combined altitude and speed panel
# =========================================================

fig, ax1 = plt.subplots(figsize=(11, 6), facecolor=bg)
ax1.set_facecolor(panel)
ax2 = ax1.twinx()

ax1.plot(entry_time_min[mask_entry], altitude_km[mask_entry], label="Altitude", color=entry_color, linewidth=2.0)
ax2.plot(entry_time_min[mask_entry], speed_mars_relative_kms[mask_entry], label="Mars-relative speed", color=ship_color, linewidth=2.0)

ax1.axhline(125.0, linestyle=":", color=entry_color, alpha=0.75)
ax1.axhline(0.0, linestyle=":", color=impact_color, alpha=0.75)

add_entry_event_lines(ax1)

ax1.set_xlim(entry_xmin, entry_xmax)

ax1.set_xlabel("Time from atmospheric entry [min]")
ax1.set_ylabel("Altitude [km]", color=text)
ax2.set_ylabel("Speed [km/s]", color=text)
ax1.set_title("Mars Entry: Altitude and Speed")

style_axis(ax1)
ax2.tick_params(colors=muted)
ax2.yaxis.label.set_color(text)

lines1, labels1 = ax1.get_legend_handles_labels()
lines2, labels2 = ax2.get_legend_handles_labels()
ax1.legend(lines1 + lines2, labels1 + labels2, facecolor="#0c111b", edgecolor="#30363d")

plt.tight_layout()
plt.savefig(figures_dir / "mars_entry_altitude_speed_panel.png", dpi=240, facecolor=bg)
plt.close()


# =========================================================
# 10. Full velocity profile
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(time_tel, speed_heliocentric_kms, label="Heliocentric speed", color=earth_color)
plt.plot(time_tel, speed_mars_relative_kms, label="Speed relative to Mars", color=ship_color)

plt.axvline(time_tel[i_close], linestyle="--", linewidth=1.3, label="Closest approach", color=close_color)
add_event_lines(plt.gca())

plt.xlabel("Time [days]")
plt.ylabel("Speed [km/s]")
plt.title("Velocity Profile")
style_axis(plt.gca())
legend(plt.gca())
savefig("velocity_profile.png")


# =========================================================
# 11. Mass profile
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(time_tel, mass_kg, label="Spacecraft mass after Earth departure", color=ship_color, linewidth=2.0)

if i_correction is not None:
    plt.axvline(time_tel[i_correction], linestyle="--", color=correction_color, label="Correction burn")

mass_min = np.min(mass_kg)
mass_max = np.max(mass_kg)
mass_margin = max((mass_max - mass_min) * 0.30, 1000.0)
plt.ylim(mass_min - mass_margin, mass_max + mass_margin)

plt.xlabel("Time [days]")
plt.ylabel("Mass [kg]")
plt.title("Spacecraft Mass After Earth Departure")
style_axis(plt.gca())
legend(plt.gca())
savefig("mass_profile.png")


# =========================================================
# 12. Distance from Sun
# =========================================================

plt.figure(figsize=(11, 6))
plt.plot(time_tel, distance_sun_au, label="Distance from Sun", color=sun_color, linewidth=2.0)

plt.xlabel("Time [days]")
plt.ylabel("Distance [AU]")
plt.title("Spacecraft Distance from the Sun")
style_axis(plt.gca())
legend(plt.gca())
savefig("sun_distance_profile.png")


# =========================================================
# Print summary
# =========================================================

print("Saved:")
print(figures_dir / "trajectory_full.png")
print(figures_dir / "trajectory_3d.png")
print(figures_dir / "mars_reentry_1min_zoom.png")
print(figures_dir / "distance_profile.png")

if i_correction is not None:
    print(figures_dir / "correction_burn_zoom.png")

print(figures_dir / "mars_entry_altitude_zoom.png")
print(figures_dir / "mars_entry_speed_zoom.png")
print(figures_dir / "mars_entry_distance_zoom.png")
print(figures_dir / "mars_entry_altitude_speed_panel.png")
print(figures_dir / "velocity_profile.png")
print(figures_dir / "mass_profile.png")
print(figures_dir / "sun_distance_profile.png")

print()
print(f"Closest Mars approach = {closest_km:.2f} km at day {closest_day:.5f}")
print(f"Closest altitude = {closest_altitude_km:.2f} km")
print(f"Mars-relative speed at closest approach = {speed_mars_relative_kms[i_close]:.5f} km/s")

if i_correction is not None:
    print(f"Correction burn at day {time_tel[i_correction]:.5f}")
else:
    print("No correction burn detected.")

if i_entry is not None:
    print(f"Atmospheric entry reached at day {time_tel[i_entry]:.5f}")
else:
    print("Atmospheric entry not reached.")

if i_landed is not None:
    print(f"Landing detected at day {time_tel[i_landed]:.5f}")
elif i_impact is not None:
    print(f"Impact detected at day {time_tel[i_impact]:.5f}")
else:
    print("No landing or impact detected.")