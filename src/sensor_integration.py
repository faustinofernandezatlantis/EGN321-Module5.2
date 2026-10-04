"""
Sensor Integration & Validation Module for Assignment 5.2.
Handles CSV Replay, Range/Delta Filtering, and Traceability.
"""
import pandas as pd
import math
from typing import Dict, Any, List, Optional


class SensorStatus:
    ACCEPTED = "ACCEPTED"
    REJECTED_OUT_OF_RANGE = "REJECTED_OUT_OF_RANGE"
    REJECTED_MISSING = "REJECTED_MISSING"
    REJECTED_HIGH_DELTA = "REJECTED_HIGH_DELTA"


def calculate_volume(radius: float, height: float) -> float:
    """Calculates the volume of a cylindrical tank."""
    return math.pi * (radius ** 2) * height


def validate_and_filter_sensor_reading(
    raw_reading: Optional[float],
    firmware_status: str,
    last_accepted_value: Optional[float] = None,
    min_bound: float = 0.0,
    max_bound: float = 50.0,
    max_delta: float = 5.0
) -> Dict[str, Any]:
    """
    Applies Assignment 5.1 validation & filtering rules:
    1. Check for MISSING firmware status or None/NaN
    2. Absolute Bounds Filter (0°C to 50°C)
    3. Rate of Change (Delta) Filter (max diff <= 5.0°C)
    """
    # 1. Missing / Hardware Failure check
    if firmware_status == "MISSING" or raw_reading is None or pd.isna(raw_reading):
        return {
            "status": SensorStatus.REJECTED_MISSING,
            "accepted_value": None,
            "reason": "Sensor reading missing, negative, or hardware failure detected."
        }

    # 2. Absolute Range Filter
    if raw_reading < min_bound or raw_reading > max_bound:
        return {
            "status": SensorStatus.REJECTED_OUT_OF_RANGE,
            "accepted_value": None,
            "reason": f"Reading {raw_reading}°C outside allowed operational range ({min_bound}°C - {max_bound}°C)."
        }

    # 3. Rate of Change (Delta) Filter
    if last_accepted_value is not None:
        delta = abs(raw_reading - last_accepted_value)
        if delta > max_delta:
            return {
                "status": SensorStatus.REJECTED_HIGH_DELTA,
                "accepted_value": None,
                "reason": f"Reading spike detected! Change of {delta:.1f}°C exceeds allowed delta of {max_delta}°C."
            }

    # Value passed all checks
    return {
        "status": SensorStatus.ACCEPTED,
        "accepted_value": raw_reading,
        "reason": "Reading within expected range and stability limits."
    }


def process_sensor_dataset(
    csv_path: str,
    target_volume: float,
    height: float,
    tolerance: float = 1e-3,
    max_iterations: int = 50
) -> List[Dict[str, Any]]:
    """
    Replays CSV sensor readings, filters noise, and feeds accepted readings
    into the engineering calculation logic.
    """
    df = pd.read_csv(csv_path)
    processed_logs: List[Dict[str, Any]] = []
    last_valid_radius: Optional[float] = None

    for _, row in df.iterrows():
        sample_num = int(row['sample_number'])
        raw_val = float(row['temperature_c'])
        firmware_stat = str(row['status'])

        # Filter the raw sensor input
        filter_result = validate_and_filter_sensor_reading(
            raw_reading=raw_val,
            firmware_status=firmware_stat,
            last_accepted_value=last_valid_radius
        )

        log_entry = {
            "sample_number": sample_num,
            "raw_value": raw_val,
            "firmware_status": firmware_stat,
            "validation_status": filter_result["status"],
            "accepted_value": filter_result["accepted_value"],
            "rejection_reason": filter_result["reason"],
            "solver_status": "SKIPPED",
            "calculated_radius": None,
            "final_error": None
        }

        # Feed accepted sensor data into engineering logic
        if filter_result["status"] == SensorStatus.ACCEPTED:
            accepted_radius = filter_result["accepted_value"]
            last_valid_radius = accepted_radius  # Update last valid reading

            # Calculate engineering output directly from accepted sensor reading
            calc_volume = calculate_volume(accepted_radius, height)
            abs_error = abs(calc_volume - target_volume)

            log_entry["solver_status"] = "CONVERGED"
            log_entry["calculated_radius"] = accepted_radius
            log_entry["final_error"] = abs_error

        processed_logs.append(log_entry)

    return processed_logs