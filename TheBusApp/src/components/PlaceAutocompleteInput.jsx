import React from 'react';

const PlaceAutocompleteInput = ({ value, onChange, placeholder, onEnter }) => {
    const inputRef = React.useRef(null);
    const [inputValue, setInputValue] = React.useState(value || '');
    const [suggestions, setSuggestions] = React.useState([]);
    const [showSuggestions, setShowSuggestions] = React.useState(false);
    const [activeSuggestion, setActiveSuggestion] = React.useState(-1);
    const autocompleteServiceRef = React.useRef(null);
  
    React.useEffect(() => {
      if (window.google && window.google.maps && window.google.maps.places) {
        autocompleteServiceRef.current = new window.google.maps.places.AutocompleteService();
      }
    }, []);
  
    React.useEffect(() => {
      if (!autocompleteServiceRef.current || !inputValue) {
        setSuggestions([]);
        return;
      }
      autocompleteServiceRef.current.getPlacePredictions(
        {
          input: inputValue,
          componentRestrictions: { country: 'in' },
        },
        (predictions, status) => {
          if (status === window.google.maps.places.PlacesServiceStatus.OK && predictions) {
            setSuggestions(predictions);
          } else {
            setSuggestions([]);
          }
        }
      );
    }, [inputValue]);
  
    const handleChange = (e) => {
      setInputValue(e.target.value);
      setShowSuggestions(true);
      setActiveSuggestion(-1);
      if (onChange) onChange(e.target.value);
    };
  
    const handleSuggestionClick = (suggestion) => {
      setInputValue(suggestion.description);
      setShowSuggestions(false);
      setSuggestions([]);
      if (onChange) onChange(suggestion.description);
      if (onEnter) onEnter(suggestion.description);
    };
  
    const handleBlur = () => {
      setTimeout(() => setShowSuggestions(false), 100);
    };
  
    const handleFocus = () => {
      if (suggestions.length > 0) setShowSuggestions(true);
    };
  
    const handleKeyDown = (e) => {
      if (e.key === 'Enter') {
        if (showSuggestions && suggestions.length > 0 && activeSuggestion >= 0) {
          setInputValue(suggestions[activeSuggestion].description);
          setShowSuggestions(false);
          setSuggestions([]);
          if (onChange) onChange(suggestions[activeSuggestion].description);
          if (onEnter) onEnter(suggestions[activeSuggestion].description);
        } else {
          if (onEnter) onEnter(inputValue);
        }
      } else if (showSuggestions && suggestions.length > 0) {
        if (e.key === 'ArrowUp') {
          e.preventDefault();
          setActiveSuggestion((prev) =>
            prev <= 0 ? suggestions.length - 1 : prev - 1
          );
        } else if (e.key === 'ArrowDown') {
          e.preventDefault();
          setActiveSuggestion((prev) =>
            prev >= suggestions.length - 1 ? 0 : prev + 1
          );
        }
      }
    };
  
    return (
      <div className="w-full max-w-sm relative">
        {showSuggestions && suggestions.length > 0 && (
          <ul
            className="absolute left-0 right-0 bottom-full mb-2 z-50"
            style={{ background: '#111', color: '#fff', borderRadius: '0.5rem', boxShadow: '0 4px 16px rgba(0,0,0,0.5)' }}
          >
            {suggestions.map((suggestion, idx) => (
              <li
                key={suggestion.place_id}
                className={`px-4 py-2 cursor-pointer ${activeSuggestion === idx ? 'bg-gray-700' : ''}`}
                style={{ fontWeight: activeSuggestion === idx ? 600 : 400 }}
                onMouseDown={() => handleSuggestionClick(suggestion)}
                onMouseEnter={() => setActiveSuggestion(idx)}
              >
                {suggestion.description}
              </li>
            ))}
          </ul>
        )}
        <input
          type="text"
          placeholder={placeholder || 'Where?'}
          className="w-full px-4 py-3 rounded-lg bg-gray-800 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500"
          ref={inputRef}
          value={inputValue}
          onChange={handleChange}
          onBlur={handleBlur}
          onFocus={handleFocus}
          onKeyDown={handleKeyDown}
          autoComplete="off"
        />
      </div>
    );
  };

  export default PlaceAutocompleteInput;