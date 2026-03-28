// Behike Chat Widget - Connects to Cobo's Ollama API
// Inject into any landing page

(function() {
  const API_URL = window.BEHIKE_CHAT_API || '';
  const RATE_LIMIT_MS = 2000;
  const SESSION_KEY = 'behike-chat-history';
  const GREETING = "Hey! I'm Behike AI. Ask me anything about our products.";

  let isOpen = false;
  let lastSendTime = 0;
  let isWaiting = false;

  // Load conversation from sessionStorage
  function loadHistory() {
    try {
      const saved = sessionStorage.getItem(SESSION_KEY);
      return saved ? JSON.parse(saved) : [{ role: 'assistant', content: GREETING }];
    } catch (e) {
      return [{ role: 'assistant', content: GREETING }];
    }
  }

  function saveHistory(messages) {
    try {
      sessionStorage.setItem(SESSION_KEY, JSON.stringify(messages));
    } catch (e) {
      // sessionStorage full or unavailable
    }
  }

  let messages = loadHistory();

  function createWidget() {
    const widget = document.createElement('div');
    widget.id = 'behike-chat';
    widget.innerHTML = `
      <style>
        #behike-chat-toggle {
          position: fixed;
          bottom: 24px;
          left: 24px;
          z-index: 9999;
          width: 48px;
          height: 48px;
          border-radius: 50%;
          background: var(--blue, #0A84FF);
          border: none;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          font-size: 22px;
          box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
          transition: transform 0.2s, box-shadow 0.2s;
          line-height: 1;
        }
        #behike-chat-toggle:hover {
          transform: scale(1.1);
          box-shadow: 0 6px 28px rgba(0, 0, 0, 0.5);
        }

        #behike-chat-panel {
          position: fixed;
          bottom: 84px;
          left: 24px;
          z-index: 9998;
          width: 320px;
          height: 450px;
          background: rgba(20, 20, 20, 0.95);
          backdrop-filter: blur(20px);
          -webkit-backdrop-filter: blur(20px);
          border-radius: 16px;
          border: 1px solid rgba(255, 255, 255, 0.1);
          box-shadow: 0 8px 40px rgba(0, 0, 0, 0.6);
          display: none;
          flex-direction: column;
          overflow: hidden;
          animation: chatSlideUp 0.25s ease-out;
        }
        #behike-chat-panel.open {
          display: flex;
        }

        @keyframes chatSlideUp {
          from { opacity: 0; transform: translateY(10px); }
          to { opacity: 1; transform: translateY(0); }
        }

        .chat-header {
          display: flex;
          align-items: center;
          justify-content: space-between;
          padding: 14px 16px;
          border-bottom: 1px solid rgba(255, 255, 255, 0.08);
        }
        .chat-header-title {
          font-size: 15px;
          font-weight: 600;
          color: #F5F5F7;
          font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', sans-serif;
        }
        .chat-close {
          background: none;
          border: none;
          color: #86868B;
          font-size: 18px;
          cursor: pointer;
          padding: 2px 6px;
          border-radius: 6px;
          transition: background 0.15s, color 0.15s;
          line-height: 1;
        }
        .chat-close:hover {
          background: rgba(255, 255, 255, 0.08);
          color: #F5F5F7;
        }

        .chat-messages {
          flex: 1;
          overflow-y: auto;
          padding: 16px;
          display: flex;
          flex-direction: column;
          gap: 12px;
          scrollbar-width: thin;
          scrollbar-color: rgba(255,255,255,0.1) transparent;
        }
        .chat-messages::-webkit-scrollbar {
          width: 4px;
        }
        .chat-messages::-webkit-scrollbar-track {
          background: transparent;
        }
        .chat-messages::-webkit-scrollbar-thumb {
          background: rgba(255, 255, 255, 0.1);
          border-radius: 4px;
        }

        .chat-msg {
          max-width: 85%;
          padding: 10px 14px;
          border-radius: 14px;
          font-size: 13px;
          line-height: 1.5;
          font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
          word-wrap: break-word;
        }
        .chat-msg.assistant {
          background: rgba(255, 255, 255, 0.08);
          color: #F5F5F7;
          align-self: flex-start;
          border-bottom-left-radius: 4px;
        }
        .chat-msg.user {
          background: var(--blue, #0A84FF);
          color: #fff;
          align-self: flex-end;
          border-bottom-right-radius: 4px;
        }
        .chat-msg.error {
          background: rgba(255, 59, 48, 0.15);
          color: #FF6961;
          align-self: flex-start;
          border-bottom-left-radius: 4px;
        }

        .chat-typing {
          align-self: flex-start;
          display: none;
          gap: 4px;
          padding: 10px 14px;
          background: rgba(255, 255, 255, 0.08);
          border-radius: 14px;
          border-bottom-left-radius: 4px;
        }
        .chat-typing.visible {
          display: flex;
        }
        .chat-typing-dot {
          width: 6px;
          height: 6px;
          background: #86868B;
          border-radius: 50%;
          animation: typingBounce 1.2s infinite;
        }
        .chat-typing-dot:nth-child(2) { animation-delay: 0.2s; }
        .chat-typing-dot:nth-child(3) { animation-delay: 0.4s; }

        @keyframes typingBounce {
          0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
          30% { transform: translateY(-4px); opacity: 1; }
        }

        .chat-input-area {
          display: flex;
          gap: 8px;
          padding: 12px 16px;
          border-top: 1px solid rgba(255, 255, 255, 0.08);
        }
        .chat-input {
          flex: 1;
          padding: 10px 14px;
          background: rgba(255, 255, 255, 0.06);
          border: 1px solid rgba(255, 255, 255, 0.1);
          border-radius: 980px;
          color: #F5F5F7;
          font-size: 13px;
          outline: none;
          transition: border-color 0.2s;
          font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', sans-serif;
        }
        .chat-input::placeholder {
          color: #86868B;
        }
        .chat-input:focus {
          border-color: var(--blue, #0A84FF);
        }
        .chat-send {
          background: var(--blue, #0A84FF);
          border: none;
          color: #fff;
          width: 36px;
          height: 36px;
          border-radius: 50%;
          cursor: pointer;
          display: flex;
          align-items: center;
          justify-content: center;
          transition: opacity 0.15s;
          flex-shrink: 0;
        }
        .chat-send:hover {
          opacity: 0.85;
        }
        .chat-send:disabled {
          opacity: 0.4;
          cursor: default;
        }
        .chat-send svg {
          width: 16px;
          height: 16px;
          fill: #fff;
        }

        @media (max-width: 480px) {
          #behike-chat-panel {
            left: 12px;
            right: 12px;
            bottom: 78px;
            width: auto;
            height: 400px;
          }
          #behike-chat-toggle {
            left: 16px;
            bottom: 16px;
          }
        }
      </style>

      <button id="behike-chat-toggle" aria-label="Chat">
        <span style="pointer-events:none;">&#x1F4AC;</span>
      </button>

      <div id="behike-chat-panel">
        <div class="chat-header">
          <span class="chat-header-title">Behike AI</span>
          <button class="chat-close" aria-label="Close chat">&times;</button>
        </div>
        <div class="chat-messages" id="chatMessages"></div>
        <div class="chat-typing" id="chatTyping">
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
          <div class="chat-typing-dot"></div>
        </div>
        <div class="chat-input-area">
          <input type="text" class="chat-input" id="chatInput" placeholder="Ask something..." autocomplete="off">
          <button class="chat-send" id="chatSend" aria-label="Send">
            <svg viewBox="0 0 24 24"><path d="M2.01 21L23 12 2.01 3 2 10l15 2-15 2z"/></svg>
          </button>
        </div>
      </div>
    `;
    document.body.appendChild(widget);

    // Elements
    const toggle = document.getElementById('behike-chat-toggle');
    const panel = document.getElementById('behike-chat-panel');
    const closeBtn = panel.querySelector('.chat-close');
    const messagesEl = document.getElementById('chatMessages');
    const typingEl = document.getElementById('chatTyping');
    const inputEl = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSend');

    // Render all messages from history
    function renderMessages() {
      messagesEl.innerHTML = '';
      messages.forEach(function(msg) {
        appendMessageDOM(msg.role, msg.content);
      });
      scrollToBottom();
    }

    function appendMessageDOM(role, content) {
      var div = document.createElement('div');
      div.className = 'chat-msg ' + role;
      div.textContent = content;
      messagesEl.appendChild(div);
    }

    function scrollToBottom() {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function showTyping(show) {
      typingEl.classList.toggle('visible', show);
      if (show) {
        messagesEl.appendChild(typingEl);
        scrollToBottom();
      }
    }

    // Send message
    async function sendMessage() {
      var text = inputEl.value.trim();
      if (!text || isWaiting) return;

      // Rate limit
      var now = Date.now();
      if (now - lastSendTime < RATE_LIMIT_MS) return;
      lastSendTime = now;

      // Add user message
      messages.push({ role: 'user', content: text });
      appendMessageDOM('user', text);
      inputEl.value = '';
      scrollToBottom();
      saveHistory(messages);

      // Build history for API (exclude the greeting)
      var apiHistory = messages
        .filter(function(m) { return m.content !== GREETING; })
        .map(function(m) { return { role: m.role, content: m.content }; });

      isWaiting = true;
      sendBtn.disabled = true;
      showTyping(true);

      try {
        var response = await fetch(API_URL + '/chat', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(
            apiHistory.length > 2
              ? { messages: apiHistory }
              : { message: text }
          )
        });

        if (!response.ok) throw new Error('Server error');

        var data = await response.json();
        var reply = data.response || 'Sorry, I didn\'t get that.';

        messages.push({ role: 'assistant', content: reply });
        showTyping(false);
        appendMessageDOM('assistant', reply);
        scrollToBottom();
        saveHistory(messages);

      } catch (e) {
        showTyping(false);
        var errorMsg = 'Chat is currently offline. DM us on Instagram @behikeai';
        messages.push({ role: 'error', content: errorMsg });
        appendMessageDOM('error', errorMsg);
        scrollToBottom();
        saveHistory(messages);
      }

      isWaiting = false;
      sendBtn.disabled = false;
      inputEl.focus();
    }

    // Events
    toggle.addEventListener('click', function() {
      isOpen = !isOpen;
      panel.classList.toggle('open', isOpen);
      if (isOpen) {
        inputEl.focus();
        scrollToBottom();
      }
    });

    closeBtn.addEventListener('click', function() {
      isOpen = false;
      panel.classList.remove('open');
    });

    sendBtn.addEventListener('click', sendMessage);

    inputEl.addEventListener('keydown', function(e) {
      if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
      }
    });

    // Close on outside click
    document.addEventListener('click', function(e) {
      if (isOpen && !panel.contains(e.target) && !toggle.contains(e.target)) {
        isOpen = false;
        panel.classList.remove('open');
      }
    });

    // Initial render
    renderMessages();
  }

  // Init
  document.addEventListener('DOMContentLoaded', createWidget);
})();
