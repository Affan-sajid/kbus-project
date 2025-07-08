import React, { useState, useEffect, useRef } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import { motion } from 'framer-motion';
import ChatBubble from '../components/ChatBubble';
import TypingIndicator from '../components/TypingIndicator';
import BusCard from '../components/BusCard';
import AcknowMoreBubble from '../components/AcknowMoreBubble';
import useTypewriter from '../hooks/useTypewriter';
import extractPlaceName from '../utils/extractPlaceName';

// Sample bus data (replace with real API data as needed)
const BUS_DATA = [
  {
    "name": "Bus 42A - City Express",
    "duration": "32 mins",
    "drive in": "Departs in 5 mins",
    "fare": "₹15"
  },
  {
    "name": "Bus 101B - Fast Line",
    "duration": "47 mins",
    "drive in": "Departs in 12 mins",
    "fare": "₹22"
  },
  {
    "name": "Bus 77C - Night Rider",
    "duration": "55 mins",
    "drive in": "Departs in 20 mins",
    "fare": "₹18"
  },
  {
    "name": "Bus 12D - Rapid Metro",
    "duration": "29 mins",
    "drive in": "Departs in 2 mins",
    "fare": "₹20"
  }
];

/**
 * ChatScreen manages the staged chat UI for the bus route finder.
 * It uses modular chat bubble components and staged animation for a conversational feel.
 */
const ChatScreen = () => {
  // React Router hooks to get navigation and passed-in place
  const location = useLocation();
  const navigate = useNavigate();

  // Use sessionStorage to determine if we should animate (only after coming from FirstScreen)
  const [shouldAnimate, setShouldAnimate] = useState(null); // null = not ready, true/false = ready
  const didCheckFlag = useRef(false);

  // State for staged animation of each chat step
  const [showUserMsg, setShowUserMsg] = useState(false);
  const [showBotMsg1, setShowBotMsg1] = useState(false);
  const [showTyping, setShowTyping] = useState(false);
  const [showBusList, setShowBusList] = useState(false);
  const [showAcknowMore, setShowAcknowMore] = useState(false);
  const [showBotMsg2, setShowBotMsg2] = useState(false);
  const [showBack, setShowBack] = useState(false);

  // Ref to scroll chat to bottom as new messages appear
  const chatEndRef = useRef(null);

  // Get the full place/address from navigation state
  const placeFull = location.state?.initialMessage || '';
  // Extract a short place name for the bot's reply
  let placeName = extractPlaceName(placeFull);
  if (!placeName) placeName = 'your destination';

  // Bot messages
  const botText1 = `alright I see you want to go to ${placeName}`;
  const botText2 = 'Click on a bus route to see more information.';

  // Show only 3 buses at first, then "Acknow More" if there are more
  const busList = BUS_DATA;
  const showMore = busList.length > 3;

  // Determine animation mode on mount
  useEffect(() => {
    if (didCheckFlag.current) return;
    didCheckFlag.current = true;
    const flag = sessionStorage.getItem('fromFirstScreen');
    console.log('[DEBUG] sessionStorage fromFirstScreen:', flag);
    if (flag === 'yes') {
      setShouldAnimate(true);
      sessionStorage.removeItem('fromFirstScreen');
      console.log('[DEBUG] shouldAnimate set to TRUE (fromFirstScreen flag found)');
    } else {
      setShouldAnimate(false);
      console.log('[DEBUG] shouldAnimate set to FALSE (no fromFirstScreen flag)');
    }
  }, []);

  // Main effect: controls staged animation or instant reveal
  useEffect(() => {
    console.log('[DEBUG] useEffect (main) shouldAnimate:', shouldAnimate);
    if (shouldAnimate === null) return; // Wait until ready
    if (!shouldAnimate) {
      setShowUserMsg(true);   console.log('[DEBUG] showUserMsg set TRUE (no animation)');
      setShowBotMsg1(true);   console.log('[DEBUG] showBotMsg1 set TRUE (no animation)');
      setShowTyping(false);   console.log('[DEBUG] showTyping set FALSE (no animation)');
      setShowBusList(true);   console.log('[DEBUG] showBusList set TRUE (no animation)');
      setShowAcknowMore(showMore); console.log('[DEBUG] showAcknowMore set', showMore, '(no animation)');
      setShowBotMsg2(true);   console.log('[DEBUG] showBotMsg2 set TRUE (no animation)');
      setShowBack(true);      console.log('[DEBUG] showBack set TRUE (no animation)');
      return;
    }
    // Animated staged sequence
    setShowUserMsg(false);   console.log('[DEBUG] showUserMsg set FALSE (start animation)');
    setShowBotMsg1(false);   console.log('[DEBUG] showBotMsg1 set FALSE (start animation)');
    setShowTyping(false);    console.log('[DEBUG] showTyping set FALSE (start animation)');
    setShowBusList(false);   console.log('[DEBUG] showBusList set FALSE (start animation)');
    setShowAcknowMore(false);console.log('[DEBUG] showAcknowMore set FALSE (start animation)');
    setShowBotMsg2(false);   console.log('[DEBUG] showBotMsg2 set FALSE (start animation)');
    setShowBack(false);      console.log('[DEBUG] showBack set FALSE (start animation)');
    setTimeout(() => { setShowUserMsg(true); console.log('[DEBUG] showUserMsg set TRUE (animation)'); }, 200);
    setTimeout(() => { setShowBotMsg1(true); console.log('[DEBUG] showBotMsg1 set TRUE (animation)'); }, 700);
    setTimeout(() => { setShowTyping(true); console.log('[DEBUG] showTyping set TRUE (animation)'); }, 700 + botText1.length * 30 + 300);
    setTimeout(() => { setShowTyping(false); console.log('[DEBUG] showTyping set FALSE (animation)'); }, 700 + botText1.length * 30 + 1300);
    setTimeout(() => { setShowBusList(true); console.log('[DEBUG] showBusList set TRUE (animation)'); }, 700 + botText1.length * 30 + 1400);
    if (showMore) {
      setTimeout(() => { setShowAcknowMore(true); console.log('[DEBUG] showAcknowMore set TRUE (animation)'); }, 700 + botText1.length * 30 + 1800);
      setTimeout(() => { setShowBotMsg2(true); console.log('[DEBUG] showBotMsg2 set TRUE (animation)'); }, 700 + botText1.length * 30 + 2200);
      setTimeout(() => { setShowBack(true); console.log('[DEBUG] showBack set TRUE (animation)'); }, 700 + botText1.length * 30 + 2600);
    } else {
      setTimeout(() => { setShowBotMsg2(true); console.log('[DEBUG] showBotMsg2 set TRUE (animation)'); }, 700 + botText1.length * 30 + 1800);
      setTimeout(() => { setShowBack(true); console.log('[DEBUG] showBack set TRUE (animation)'); }, 700 + botText1.length * 30 + 2200);
    }
  }, [shouldAnimate, botText1.length, showMore]);

  // Scroll to bottom as new chat bubbles appear
  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [showUserMsg, showBotMsg1, showBusList, showAcknowMore, showBotMsg2]);

  // Handler for clicking a bus card: navigate to bus details page
  const handleBusClick = (bus) => {
    navigate('/bus-details', { state: { bus, placeFull } });
  };

  // Always call the typewriter hooks FIRST
  const typewriter1 = useTypewriter(botText1, showBotMsg1, 30);
  const typewriter2 = useTypewriter(botText2, showBotMsg2, 30);
  const typedBotText1 = shouldAnimate ? typewriter1 : botText1;
  const typedBotText2 = shouldAnimate ? typewriter2 : botText2;

  // Wait for shouldAnimate to be determined before rendering chat UI
  if (shouldAnimate === null) return null;

  return (
    <div className="min-h-screen flex items-center justify-center bg-gray-900 relative">
      {/* Back button at top left, slides in after bot reply */}
      {showBack && (
        <motion.button
          className="absolute top-4 left-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800"
          onClick={() => navigate('/')}
          initial={{ x: -80, opacity: 0 }}
          animate={{ x: 0, opacity: 1 }}
          exit={{ x: -80, opacity: 0 }}
          transition={{ type: 'spring', stiffness: 300, damping: 30 }}
        >
          ← Back
        </motion.button>
      )}
      {/* Chat history, messages start from the bottom */}
      <div className="w-full max-w-sm flex flex-col justify-end h-[70vh] pb-4 overflow-y-auto" style={{ minHeight: '300px' }}>
        <div className="flex flex-col justify-end h-full space-y-2">
          {/* User's original place message */}
          {showUserMsg && <ChatBubble isUser>{placeFull}</ChatBubble>}
          {/* Bot: acknowledges the place (typewriter effect or instant) */}
          {showBotMsg1 && <ChatBubble>{typedBotText1}</ChatBubble>}
          {/* Typing indicator (animated three dots) */}
          {showTyping && <TypingIndicator />}
          {/* Bus cards (up to 3) */}
          {showBusList && (
            <div className="flex flex-col space-y-2">
              {busList.slice(0, 3).map((bus, idx) => (
                <BusCard key={bus.name} bus={bus} onClick={() => handleBusClick(bus)} />
              ))}
            </div>
          )}
          {/* "Acknow More" bubble if more than 3 buses */}
          {showAcknowMore && <AcknowMoreBubble />}
          {/* Bot: instructs user to click a bus (typewriter effect or instant) */}
          {showBotMsg2 && <ChatBubble>{typedBotText2}</ChatBubble>}
          {/* Dummy div to keep chat scrolled to bottom */}
          <div ref={chatEndRef} />
        </div>
      </div>
    </div>
  );
};

export default ChatScreen; 