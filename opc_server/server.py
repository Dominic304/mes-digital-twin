import asyncio
import json
from asyncua import Server, ua

machine_state_node = None
parts_produced_node = None
machine_temperature_node = None
scrap_produced_node = None

parts_count = 0
scrap_count = 0


class GodotUDPProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        global parts_count,scrap_count
        message = data.decode()

        try:
            payload = json.loads(message)
            event = payload.get("event")

            if event == "state" and machine_state_node:
                new_state = payload.get("value")
                print(f"Network Event -> State changed to: {new_state}")
                asyncio.create_task(machine_state_node.write_value(new_state))
            elif event == "produced" and parts_produced_node:
                parts_count += 1
                print(f"Network Event -> Part Produced! Total: {parts_count}")
                new_val = ua.Variant(parts_count, ua.VariantType.Int64)
                asyncio.create_task(parts_produced_node.write_value(new_val))
            elif event == "scrap" and scrap_produced_node:
                scrap_count += 1
                print(f"Network Event -> Scrap Produced! Total: {scrap_count}") 
                new_val = ua.Variant(scrap_count, ua.VariantType.Int64)
                asyncio.create_task(scrap_produced_node.write_value(new_val))       
            elif event == "temperature" and machine_temperature_node:
                temp_val = payload.get("value")
                print(f"Network Event -> Temp updated to: {temp_val}") 
                new_val = ua.Variant(temp_val, ua.VariantType.Int64)
                asyncio.create_task(machine_temperature_node.write_value(new_val))

        except Exception as e:
            print(f"Error parsing packet:{e}")
async def main():
    global machine_state_node, parts_produced_node, scrap_produced_node, machine_temperature_node
    
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840/freeopcua/server/")
    server.set_server_name("Factory Digital Twin Server")

    uri = "http://factory.simulation.github.io"
    idx = await server.register_namespace(uri)
    myobj = await server.nodes.objects.add_object(idx, "Machine_1")

    machine_state_node = await myobj.add_variable(idx, "Machine_State", "IDLE")
    parts_produced_node = await myobj.add_variable(idx, "Parts_Produced", 0)
    scrap_produced_node = await myobj.add_variable(idx, "Scrap_Produced", 0)
    machine_temperature_node = await myobj.add_variable(idx, "Machine_Temperature", 20)

    await machine_state_node.set_writable()
    await parts_produced_node.set_writable()
    await scrap_produced_node.set_writable()
    await machine_temperature_node.set_writable()

    loop = asyncio.get_running_loop()
    transport,protocol = await loop.create_datagram_endpoint(
    lambda: GodotUDPProtocol(), local_addr=('127.0.0.1',5005)
    )

    print("OPC UA Server started on opc.tcp://127.0.0.1:4840/")
    print("Listening for Godot UDP packets on port 5005...\n")

    async with server:
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())