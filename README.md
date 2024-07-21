
# psutil-websocket-monitor

A simple system and network monitoring solution with real-time data transmission via a websocket server. This project was originally designed for connecting with the [Pi Monitor](https://github.com/sentrychris/pi-monitor-v3), however it can be used on any generic system.

This project includes [psutil](https://pypi.org/project/psutil/) scripts for gathering system and network statistics, and a [tornado](https://pypi.org/project/tornado/)-based websocket server for transmitting these statistics to connected clients.

## Requirements

- Python 3
- Supervisor (required if you would like to run the websocket server process as a daemon)

## Features

- **Asynchronous Data Collection**: Utilizes asyncio and ThreadPoolExecutor for efficient, non-blocking data collection.
- **Real-Time Monitoring**: Transmits live system and network statistics to clients via WebSocket.
- **System Statistics**: Provides CPU usage, memory usage, disk usage, system uptime, and top processes by memory usage.
- **Network Statistics**: Monitors data sent and received on a specified network interface.
- **Websocket Server**: Tornado-based server for real-time data transmission.

## Quick Start

1. Clone this repository:
    ```sh
    git clone git@github.com:sentrychris/psutil-websocket-monitor.git
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the server:
    ```sh
    python manage.py run --port=<port> --address=<address>
    ```

### Testing it works

The websocket server comes with a simple frontend to test the websocket connection:

![Image](https://i.imgur.com/d52ULxS.png)

### Running in the background

If you would like to run the server in the background, you can use the supervisor script provided.

1. Copy the supervisor script:
    ```sh
    cp ./supervisor/monitor.supervisor /etc/supervisor/conf.d/
    ```

2. Make any necessary changes (for example, you might need to modify the filepath in the command):
    ```conf
    [program:psutil-websocket-monitor]
    process_name = psutil-websocket-monitor-%(process_num)s
    command = python /var/www/psutil-websocket-monitor/manage.py --daemon
    stdout_logfile=/var/log/supervisor/%(program_name)s-%(process_num)s.log
    numprocs = 1
    numprocs_start = 9005
    ```

3. Start supervisor
    ```sh
    supervisord
    ```

### Next steps

To connect to the WebSocket server, you can use any WebSocket client. Here is an example of how to connect using JavaScript:

1. Retrieve the assigned worker:

    ```js
    const client = await fetch(`http://<server-address>`, {
        method: 'POST',
        body: { connection: 'monitor' }
    });
    const worker = await client.json()
    ```

2. Open the WebSocket connection and retrieve data:
    ```js
    const url = `ws://<server-address>:<port>/ws?id=${worker.id}`;

    connection = new WebSocket(url);
    connection.onopen = () => {
        log.write('event', 'websocket is connected');
    }
    connection.onmessage = (response) => {
        const data = JSON.parse(response.data);
    }
    ```

You can also use WebSocket clients in other programming languages, such as Python, to connect to the server:

1. Retrieve an assigned worker:

    ```python
    import requests

    response = requests.post('http://<server-address>', json={'connection': 'monitor'})
    worker = response.json()
    ```

2. Open the WebSocket connection and retrieve data:
    ```python
    import asyncio
    import websockets

    async def connect():
        uri = f"ws://<server-address>:<port>/ws?id={worker['id']}"
        async with websockets.connect(uri) as websocket:
            async for message in websocket:
                print(message)

    asyncio.run(connect())
    ```

You can use the frontend client located at `public/index.html`  for further testing and exploration.

If you are using the [Pi Monitor](https://github.com/chrisrowles/pi-monitor-v3), there are instructions contained there to help you get setup and connected.

I hope you like it!

## Contributing

Feel free to contribute to this project, or the [Pi Monitor](https://github.com/chrisrowles/pi-monitor-v3), or the [Pi Monitor API](https://github.com/chrisrowles/pi-monitor-api).

I'm always looking for help and new ideas, this is a fun personal project and so if you're a bit new of a bit anxious about contributing to projects, then please feel free to get in tocuh with me and we'll find a way to get you started, we all start somewhere! :)

## License
This software is open-sourced software licensed under the MIT license.
