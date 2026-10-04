import streamlit as st
import pandas as pd
from src.sensor_integration import process_sensor_dataset, SensorStatus

st.set_page_config(page_title="Sensor-Driven Tank Sizing Tool", layout="wide")

st.title("⚙️ Sensor-Driven Iterative Tank Sizing Tool")
st.markdown("Automated engineering calculation tool fed by real-time virtual sensor data (CSV Replay).")

st.sidebar.header("Sensor Input Source")
uploaded_file = st.sidebar.file_uploader("Upload Sensor Dataset (.csv)", type=["csv"])

if uploaded_file is not None:
    # Save temporary CSV file for processing
    with open("temp_sensor_data.csv", "wb") as f:
        f.write(uploaded_file.getbuffer())

    if st.sidebar.button("Process Sensor Stream", type="primary"):
        # Process sensor stream using default system parameters (Volume=100.0, Height=5.0)
        logs = process_sensor_dataset("temp_sensor_data.csv", target_volume=100.0, height=5.0)
        df_logs = pd.DataFrame(logs)

        # Summary Metrics
        total_samples = len(df_logs)
        accepted_samples = len(df_logs[df_logs["validation_status"] == SensorStatus.ACCEPTED])
        rejected_samples = total_samples - accepted_samples

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Sensor Samples", total_samples)
        col2.metric("Accepted Readings (Fed to Tool)", accepted_samples)
        col3.metric("Rejected Readings (Filtered)", rejected_samples)

        st.subheader("Raw vs. Accepted Value Traceability Log")
        st.dataframe(df_logs, use_container_width=True)

        # Filtered Visualization
        accepted_df = df_logs[df_logs["validation_status"] == SensorStatus.ACCEPTED]
        if not accepted_df.empty:
            st.subheader("Calculated Output Trajectory (Accepted Readings)")
            st.line_chart(accepted_df.set_index("sample_number")[["accepted_value", "calculated_radius"]])
else:
    st.info("Please upload your `sensor_readings.csv` file from the sidebar to begin testing.")