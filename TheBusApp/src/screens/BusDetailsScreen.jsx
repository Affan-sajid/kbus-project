import React, { useEffect, useRef } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';

/**
 * BusDetailsScreen shows a map centered on the destination and details about the selected bus.
 * Expects router state: { bus, placeFull }
 */
const BusDetailsScreen = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const mapRef = useRef(null);
  const { bus, placeFull } = location.state || {};

  // Center map on the destination using Google Maps Places API
  useEffect(() => {
    if (!window.google || !placeFull || !mapRef.current) return;
    const map = new window.google.maps.Map(mapRef.current, {
      zoom: 13,
      center: { lat: 20.5937, lng: 78.9629 }, // fallback: center of India
    });
    // Geocode the placeFull to get coordinates
    const geocoder = new window.google.maps.Geocoder();
    geocoder.geocode({ address: placeFull }, (results, status) => {
      if (status === 'OK' && results[0]) {
        map.setCenter(results[0].geometry.location);
        new window.google.maps.Marker({
          map,
          position: results[0].geometry.location,
          title: placeFull,
        });
      }
    });
  }, [placeFull]);

  if (!bus || !placeFull) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-900 text-white">
        <div>
          <div className="mb-4">No bus or place data found.</div>
          <button className="px-4 py-2 bg-blue-600 rounded" onClick={() => navigate(-1)}>
            ← Back
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center justify-center bg-gray-900 text-white p-4">
      {/* Back button */}
      <button
        className="self-start mb-4 px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-800"
        onClick={() => navigate(-1)}
      >
        ← Back
      </button>
      {/* Map */}
      <div className="w-full max-w-md h-64 rounded-lg overflow-hidden mb-6 border border-blue-700" ref={mapRef} />
      {/* Bus details */}
      <div className="bg-gray-800 rounded-lg shadow-md p-6 w-full max-w-md">
        <div className="font-bold text-xl mb-2">{bus.name}</div>
        <div className="mb-1"><span className="font-semibold">Destination:</span> {placeFull}</div>
        <div className="mb-1"><span className="font-semibold">Duration:</span> {bus.duration}</div>
        <div className="mb-1"><span className="font-semibold">Departure:</span> {bus["drive in"]}</div>
        <div className="mb-1"><span className="font-semibold">Fare:</span> {bus.fare}</div>
        {/* Add more details here as needed */}
      </div>
    </div>
  );
};

export default BusDetailsScreen; 