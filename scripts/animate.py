import numpy as np
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from pathlib import Path

base_dir = Path(__file__).resolve().parents[1]
results_dir = base_dir / "results"
figures_dir = base_dir / "figures"

figures_dir.mkdir(parents=True, exist_ok=True)

au = 1.495978707e11
mars_radius_km = 3389.5
entry_altitude_km = 125.0
entry_radius_km = mars_radius_km + entry_altitude_km

trajectory = np.loadtxt(results_dir / "trajectory3d.txt")
telemetry = np.loadtxt(results_dir / "telemetry.txt")

time = trajectory[:, 0]

earth_au = trajectory[:, 1:4] / au
mars_au = trajectory[:, 4:7] / au
ship_au = trajectory[:, 7:10] / au

mars_km = trajectory[:, 4:7] / 1000.0
ship_km = trajectory[:, 7:10] / 1000.0
ship_rel_km = ship_km - mars_km

distance_mars_km = telemetry[:, 2]
speed_mars_relative_kms = telemetry[:, 5]
mass_kg = telemetry[:, 6]

entry_flag = telemetry[:, 7]
altitude_km = telemetry[:, 8] if telemetry.shape[1] > 8 else distance_mars_km - mars_radius_km
landed_flag = telemetry[:, 9] if telemetry.shape[1] > 9 else np.zeros_like(time)
impact_flag = telemetry[:, 10] if telemetry.shape[1] > 10 else np.zeros_like(time)
correction_flag = telemetry[:, 11] if telemetry.shape[1] > 11 else np.zeros_like(time)

valid = time > 120.0
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
i_final = i_surface if i_surface is not None else i_close

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
plt.rcParams["font.size"] = 10


def unique_frames(values):
    out = []
    last = -1

    for value in values:
        i = int(value)

        if 0 <= i < len(time) and i != last:
            out.append(i)
            last = i

    return out


full_end = i_correction if i_correction is not None else i_entry if i_entry is not None else i_close
approach_start = i_correction if i_correction is not None else full_end
approach_end = i_entry if i_entry is not None else i_close

entry_start = i_entry - 700 if i_entry is not None else i_close - 700
entry_end = i_final + 450

entry_start = max(0, entry_start)
entry_end = min(len(time) - 1, entry_end)

frame_plan = []

for i in unique_frames(np.linspace(0, full_end, 150)):
    frame_plan.append(("full3d", i))

if approach_end > approach_start:
    for i in unique_frames(np.linspace(approach_start, approach_end, 140)):
        frame_plan.append(("approach2d", i))

for i in unique_frames(np.linspace(entry_start, entry_end, 180)):
    frame_plan.append(("entry2d", i))


fig = plt.figure(figsize=(10, 10), facecolor=bg)


def status_at(i):
    if impact_flag[i] > 0.5:
        return "Impact / hard touchdown", impact_color

    if landed_flag[i] > 0.5:
        return "Landing completed", landing_color

    if entry_flag[i] > 0.5:
        return "Atmospheric entry and landing burn", entry_color

    if correction_flag[i] > 0.5:
        return "After Mars approach correction", correction_color

    return "Interplanetary transfer", ship_color


def set_dark_3d(ax):
    ax.set_facecolor(panel)
    ax.grid(color=grid, linewidth=0.7, alpha=0.5)

    ax.xaxis.pane.set_facecolor((0.03, 0.04, 0.07, 1))
    ax.yaxis.pane.set_facecolor((0.03, 0.04, 0.07, 1))
    ax.zaxis.pane.set_facecolor((0.03, 0.04, 0.07, 1))

    ax.xaxis.pane.set_edgecolor((0.28, 0.32, 0.38, 1))
    ax.yaxis.pane.set_edgecolor((0.28, 0.32, 0.38, 1))
    ax.zaxis.pane.set_edgecolor((0.28, 0.32, 0.38, 1))

    ax.tick_params(colors=muted, labelsize=8)

    ax.xaxis.label.set_color(text)
    ax.yaxis.label.set_color(text)
    ax.zaxis.label.set_color(text)


def set_dark_2d(ax):
    ax.set_facecolor(panel)
    ax.grid(color=grid, linewidth=0.8, alpha=0.55)
    ax.tick_params(colors=muted)
    ax.xaxis.label.set_color(text)
    ax.yaxis.label.set_color(text)
    ax.title.set_color(text)


def draw_info(ax, i, camera_text):
    status, status_color = status_at(i)

    def put_text(x, y, content, color=text, fontsize=10, alpha=0.34):
        if hasattr(ax, "text2D"):
            ax.text2D(
                x,
                y,
                content,
                transform=ax.transAxes,
                color=color,
                fontsize=fontsize,
                bbox=dict(facecolor="#000000", alpha=alpha, edgecolor="none", boxstyle="round,pad=0.35")
            )
        else:
            ax.text(
                x,
                y,
                content,
                transform=ax.transAxes,
                color=color,
                fontsize=fontsize,
                bbox=dict(facecolor="#000000", alpha=alpha, edgecolor="none", boxstyle="round,pad=0.35")
            )

    put_text(
        0.03,
        0.94,
        status,
        color=status_color,
        fontsize=12,
        alpha=0.42
    )

    put_text(
        0.03,
        0.88,
        f"Day {time[i]:.3f}\n"
        f"Altitude: {altitude_km[i]:.2f} km\n"
        f"Mars-relative speed: {speed_mars_relative_kms[i]:.3f} km/s",
        color=text,
        fontsize=10,
        alpha=0.34
    )

    put_text(
        0.03,
        0.04,
        camera_text,
        color=text,
        fontsize=10,
        alpha=0.34
    )


def draw_legend(ax):
    legend = ax.legend(loc="upper right", frameon=True)

    if legend is not None:
        legend.get_frame().set_facecolor("#0c111b")
        legend.get_frame().set_edgecolor("#30363d")
        legend.get_frame().set_alpha(0.92)


def draw_full3d(i, frame_id):
    ax = fig.add_subplot(111, projection="3d")
    set_dark_3d(ax)

    ax.plot(earth_au[:, 0], earth_au[:, 1], earth_au[:, 2], color=earth_color, linewidth=0.8, alpha=0.22)
    ax.plot(mars_au[:, 0], mars_au[:, 1], mars_au[:, 2], color=mars_color, linewidth=0.8, alpha=0.22)

    trail = 220
    j0 = max(0, i - trail)

    ax.plot(earth_au[j0:i + 1, 0], earth_au[j0:i + 1, 1], earth_au[j0:i + 1, 2], color=earth_color, linewidth=1.5, label="Earth path")
    ax.plot(mars_au[j0:i + 1, 0], mars_au[j0:i + 1, 1], mars_au[j0:i + 1, 2], color=mars_color, linewidth=1.5, label="Mars path")
    ax.plot(ship_au[:i + 1, 0], ship_au[:i + 1, 1], ship_au[:i + 1, 2], color=ship_color, linewidth=2.2, label="Starship path")

    ax.scatter([0], [0], [0], s=170, color=sun_color, edgecolors="none", label="Sun")
    ax.scatter([earth_au[i, 0]], [earth_au[i, 1]], [earth_au[i, 2]], s=55, color=earth_color, edgecolors="none", label="Earth")
    ax.scatter([mars_au[i, 0]], [mars_au[i, 1]], [mars_au[i, 2]], s=55, color=mars_color, edgecolors="none", label="Mars")
    ax.scatter([ship_au[i, 0]], [ship_au[i, 1]], [ship_au[i, 2]], s=55, color="white", edgecolors="none", label="Starship")

    if i_correction is not None and i >= i_correction:
        ax.scatter([ship_au[i_correction, 0]], [ship_au[i_correction, 1]], [ship_au[i_correction, 2]], s=70, color=correction_color, edgecolors="none", label="Correction burn")

    ax.set_xlim(-1.8, 1.8)
    ax.set_ylim(-1.8, 1.8)
    ax.set_zlim(-0.15, 0.15)

    ax.set_xlabel("x [AU]")
    ax.set_ylabel("y [AU]")
    ax.set_zlabel("z [AU]")
    ax.set_title("Starship-like Mars Mission - Full 3D View", color=text, fontsize=14, pad=16)

    ax.view_init(elev=24, azim=42 + frame_id * 0.02)

    draw_info(ax, i, "Scene 1: Sun-centered 3D mission overview")
    draw_legend(ax)


def smooth_zoom(progress, start_zoom, end_zoom):
    p = 0.5 - 0.5 * np.cos(np.pi * progress)
    return start_zoom * (1.0 - p) + end_zoom * p


def draw_approach2d(i, local_frame, total_frames):
    ax = fig.add_subplot(111)
    set_dark_2d(ax)

    progress = local_frame / max(total_frames - 1, 1)
    zoom = smooth_zoom(progress, 0.40, 0.045)

    center = mars_au[i, :2]

    j0 = max(0, i - 500)
    j1 = min(len(time), i + 120)

    ax.plot(earth_au[:, 0], earth_au[:, 1], color=earth_color, linewidth=0.7, alpha=0.14)
    ax.plot(mars_au[:, 0], mars_au[:, 1], color=mars_color, linewidth=0.7, alpha=0.16)

    ax.plot(mars_au[j0:j1, 0], mars_au[j0:j1, 1], color=mars_color, linewidth=1.6, alpha=0.9, label="Mars path")
    ax.plot(ship_au[j0:i + 1, 0], ship_au[j0:i + 1, 1], color=ship_color, linewidth=2.4, label="Starship path")

    ax.scatter([mars_au[i, 0]], [mars_au[i, 1]], s=85, color=mars_color, edgecolors="none", label="Mars")
    ax.scatter([ship_au[i, 0]], [ship_au[i, 1]], s=70, color="white", edgecolors="none", label="Starship")

    if i_correction is not None:
        ax.scatter([ship_au[i_correction, 0]], [ship_au[i_correction, 1]], s=75, color=correction_color, edgecolors="none", label="Correction burn")

    if i_entry is not None:
        ax.scatter([ship_au[i_entry, 0]], [ship_au[i_entry, 1]], s=75, color=entry_color, edgecolors="none", label="Entry point")

    ax.set_xlim(center[0] - zoom, center[0] + zoom)
    ax.set_ylim(center[1] - zoom, center[1] + zoom)
    ax.set_aspect("equal", adjustable="box")

    ax.set_xlabel("x [AU]")
    ax.set_ylabel("y [AU]")
    ax.set_title("Mars Approach - Smooth Top View Zoom", color=text, fontsize=14, pad=14)

    draw_info(ax, i, "Scene 2: top-down zoom toward Mars approach")
    draw_legend(ax)


def draw_entry2d(i, local_frame, total_frames):
    ax = fig.add_subplot(111)
    set_dark_2d(ax)

    j0 = max(entry_start, i - 450)

    surface = plt.Circle((0, 0), mars_radius_km, color=mars_color, alpha=0.32, label="Mars surface")
    entry = plt.Circle((0, 0), entry_radius_km, fill=False, color=entry_color, linestyle="--", linewidth=1.5, alpha=0.85, label="125 km entry interface")

    ax.add_patch(surface)
    ax.add_patch(entry)

    ax.plot(ship_rel_km[entry_start:entry_end + 1, 0], ship_rel_km[entry_start:entry_end + 1, 1], color=ship_color, linewidth=1.1, alpha=0.20)
    ax.plot(ship_rel_km[j0:i + 1, 0], ship_rel_km[j0:i + 1, 1], color=ship_color, linewidth=2.8, label="Starship path")

    ax.scatter([ship_rel_km[i, 0]], [ship_rel_km[i, 1]], s=75, color="white", edgecolors="none", label="Starship")

    if i_entry is not None and entry_start <= i_entry <= entry_end:
        ax.scatter([ship_rel_km[i_entry, 0]], [ship_rel_km[i_entry, 1]], s=85, color=entry_color, edgecolors="none", label="Atmospheric entry")

    if i_landed is not None and entry_start <= i_landed <= entry_end:
        ax.scatter([ship_rel_km[i_landed, 0]], [ship_rel_km[i_landed, 1]], s=95, color=landing_color, edgecolors="none", label="Landing")

    if i_impact is not None and entry_start <= i_impact <= entry_end:
        ax.scatter([ship_rel_km[i_impact, 0]], [ship_rel_km[i_impact, 1]], s=95, color=impact_color, edgecolors="none", label="Impact")

    limit = 6200.0
    ax.set_xlim(-limit, limit)
    ax.set_ylim(-limit, limit)
    ax.set_aspect("equal", adjustable="box")

    ax.set_xlabel("x relative to Mars [km]")
    ax.set_ylabel("y relative to Mars [km]")
    ax.set_title("Mars Entry and Landing - Top View", color=text, fontsize=14, pad=14)

    draw_info(ax, i, "Scene 3: Mars-centered entry and landing top view")
    draw_legend(ax)


scene_lengths = []
last_mode = None
count = 0

for mode, i in frame_plan:
    if mode != last_mode:
        if last_mode is not None:
            scene_lengths.append((last_mode, count))
        last_mode = mode
        count = 1
    else:
        count += 1

scene_lengths.append((last_mode, count))

mode_counts = {}
for mode, count in scene_lengths:
    mode_counts[mode] = count

mode_seen = {
    "full3d": 0,
    "approach2d": 0,
    "entry2d": 0
}


def update(frame_id):
    fig.clear()

    mode, i = frame_plan[frame_id]

    if mode == "full3d":
        draw_full3d(i, frame_id)

    elif mode == "approach2d":
        local = mode_seen["approach2d"]
        total = mode_counts["approach2d"]
        draw_approach2d(i, local, total)
        mode_seen["approach2d"] += 1

    else:
        local = mode_seen["entry2d"]
        total = mode_counts["entry2d"]
        draw_entry2d(i, local, total)
        mode_seen["entry2d"] += 1

    return []


animation = FuncAnimation(
    fig,
    update,
    frames=len(frame_plan),
    interval=70,
    blit=False
)

output_path = figures_dir / "mars_mission_smooth_zoom_dark.gif"
animation.save(output_path, writer=PillowWriter(fps=14), dpi=115)

plt.close(fig)

print("Saved:")
print(output_path)
print(f"Frames rendered = {len(frame_plan)}")

if i_correction is not None:
    print(f"Correction burn at day {time[i_correction]:.5f}")

if i_entry is not None:
    print(f"Atmospheric entry at day {time[i_entry]:.5f}")

if i_landed is not None:
    print(f"Landing detected at day {time[i_landed]:.5f}")
elif i_impact is not None:
    print(f"Impact detected at day {time[i_impact]:.5f}")
else:
    print("No landing or impact detected.")