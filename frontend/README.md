# Bus Time Finder - Frontend

A mobile-friendly, single-page web application for finding bus routes in India. Built with vanilla HTML, CSS, and JavaScript with Google Maps integration.

## Features

- 🚌 **Bus Route Search**: Find bus routes between any two locations in India
- 📍 **Google Maps Integration**: Powered by Google Places Autocomplete
- 📱 **Mobile-First Design**: Responsive design optimized for mobile devices
- 🎯 **Geolocation**: Use current location with GPS detection
- 🔍 **Smart Search**: Real-time autocomplete for locations
- 📋 **Results Modal**: Clean display of bus routes with detailed information
- ✅ **Trip Confirmation**: Select and confirm your preferred route

## Setup Instructions

### 1. Google Maps API Key

**Important**: You need a Google Maps API key for the application to work.

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project or select an existing one
3. Enable the following APIs:
   - Maps JavaScript API
   - Places API
   - Geocoding API (optional, for better reverse geocoding)
4. Create credentials (API Key)
5. Replace `YOUR_GOOGLE_MAPS_API_KEY` in `index.html` with your actual API key:

```html
<script src="https://maps.googleapis.com/maps/api/js?key=YOUR_ACTUAL_API_KEY&libraries=places"></script>
```

### 2. Backend Integration

The frontend expects a Flask backend running on the same domain with the following endpoint:

**POST** `/get-bus-times`

**Request Body:**
```json
{
  "from": "Mumbai, Maharashtra",
  "to": "Pune, Maharashtra"
}
```

**Expected Response:**
```json
{
  "next_buses": [
    {
      "bus_number": "AC-123",
      "departure_time": "09:30",
      "arrival_time": "10:15",
      "duration": "45 mins",
      "fare": "150",
      "interchanges": 0,
      "route": "Via Expressway"
    }
  ]
}
```

### 3. Running the Application

1. **Development**: Open `index.html` in a web browser
2. **Production**: Serve the files through a web server (required for geolocation)

```bash
# Using Python
python -m http.server 8000

# Using Node.js
npx serve .

# Using PHP
php -S localhost:8000
```

## File Structure

```
frontend/
├── index.html          # Main HTML structure
├── style.css           # Complete styling with mobile-first design
├── script.js           # JavaScript functionality
└── README.md           # This file
```

## Key Features Implementation

### Google Maps Autocomplete
- Restricted to India (`componentRestrictions: { country: 'in' }`)
- Supports both establishments and geocoding
- Real-time suggestions as you type

### Geolocation
- Uses browser's `navigator.geolocation` API
- Reverse geocoding via OpenStreetMap Nominatim
- Fallback to "Current Location" if geocoding fails

### Mobile-First Design
- Responsive breakpoints for different screen sizes
- Touch-friendly buttons and inputs
- Optimized for mobile browsers

### Modal System
- Centered overlay with backdrop
- Smooth animations and transitions
- Keyboard and click-to-close support

## Browser Compatibility

- ✅ Chrome 60+
- ✅ Firefox 55+
- ✅ Safari 12+
- ✅ Edge 79+
- ✅ Mobile browsers (iOS Safari, Chrome Mobile)

## API Dependencies

- **Google Maps JavaScript API**: For Places Autocomplete
- **OpenStreetMap Nominatim**: For reverse geocoding (free alternative to Google Geocoding)
- **Font Awesome**: For icons
- **Google Fonts (Inter)**: For typography

## Customization

### Colors
The app uses a purple gradient theme. To customize colors, modify the CSS variables in `style.css`:

```css
:root {
  --primary-color: #667eea;
  --secondary-color: #764ba2;
  --success-color: #38a169;
  --error-color: #e53e3e;
}
```

### Styling
- All components use CSS Grid and Flexbox for layout
- Smooth transitions and hover effects
- Consistent spacing using a modular scale
- Mobile-first responsive design

## Troubleshooting

### Google Maps Not Loading
- Check your API key is correct
- Ensure Maps JavaScript API and Places API are enabled
- Check browser console for error messages

### Geolocation Not Working
- Ensure you're running on HTTPS (required for geolocation)
- Check browser permissions for location access
- Some browsers require user interaction before allowing geolocation

### Autocomplete Not Working
- Verify Places API is enabled in Google Cloud Console
- Check API key has proper restrictions and quotas
- Ensure you're not hitting API limits

## Development Notes

- The app is built with vanilla JavaScript (ES6+)
- No build tools or frameworks required
- Modular class-based architecture
- Error handling for all async operations
- Graceful fallbacks for failed API calls

## License

This frontend is part of the Bus Time Finder project. Please refer to the main project license. 