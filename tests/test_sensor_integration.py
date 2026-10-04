import pytest
from src.sensor_integration import (
    validate_and_filter_sensor_reading,
    process_sensor_dataset,
    SensorStatus
)


def test_normal_sensor_reading():
    res = validate_and_filter_sensor_reading(20.4, "OK")
    assert res["status"] == SensorStatus.ACCEPTED
    assert res["accepted_value"] == 20.4


def test_missing_sensor_reading():
    res = validate_and_filter_sensor_reading(-8.5, "MISSING")
    assert res["status"] == SensorStatus.REJECTED_MISSING
    assert res["accepted_value"] is None


def test_out_of_range_reading():
    res = validate_and_filter_sensor_reading(78.1, "OUT_OF_RANGE")
    assert res["status"] == SensorStatus.REJECTED_OUT_OF_RANGE
    assert res["accepted_value"] is None


def test_suspicious_spike_delta():
    # Reading jumps from 20.4 to 30.0 (delta = 9.6 > 5.0)
    res = validate_and_filter_sensor_reading(30.0, "OK", last_accepted_value=20.4)
    assert res["status"] == SensorStatus.REJECTED_HIGH_DELTA
    assert res["accepted_value"] is None


def test_process_sensor_dataset_flow(tmp_path):
    # Create a temporary mini CSV dataset for integration test
    csv_file = tmp_path / "test_readings.csv"
    csv_file.write_text(
        "sample_number,temperature_c,status\n"
        "1,20.4,OK\n"
        "2,78.1,OUT_OF_RANGE\n"
        "3,-8.5,MISSING\n"
    )

    logs = process_sensor_dataset(str(csv_file), target_volume=100.0, height=5.0)
    assert len(logs) == 3
    assert logs[0]["validation_status"] == SensorStatus.ACCEPTED
    assert logs[1]["validation_status"] == SensorStatus.REJECTED_OUT_OF_RANGE
    assert logs[2]["validation_status"] == SensorStatus.REJECTED_MISSING