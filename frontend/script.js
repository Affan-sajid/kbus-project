// Bus Time Finder App - Simple, Commented Version
// This script powers the interactive map and search for the Bus Time Finder app.
// It manages the map, search inputs, markers, and the travel plans overlay.

// This function is called by Google Maps when the map is ready

// Declare busApp in the module scope
let busApp;

// Define initApp function
function initApp() {
    busApp = new SimpleBusTimeFinder();
}

// Make initApp available globally for Google Maps
window.initApp = initApp;

// Main app class
class SimpleBusTimeFinder {
    constructor() {
        // Store references to important HTML elements
        this.ui = {
            mapDiv: document.getElementById('map'),
            searchArea: document.getElementById('searchArea'),
            collapsedInput: document.getElementById('destination-collapsed'),
            expandedSearch: document.getElementById('searchExpanded'),
            fromInput: document.getElementById('origin'),
            toInput: document.getElementById('destination'),
            useLocationBtn: document.getElementById('originLocationBtn'),
            findBusBtn: document.getElementById('findBusBtn'),
            bottomSheet: document.getElementById('bottom-sheet'),
            overlay: document.getElementById('travelPlansOverlay'),
            travelList: document.getElementById('travelList'),
            confirmBtn: document.getElementById('confirmTripBtn'),
            backBtn: document.getElementById('backToMapBtn'),
            collapsedRow: document.getElementById('searchRowCollapsed'),
            payTicketBtn: document.getElementById('payTicketBtn'),
            backToMainBtn: document.getElementById('backToMainBtn'),
            PaymentMenuScrBtn: document.getElementById('PaymentMenuScrBtn'),
            PaymentMenuScrOverlay: document.getElementById('PaymentMenuScr'),
        };

        // Store state (what's currently shown, selected, etc)
        this.state = {
            expanded: false, // Is the search area expanded?
            overlayOpen: false, // Is the travel plans overlay open?
            currentLocation: null, // User's geolocation
            selectedRoute: null, // Which bus route is selected?
        };

        // Google Maps objects
        this.map = null;
        this.fromMarker = null;
        this.toMarker = null;
        this.fromAutocomplete = null;
        this.toAutocomplete = null;
        this.routeLine = null;
        this.qrScanner = null;
        this.qrVideoElem = document.getElementById('qr-video');


        // Start the app
        this.init();
    }

    // Main setup function
    init() {
        this.setupMap();
        this.setupAutocomplete();
        this.setupEvents();
        this.showCollapsedSearch();
        // this.initQrScanner();
        this.hidepaynowscannereen();

    }
    stopQrScanner() {
        if (this.qrScanner) {
            this.qrScanner.stop();
        }
    }

    onQrScanned(result) {
        console.log('QR code result:', result);
        // You can add your logic here, e.g., process payment, close overlay, etc.
        this.qrScanner.stop(); // Optionally stop scanning after a successful scan
    }

    initQrScanner() {
        if (!this.qrScanner) {
            this.qrScanner = new QrScanner(
                this.qrVideoElem,
                result => this.onQrScanned(result),
                { returnDetailedScanResult: true }
            );
        }
        this.qrScanner.start();
    }

    showpaynowscannereen() {
        document.getElementById('paynowscanner').style.display = 'block';
        this.initQrScanner();

    }
    
    hidepaynowscannereen() {
        document.getElementById('paynowscanner').style.display = 'none';
        this.stopQrScanner();
        this.ui.bottomSheet.classList.add('collapsed');
        this.ui.bottomSheet.classList.remove('hidden');
        this.ui.bottomSheet.classList.remove('expanded');
    }

    // Set up the Google Map
    setupMap() {
        // Default to center of India
        const india = { lat: 20.5937, lng: 78.9629 };
        this.map = new google.maps.Map(this.ui.mapDiv, {
            center: india,
            zoom: 5,
            disableDefaultUI: true,
            gestureHandling: "greedy",
            styles: [ /* custom map style if needed */ ]
        });
        // Create markers (but hide them for now)
        this.fromMarker = new google.maps.Marker({ 
            map: this.map, 
            visible: false,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#34a853', // Green for 'from'
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#fff'
            }
        });
        this.toMarker = new google.maps.Marker({ 
            map: this.map, 
            visible: false,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale: 10,
                fillColor: '#ea4335', // Red for 'to'
                fillOpacity: 1,
                strokeWeight: 2,
                strokeColor: '#fff'
            }
        });
        // Try to get user's location
        if (navigator.geolocation) {
            navigator.geolocation.getCurrentPosition(
                (pos) => {
                    const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                    this.state.currentLocation = loc;
                    this.map.setCenter(loc);
                    this.map.setZoom(15);
                    this.fillFromWithLocation(loc);
                    this.setMarker('from', loc);
                },
                () => {
                    // If denied, just stay on India
                }
            );
        }
    }

    // Set up Google Places autocomplete for both inputs
    setupAutocomplete() {
        // Destination (To)
        this.toAutocomplete = new google.maps.places.Autocomplete(this.ui.toInput, {
            componentRestrictions: { country: 'in' },
            fields: ['place_id', 'geometry', 'name', 'formatted_address']
        });
        this.toAutocomplete.addListener('place_changed', () => {
            const place = this.toAutocomplete.getPlace();
            if (place && place.geometry) {
                this.setMarker('to', place.geometry.location);
                this.map.panTo(place.geometry.location);
                this.map.setZoom(15);
                // Store essential place data
                this.storePlaceData('to', place);
            }
        });
        // Origin (From)
        this.fromAutocomplete = new google.maps.places.Autocomplete(this.ui.fromInput, {
            componentRestrictions: { country: 'in' },
            fields: ['place_id', 'geometry', 'name', 'formatted_address']
        });
        this.fromAutocomplete.addListener('place_changed', () => {
            const place = this.fromAutocomplete.getPlace();
            if (place && place.geometry) {
                this.setMarker('from', place.geometry.location);
                // Store essential place data
                this.storePlaceData('from', place);
            }
        });
    }

    // Set up all button and input events
    setupEvents() {
        // Expand search when collapsed input is focused or clicked
        this.ui.collapsedInput.addEventListener('focus', () => this.showExpandedSearch());
        this.ui.collapsedInput.addEventListener('click', () => this.showExpandedSearch());

        // Collapse search if clicking outside (but not if overlay is open)
        document.addEventListener('click', (e) => {
            if (this.state.expanded && !this.ui.searchArea.contains(e.target) && !this.state.overlayOpen) {
                this.showCollapsedSearch();
            }
        });

        // Prevent form submit (so page doesn't reload)
        this.ui.searchArea.querySelector('form').addEventListener('submit', e => e.preventDefault());

        // Use geolocation for 'From' input get current location
        this.ui.useLocationBtn.addEventListener('click', () => {
            if (navigator.geolocation) {
                navigator.geolocation.getCurrentPosition(
                    (pos) => {
                        const loc = { lat: pos.coords.latitude, lng: pos.coords.longitude };
                        this.state.currentLocation = loc;
                        this.fillFromWithLocation(loc);
                        this.setMarker('from', loc);
                        this.map.setCenter(loc);
                        this.map.setZoom(15);
                        // Store current location as place data
                        this.storeCurrentLocationData(loc);
                    },
                    () => this.showNotification('Could not get your location.', 'error')
                );
            }
        });

        // Enable/disable Find Bus button as user types
        [this.ui.fromInput, this.ui.toInput].forEach(input => {
            input.addEventListener('input', () => this.updateFindBusButton());
        });

        // Show travel plans overlay when Find Bus is clicked
        this.ui.findBusBtn.addEventListener('click', () => {
            if (!this.ui.findBusBtn.classList.contains('enabled')) return;
            this.showOverlay();
        });

        // Hide overlay and go back to map
        this.ui.backBtn.addEventListener('click', () => this.hideOverlay());

        // Confirm trip
        this.ui.confirmBtn.addEventListener('click', () => this.confirmTrip());

        this.ui.bottomSheet.addEventListener('click', () => {
            if (this.ui.bottomSheet.classList.contains('collapsed')) {
                this.ui.bottomSheet.classList.remove('collapsed');
                this.ui.bottomSheet.classList.add('expanded');
            } else {
                this.ui.bottomSheet.classList.remove('expanded');
                this.ui.bottomSheet.classList.add('collapsed');
            }
            this.ui.bottomSheet.classList.remove('hidden');
        });

        this.ui.payTicketBtn.addEventListener('click', () => this.showpaynowscannereen());
        this.ui.backToMainBtn.addEventListener('click', () => this.hidepaynowscannereen());
        // Show recharge wallet overlay
        this.ui.PaymentMenuScrBtn.addEventListener('click', () => this.showPaymentMenuScr());
        // Close recharge wallet overlay
        const closeRechargeBtn = document.getElementById('closePaymentMenuScrBtn');
        if (closeRechargeBtn) {
            closeRechargeBtn.addEventListener('click', () => this.hidePaymentMenuScr());
        }
    }

    // Show collapsed search (single input)
    showCollapsedSearch() {
        this.state.expanded = false;
        this.ui.collapsedRow.style.display = '';
        this.ui.expandedSearch.style.display = 'none';
        this.ui.findBusBtn.style.display = 'none';
        this.ui.bottomSheet.classList.add('collapsed');
        this.ui.bottomSheet.classList.remove('hidden');
        this.ui.bottomSheet.classList.remove('expanded');
    }

    // Show expanded search (both inputs)
    showExpandedSearch() {
        this.state.expanded = true;
        this.ui.collapsedRow.style.display = 'none';
        this.ui.expandedSearch.style.display = '';
        this.ui.bottomSheet.classList.remove('collapsed');
        this.ui.bottomSheet.classList.remove('expanded');
        this.ui.bottomSheet.classList.add('hidden');
        this.updateFindBusButton();
    }

    // Enable Find Bus button only if both fields are filled
    updateFindBusButton() {
        const from = this.ui.fromInput.value.trim();
        const to = this.ui.toInput.value.trim();
        if (to) {
            this.ui.findBusBtn.style.display = 'block';
            this.ui.findBusBtn.classList.add('enabled');
            this.ui.findBusBtn.disabled = false;
        } else {
            this.ui.findBusBtn.style.display = 'block';
            this.ui.findBusBtn.classList.remove('enabled');
            this.ui.findBusBtn.disabled = true;
        }
    }

    // Place or move a marker on the map
    setMarker(type, location) {
        if (!location) return;
        if (type === 'from') {
            this.fromMarker.setPosition(location);
            this.fromMarker.setVisible(true);
            this.fromMarkerLoc = location;
        } else if (type === 'to') {
            this.toMarker.setPosition(location);
            this.toMarker.setVisible(true);
            this.toMarkerLoc = location;
        }
        // Draw or update the line if both markers are set
        if (this.fromMarker.getVisible() && this.toMarker.getVisible()) {
            // Remove old line if exists
            if (this.routeLine) this.routeLine.setMap(null);
            this.routeLine = new google.maps.Polyline({
                path: [
                    this.fromMarker.getPosition(),
                    this.toMarker.getPosition()
                ],
                geodesic: true,
                strokeColor: '#3182ce',
                strokeOpacity: 0.9,
                strokeWeight: 4,
                map: this.map
            });
            // --- Fit map to show both markers ---
            const bounds = new google.maps.LatLngBounds();
            bounds.extend(this.fromMarker.getPosition());
            bounds.extend(this.toMarker.getPosition());
            this.map.fitBounds(bounds, 100); // 100px padding
        } else if (this.routeLine) {
            // Remove the line if one marker is missing
            this.routeLine.setMap(null);
            this.routeLine = null;
        }
    }

    // Fill the 'From' input with the user's current location (reverse geocode)
    async fillFromWithLocation(location) {
        const geocoder = new google.maps.Geocoder();
        try {
            const response = await geocoder.geocode({ location });
            if (response.results[0]) {
                this.ui.fromInput.value = '';
                this.ui.fromInput.setAttribute('data-current-address', response.results[0].formatted_address);
                this.ui.fromInput.setAttribute('placeholder', `current location - ${response.results[0].formatted_address}`);
            }
        } catch (e) {
            this.showNotification('Could not get address for your location.', 'error');
        }
    }

    // Show the travel plans overlay
    showOverlay() {
        let fromLocation = this.ui.fromInput.value.trim();
        const toLocation = this.ui.toInput.value.trim();
        const currentAddress = this.ui.fromInput.getAttribute('data-current-address');
        
        // Get structured place data
        let fromPlaceData = this.ui.fromInput.getAttribute('data-place-data');
        const toPlaceData = this.ui.toInput.getAttribute('data-place-data');
        
        this.state.overlayOpen = true;
        this.ui.overlay.style.display = 'flex';
        this.ui.bottomSheet.classList.add('hidden');
        this.renderTravelPlans(fromLocation, toLocation, fromPlaceData, toPlaceData);
    }

    // Hide the overlay and go back to expanded search
    hideOverlay() {
        this.state.overlayOpen = false;
        this.ui.overlay.style.display = 'none';
        this.ui.bottomSheet.classList.remove('hidden');
        this.showExpandedSearch();
    }

    // Show a list of possible bus routes (fetch from backend)
    async renderTravelPlans(fromLocation, toLocation, fromPlaceData, toPlaceData) {
        try {
            // Show loading state
            this.ui.travelList.innerHTML = '<div class="loading">Finding routes...</div>';
            
            // Fetch routes from backend
            const response = await fetch('http://localhost:8000/test', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    from: fromLocation,
                    to: toLocation,
                    fromPlaceData: fromPlaceData,
                    toPlaceData: toPlaceData
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            const routes = data.routes || [];
            
            // Clear loading and render routes
            this.ui.travelList.innerHTML = '';
            
            if (routes.length === 0) {
                this.ui.travelList.innerHTML = '<div class="no-routes">No routes found for this journey.</div>';
                return;
            }
            
            routes.forEach((route) => {
                
                console.log(route.plan)
                console.log(routes)
                

                const card = document.createElement('div');
                card.className = 'route-card';
                card.innerHTML = `
                   <div class="left">
                    <div class="up">
                        <div class="busname">
                            <span class="icon">
                                <img src="assets/Frame 26.png" alt="">
                            </span>
                            <span class="text">${route.bus_name}</span>
                        </div>
                        <div class="fare">
                            <span class="faretext">${route.fare}</span>
                        </div>
                    </div>
                    <div class="down">
                        <div class="details">

                            <div class="arrival">
                                <span class="icon">
                                    <img src="assets/Arrow.png" alt="">
                                </span>
                                <span class="arrivatext">
                                    Arrival : ${route.arrival}
                                </span>
                            </div>

                            <div class="duration">
                                <span class="icon">
                                    <img src="assets/clock.png" alt="clock">
                                </span>
                                <span class="durationtext">Duration : ${route.duration}</span>
                            </div>
                        </div>
                        <div class="busroute">
                            <div class="center">
                                ${route.plan.map(planpart => `
                                    <div class="object">
                                        <img src="assets/icons/${planpart.type}.png" alt="">
                                        <span>${planpart.distance}</span>
                                    </div>
                                `).join('')}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="right">
                    <span class="time">${route.departure_in}</span>
                    <span>min</span>
                </div>
                `
                card.addEventListener('click', () => this.selectRoute(card, route));
                this.ui.travelList.appendChild(card);
            });
            this.state.selectedRoute = null;
            this.ui.confirmBtn.style.display = 'none';
        } catch (error) {
            console.error('Error fetching routes:', error);
            this.ui.travelList.innerHTML = '<div class="error">Failed to load routes. Please try again.</div>';
            this.showNotification('Failed to load routes. Please check your connection.', 'error');
        }
    }

    // When a route card is clicked, highlight it and show confirm button
    selectRoute(card, route) {
        document.querySelectorAll('.route-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.state.selectedRoute = route;
        this.ui.confirmBtn.style.display = 'block';
    }

    // When confirm is clicked, show notification and return to map
    confirmTrip() {
        if (!this.state.selectedRoute) return;
        this.showNotification('Trip confirmed!', 'success');
        setTimeout(() => this.hideOverlay(), 1200);
        this.showJourneyOverlay();
    }

    // Show a notification at the top of the screen
    showNotification(message, type) {
        const old = document.querySelector('.notification');
        if (old) old.remove();
        const note = document.createElement('div');
        note.className = `notification ${type}`;
        note.innerHTML = `<i class="fas fa-${type === 'error' ? 'exclamation-circle' : 'check-circle'}"></i> ${message}`;
        document.body.appendChild(note);
        setTimeout(() => note.remove(), 4000);
    }

    // Store essential place data from Google Places API
    storePlaceData(type, place) {
        // Create a clean place object with only essential data
        const placeData = {
            place_id: place.place_id,
            name: place.name,
            formatted_address: place.formatted_address,
            coordinates: {
                lat: place.geometry.location.lat(),
                lng: place.geometry.location.lng()
            }
        };
        // Store as JSON string in data attribute
        const input = type === 'from' ? this.ui.fromInput : this.ui.toInput;
        input.setAttribute('data-place-data', JSON.stringify(placeData));
        // Also store coordinates separately for backward compatibility
        input.setAttribute('data-lat', place.geometry.location.lat());
        input.setAttribute('data-lng', place.geometry.location.lng());
        console.log(`${type.toUpperCase()} Place Data:`, placeData);
    }

    // Store current location as place data
    storeCurrentLocationData(location) {
        // Create a clean place object with only essential data
        const placeData = {
            place_id: null,
            name: 'Current Location',
            formatted_address: this.ui.fromInput.getAttribute('data-current-address') || 'Current Location',
            coordinates: {
                lat: location.lat,
                lng: location.lng
            }
        };
        // Store as JSON string in data attribute
        this.ui.fromInput.setAttribute('data-place-data', JSON.stringify(placeData));
        // Also store coordinates separately for backward compatibility
        this.ui.fromInput.setAttribute('data-lat', location.lat);
        this.ui.fromInput.setAttribute('data-lng', location.lng);
        console.log('Current Location Data:', placeData);
    }

    showPaymentMenuScr() {
        this.ui.PaymentMenuScrOverlay.style.display = 'flex';
    }
    hidePaymentMenuScr() {
        this.ui.PaymentMenuScrOverlay.style.display = 'none';
    }
}

// If Google Maps fails to load, show an error in the console
window.addEventListener('error', (e) => {
    if (e.message && e.message.includes('Google Maps')) {
        console.error('Google Maps API failed to load');
    }
});

// function showPage(pageId) {
//     document.querySelectorAll('.page-section').forEach(div => div.classList.remove('active'));
//     document.getElementById(pageId).classList.add('active');
// }

// Show the journey overlay and initialize the map
function showJourneyOverlay() {
    // Show the overlay
    document.getElementById('confirmTrip').style.display = 'flex';

    // Initialize the map only if not already initialized
    const mapDiv = document.getElementById('journeyMap');
    if (!mapDiv) return;
    if (mapDiv.dataset.mapInitialized) return;

    // Example center (Calicut Railway Station)
    const center = { lat: 11.2541, lng: 75.7810 };
    const journeyMap = new google.maps.Map(mapDiv, {
        center: center,
        zoom: 15,
        disableDefaultUI: true,
    });
    // Example marker
    new google.maps.Marker({ position: center, map: journeyMap, title: "Start" });

    mapDiv.dataset.mapInitialized = 'true';
}

// load the map