import React from 'react';
import { motion } from 'framer-motion';

const TypingIndicator = () => (
  <motion.div
    className="flex items-center space-x-1 px-4 py-2 bg-gray-700 text-white rounded-lg w-fit self-start"
    initial={{ opacity: 0 }}
    animate={{ opacity: 1 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
    style={{ fontSize: '1.5rem', minWidth: '2.5rem' }}
  >
    <span className="dot">•</span>
    <span className="dot">•</span>
    <span className="dot">•</span>
    <style>{`
      .dot {
        animation: blink 1.4s infinite both;
        opacity: 0.4;
      }
      .dot:nth-child(2) { animation-delay: 0.2s; }
      .dot:nth-child(3) { animation-delay: 0.4s; }
      @keyframes blink {
        0%, 80%, 100% { opacity: 0.4; }
        40% { opacity: 1; }
      }
    `}</style>
  </motion.div>
);

export default TypingIndicator; 