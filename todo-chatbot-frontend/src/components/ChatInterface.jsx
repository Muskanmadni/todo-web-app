import React, { useState } from 'react';
import { useChatKit } from '@openai/chatkit-react';
import { TodoAPI } from '../services/api';

const ChatInterface = () => {
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  // Initialize ChatKit
  const {
    connect,
    sendMessage,
    messages,
    users,
    currentUser,
    isConnecting
  } = useChatKit();

  // Initialize connection when component mounts
  React.useEffect(() => {
    // Connect to ChatKit with your instance locator and token provider
    // Note: You would need to provide actual credentials here
    connect({
      instanceLocator: process.env.REACT_APP_CHATKIT_INSTANCE_LOCATOR || 'your-instance-locator',
      userId: 'default-user',
      tokenProvider: {
        type: 'url',
        url: process.env.REACT_APP_CHATKIT_TOKEN_PROVIDER_URL || 'your-token-provider-url'
      }
    });
  }, [connect]);

  // Function to handle sending a message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isConnecting) return;

    // Add user's message to the chat
    const userMessage = inputValue;
    setInputValue('');
    setIsLoading(true);

    try {
      // Send message via ChatKit
      await sendMessage({ text: userMessage });

      // Also call the backend API to process the natural language and get a response
      const response = await TodoAPI.processNaturalLanguageRequest(userMessage);

      // Send bot response via ChatKit
      await sendMessage({ text: response });
    } catch (error) {
      console.error('Error processing natural language request:', error);
      await sendMessage({ text: 'Sorry, I encountered an error processing your request.' });
    } finally {
      setIsLoading(false);
    }
  };

  // Handle Enter key press to send message
  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  return (
    <div style={{ height: '80vh', display: 'flex', flexDirection: 'column' }}>
      <div style={{ flex: 1, overflowY: 'auto', padding: '10px', backgroundColor: '#f5f5f5' }}>
        {isConnecting && (
          <div style={{
            padding: '10px',
            backgroundColor: '#e9ecef',
            borderRadius: '8px',
            maxWidth: '70%',
            margin: '5px 0'
          }}>
            Connecting to chat service...
          </div>
        )}

        {messages?.map((msg) => (
          <div key={msg.id} style={{ marginBottom: '10px' }}>
            <div style={{
              padding: '10px',
              backgroundColor: msg.sender?.id === currentUser?.id ? '#007bff' : '#e9ecef',
              color: msg.sender?.id === currentUser?.id ? 'white' : 'black',
              borderRadius: '8px',
              maxWidth: '70%',
              marginLeft: msg.sender?.id === currentUser?.id ? 'auto' : '0',
              marginRight: msg.sender?.id === currentUser?.id ? '0' : 'auto'
            }}>
              <strong>{msg.sender?.name || msg.sender?.id}: </strong>
              {msg.text}
            </div>
          </div>
        ))}

        {isLoading && (
          <div style={{
            padding: '10px',
            backgroundColor: '#e9ecef',
            borderRadius: '8px',
            maxWidth: '70%',
            marginLeft: 'auto',
            marginRight: '0'
          }}>
            <strong>AI Assistant: </strong>Typing...
          </div>
        )}
      </div>

      <div style={{ display: 'flex', padding: '10px', borderTop: '1px solid #ccc' }}>
        <textarea
          value={inputValue}
          onChange={(e) => setInputValue(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your message here..."
          style={{
            flex: 1,
            padding: '10px',
            border: '1px solid #ccc',
            borderRadius: '4px',
            resize: 'none',
            minHeight: '60px'
          }}
          disabled={isConnecting}
        />
        <button
          onClick={handleSendMessage}
          disabled={isLoading || !inputValue.trim() || isConnecting}
          style={{
            marginLeft: '10px',
            padding: '10px 20px',
            backgroundColor: '#007bff',
            color: 'white',
            border: 'none',
            borderRadius: '4px',
            cursor: (isLoading || !inputValue.trim() || isConnecting) ? 'not-allowed' : 'pointer'
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatInterface;