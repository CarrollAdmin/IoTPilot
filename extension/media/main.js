document.addEventListener("DOMContentLoaded", function() {
    console.log("JavaScript is working!");
});

let messages = [
    // { sender: 'user', text: 'Hello!' },
    { sender: 'IoTPilot', text: 'Hello, I\'m IoTpilot.                ' },
];

// 渲染消息到聊天窗口
function renderMessages() {
    const chatWindow = document.getElementById('chat-window');
    const message = messages[messages.length - 1];
    const messageBox = document.createElement('div');
    messageBox.className = `message-box`;
    const icon = document.createElement('img');
    icon.src = 'placeholder_icon.png';
    const senderBox = document.createElement('div');
    senderBox.className = 'sender-box ${message.sender}';
    // senderBox.textContent = `${message.sender}:`;
    senderBox.appendChild(icon);
    senderBox.appendChild(document.createTextNode(`${message.sender}:`));
    const textBox = document.createElement('div');
    textBox.className = 'text-box';
    textBox.textContent = message.text;
    textBox.innerHTML = textBox.innerHTML.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;');
    messageBox.appendChild(senderBox);
    messageBox.appendChild(textBox);
    chatWindow.appendChild(messageBox);


    // 滚动到底部
    chatWindow.scrollTop = chatWindow.scrollHeight;
}

// 处理发送按钮点击事件
async function handleSend() {
    const inputField = document.getElementById('message-input'); 
    const newMessageText = inputField.value.trim();

    if (newMessageText !== '') { 
        // 添加新消息到数组 
        messages.push({sender:'user',text:newMessageText}); 

        // 清空输入框并重新渲染消息 
        inputField.value=''; 
        renderMessages(); 

        try {
            // 获取当前网页的url 与 html内容
            
            const response = await axios.post("XXXX-9 ",{username:"emm" ,userproblem: newMessageText});
            // 拿到的response.data是一个json对象，包含action和content
            const content = response['data']['result']; //好奇怪 这里用response['data']可以顺利渲染，response.data会输出[object object]
            console.log("response:\n",response);   
            console.log("content: ",content); 

            const llmMessage = {sender: 'IoTPilot', text: content}; 
            messages.push(llmMessage);

            renderMessages();
            
        }catch(error){
            console.error('Error:', error);
        }
              
   } 
}

document.getElementById('send_button').addEventListener('click', handleSend); // 将handleSend绑定到发送按钮

document.getElementById('message-input').addEventListener('keydown', function(event){
    if (event.key == 'Enter' && !event.shiftKey){
        event.preventDefault(); // prevent default behavior
        handleSend();
    }
}); //  add event listener for keydown


// init messages
renderMessages();