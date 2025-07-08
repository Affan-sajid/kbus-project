import React, { useState, useEffect } from 'react';
import { Routes, Route } from 'react-router-dom';
import FirstScreen from './screens/FirstScreen';
import ChatScreen from './screens/ChatScreen';
import BusDetailsScreen from './screens/BusDetailsScreen';

const MOBILE_MAX_WIDTH = 600;

const App = () => {
  const [showOverlay, setShowOverlay] = useState(false);

  useEffect(() => {
    function checkMobile() {
      const isMobileUA = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
      const isSmallScreen = window.innerWidth <= MOBILE_MAX_WIDTH;
      setShowOverlay(!(isMobileUA && isSmallScreen));
    }
    checkMobile();
    window.addEventListener('resize', checkMobile);
    return () => window.removeEventListener('resize', checkMobile);
  }, []);

  return (
    <div style={{
      minHeight: '100vh',
      minWidth: '100vw',
      width: '100vw',
      height: '100vh',
      position: 'fixed',
      top: 0,
      left: 0,
      zIndex: 0,
      background: 'radial-gradient(circle at 50% 40%, #473404 0%, #0a2342 100%)',
    }}>
      <div style={{ position: 'relative', zIndex: 1, minHeight: '100vh' }}>
        {showOverlay && (
          <div style={{
            position: 'fixed',
            top: 0,
            left: 0,
            width: '100vw',
            height: '100vh',
            background: 'radial-gradient(circle at 50% 40%, #2d2a4a 0%, #23272f 60%, #111215 100%)',
            color: '#fff',
            zIndex: 9999,
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            fontSize: '1.3rem',
            textAlign: 'center',
            padding: '2rem',
          }}>
            <div>
              <strong>This app is mobile-only.</strong><br/>
              Please open on a mobile device or resize your window to a mobile width.
            </div>
          </div>
        )}
        <Routes>
          <Route path="/" element={<FirstScreen />} />
          <Route path="/chat" element={<ChatScreen />} />
          <Route path="/bus-details" element={<BusDetailsScreen />} />
        </Routes>
      </div>
    </div>
  );
};

export default App;