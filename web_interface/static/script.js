function restartBot() {
    const socket = new WebSocket("ws://localhost:8000/ws");
    socket.onopen = () => {
        socket.send("restart");
    };
    socket.onmessage = (event) => {
        alert(event.data);
    };
}
