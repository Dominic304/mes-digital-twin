import asyncio
from asyncua import Server

async def main():
    #initialize
    server = Server()
    await server.init()
    server.set_endpoint("opc.tcp://127.0.0.1:4840/freeopcua/server/")
    server.set_server_name("Factory Digital Twin Server")

    uri = "http://factory.simulation.github.io"
    idx = await server.register_namespace(uri)
    myobj = await server.nodes.objects.add_object(idx, "Machine_1")
    state_var = await myobj.add_variable(idx, "Machine_State", "IDLE")

   
    await state_var.set_writable()

    print("Hello from Python! OPC UA Server Started at opc.tcp://127.0.0.1:4840/")

    
    async with server:
        while True:
            await asyncio.sleep(1)

if __name__ == "__main__":
    asyncio.run(main())