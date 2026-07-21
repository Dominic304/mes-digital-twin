import asyncio
from asyncua import Client

async def main():
    url = "opc.tcp://127.0.0.1:4840/freeopcua/server/"
    print(f"Connecting to {url} ...")

    async with Client(url=url) as client:
        print("Hello from Client! Successfully connected to OPC UA Server.")

        uri = "http://factory.simulation.github.io"
        idx = await client.get_namespace_index(uri)

        state_var = await client.nodes.root.get_child(
            ["0:Objects", f"{idx}:Machine_1", f"{idx}:Machine_State"]
        )

        value = await state_var.read_value()
        print(f"Current Machine State from Server: {value}")

if __name__ == "__main__":
    asyncio.run(main())