// Bus Time Finder App - Simple, Commented Version
// This script powers the interactive map and search for the Bus Time Finder app.
// It manages the map, search inputs, markers, and the travel plans overlay.

// This function is called by Google Maps when the map is ready
function initApp() {
    // Create our main app object
    busApp = new SimpleBusTimeFinder();
}

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

        // Start the app
        this.init();
    }

    // Main setup function
    init() {
        this.setupMap();
        this.setupAutocomplete();
        this.setupEvents();
        this.showCollapsedSearch();
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
            this.ui.bottomSheet.classList.add('expanded');
            this.ui.bottomSheet.classList.remove('collapsed');

        });
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
                this.ui.fromInput.setAttribute('data-actual-address', response.results[0].formatted_address);
                this.ui.fromInput.setAttribute('placeholder', `current location - ${response.results[0].formatted_address}`);
            }
        } catch (e) {
            this.showNotification('Could not get address for your location.', 'error');
        }
    }

    // Show the travel plans overlay
    showOverlay() {
        this.state.overlayOpen = true;
        this.ui.overlay.style.display = 'flex';
        this.ui.bottomSheet.classList.add('hidden');
        this.renderTravelPlans();
    }

    // Hide the overlay and go back to expanded search
    hideOverlay() {
        this.state.overlayOpen = false;
        this.ui.overlay.style.display = 'none';
        this.ui.bottomSheet.classList.remove('hidden');
        this.showExpandedSearch();
    }

    // Show a list of possible bus routes (mock data)
    renderTravelPlans() {
        // Example routes (replace with real data from backend later)
        const routes = [
            { bus_number: "Bus Nº 31", route: "A → B", departure: "16:00", arrival: "17:00", duration: "1h", transfers: 0, fare: "₹30" },
            { bus_number: "Central Line", route: "A → C → B", departure: "16:15", arrival: "17:30", duration: "1h 15m", transfers: 1, fare: "₹25" },
            { bus_number: "Tram Nº 17", route: "A → D → B", departure: "16:20", arrival: "17:40", duration: "1h 20m", transfers: 2, fare: "₹20" },
        ];
        this.ui.travelList.innerHTML = '';
        routes.forEach((route) => {
            const card = document.createElement('div');
            card.className = 'travel-card';
            card.innerHTML = `
                <div class="card-row">
                    <span class="bus-icon"><i class="fas fa-bus"></i></span>
                    <span class="route-name">${route.bus_number}</span>
                    <span class="fare">${route.fare}</span>
                </div>
                <div class="card-row times">
                    <span>Dep: ${route.departure}</span>
                    <span>Arr: ${route.arrival}</span>
                    <span>${route.duration}</span>
                </div>
                <div class="details">
                    <span>${route.transfers === 0 ? 'Direct' : `Change ${route.transfers} time${route.transfers > 1 ? 's' : ''}`}</span>
                    <span>${route.route}</span>
                </div>
            `;
            card.addEventListener('click', () => this.selectRoute(card, route));
            this.ui.travelList.appendChild(card);
        });
        this.state.selectedRoute = null;
        this.ui.confirmBtn.style.display = 'none';
    }

    // When a route card is clicked, highlight it and show confirm button
    selectRoute(card, route) {
        document.querySelectorAll('.travel-card').forEach(c => c.classList.remove('selected'));
        card.classList.add('selected');
        this.state.selectedRoute = route;
        this.ui.confirmBtn.style.display = 'block';
    }

    // When confirm is clicked, show notification and return to map
    confirmTrip() {
        if (!this.state.selectedRoute) return;
        this.showNotification('Trip confirmed!', 'success');
        setTimeout(() => this.hideOverlay(), 1200);
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
//   }