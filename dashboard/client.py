import streamlit as st
import asyncio
from asyncua import Client
import time

st.set_page_config(page_title="MES Digital Twin", layout ="wide")

async def get_factory_data():
    url = "opc.tcp://127.0.0.1:4840/freeopcua/server/"
    try:
        async with Client(url=url) as client:
            uri = "http://factory.simulation.github.io"
            idx = await client.get_namespace_index(uri)

            state_node = await client.nodes.objects.get_child(
                [f"{idx}:Machine_1", f"{idx}:Machine_State"]
            )
            parts_node = await client.nodes.objects.get_child(
                [f"{idx}:Machine_1", f"{idx}:Parts_Produced"]
            )

            current_state = await state_node.read_value()
            parts_produced = await parts_node.read_value()

            return current_state, parts_produced
    except Exception as e:
        return f"ERROR: {str(e)}", 0
    
st.title("Smart Factory MES Dashboard")
st.markdown("Real-time telemetry from the Godot Edge Simulation")
st.markdown("---")

col1, col2 = st.columns(2)
state, parts = asyncio.run(get_factory_data())

with col1:
    st.metric(label="Machine Status", value=state)
    if "ERROR" in str(state):
        st.error(state)
    if state == "FAULT":
        st.error("Machine Breakdown Detected!")
    elif state == "PROCESSING":
        st.info("Machine is currently processing material.")
    elif state == "IDLE":
        st.warning("Machine is idle, Awaiting materials.")

with col2:
    st.metric(label="Total Parts Produced", value=parts)

time.sleep(0.2)
st.rerun()
