# physics.py
import math

# ── Gravity & Movement ───────────────────────────────────
GRAVITY = 0.024

def apply_gravity(velocity_y):
    return velocity_y + GRAVITY

def apply_physics(x, y, velocity_x, velocity_y):
    velocity_y = apply_gravity(velocity_y)
    x += velocity_x
    y += velocity_y
    return x, y, velocity_x, velocity_y

# ── Collision Detection ──────────────────────────────────
def point_line_segment_distance_sq(px, py, x1, y1, x2, y2):
    """
    Squared distance from point (px,py) to line segment (x1,y1)-(x2,y2).
    Squared to avoid expensive sqrt when not needed.
    """
    dx = x2 - x1
    dy = y2 - y1

    if dx == 0 and dy == 0:
        return (px - x1)**2 + (py - y1)**2

    t = ((px - x1) * dx + (py - y1) * dy) / (dx*dx + dy*dy)
    t = max(0, min(1, t))

    closest_x = x1 + t * dx
    closest_y = y1 + t * dy

    return (px - closest_x)**2 + (py - closest_y)**2

def check_capsule_circle_collision(p1, p2, thickness, center, radius):
    """
    Checks if the blade (capsule shape) intersects a fruit (circle).
    p1, p2   : blade segment start and end points as (x, y)
    thickness: how wide/thick the blade is
    center   : fruit center as (x, y)
    radius   : fruit radius
    """
    dist_sq   = point_line_segment_distance_sq(
                    center[0], center[1],
                    p1[0], p1[1],
                    p2[0], p2[1]
                )
    threshold = (thickness + radius) ** 2
    return dist_sq <= threshold
