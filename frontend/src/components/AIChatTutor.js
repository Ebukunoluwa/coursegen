import React, { useState, useRef, useEffect } from 'react';
import { MessageCircle, X, Send, ChevronUp, ChevronDown, Lightbulb, Code, HelpCircle, BookOpen } from 'lucide-react';

const AIChatTutor = ({ 
  isVisible, 
  onToggle, 
  currentLesson, 
  currentModule, 
  userProgress, 
  courseContent 
}) => {
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [isExpanded, setIsExpanded] = useState(false);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Quick action suggestions
  const quickActions = [
    {
      icon: <Lightbulb className="h-4 w-4" />,
      text: "Explain this concept",
      action: () => handleQuickAction("Explain this concept")
    },
    {
      icon: <Code className="h-4 w-4" />,
      text: "Help with code",
      action: () => handleQuickAction("Help with code")
    },
    {
      icon: <HelpCircle className="h-4 w-4" />,
      text: "Quiz me",
      action: () => handleQuickAction("Quiz me")
    },
    {
      icon: <BookOpen className="h-4 w-4" />,
      text: "Summarize lesson",
      action: () => handleQuickAction("Summarize this lesson")
    }
  ];

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  // Focus input when chat becomes visible
  useEffect(() => {
    if (isVisible && isExpanded) {
      setTimeout(() => {
        inputRef.current?.focus();
      }, 100);
    }
  }, [isVisible, isExpanded]);

  const handleQuickAction = (action) => {
    const contextMessage = `I'm currently studying: ${currentLesson?.title || 'Unknown lesson'} in module: ${currentModule?.title || 'Unknown module'}. ${action}`;
    sendMessage(contextMessage);
  };

  const sendMessage = async (message = inputMessage) => {
    if (!message.trim()) return;

    const userMessage = {
      id: Date.now(),
      type: 'user',
      content: message,
      timestamp: new Date().toLocaleTimeString()
    };

    setMessages(prev => [...prev, userMessage]);
    setInputMessage('');
    setIsLoading(true);

    try {
      // Simulate AI response (replace with actual API call)
      const aiResponse = await generateAIResponse(message, userMessage);
      
      const aiMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: aiResponse,
        timestamp: new Date().toLocaleTimeString()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);
      const errorMessage = {
        id: Date.now() + 1,
        type: 'ai',
        content: "Sorry, I'm having trouble connecting right now. Please try again later.",
        timestamp: new Date().toLocaleTimeString()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const generateAIResponse = async (message, userMessage) => {
    // Simulate API delay
    await new Promise(resolve => setTimeout(resolve, 1000));
    
    // Mock AI responses based on message content
    const lowerMessage = message.toLowerCase();
    
    if (lowerMessage.includes('explain') || lowerMessage.includes('concept')) {
      return `I'd be happy to explain that concept! Based on your current lesson "${currentLesson?.title}", here's a clear explanation...`;
    } else if (lowerMessage.includes('code') || lowerMessage.includes('help')) {
      return `Let me help you with the code! Here's a step-by-step solution for your current lesson...`;
    } else if (lowerMessage.includes('quiz') || lowerMessage.includes('test')) {
      return `Great idea! Let me quiz you on what you've learned in "${currentLesson?.title}". Here are some questions...`;
    } else if (lowerMessage.includes('summarize')) {
      return `Here's a summary of "${currentLesson?.title}": [Key points and main takeaways from the lesson]`;
    } else {
      return `I understand you're asking about "${message}". Let me provide a helpful response based on your current progress in the course...`;
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  if (!isVisible) return null;

  return (
    <div className="fixed bottom-4 right-4 z-50">
      {/* Chat Toggle Button */}
      <button
        onClick={onToggle}
        className="bg-blue-600 hover:bg-blue-700 text-white p-3 rounded-full shadow-lg transition-all duration-300 hover:scale-110"
        title="AI Chat Tutor"
      >
        <MessageCircle className="h-6 w-6" />
      </button>

      {/* Chat Interface */}
      {isExpanded && (
        <div className="absolute bottom-16 right-0 w-96 bg-white rounded-lg shadow-2xl border border-gray-200">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 rounded-t-lg">
            <div className="flex items-center justify-between">
              <div className="flex items-center space-x-2">
                <MessageCircle className="h-5 w-5" />
                <h3 className="font-semibold">AI Tutor</h3>
              </div>
              <button
                onClick={() => setIsExpanded(false)}
                className="text-white hover:text-gray-200 transition-colors"
              >
                <X className="h-5 w-5" />
              </button>
            </div>
            
            {/* Context Indicator */}
            {currentLesson && (
              <div className="mt-2 text-sm text-blue-100">
                <span className="font-medium">Current:</span> {currentLesson.title}
              </div>
            )}
          </div>

          {/* Messages */}
          <div className="h-80 overflow-y-auto p-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="text-center text-gray-500 py-8">
                <MessageCircle className="h-12 w-12 mx-auto mb-4 text-gray-300" />
                <h4 className="font-semibold mb-2">AI Tutor Ready!</h4>
                <p className="text-sm mb-4">Ask me anything about your course content.</p>
                
                {/* Quick Actions */}
                <div className="space-y-2">
                  {quickActions.map((action, index) => (
                    <button
                      key={index}
                      onClick={action.action}
                      className="w-full text-left p-3 bg-white rounded-lg border border-gray-200 hover:border-blue-300 hover:bg-blue-50 transition-all duration-200 flex items-center space-x-2"
                    >
                      {action.icon}
                      <span className="text-sm">{action.text}</span>
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((message) => (
                  <div
                    key={message.id}
                    className={`flex ${message.type === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        message.type === 'user'
                          ? 'bg-blue-600 text-white'
                          : 'bg-white border border-gray-200 text-gray-800'
                      }`}
                    >
                      <p className="text-sm">{message.content}</p>
                      <p className={`text-xs mt-1 ${
                        message.type === 'user' ? 'text-blue-100' : 'text-gray-500'
                      }`}>
                        {message.timestamp}
                      </p>
                    </div>
                  </div>
                ))}
                
                {isLoading && (
                  <div className="flex justify-start">
                    <div className="bg-white border border-gray-200 text-gray-800 px-4 py-2 rounded-lg">
                      <div className="flex items-center space-x-2">
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-600"></div>
                        <span className="text-sm">AI is thinking...</span>
                      </div>
                    </div>
                  </div>
                )}
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <div className="p-4 border-t border-gray-200">
            <div className="flex space-x-2">
              <input
                ref={inputRef}
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={handleKeyPress}
                placeholder="Ask your AI tutor..."
                className="flex-1 px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                onClick={() => sendMessage()}
                disabled={!inputMessage.trim() || isLoading}
                className="bg-blue-600 hover:bg-blue-700 disabled:bg-gray-400 text-white px-4 py-2 rounded-lg transition-colors duration-200"
              >
                <Send className="h-4 w-4" />
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default AIChatTutor; 