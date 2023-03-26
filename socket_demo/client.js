// 在 Node.js 中，您可以使用 `net` 模块来创建 TCP 或 Unix 域套接字客户端和服务器。下面是一个简单的示例 TCP 客户端：

const net = require('net');

// 创建客户端
const client = new net.Socket();

// 连接到服务器
client.connect(43999, 'localhost', function() {
    console.log('已连接到服务器');

    // 发送数据到服务器
    client.write('Hello, server!');
});

// 监听服务器发送的数据
client.on('data', function(data) {
    console.log('收到来自服务器的数据: ' + data);
});

// 监听服务器关闭连接
client.on('close', function() {
    console.log('已从服务器断开连接');
});

// 在这个示例中，我们首先引入了 `net` 模块，并创建了一个 `net.Socket` 对象。然后，我们使用 `client.connect()` 方法连接到服务器，并在连接成功后发送一条消息。接着，我们监听了 `data` 事件，当从服务器接收到数据时就会触发该事件并输出接收到的数据。最后，我们监听了 `close` 事件，在连接关闭时输出已断开连接的消息。

// 要注意的是，这只是一个基本的示例，您可能需要根据自己的需求修改代码来实现更加完整和稳健的客户端应用程序。另外，在生产环境中，您需要考虑网络安全性和错误处理等方面的问题。
