import React, { useState } from 'react';
import PlaceAutocompleteInput from '../components/PlaceAutocompleteInput';
import { useNavigate } from 'react-router-dom';
import { motion } from 'framer-motion';

const FirstScreen = () => {
  const [place, setPlace] = useState('');
  const [inputVisible, setInputVisible] = useState(true);
  const navigate = useNavigate();

  const handleEnter = (value) => {
    if (!value.trim()) return;
    setInputVisible(false);
    setTimeout(() => {
      sessionStorage.setItem('fromFirstScreen', 'yes');
      navigate('/chat', { state: { initialMessage: value } });
    }, 400); // match fade duration
  };

  return (
    <div className="min-h-screen flex items-center justify-center ">
      <div className="w-full max-w-sm flex flex-col items-center">
        {inputVisible && (
          <motion.div
            key="input"
            initial={{ opacity: 1 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.4 }}
            className="w-full"
            style={{
              boxShadow: '0 8px 32px 0 rgba(0,0,0,0.35), 0 1.5px 8px 0 rgba(71,52,4,0.15)',
              borderRadius: '1rem',
              background: 'rgba(255,255,255,0.04)',
              backdropFilter: 'blur(2px)',
              transform: 'translateY(-8px) scale(1.03)',
            }}
          >
            <PlaceAutocompleteInput
              value={place}
              onChange={setPlace}
              placeholder="Where?"
              onEnter={handleEnter}
            />
          </motion.div>
        )}
      </div>
    </div>
  );
};

export default FirstScreen; 