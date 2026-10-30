from datetime import time

START_HOUR = 7    # first row starts at 7:00 AM
END_HOUR = 21     # last row ends at 9:00 PM
STEP = 30         # minutes per cell (30 or 60 work well)

DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def block_starts():
    return list(range(START_HOUR * 60, END_HOUR * 60, STEP))


def to_time(minutes):
    return time(minutes // 60, minutes % 60)


def minutes_of(t):
    return t.hour * 60 + t.minute


def label(minutes):
    h, m = divmod(minutes, 60)
    suffix = "AM" if h < 12 else "PM"
    return f"{h % 12 or 12}:{m:02d} {suffix}"


def slots_to_blocks(slots):
    """Turn saved slots into a set of (day, start_minute) grid cells."""
    blocks = set()
    for s in slots:
        start, end = minutes_of(s.start_time), minutes_of(s.end_time)
        for m in block_starts():
            if start <= m < end:
                blocks.add((s.day, m))
    return blocks


def blocks_to_ranges(blocks):
    """Merge neighboring cells into (day, start_minute, end_minute) ranges."""
    ranges = []
    for day in range(7):
        mins = sorted(m for d, m in blocks if d == day)
        run_start = prev = None
        for m in mins:
            if run_start is None:
                run_start = prev = m
            elif m == prev + STEP:
                prev = m
            else:
                ranges.append((day, run_start, prev + STEP))
                run_start = prev = m
        if run_start is not None:
            ranges.append((day, run_start, prev + STEP))
    return ranges


def build_rows(blocks):
    rows = []
    for m in block_starts():
        rows.append({
            "minutes": m,
            "hour": m % 60 == 0,
            "label": label(m) if m % 60 == 0 else "",
            "cells": [{"day": d, "on": (d, m) in blocks} for d in range(7)],
        })
    return rows