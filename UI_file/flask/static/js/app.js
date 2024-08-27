document.addEventListener("DOMContentLoaded", () => {
    // WebSocket 연결 설정
    var socket = io.connect('http://' + document.domain + ':' + location.port);

    // 서버에 제어 명령을 보내는 함수
    function sendControlCommand(command) {
        console.log('제어 명령 전송:', command);
        socket.emit('control_command', { command: command });
    }

    // 서버로부터 응답을 수신하는 이벤트 리스너
    socket.on('robot_response', function(data) {
        console.log('로봇 응답:', data);
        document.getElementById('response').innerText = data.status;
    });

    // sendControlCommand 함수를 전역 범위에 노출
    window.sendControlCommand = sendControlCommand;
});