import DBUtils from "./data.js";
import WebSocket, { WebSocketServer } from 'ws';


/**
 * Get completion from OpenAI
 * @param username
 * @param message
 */
async function chatgpt(username: string, message: string): Promise<string> {
  console.log("尝试连接ChatGPT");

  // 先将用户输入的消息添加到数据库中
  // DBUtils.addUserMessage(username, message);
  // const messages = DBUtils.getChatMessage(username);

  // 打开连接
  var ws = new WebSocket("ws://localhost:14514");

  // 发送数据
  ws.onopen = function () {
    // 使用send()方法发送数据
    ws.send("friend-" + username + ":::" + message+":::False");
  };

  // 接收数据
  const res: string = await new Promise((resolve, reject) => {
   
      ws.onmessage = function (evt) {

        console.log("Received Message " + evt.data);
        
        ws.close();
        
        var received_msg = evt.data.toString();
        resolve(received_msg);
    }
  });

  if (res) {
    return res;
  } else {
    return "Something went wrong";
  }

}

/**
 * Get image from Dall·E
 * @param username
 * @param prompt
 */
async function dalle(username: string, prompt: string) {
  return "Not implemented yet"
}

/**
 * Speech to text
 * @param username
 * @param videoPath
 */
async function whisper(username: string, videoPath: string): Promise<string> {
  return "Not implemented yet"
}

export { chatgpt, dalle, whisper };