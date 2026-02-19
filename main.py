import serial
import time
import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
from collections import deque

# Configure the page
st.set_page_config(
    page_title="Serial Data Monitor",
    page_icon="📊",
    layout="wide"
)

# Initialize session state for data storage
if 'timestamps' not in st.session_state:
    st.session_state.timestamps = deque(maxlen=100)
if 'temperatures' not in st.session_state:
    st.session_state.temperatures = deque(maxlen=100)
if 'humidities' not in st.session_state:
    st.session_state.humidities = deque(maxlen=100)
if 'serial_connected' not in st.session_state:
    st.session_state.serial_connected = False
if 'ser' not in st.session_state:
    st.session_state.ser = None

# Title
st.title("📊 Real-Time Serial Data Monitor")
st.markdown("---")

# Sidebar for configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    serial_port = st.text_input("Serial Port", value="COM8", help="e.g., COM5 (Windows) or /dev/ttyUSB0 (Linux)")
    baud_rate = st.selectbox("Baud Rate", [9600, 19200, 38400, 57600, 115200], index=4)
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("🔌 Connect", use_container_width=True):
            try:
                if st.session_state.ser and st.session_state.ser.is_open:
                    st.session_state.ser.close()
                st.session_state.ser = serial.Serial(serial_port, baud_rate, timeout=1)
                time.sleep(2)
                st.session_state.serial_connected = True
                st.success(f"Connected to {serial_port}")
            except serial.SerialException as e:
                st.error(f"Error: {e}")
                st.session_state.serial_connected = False
    
    with col2:
        if st.button("🔴 Disconnect", use_container_width=True):
            if st.session_state.ser and st.session_state.ser.is_open:
                st.session_state.ser.close()
                st.session_state.serial_connected = False
                st.info("Disconnected")
    
    st.markdown("---")

    # ✅ เพิ่ม threshold settings
    st.header("🚨 Alert Thresholds")
    temp_max = st.number_input("Max Temperature (°C)", value=35.0, step=0.5)
    temp_min = st.number_input("Min Temperature (°C)", value=10.0, step=0.5)
    hum_max = st.number_input("Max Humidity (%)", value=80.0, step=1.0)
    hum_min = st.number_input("Min Humidity (%)", value=20.0, step=1.0)

    st.markdown("---")
    
    if st.button("🗑️ Clear Data"):
        st.session_state.timestamps.clear()
        st.session_state.temperatures.clear()
        st.session_state.humidities.clear()
        st.rerun()
    
    st.markdown("---")
    st.markdown("### 📈 Data Points")
    st.metric("Readings", len(st.session_state.timestamps))

# Main content area
if st.session_state.serial_connected:
    st.success("✅ Serial port connected and reading data...")
    
    # Read data from serial port
    try:
        if st.session_state.ser and st.session_state.ser.is_open:
            raw_data = st.session_state.ser.readline()
            print(f"Raw data: {raw_data}")

            if raw_data:
                decoded_data = raw_data.decode('utf-8').strip().split()
                if len(decoded_data) >= 3:
                    timestamp_ms = decoded_data[0]
                    temperature = float(decoded_data[1])
                    humidity = float(decoded_data[2])
                    current_time = datetime.now()
                    st.session_state.timestamps.append(current_time)
                    st.session_state.temperatures.append(temperature)
                    st.session_state.humidities.append(humidity)

    except Exception as e:
        st.error(f"Error reading data: {e}")

    # ✅ ตรวจสอบและแสดง Alert Banner
    if st.session_state.temperatures and st.session_state.humidities:
        current_temp = st.session_state.temperatures[-1]
        current_hum = st.session_state.humidities[-1]

        alerts = []
        if current_temp > temp_max:
            alerts.append(f"🌡️ Temperature สูงเกินกำหนด! **{current_temp:.1f}°C** > {temp_max}°C")
        if current_temp < temp_min:
            alerts.append(f"🌡️ Temperature ต่ำเกินกำหนด! **{current_temp:.1f}°C** < {temp_min}°C")
        if current_hum > hum_max:
            alerts.append(f"💧 Humidity สูงเกินกำหนด! **{current_hum:.1f}%** > {hum_max}%")
        if current_hum < hum_min:
            alerts.append(f"💧 Humidity ต่ำเกินกำหนด! **{current_hum:.1f}%** < {hum_min}%")

        if alerts:
            for alert in alerts:
                st.error(f"🚨 ALERT: {alert}")  # Banner สีแดง
        else:
            st.success("✅ ค่าทั้งหมดอยู่ในช่วงปกติ")

    # Create containers
    metrics_container = st.container()
    chart_container = st.container()
    data_container = st.container()

    # Display metrics
    with metrics_container:
        col1, col2, col3 = st.columns(3)
        
        with col1:
            if st.session_state.temperatures:
                current_temp = st.session_state.temperatures[-1]
                # ✅ ไฮไลท์สีที่ label ถ้าผิดปกติ
                temp_label = "🌡️ Temperature 🚨" if (current_temp > temp_max or current_temp < temp_min) else "🌡️ Temperature"
                st.metric(
                    temp_label,
                    f"{current_temp:.1f}°C",
                    delta=f"{current_temp - st.session_state.temperatures[-2]:.1f}°C" if len(st.session_state.temperatures) > 1 else None
                )
            else:
                st.metric("🌡️ Temperature", "-- °C")

        with col2:
            if st.session_state.humidities:
                current_hum = st.session_state.humidities[-1]
                hum_label = "💧 Humidity 🚨" if (current_hum > hum_max or current_hum < hum_min) else "💧 Humidity"
                st.metric(
                    hum_label,
                    f"{current_hum:.1f}%",
                    delta=f"{current_hum - st.session_state.humidities[-2]:.1f}%" if len(st.session_state.humidities) > 1 else None
                )
            else:
                st.metric("💧 Humidity", "-- %")

        with col3:
            if st.session_state.timestamps:
                st.metric("🕒 Last Update", st.session_state.timestamps[-1].strftime("%H:%M:%S"))
            else:
                st.metric("🕒 Last Update", "--")

    # Display charts
    with chart_container:
        if st.session_state.timestamps:
            df = pd.DataFrame({
                'Time': list(st.session_state.timestamps),
                'Temperature': list(st.session_state.temperatures),
                'Humidity': list(st.session_state.humidities)
            })

            # Temperature chart with threshold lines
            st.subheader("🌡️ Temperature Over Time")
            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=df['Time'], y=df['Temperature'],
                mode='lines+markers', name='Temperature',
                line=dict(color='#FF6B6B', width=2), marker=dict(size=6)
            ))
            # ✅ เส้น threshold บนกราฟ
            fig_temp.add_hline(y=temp_max, line_dash="dash", line_color="red", annotation_text=f"Max {temp_max}°C")
            fig_temp.add_hline(y=temp_min, line_dash="dash", line_color="blue", annotation_text=f"Min {temp_min}°C")
            fig_temp.update_layout(xaxis_title="Time", yaxis_title="Temperature (°C)", hovermode='x unified', height=300)
            st.plotly_chart(fig_temp, use_container_width=True)

            # Humidity chart with threshold lines
            st.subheader("💧 Humidity Over Time")
            fig_hum = go.Figure()
            fig_hum.add_trace(go.Scatter(
                x=df['Time'], y=df['Humidity'],
                mode='lines+markers', name='Humidity',
                line=dict(color='#4ECDC4', width=2), marker=dict(size=6)
            ))
            # ✅ เส้น threshold บนกราฟ
            fig_hum.add_hline(y=hum_max, line_dash="dash", line_color="red", annotation_text=f"Max {hum_max}%")
            fig_hum.add_hline(y=hum_min, line_dash="dash", line_color="blue", annotation_text=f"Min {hum_min}%")
            fig_hum.update_layout(xaxis_title="Time", yaxis_title="Humidity (%)", hovermode='x unified', height=300)
            st.plotly_chart(fig_hum, use_container_width=True)

    # Data table
    with data_container:
        if st.session_state.timestamps:
            st.subheader("📋 Recent Data")
            df_display = pd.DataFrame({
                'Time': [t.strftime("%H:%M:%S") for t in list(st.session_state.timestamps)[-10:]],
                'Temperature (°C)': [f"{t:.1f}" for t in list(st.session_state.temperatures)[-10:]],
                'Humidity (%)': [f"{h:.1f}" for h in list(st.session_state.humidities)[-10:]]
            })
            st.dataframe(df_display, use_container_width=True, hide_index=True)

    time.sleep(1)
    st.rerun()

else:
    st.info("👈 Please connect to a serial port using the sidebar to start monitoring data.")
    st.markdown("### 📝 Expected Data Format")
    st.code("['114538', '21.6', '74.2']", language="python")
    st.markdown("""
    - First value: Timestamp (milliseconds)
    - Second value: Temperature (°C)
    - Third value: Humidity (%)
    """)

# Cleanup
if st.session_state.ser and st.session_state.ser.is_open:
    try:
        st.session_state.ser.close()
    except:
        pass