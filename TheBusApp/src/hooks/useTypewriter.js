import { useState, useEffect } from 'react';

const useTypewriter = (text, start, speed = 30) => {
  const [displayed, setDisplayed] = useState('');
  useEffect(() => {
    if (!start) return;
    setDisplayed('');
    let i = 0;
    const interval = setInterval(() => {
      if (text && typeof text[i] !== 'undefined') {
        setDisplayed((prev) => prev + text[i]);
        i++;
        if (i >= text.length) clearInterval(interval);
      } else {
        clearInterval(interval);
      }
    }, speed);
    return () => clearInterval(interval);
  }, [text, start, speed]);
  return displayed;
};

export default useTypewriter; 