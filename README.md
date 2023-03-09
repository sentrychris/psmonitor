# Pi Monitor Websocket Server

This is the websocket server used for sending data to and from the [Pi Monitor](https://github.com/chrisrowles/pi-monitor-v3).

## Requirements

- Python 3
- Supervisor (required if you would like to run the websocket server process as a daemon)

## Set Up

1. Clone this repository:
    ```sh
    git clone https://github.com/chrisrowles/pi-monitor-wss.git
    ```

2. Install dependencies:
    ```sh
    pip install -r requirements.txt
    ```

3. Run the server:
    ```sh
    python manage.py run
    ```

### Testing it works

Pi Monitor WSS comes with a simple frontend to test the websocket connection:

![Image](https://i.imgur.com/d52ULxS.png)

### Running in the background

If you would like to run the server in the background, you can use the supervisor script provided.

1. Copy the supervisor script:
    ```sh
    cp ./supervisor/monitor.supervisor /etc/supervisor/conf.d/
    ```

2. Make any necessary changes (for example, you might need to modify the filepath in the command):
    ```conf
    [program:pi-monitor-websoscket]
    process_name = pi-monitor-websocket-%(process_num)s
    command = python /var/www/tornado-websocket/manage.py --daemon
    stdout_logfile=/var/log/supervisor/%(program_name)s-%(process_num)s.log
    numprocs = 1
    numprocs_start = 9005
    ```

2. Start supervisor
    ```sh
    supervisord
    ```

### Next steps

To connect to the websocket server, you first have to make an XHR POST request to retrieve an assigned worker. For example:
```js
const client = await fetch(location.pathname, {
    method: 'POST',
    body: { connection: 'monitor' }
});

const worker = await client.json()
```

Once you have your assigned worker, you can proceed to open the websocket connection and retrieve data:
```js
const url = `ws://{{WSS_URL}}:{{WSS_PORT}}/ws?id=${worker.id}`;

connection = new WebSocket(url);

connection.onopen = () => {
    log.write('event', 'websocket is connected');
}

connection.onmessage = (response) => {
    const data = JSON.parse(response.data);
}
```

You can use the frontend client located at `public/index.html` to find out more.

If you are using the [Pi Monitor](https://github.com/chrisrowles/pi-monitor-v3), there are instructions contained there to help you get setup and connected.

I hope you like it!

## Contributing

Feel free to contribute to this project, or the [Pi Monitor](https://github.com/chrisrowles/pi-monitor-v3), or the [Pi Monitor API](https://github.com/chrisrowles/pi-monitor-api).

I'm alaways looking for help and new ideas, this is a fun personal project and so if you're a bit new of a bit anxious about contributing to projects, then please feel free to get in tocuh with me and we'll find a way to get you started, we all start somewhere! :)

## License
This software is open-sourced software licensed under the MIT license.
