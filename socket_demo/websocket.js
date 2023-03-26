const WebSocket = require('ws');

var loginInfo = "****heyhey*" ;

// 打开连接
var ws = new WebSocket("ws://localhost:8765");

// 发送数据
ws.onopen = function () {
    // 使用send()方法发送数据
    ws.send(loginInfo);
};

// 接收数据
ws.onmessage = function (evt) {
    var received_msg = evt.data;
    console.log(received_msg);
    // 作为一个好习惯，在接收完数据后就关闭连接，这样可以减少服务器的负担
    ws.close();
};

// 关闭连接后的事件
ws.onclose = function () {
};