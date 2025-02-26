document.addEventListener('DOMContentLoaded', () => {
    const input = document.getElementById('userInput');
    const sendButton = document.getElementById('sendButton');
    const chatLog = document.getElementById('chatLog');
    let isGenerating = false;

    function createMessageElement(content, role) {
        const messageDiv = document.createElement('div');
        messageDiv.className = `message ${role}-message`;
        messageDiv.textContent = content;
        return messageDiv;
    }

    function appendThinkingIndicator() {
        const indicator = document.createElement('div');
        indicator.className = 'message assistant-message thinking-indicator';
        indicator.textContent = 'Thinking...';
        chatLog.appendChild(indicator);
        return indicator;
    }

    async function sendMessage() {
        if (isGenerating) return;
        
        const message = input.value.trim();
        if (!message) return;

        isGenerating = true;
        input.disabled = true;
        sendButton.disabled = true;
        
        // Add user message
        chatLog.appendChild(createMessageElement(message, 'user'));
        input.value = '';
        
        // Add thinking indicator
        const thinkingIndicator = appendThinkingIndicator();
        chatLog.scrollTop = chatLog.scrollHeight;

        try {
            const response = await fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message })
            });

            if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);

            // Remove thinking indicator
            chatLog.removeChild(thinkingIndicator);

            const reader = response.body.getReader();
            const decoder = new TextDecoder();
            let assistantMessage = '';
            const messageDiv = createMessageElement('', 'assistant');
            chatLog.appendChild(messageDiv);

            while (true) {
                const { done, value } = await reader.read();
                if (done) break;
                const chunk = decoder.decode(value, { stream: true });
                assistantMessage += chunk;
                messageDiv.textContent = assistantMessage;
                chatLog.scrollTop = chatLog.scrollHeight;
            }
        } catch (error) {
            chatLog.removeChild(thinkingIndicator);
            const errorDiv = createMessageElement(`Error: ${error.message}`, 'assistant');
            chatLog.appendChild(errorDiv);
        } finally {
            isGenerating = false;
            input.disabled = false;
            sendButton.disabled = false;
            input.focus();
        }
    }

    sendButton.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            sendMessage();
        }
    });
});