const net = require('net');

const server = net.createServer((socket) => {
  console.log('客户端已连接');

  socket.on('data', (data) => {
    console.log(`接收到客户端的数据: ${data}`);
    socket.write('已收到您的消息！');
  });

  socket.on('end', () => {
    console.log('客户端已断开连接');
  });

  socket.write('欢迎使用 Socket 服务器！');
});

server.listen(8765, () => {
  console.log('Socket 服务器已启动');
});