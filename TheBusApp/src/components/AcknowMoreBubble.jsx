import React from 'react';
import { motion } from 'framer-motion';

const AcknowMoreBubble = ({ onClick }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.8, y: 30 }}
    animate={{ opacity: 1, scale: 1, y: 0 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
    className="px-4 py-2 rounded-lg max-w-[60%] bg-gray-800 text-blue-400 self-start mr-auto text-center cursor-pointer border border-blue-400 hover:bg-gray-700"
    style={{ textAlign: 'center' }}
    onClick={onClick}
  >
    Acknow More
  </motion.div>
);

export default AcknowMoreBubble; 