import React from 'react';

const ChatBubble = ({ children, isUser, className = '' }) => (
  <div
    className={`px-4 py-2 rounded-lg max-w-[80%] ${isUser ? 'bg-blue-600 text-white self-end ml-auto' : 'bg-gray-700 text-white self-start mr-auto'} ${className}`}
    style={{ textAlign: isUser ? 'right' : 'left' }}
  >
    {children}
  </div>
);

export default ChatBubble; 