
```
# Feed the Tool: Replace Typed Input with Virtual Sensor Data

## Project Overview
This project upgrades an existing engineering tool by replacing manual user input with simulated sensor data (CSV Replay from Module 5.1). The system filters raw sensor streams through validation rules before feeding valid measurements into the engineering solver.

---

## Workflow Architecture

```

[Virtual Sensor / CSV] ──> [Raw Reading] ──> [Validation & Filtering] ──> [Accepted Value] ──> [Engineering Solver] ──> [Result Log]
│
└──> [Rejected Status & Reason]

```

---

## Sensor Integration & Validation Rules
The tool applies a **Two-Tiered Filtering Rule** to validate raw incoming readings:

1. **Hardware Failure Check:** Rejects any reading with a `MISSING` firmware status or empty value.
2. **Absolute Range Filter:** Accepts only values within the operational temperature bounds (**0.0 °C to 50.0 °C**).
3. **Rate of Change (Delta) Filter:** Rejects readings that deviate by more than **±5.0 °C** from the previous valid sample to eliminate noise spikes.

---

## Assumptions Broken by Sensor Input

| Original Assumption | What the Sensor Did | Software Change Implemented |
| :--- | :--- | :--- |
| **Input always exists** | Sensor readings dropped to negative values or became unavailable (`MISSING` state). | Added explicit missing-value check (`REJECTED_MISSING`) that halts calculation safely instead of throwing errors. |
| **Input is always valid** | Sensor produced extreme high values exceeding 400 °C (`OUT_OF_RANGE`). | Added an Absolute Range Filter (0 °C to 50 °C) before passing inputs to calculation logic. |
| **Input is static unless edited by user** | Sensor values arrived continuously at 1 Hz frequency. | Implemented automated CSV stream iteration/replay instead of static user form input. |
| **Input changes smoothly / is stable** | Sensor introduced physical spikes (> 400 °C jumps in 1 second). | Added Rate of Change (Delta) filter rejecting deviations greater than ±5.0 °C. |
| **Input is always trusted** | Raw sensor readings contained electrical noise and hardware disconnections. | Created a clear separation between raw inputs and accepted filtered inputs for full auditability. |

---

## Traceability & Data Logging
The application retains full auditability by keeping raw readings and filtered output separate. Each sample is logged with:
* `sample_number`: Sequence identifier.
* `raw_value`: Unfiltered temperature/sensor reading.
* `firmware_status`: Initial status from Arduino (`OK`, `OUT_OF_RANGE`, `MISSING`).
* `validation_status`: Filtering result (`ACCEPTED`, `REJECTED_OUT_OF_RANGE`, `REJECTED_MISSING`, `REJECTED_HIGH_DELTA`).
* `accepted_value`: Filtered value passed to solver (or `None`).
* `calculated_radius`: Final output produced by original engineering calculation.

---

## File Structure
* `app.py` - Interactive Streamlit web interface with CSV stream processing and visual logs.
* `sensor_readings.csv` - Replay dataset containing 101 simulated sensor readings.
* `src/sensor_integration.py` - Validation, filtering, and CSV dataset replay engine.
* `tests/test_sensor_integration.py` - Automated test suite covering normal, boundary, spike, and failure cases.
* `requirements.txt` - Dependencies required to run the project.
* `README.md` - Documentation, architecture overview, and broken assumptions analysis.

---

## How to Run
1. Install dependencies:
   ```bash
   pip install -r requirements.txt

```

2. Launch Streamlit interface:
```bash
streamlit run app.py

```


3. Run automated tests:
```bash
pytest

```



```

```