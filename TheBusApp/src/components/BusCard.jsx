import React from 'react';
import { motion } from 'framer-motion';

const BusCard = ({ bus, onClick }) => (
  <motion.div
    initial={{ opacity: 0, scale: 0.8, y: 30 }}
    animate={{ opacity: 1, scale: 1, y: 0 }}
    exit={{ opacity: 0 }}
    transition={{ duration: 0.3 }}
    className="bg-gray-800 text-white rounded-lg shadow-md px-4 py-3 max-w-[85%] self-start mr-auto cursor-pointer hover:bg-gray-700 border border-gray-700"
    style={{ textAlign: 'left', minWidth: '220px' }}
    onClick={onClick}
  >
    <div className="font-semibold text-base mb-1">{bus.name}</div>
    <div className="flex justify-between text-sm mb-1">
      <span className="text-gray-300">{bus.duration}</span>
      <span className="text-gray-400">{bus["drive in"]}</span>
    </div>
    <div className="text-blue-400 font-bold text-sm">{bus.fare}</div>
  </motion.div>
);

export default BusCard; 