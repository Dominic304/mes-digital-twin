import asyncio
import json
from asyncua import Server

machine_state_node = None
parts_produced_node = None
parts_count = 0

class GodotUDPProtocol(asyncio.DatagramProtocol):
    def datagram_received(self, data, addr):
        global parts_count
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
                asyncio.create_task(parts_produced_node.write_value(parts_count))
        except Exception as e:
            print(f"Error parsing packet:{e}")
async def main():
    global machine_state_node, parts_produced_node
    
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840/freeopcua/server/")
    server.set_server_name("Factory Digital Twin Server")

    uri = "http://factory.simulation.github.io"
    idx = await server.register_namespace(uri)
    myobj = await server.nodes.objects.add_object(idx, "Machine_1")

    machine_state_node = await myobj.add_variable(idx, "Machine_State", "IDLE")
    parts_produced_node = await myobj.add_variable(idx, "Parts_Produced",0)

    await machine_state_node.set_writable()
    await parts_produced_node.set_writable()

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