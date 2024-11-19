# Netter Botnet: Command Creation Guide

This guide explains how to create and integrate custom commands for the Netter Botnet framework. Commands are modular and allow server-client interactions for a variety of purposes.

## Command Structure

Every command must follow a specific structure to work seamlessly with the Netter Botnet framework. Below are the required components:

### Key Attributes

- `__aliases__`:
  A list of strings defining alternative command names (e.g., `["screenshot", "ss"]`).
  These aliases can be used in the terminal.

- `__description__`:
  A short string describing the purpose of the command.

- `__extra__`:
  A string providing additional information or usage examples for the command.

## Required Functions

### 1. `execute(netServer: "NetterServer", *args) -> Union[bool, NetterClient]`

This function is the entry point for the command. It is called when the command is executed from the terminal.

- **Parameters**:
  - `netServer`: The `NetterServer` instance managing the botnet.
  - `*args`: Additional arguments passed with the command.

- **Returns**:
  - `False`, `None`, or nothing: Indicates incorrect usage or failure.
  - `NetterClient`: If the command is successful, this triggers a wait for the first incoming packet from the client.

- **Example**:
  ```python
  def execute(netServer: "NetterServer", *args) -> bool:
      if not args and not netServer.selectedClient:
          netServer.inputHandler.handle('help <command_name>')  # Show usage info
          return False

      client = netServer.get(UUID=args[0])  # Fetch the client by ID
      if client is None:
          netServer.console_log('Client not found.', level='ERROR')
          return False

      client.socket_.send_(packetType=PacketType.COMMAND, data='<command_data>')
      return client
    ```

### 2. `on_server_receive(netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse")`

Handles data received from the client after the command is executed.

- **Parameters**:
  - `netServer`: The `NetterServer` instance managing the botnet.
  - `client`: The `NetterClient` that sent the data.
  - `packet`: The packet received from the client, containing the response data.

- **Examples**:
  ```python
  def on_server_receive(netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse"):
    netServer.console_log(f"Received packet from {client.username} with data: {packet.data}")
  ```

### 3. `on_client_receive(serverHandler: "Connect")`

Executes the client-side logic for the command and sends the result back to the server.

- **Parameters**:
  -` serverHandler`: The `Connect` instance used to communicate with the server.

- **Examples:**
  ```python
  def on_client_receive(serverHandler: Connect):
    # Apply some logic here
    return b"Hello World!"
  ```

# Examples

```python
def execute(netServer: "NetterServer", *args):
    client: "NetterClient" = netServer.get(UUID = args[0])
    client.socket_.send_(b'Say hello world')
    return client

def on_client_receive(serverHandler: "Connect"):
    return "Hello World!"

def on_server_receive(netServer: "NetterServer", client: "NetterClient", packet: "ClientResponse"):
    netServer.console_log("Received packet from {} with data: {}".format(
        client.username,
        packet.data
    ))
```

## Command Debugging Tips

- Check Aliases: Ensure __aliases__ is unique and does not conflict with existing commands.
- Error Logging: Use netServer.console_log for clear error messages during execution.
- Packet Handling: Ensure the data sent by the client matches what the server expects.
