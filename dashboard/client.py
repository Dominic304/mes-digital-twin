import streamlit as st
import asyncio
from asyncua import Client
import time

st.set_page_config(page_title="MES Digital Twin", layout ="wide")

if 'temp_history' not in st.session_state:
    st.session_state.temp_history = []

async def get_factory_data():
    url = "opc.tcp://127.0.0.1:4840/freeopcua/server/"
    try:
        async with Client(url=url) as client:
            uri = "http://factory.simulation.github.io"
            idx = await client.get_namespace_index(uri)

            state_node = await client.nodes.objects.get_child([f"{idx}:Machine_1", f"{idx}:Machine_State"])
            parts_node = await client.nodes.objects.get_child([f"{idx}:Machine_1", f"{idx}:Parts_Produced"])
            scrap_node = await client.nodes.objects.get_child([f"{idx}:Machine_1", f"{idx}:Scrap_Produced"])
            temp_node = await client.nodes.objects.get_child([f"{idx}:Machine_1", f"{idx}:Machine_Temperature"])

            current_state = await state_node.read_value()
            parts_produced = await parts_node.read_value()
            scrap_produced = await scrap_node.read_value()
            current_temp = await temp_node.read_value()

            current_state = await state_node.read_value()
            parts_produced = await parts_node.read_value()

            return current_state, parts_produced, scrap_produced, current_temp
    except Exception as e:
        return f"ERROR: {str(e)}", 0, 0, 20
    
st.title("Smart Factory MES Dashboard")
st.markdown("Real-time telemetry from the Godot Edge Simulation")
st.markdown("---")


col1, col2, col3, col4 = st.columns(4)

state, parts, scrap, temp = asyncio.run(get_factory_data())

st.session_state.temp_history.append(temp)
if len(st.session_state.temp_history) > 60:
    st.session_state.temp_history.pop(0)

with col1:
    st.metric(label="Machine Status", value=state)
with col2:
    st.metric(label="Good Parts Produced", value=parts)
with col3:
    st.metric(label="Scrap Parts", value=scrap)
with col4:
    st.metric(label="Current Core Temp (°C)", value=f"{temp} °C", 
              delta=f"{temp - 90} from Overheat" if temp > 60 else "Safe")

col_alert, col_chart = st.columns([1, 2])

with col_alert:
    st.subheader("System Alerts")
    if state == "FAULT":
        st.error("CRITICAL: Machine Breakdown Detected!")
        if temp > 60:
            st.warning("Machine too hot for repairs! Awaiting cooling...")
    elif state == "PROCESSING":
        st.info("Machine is currently processing material.")
    elif state == "IDLE":
        st.warning("Machine is idle. Awaiting materials.")

with col_chart:
    st.subheader("Live Thermal Telemetry")
    st.line_chart(st.session_state.temp_history)

time.sleep(0.2)
st.rerun()
