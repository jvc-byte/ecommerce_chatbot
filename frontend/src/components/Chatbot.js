import React, { useState, useRef, useEffect } from 'react';
import './Chatbot.css';
import { FaComments } from 'react-icons/fa';

const Chatbot = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState('');
  const [isOpen, setIsOpen] = useState(false);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const sendMessage = async (e) => {
    e.preventDefault();
    if (!input.trim()) return;

    const userMessage = {
      text: input,
      sender: 'user',
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');

    try {
      const response = await fetch('http://localhost:5001/api/chatbot', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ message: input })
      });

      const data = await response.json();
      
      let botMessage = {
        text: '',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      };

      switch (data.type) {
        case 'products':
          botMessage.text = `I found some products for you:\n\n${
            data.results.map(p => `- ${p.name} - $${p.price.toFixed(2)}`).join('\n')
          }`;
          break;
        case 'comparison':
          botMessage.text = `Comparing products:\n\n${
            data.products.map(p => `${p.name}:\n- Price: $${p.price.toFixed(2)}\n- ${p.description}`).join('\n\n')
          }`;
          break;
        case 'faq':
          botMessage.text = data.answer;
          break;
        case 'availability':
          botMessage.text = data.available 
            ? 'The product is currently in stock!'
            : 'I apologize, but this product is currently out of stock.';
          break;
        case 'recommendations':
          botMessage.text = `Here are some products you might like:\n\n${
            data.products.map(p => `- ${p.name} - $${p.price.toFixed(2)}`).join('\n')
          }`;
          break;
        default:
          botMessage.text = data.message;
      }

      setMessages(prev => [...prev, botMessage]);
    } catch (error) {
      console.error('Error:', error);
      setMessages(prev => [...prev, {
        text: 'Sorry, I encountered an error. Please try again later.',
        sender: 'bot',
        timestamp: new Date().toLocaleTimeString()
      }]);
    }
  };

  return (
    <div className="chatbot-container">
      <button 
        className="chatbot-toggle"
        onClick={() => setIsOpen(!isOpen)}
        aria-label="Toggle chatbot"
      >
        <FaComments size={24} />
      </button>
      {isOpen && (
        <div className="chatbot-popup">
          <div className="chatbot-header">
            <h3>Customer Support Chatbot</h3>
            <button 
              className="chatbot-close"
              onClick={() => setIsOpen(false)}
              aria-label="Close chatbot"
            >
              ×
            </button>
          </div>
          <div className="chatbot-messages">
            {messages.map((message, index) => (
              <div 
                key={index}
                className={`message ${message.sender}`}
              >
                <div className="message-content">
                  <p>{message.text}</p>
                  <span className="timestamp">{message.timestamp}</span>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>
          <form onSubmit={sendMessage} className="chatbot-input">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Type your message..."
            />
            <button type="submit">Send</button>
          </form>
        </div>
      )}
    </div>
  );
};

export default Chatbot;
