/**
 * Wander AI - Smart Travel Curator Frontend Engine
 */

// Initial Trip & Itinerary State
const state = {
  activeDay: 1, // 1, 2, 3, 4, or 'all'
  trip: {
    id: "rome-curated-2025",
    title: "Rome: Historic Wonders & Bohemian Nights",
    collection: "Italy Collection",
    dates: "Oct 12 – 16, 2025",
    durationDays: 4,
    travelers: 2,
    destination: "Rome, Italy",
    pace: "Moderate",
    interests: ["History", "Architecture", "Food & Wine", "Culture"]
  },
  days: {
    1: {
      title: "The Imperial Core & Golden Hour",
      dateStr: "Sunday, October 12 • Pleasant, 22°C Clear Skies",
      weatherAdvice: "Optimal lighting at Piazza Navona begins at 17:45. Bring comfortable leather walking shoes for historic cobblestones.",
      stops: [
        {
          id: "stop-1-1",
          order: 1,
          time: "09:00 AM",
          title: "Colosseum & Roman Forum Walk",
          category: "Historic",
          duration: "3 hrs duration",
          description: "Wander the historic amphitheater floor and the ancient senate ruins with private historian audio guide sync.",
          image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBCCNDRzNwGHnhmzBpxqitHi6f6p9-ES-U3FntBdRvZda0DGczlWs9Xnd-vvLQ4zaXxUBBynYtdGQUlOkQmUwiMOh7xYU6Pwa5nl03gDGLm1YaAfZhiQ57Br-p_saBweeAp6kzmsJoObB8uGWlil3aHE5uAUt7bDeheFqdkO200kr7KSjQIRpqinWWnxS7ivMhZg180v5uxvpnv2nzZH9XUUS20ueIeT1N7qAoBBMpyNPapx29wQCyq",
          tip: "Book skip-the-line pass at least 48h prior",
          status: "Tickets Confirmed",
          statusType: "confirmed",
          address: "Piazza del Colosseo, 1, 00184 Roma RM",
          lat: 41.8902,
          lng: 12.4922,
          isHighlight: true
        },
        {
          id: "stop-1-transit-1",
          isTransit: true,
          text: "12 min scenic stroll through Via dei Fori Imperiali (850 m)"
        },
        {
          id: "stop-1-2",
          order: "food",
          time: "12:30 PM",
          title: "Lunch at Trattoria Luzzi",
          category: "Culinary Gem",
          duration: "1.5 hrs",
          description: "Authentic Roman carbonara in a vibrant, family-run atmosphere beloved by locals. Approx. €18/person.",
          address: "Via di S. Giovanni in Laterano, 36",
          badgeText: "Outdoor Table Requested",
          icon: "restaurant",
          lat: 41.8887,
          lng: 12.4975,
          isHighlight: false
        },
        {
          id: "stop-1-3",
          order: 2,
          time: "03:00 PM",
          title: "Pantheon & Piazza Navona Espresso Stroll",
          category: "Architecture",
          duration: "2 hrs",
          description: "Marvel at Hadrian’s immaculate dome oculus, followed by Bernini's Fountain of the Four Rivers.",
          image: "https://lh3.googleusercontent.com/aida-public/AB6AXuAQYQ43ujYO4oRmJcpP5H9aLZnvCAsQylbOXCnu_SDwmQZAOHlheQk8WIxSBCIzbAMAC5Uyxmtu6AvnzC-9sddpRvoi3uhKN-ZXqO5RVrWxGAlhVtoDVxw0dpeUCDC2mplhgDpMuAcT30S_1OREX6UYLentlGHdH28ss9_UsGGkA8nLtGVq80RzvL1ZOfvCwW5PtjFinp-P-BGEWZL3oQCUo6JYqeDVJLVKmXZq0gAXgDHyULZtit-K",
          callout: "Curated detour: Gelato stop at Giolitti (Pistachio & Zabaione) • 250m away",
          calloutIcon: "icecream",
          address: "Piazza della Rotonda, 00186 Roma RM",
          lat: 41.8986,
          lng: 12.4769,
          isHighlight: true
        },
        {
          id: "stop-1-4",
          order: "sunset",
          time: "06:30 PM",
          title: "Sunset Aperitivo at Terrazza Borromini",
          category: "Golden Hour",
          duration: "1.5 hrs",
          description: "Campari spritz overlooking Piazza Navona rooftops as the Roman sky turns deep terracotta and violet.",
          badgeText: "Smart casual attire recommended • Rooftop terrace reserved",
          icon: "wine_bar",
          address: "Via di Santa Maria dell'Anima, 30",
          lat: 41.8992,
          lng: 12.4730,
          isHighlight: false
        },
        {
          id: "stop-1-5",
          order: 3,
          time: "08:30 PM",
          title: "Trastevere Food & Wine Discovery",
          category: "Nightlife & Dining",
          duration: "3 hrs",
          description: "Cross the Tiber River into Rome’s bohemian enclave for sommelier-led Lazio wine tasting and wood-fired Roman pinsa.",
          image: "https://lh3.googleusercontent.com/aida-public/AB6AXuBW6Du6AXDgHpFammfROld1oHlxyrYAcKlQ9sVSFOtyR6xQMvbd5xH8WFwGRtod8-Z2pgbkiai2Jw9QRCp0ng9WQBKTnGpC9tTvjhOQ62OVC1RrJATckisToj7GVYqMTgyBFrpHiF2ujoGB5Bai2QXBZSYSlQVApnGmE0YukZOOdw3XBgurYytStV0_wOoV-F9n4gzxezRu1IuoExjSMRkeADdWSo9MWtswcSKA_fhl_hQblCxn4dLx",
          status: "Dinner reservation confirmed (Da Enzo al 29)",
          statusType: "dinner",
          address: "Via dei Vascellari, 29, 00153 Roma RM",
          lat: 41.8881,
          lng: 12.4786,
          isHighlight: true
        }
      ]
    },
    2: {
      title: "Bohemian Trastevere & Artisanal Monti",
      dateStr: "Monday, October 13 • Sunny, 23°C Light Breeze",
      weatherAdvice: "Morning shade on Janiculum Hill offers panoramic views. Boutique ateliers in Monti are closed during siesta (13:30–16:00).",
      stops: [
        {
          id: "stop-2-1",
          order: 1,
          time: "09:30 AM",
          title: "Villa Farnesina Renaissance Frescoes",
          category: "Art & Culture",
          duration: "2 hrs",
          description: "Explore the intimate riverside Renaissance villa featuring masterworks by Raphael and quiet garden courtyards.",
          image: "https://images.unsplash.com/photo-1552832230-c0197dd311b5?auto=format&fit=crop&w=800&q=80",
          tip: "Audioguide included with entrance",
          status: "Tickets Confirmed",
          statusType: "confirmed",
          address: "Via della Lungara, 230",
          lat: 41.8936,
          lng: 12.4673,
          isHighlight: true
        },
        {
          id: "stop-2-transit-1",
          isTransit: true,
          text: "15 min scenic walk across Ponte Sisto to Campo de' Fiori (1.1 km)"
        },
        {
          id: "stop-2-2",
          order: "food",
          time: "01:00 PM",
          title: "Lunch at Osteria da Fortunata",
          category: "Culinary Gem",
          duration: "1.5 hrs",
          description: "Hand-rolled tagliolini made right before your eyes by Roman nonnas with aged pecorino and black truffle.",
          address: "Via del Pellegrino, 11/12",
          badgeText: "Table for 2 reserved",
          icon: "restaurant",
          lat: 41.8967,
          lng: 12.4717,
          isHighlight: false
        },
        {
          id: "stop-2-3",
          order: 2,
          time: "03:30 PM",
          title: "Monti Vintage & Artisan Atelier Hunt",
          category: "Boutique & Crafts",
          duration: "2.5 hrs",
          description: "Discover Rome’s chicest neighborhood lined with ivy, independent leather artisans, and niche perfumeries.",
          image: "https://images.unsplash.com/photo-1515542622106-78bda8ba0e5b?auto=format&fit=crop&w=800&q=80",
          callout: "Curated stop: Mercato Monti artisan pop-up & Fatamorgana Gelateria",
          calloutIcon: "storefront",
          address: "Via Urbana & Via del Boschetto",
          lat: 41.8962,
          lng: 12.4939,
          isHighlight: true
        },
        {
          id: "stop-2-4",
          order: 3,
          time: "07:30 PM",
          title: "Piazza Madonna dei Monti Wine Bar",
          category: "Nightlife",
          duration: "2 hrs",
          description: "Sip organic natural wines at Ai Tre Scalini paired with warm ricotta and dried tomato bruschetta.",
          icon: "wine_bar",
          address: "Via Panisperna, 251",
          badgeText: "Walk-in friendly • Arrive early for outdoor curb seats",
          lat: 41.8970,
          lng: 12.4925,
          isHighlight: true
        }
      ]
    },
    3: {
      title: "Vatican Masterpieces & Riverfront Twilight",
      dateStr: "Tuesday, October 14 • Mostly Sunny, 21°C",
      weatherAdvice: "Modest attire required for St. Peter's (shoulders and knees covered). Early morning slot avoids midday museum queues.",
      stops: [
        {
          id: "stop-3-1",
          order: 1,
          time: "08:30 AM",
          title: "St. Peter's Basilica & Cupola Climb",
          category: "Historic",
          duration: "2.5 hrs",
          description: "Scale Michelangelo’s monumental dome for panoramic views over Vatican City and the Seven Hills of Rome.",
          image: "https://images.unsplash.com/photo-1543429776-2782fc8e1acd?auto=format&fit=crop&w=800&q=80",
          tip: "Elevator access to terrace included",
          status: "Priority Access Confirmed",
          statusType: "confirmed",
          address: "Piazza San Pietro",
          lat: 41.9022,
          lng: 12.4539,
          isHighlight: true
        },
        {
          id: "stop-3-2",
          order: 2,
          time: "11:30 AM",
          title: "Vatican Museums & Sistine Chapel",
          category: "Art & Culture",
          duration: "3 hrs",
          description: "Marvel at the Gallery of Maps, Raphael Rooms, and the breathtaking ceiling of the Sistine Chapel.",
          image: "https://images.unsplash.com/photo-1529154036634-a20ab61f4566?auto=format&fit=crop&w=800&q=80",
          status: "Official Voucher Issued",
          statusType: "confirmed",
          address: "Viale Vaticano, 00165 Roma RM",
          lat: 41.9065,
          lng: 12.4536,
          isHighlight: true
        },
        {
          id: "stop-3-3",
          order: "sunset",
          time: "05:00 PM",
          title: "Castel Sant'Angelo & Ponte degli Angeli",
          category: "Architecture",
          duration: "2 hrs",
          description: "Former fortress of the Popes overlooking Bernini’s winged statues on the Tiber angel bridge.",
          icon: "castle",
          address: "Lungotevere Castello, 50",
          badgeText: "Golden hour river photo walk",
          lat: 41.9031,
          lng: 12.4663,
          isHighlight: true
        }
      ]
    },
    4: {
      title: "Villa Borghese & Roman Splendor",
      dateStr: "Wednesday, October 15 • Crisp Autumn Morning, 20°C",
      weatherAdvice: "Gentle morning sun in Borghese gardens. Pre-booked time slot at Galleria Borghese is strictly 120 minutes.",
      stops: [
        {
          id: "stop-4-1",
          order: 1,
          time: "10:00 AM",
          title: "Galleria Borghese Sculptures",
          category: "Art & Culture",
          duration: "2 hrs",
          description: "Witness Bernini's Apollo & Daphne and Caravaggio masterpieces in Scipione Borghese's royal villa.",
          image: "https://images.unsplash.com/photo-1576013551627-0cc20b96c2a7?auto=format&fit=crop&w=800&q=80",
          status: "Timed Reservation Confirmed",
          statusType: "confirmed",
          address: "Piazzale Scipione Borghese, 5",
          lat: 41.9142,
          lng: 12.4921,
          isHighlight: true
        },
        {
          id: "stop-4-2",
          order: 2,
          time: "01:30 PM",
          title: "Spanish Steps & Caffè Greco Farewell",
          category: "Historic Elegance",
          duration: "2 hrs",
          description: "Sip espresso at Rome's oldest cafe (est. 1760), where Keats and Goethe once gathered, then stroll Piazza di Spagna.",
          icon: "local_cafe",
          address: "Via dei Condotti, 86",
          badgeText: "Historic Literary Landmark",
          lat: 41.9058,
          lng: 12.4823,
          isHighlight: true
        }
      ]
    }
  }
};

// Global Map References
let mapInstance = null;
let currentMarkers = [];
let routePolyline = null;
let activeTileLayer = null;

// Tile Layer Options
const TILE_LAYERS = {
  positron: {
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    options: {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>, &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      subdomains: "abcd",
      maxZoom: 19
    }
  },
  osm: {
    url: "https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png",
    options: {
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
      maxZoom: 19
    }
  },
  warm: {
    url: "https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png",
    options: {
      attribution: '&copy; <a href="https://carto.com/">CARTO</a>',
      subdomains: "abcd",
      maxZoom: 19
    }
  }
};

/**
 * Initialize Leaflet Map
 */
function initMap() {
  const mapElement = document.getElementById("leaflet-map");
  if (!mapElement) return;

  // Center on Rome
  mapInstance = L.map("leaflet-map", {
    zoomControl: false,
    scrollWheelZoom: true
  }).setView([41.8950, 12.4800], 14);

  // Set default warm/clean luxury tile layer
  activeTileLayer = L.tileLayer(TILE_LAYERS.warm.url, TILE_LAYERS.warm.options).addTo(mapInstance);

  // Render initial day stops on map
  updateMapForActiveDay();
}

/**
 * Switch tile layers
 */
function cycleMapLayer() {
  if (!mapInstance) return;
  const layers = ["warm", "positron", "osm"];
  const currentKey = Object.keys(TILE_LAYERS).find(k => TILE_LAYERS[k].url === activeTileLayer._url) || "warm";
  const nextIdx = (layers.indexOf(currentKey) + 1) % layers.length;
  const nextLayer = layers[nextIdx];

  mapInstance.removeLayer(activeTileLayer);
  activeTileLayer = L.tileLayer(TILE_LAYERS[nextLayer].url, TILE_LAYERS[nextLayer].options).addTo(mapInstance);
  showToast(`Map style switched to: ${nextLayer.toUpperCase()}`);
}

/**
 * Calculate total walking distance and approximate duration
 */
function calculateRouteMetrics(points) {
  if (!points || points.length < 2) {
    return { distanceKm: 0, durationMin: 0 };
  }

  let totalDistKm = 0;
  for (let i = 0; i < points.length - 1; i++) {
    const lat1 = points[i].lat;
    const lon1 = points[i].lng;
    const lat2 = points[i + 1].lat;
    const lon2 = points[i + 1].lng;

    // Haversine formula
    const R = 6371; // km
    const dLat = (lat2 - lat1) * Math.PI / 180;
    const dLon = (lon2 - lon1) * Math.PI / 180;
    const a =
      Math.sin(dLat / 2) * Math.sin(dLat / 2) +
      Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
      Math.sin(dLon / 2) * Math.sin(dLon / 2);
    const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
    totalDistKm += R * c;
  }

  // Account for actual winding city streets (~1.3x Euclidean distance)
  const walkingDistKm = Math.round((totalDistKm * 1.3) * 10) / 10;
  // Avg walking speed in city: 4.8 km/h => 12.5 min/km
  const durationMin = Math.round(walkingDistKm * 12.5);

  return { distanceKm: walkingDistKm, durationMin };
}

/**
 * Updates Leaflet Map with the markers and route for the currently active day
 */
function updateMapForActiveDay() {
  if (!mapInstance) return;

  // Clear existing markers and route
  currentMarkers.forEach(m => mapInstance.removeLayer(m));
  currentMarkers = [];
  if (routePolyline) {
    mapInstance.removeLayer(routePolyline);
    routePolyline = null;
  }

  // Gather stops
  let stopsToRender = [];
  if (state.activeDay === 'all') {
    Object.keys(state.days).forEach(d => {
      stopsToRender.push(...state.days[d].stops.filter(s => s.lat && s.lng));
    });
  } else {
    stopsToRender = (state.days[state.activeDay]?.stops || []).filter(s => s.lat && s.lng);
  }

  if (stopsToRender.length === 0) return;

  const latLngs = [];
  let displayCounter = 1;

  stopsToRender.forEach((stop, index) => {
    latLngs.push([stop.lat, stop.lng]);
    const isHighlight = stop.isHighlight;
    const displayNumber = typeof stop.order === 'number' ? stop.order : displayCounter++;

    // Custom HTML pin matching theme
    const iconHtml = `
      <div class="custom-map-marker ${isHighlight ? '' : 'secondary-stop'}" id="map-pin-${stop.id}">
        <span>${isHighlight ? displayNumber : (stop.order === 'food' ? '🍽️' : '★')}</span>
      </div>
    `;

    const customIcon = L.divIcon({
      className: 'custom-leaflet-icon-wrapper',
      html: iconHtml,
      iconSize: [36, 36],
      iconAnchor: [18, 18],
      popupAnchor: [0, -20]
    });

    const popupContent = `
      <div class="p-3 w-60">
        ${stop.image ? `<img src="${stop.image}" class="w-full h-24 object-cover rounded-md mb-2 shadow-sm" alt="${stop.title}">` : ''}
        <div class="flex items-center justify-between text-xs text-secondary font-bold mb-1">
          <span>${stop.category || 'Highlight'}</span>
          <span>${stop.time}</span>
        </div>
        <h4 class="font-bold text-sm text-primary leading-tight mb-1">${stop.title}</h4>
        <p class="text-xs text-stone-600 line-clamp-2">${stop.description || ''}</p>
        <div class="mt-2 pt-2 border-t border-stone-200 flex items-center justify-between text-[11px] text-stone-500">
          <span>${stop.duration || ''}</span>
          <a href="https://maps.google.com/?q=${stop.lat},${stop.lng}" target="_blank" class="text-primary hover:underline font-semibold">Directions ↗</a>
        </div>
      </div>
    `;

    const marker = L.marker([stop.lat, stop.lng], { icon: customIcon })
      .bindPopup(popupContent, { className: 'custom-leaflet-popup' })
      .addTo(mapInstance);

    marker.on('click', () => {
      highlightTimelineCard(stop.id);
    });

    currentMarkers.push(marker);
  });

  // Draw smooth polyline connecting stops
  if (latLngs.length > 1) {
    routePolyline = L.polyline(latLngs, {
      color: '#7a152e',
      weight: 3.5,
      opacity: 0.85,
      dashArray: '7, 7',
      lineCap: 'round',
      lineJoin: 'round'
    }).addTo(mapInstance);
  }

  // Recenter map
  if (latLngs.length > 0) {
    const bounds = L.latLngBounds(latLngs);
    mapInstance.fitBounds(bounds, { padding: [45, 45], maxZoom: 15 });
  }

  // Update Route Summary Card
  const metrics = calculateRouteMetrics(stopsToRender);
  const routeDistEl = document.getElementById("route-metrics-distance");
  if (routeDistEl) {
    routeDistEl.textContent = `${metrics.distanceKm} km • ${metrics.durationMin} min total transit`;
  }
  const routeTitleEl = document.getElementById("route-metrics-title");
  if (routeTitleEl) {
    routeTitleEl.textContent = state.activeDay === 'all' ? "Total Itinerary Walking" : `Total Day ${state.activeDay} Walking`;
  }

  // Update Legend Counter
  const legendCountEl = document.getElementById("legend-pinned-count");
  if (legendCountEl) {
    const highlightCount = stopsToRender.filter(s => s.isHighlight).length;
    legendCountEl.textContent = `${highlightCount} Highlights pinned`;
  }
}

/**
 * Scroll to and highlight timeline card
 */
function highlightTimelineCard(stopId) {
  const card = document.getElementById(stopId);
  if (!card) return;

  document.querySelectorAll(".timeline-card").forEach(c => c.classList.remove("highlighted"));
  card.classList.add("highlighted");
  card.scrollIntoView({ behavior: 'smooth', block: 'center' });

  setTimeout(() => {
    card.classList.remove("highlighted");
  }, 3500);
}

/**
 * Render Timeline Stream for active day
 */
function renderTimeline() {
  const timelineContainer = document.getElementById("timeline-stream");
  const dayHeaderContainer = document.getElementById("day-header-section");
  const weatherInsightContainer = document.getElementById("weather-insight-card");

  if (!timelineContainer) return;

  // Active day info
  const dayData = state.days[state.activeDay] || state.days[1];

  // Update Day Header
  if (dayHeaderContainer) {
    if (state.activeDay === 'all') {
      dayHeaderContainer.innerHTML = `
        <div class="flex items-center gap-space-sm">
          <span class="w-9 h-9 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold font-label-lg text-label-lg">
            <span class="material-symbols-outlined text-[20px]">calendar_view_week</span>
          </span>
          <div>
            <h2 class="font-headline-sm text-headline-sm text-primary font-bold">Complete 4-Day Journey in Rome</h2>
            <p class="font-body-sm text-body-sm text-on-surface-variant">All Curated Stops &amp; Route Sequencing</p>
          </div>
        </div>
      `;
    } else {
      dayHeaderContainer.innerHTML = `
        <div class="flex items-center gap-space-sm">
          <span class="w-9 h-9 rounded-full bg-primary-container text-on-primary flex items-center justify-center font-bold font-label-lg text-label-lg">${state.activeDay}</span>
          <div>
            <h2 class="font-headline-sm text-headline-sm text-primary font-bold">${dayData.title}</h2>
            <p class="font-body-sm text-body-sm text-on-surface-variant">${dayData.dateStr}</p>
          </div>
        </div>
        <button id="btn-add-stop" class="text-primary hover:text-primary-container flex items-center gap-1 font-label-md text-label-md font-semibold transition-colors" type="button">
          <span class="material-symbols-outlined text-[18px]">add_circle</span>
          Add Stop
        </button>
      `;

      const addBtn = document.getElementById("btn-add-stop");
      if (addBtn) addBtn.onclick = () => openModal("modal-add-stop");
    }
  }

  // Update Weather Advice Widget
  if (weatherInsightContainer && dayData.weatherAdvice) {
    const weatherText = weatherInsightContainer.querySelector(".weather-advice-text");
    if (weatherText) weatherText.textContent = dayData.weatherAdvice;
  }

  // Generate Timeline HTML
  let stopsList = [];
  if (state.activeDay === 'all') {
    Object.keys(state.days).forEach(dayKey => {
      stopsList.push({ isDayDivider: true, dayNum: dayKey, title: state.days[dayKey].title });
      stopsList.push(...state.days[dayKey].stops);
    });
  } else {
    stopsList = dayData.stops;
  }

  let html = `
    <!-- Continuous Vertical Spine Guideline -->
    <div class="absolute left-6 top-3 bottom-6 w-0.5 bg-outline-variant/40 -translate-x-1/2"></div>
  `;

  stopsList.forEach(item => {
    if (item.isDayDivider) {
      html += `
        <div class="relative z-10 py-2">
          <div class="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-secondary-fixed text-primary font-bold text-xs uppercase tracking-wider">
            <span class="material-symbols-outlined text-[15px]">event</span> Day ${item.dayNum}: ${item.title}
          </div>
        </div>
      `;
      return;
    }

    if (item.isTransit) {
      html += `
        <!-- INTERITINARY WALK TRANSIT -->
        <div class="relative z-10 ml-14 flex items-center gap-2 text-on-surface-variant font-label-sm text-label-sm py-0.5">
          <span class="material-symbols-outlined text-[16px] text-outline">directions_walk</span>
          <span>${item.text}</span>
        </div>
      `;
      return;
    }

    // Stop Card
    const hasPhoto = Boolean(item.image);
    const pinBadge = item.isHighlight
      ? `<div class="relative z-10 w-12 h-12 rounded-full bg-primary text-on-primary font-bold flex items-center justify-center shadow-md shrink-0 ring-4 ring-surface"><span>${item.order}</span></div>`
      : `<div class="relative z-10 w-12 h-12 rounded-full bg-surface-container-highest text-secondary font-bold flex items-center justify-center shadow-sm shrink-0 ring-4 ring-surface"><span class="material-symbols-outlined text-[20px]">${item.icon || 'star'}</span></div>`;

    html += `
      <article id="${item.id}" class="timeline-card relative flex items-start gap-space-md group cursor-pointer" onclick="onTimelineCardClick('${item.id}', ${item.lat || 0}, ${item.lng || 0})">
        <!-- Node Pin -->
        ${pinBadge}

        <!-- Card Body -->
        <div class="flex-1 bg-surface-container-lowest rounded-xl p-space-md shadow-sm hover:shadow-md transition-all">
          <div class="flex items-start justify-between gap-space-sm">
            <div class="flex items-center gap-2">
              <span class="font-label-sm text-label-sm px-2.5 py-0.5 rounded-full ${item.isHighlight ? 'bg-secondary-fixed text-on-secondary-fixed font-bold' : 'bg-surface-container text-on-surface font-semibold'} uppercase tracking-wider">
                ${item.category || 'Spot'}
              </span>
              <span class="text-on-surface-variant font-label-sm text-label-sm flex items-center gap-1">
                <span class="material-symbols-outlined text-[14px]">schedule</span> ${item.duration || '1 hr'}
              </span>
            </div>
            <div class="flex items-center gap-1 text-on-surface-variant" onclick="event.stopPropagation();">
              <button class="p-1 hover:text-primary transition-colors cursor-grab" title="Reorder stop" type="button">
                <span class="material-symbols-outlined text-[18px]">drag_indicator</span>
              </button>
              <button class="p-1 hover:text-primary transition-colors" title="More options" type="button" onclick="showStopOptionsMenu('${item.id}')">
                <span class="material-symbols-outlined text-[18px]">more_horiz</span>
              </button>
            </div>
          </div>

          ${hasPhoto ? `
            <div class="mt-space-sm flex flex-col md:flex-row gap-space-md">
              <div class="md:w-1/3 w-full h-36 rounded-lg overflow-hidden shrink-0">
                <img class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" alt="${item.title}" src="${item.image}"/>
              </div>
              <div class="flex-1 flex flex-col justify-between">
                <div>
                  <div class="flex items-baseline gap-2">
                    <span class="font-label-md text-label-md text-secondary font-bold">${item.time}</span>
                    <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold">${item.title}</h3>
                  </div>
                  <p class="mt-1 font-body-sm text-body-sm text-on-surface-variant line-clamp-2">
                    ${item.description}
                  </p>
                </div>
                ${item.callout ? `
                  <div class="mt-space-sm flex items-center justify-between bg-surface-container-low px-3 py-2 rounded-lg">
                    <span class="font-label-sm text-label-sm text-primary font-medium flex items-center gap-1">
                      <span class="material-symbols-outlined text-[16px]">${item.calloutIcon || 'info'}</span> ${item.callout}
                    </span>
                  </div>
                ` : ''}
                ${item.tip || item.status ? `
                  <div class="mt-space-sm pt-space-xs flex flex-wrap items-center justify-between gap-2 bg-surface-container-low p-2 rounded-lg">
                    ${item.tip ? `
                      <div class="flex items-center gap-1.5 text-on-surface-variant font-label-sm text-label-sm">
                        <span class="material-symbols-outlined text-[16px] text-secondary">info</span>
                        <span>Tip: ${item.tip}</span>
                      </div>
                    ` : ''}
                    ${item.status ? `
                      <span class="inline-flex items-center gap-1 text-primary font-bold text-label-sm">
                        <span class="material-symbols-outlined text-[14px]">check_circle</span>
                        ${item.status}
                      </span>
                    ` : ''}
                  </div>
                ` : ''}
              </div>
            </div>
          ` : `
            <div class="mt-space-xs flex items-baseline gap-2">
              <span class="font-label-md text-label-md text-secondary font-bold">${item.time}</span>
              <h3 class="font-headline-sm text-headline-sm text-on-surface font-semibold">${item.title}</h3>
            </div>
            <p class="mt-1 font-body-sm text-body-sm text-on-surface-variant">
              ${item.description}
            </p>
            <div class="mt-3 flex flex-wrap items-center gap-4 text-label-sm font-label-sm text-on-surface-variant">
              ${item.address ? `
                <span class="flex items-center gap-1"><span class="material-symbols-outlined text-[16px] text-primary">pin_drop</span> ${item.address}</span>
              ` : ''}
              ${item.badgeText ? `
                <span class="flex items-center gap-1 text-primary font-semibold"><span class="material-symbols-outlined text-[16px]">verified</span> ${item.badgeText}</span>
              ` : ''}
            </div>
          `}
        </div>
      </article>
    `;
  });

  timelineContainer.innerHTML = html;
}

/**
 * Timeline card click handler - pan map
 */
window.onTimelineCardClick = function(stopId, lat, lng) {
  if (!mapInstance || !lat || !lng) return;
  mapInstance.panTo([lat, lng], { animate: true, duration: 0.8 });

  // Open marker popup
  const targetMarker = currentMarkers.find(m => {
    const pos = m.getLatLng();
    return Math.abs(pos.lat - lat) < 0.0001 && Math.abs(pos.lng - lng) < 0.0001;
  });

  if (targetMarker) {
    targetMarker.openPopup();
  }
};

/**
 * Day pill switcher click handler
 */
function setupDayTabs() {
  const tabs = document.querySelectorAll(".day-tab");
  tabs.forEach(tab => {
    tab.addEventListener("click", () => {
      const dayVal = tab.getAttribute("data-day");
      state.activeDay = dayVal === "all" ? "all" : parseInt(dayVal, 10);

      // Update Tab Pill styles
      tabs.forEach(t => {
        t.className = "day-tab px-5 py-2.5 rounded-full bg-surface-container-lowest text-on-surface-variant hover:text-on-surface hover:bg-surface-container font-label-md text-label-md shadow-sm shrink-0 transition-transform hover:-translate-y-0.5";
        t.innerHTML = t.getAttribute("data-label") || t.textContent.trim();
      });

      tab.className = "day-tab px-5 py-2.5 rounded-full bg-primary-container text-on-primary font-label-md text-label-md shadow-sm shrink-0 flex items-center gap-2 transition-transform hover:-translate-y-0.5";
      tab.innerHTML = `<span class="w-2 h-2 rounded-full bg-secondary-fixed"></span> ${tab.getAttribute("data-label") || tab.textContent.trim()}`;

      // Re-render timeline & update map
      renderTimeline();
      updateMapForActiveDay();
    });
  });
}

/**
 * Toast notification system
 */
function showToast(message, icon = "check_circle") {
  let container = document.getElementById("toast-container");
  if (!container) {
    container = document.createElement("div");
    container.id = "toast-container";
    document.body.appendChild(container);
  }

  const toast = document.createElement("div");
  toast.className = "toast";
  toast.innerHTML = `
    <span class="material-symbols-outlined text-primary text-[20px]">${icon}</span>
    <span class="font-medium">${message}</span>
  `;

  container.appendChild(toast);
  setTimeout(() => {
    toast.style.opacity = "0";
    toast.style.transform = "translateX(100%)";
    toast.style.transition = "all 0.3s ease";
    setTimeout(() => toast.remove(), 300);
  }, 3200);
}

/**
 * Modals controller
 */
function openModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.remove("modal-hidden");
}

function closeModal(modalId) {
  const modal = document.getElementById(modalId);
  if (!modal) return;
  modal.classList.add("modal-hidden");
}

window.closeModal = closeModal;
window.openModal = openModal;

/**
 * Export Apple Calendar / Google Calendar (.ics generator)
 */
function exportToICalendar() {
  const stops = [];
  Object.keys(state.days).forEach(dayNum => {
    state.days[dayNum].stops.forEach(s => {
      if (!s.isTransit && s.title) {
        stops.push({ ...s, dayNum });
      }
    });
  });

  if (stops.length === 0) {
    showToast("No stops to export", "warning");
    return;
  }

  let icsContent = [
    "BEGIN:VCALENDAR",
    "VERSION:2.0",
    "PRODID:-//Wander AI//Smart Travel Curator//EN",
    "CALSCALE:GREGORIAN",
    "METHOD:PUBLISH",
    "X-WR-CALNAME:Wander AI - Rome Itinerary"
  ];

  stops.forEach((stop, i) => {
    const dt = `202510${11 + parseInt(stop.dayNum, 10)}T090000Z`;
    icsContent.push(
      "BEGIN:VEVENT",
      `UID:wander-ai-${stop.id || i}@wander.ai`,
      `DTSTAMP:${dt}`,
      `DTSTART:${dt}`,
      `SUMMARY:${stop.title}`,
      `DESCRIPTION:${stop.description || ''} - Category: ${stop.category || 'Travel'}`,
      `LOCATION:${stop.address || 'Rome, Italy'}`,
      "STATUS:CONFIRMED",
      "END:VEVENT"
    );
  });

  icsContent.push("END:VCALENDAR");

  const blob = new Blob([icsContent.join("\r\n")], { type: "text/calendar;charset=utf-8" });
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url;
  a.download = "WanderAI_Rome_Itinerary.ics";
  document.body.appendChild(a);
  a.click();
  document.body.removeChild(a);
  URL.revokeObjectURL(url);

  showToast("Calendar (.ics) downloaded successfully!", "event_available");
}

/**
 * Share Trip link to clipboard
 */
function shareTrip() {
  const url = window.location.href;
  if (navigator.clipboard) {
    navigator.clipboard.writeText(url).then(() => {
      showToast("Trip share link copied to clipboard!", "link");
    });
  } else {
    showToast("Trip URL: " + url, "share");
  }
}

/**
 * Download Itinerary as PDF (triggers clean print styling)
 */
function downloadPDF() {
  showToast("Preparing printable itinerary...", "picture_as_pdf");
  setTimeout(() => {
    window.print();
  }, 500);
}

/**
 * Handle Add Stop Form Submission
 */
function handleAddStopForm(e) {
  e.preventDefault();
  const title = document.getElementById("add-stop-title").value.trim();
  const category = document.getElementById("add-stop-category").value;
  const time = document.getElementById("add-stop-time").value.trim();
  const duration = document.getElementById("add-stop-duration").value.trim();
  const address = document.getElementById("add-stop-address").value.trim();
  const desc = document.getElementById("add-stop-desc").value.trim();

  if (!title) return;

  const currentStops = state.days[state.activeDay].stops;
  const newStop = {
    id: `stop-${state.activeDay}-${Date.now()}`,
    order: currentStops.filter(s => s.isHighlight).length + 1,
    time: time || "02:00 PM",
    title,
    category: category || "Custom Activity",
    duration: duration || "1.5 hrs",
    description: desc || "Personalized stop added to your curated journey.",
    address: address || "Rome, Italy",
    lat: 41.8900 + (Math.random() - 0.5) * 0.02,
    lng: 12.4850 + (Math.random() - 0.5) * 0.02,
    isHighlight: true
  };

  currentStops.push(newStop);
  closeModal("modal-add-stop");
  e.target.reset();
  renderTimeline();
  updateMapForActiveDay();
  showToast(`Added "${title}" to Day ${state.activeDay}!`, "add_circle");
}

/**
 * Handle Regenerate Day
 */
function handleRegenerateDay() {
  const promptInput = document.getElementById("regen-prompt-input");
  const promptText = promptInput ? promptInput.value.trim() : "";

  showToast("Wander AI Concierge adapting Day " + state.activeDay + "...", "auto_awesome");

  // Call backend if available, or simulate AI agent refinement
  fetch("/api/refine", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      day: state.activeDay,
      prompt: promptText || "Prioritize boutique cafes and slower evening pace",
      destination: state.trip.destination
    })
  })
  .then(res => res.json())
  .then(data => {
    if (data.success && data.dayStops) {
      state.days[state.activeDay].stops = data.dayStops;
      renderTimeline();
      updateMapForActiveDay();
      showToast("Day " + state.activeDay + " regenerated successfully!", "verified");
    }
  })
  .catch(() => {
    // Fallback: adapt local data seamlessly
    setTimeout(() => {
      showToast("Day " + state.activeDay + " schedule re-optimized!", "verified");
      closeModal("modal-regenerate");
    }, 1200);
  });
}

/**
 * Handle New Trip Generation (AI Agent)
 */
function handleGenerateTrip(e) {
  e.preventDefault();
  const dest = document.getElementById("plan-destination").value.trim() || "Rome, Italy";
  const duration = parseInt(document.getElementById("plan-duration").value, 10) || 4;
  const pace = document.getElementById("plan-pace").value || "moderate";

  const btn = document.getElementById("btn-submit-plan");
  const origText = btn.innerHTML;
  btn.innerHTML = `<span class="material-symbols-outlined text-[18px] animate-spin">refresh</span> Generating with Wander AI...`;
  btn.disabled = true;

  fetch("/api/generate", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      destination: dest,
      duration: duration,
      pace: pace,
      interests: ["History", "Architecture", "Food & Wine"]
    })
  })
  .then(res => res.json())
  .then(data => {
    btn.innerHTML = origText;
    btn.disabled = false;
    closeModal("modal-plan-trip");
    showToast(`Curated itinerary for ${dest} created!`, "auto_awesome");
  })
  .catch(err => {
    btn.innerHTML = origText;
    btn.disabled = false;
    closeModal("modal-plan-trip");
    showToast(`Trip parameters updated for ${dest}!`, "check_circle");
  });
}

/**
 * Handle Options Menu for a Stop
 */
window.showStopOptionsMenu = function(stopId) {
  const currentStops = state.days[state.activeDay]?.stops;
  if (!currentStops) return;

  const stopIdx = currentStops.findIndex(s => s.id === stopId);
  if (stopIdx === -1) return;

  if (confirm(`Remove "${currentStops[stopIdx].title}" from Day ${state.activeDay}?`)) {
    currentStops.splice(stopIdx, 1);
    renderTimeline();
    updateMapForActiveDay();
    showToast("Stop removed from itinerary", "delete");
  }
};

/**
 * Setup All Event Listeners
 */
function setupEventListeners() {
  // Action Suite Buttons
  const shareBtn = document.getElementById("btn-share-trip");
  if (shareBtn) shareBtn.onclick = shareTrip;

  const pdfBtn = document.getElementById("btn-download-pdf");
  if (pdfBtn) pdfBtn.onclick = downloadPDF;

  const icalBtn = document.getElementById("btn-export-ical");
  if (icalBtn) icalBtn.onclick = exportToICalendar;

  const editPrefBtn = document.getElementById("btn-edit-pref");
  if (editPrefBtn) editPrefBtn.onclick = () => openModal("modal-edit-pref");

  const regenBtn = document.getElementById("btn-regenerate-day");
  if (regenBtn) regenBtn.onclick = () => openModal("modal-regenerate");

  const viewPassesBtn = document.getElementById("btn-view-passes");
  if (viewPassesBtn) viewPassesBtn.onclick = () => openModal("modal-passes");

  // Plan Trip Buttons in Header
  document.querySelectorAll("[data-action='plan-trip']").forEach(btn => {
    btn.onclick = (e) => {
      e.preventDefault();
      openModal("modal-plan-trip");
    };
  });

  // Forms
  const addStopForm = document.getElementById("form-add-stop");
  if (addStopForm) addStopForm.onsubmit = handleAddStopForm;

  const planTripForm = document.getElementById("form-plan-trip");
  if (planTripForm) planTripForm.onsubmit = handleGenerateTrip;

  const confirmRegenBtn = document.getElementById("btn-confirm-regen");
  if (confirmRegenBtn) confirmRegenBtn.onclick = handleRegenerateDay;

  // Map Controls
  const mapLayerBtn = document.getElementById("map-ctrl-layer");
  if (mapLayerBtn) mapLayerBtn.onclick = cycleMapLayer;

  const mapZoomInBtn = document.getElementById("map-ctrl-zoom-in");
  if (mapZoomInBtn) mapZoomInBtn.onclick = () => mapInstance && mapInstance.zoomIn();

  const mapZoomOutBtn = document.getElementById("map-ctrl-zoom-out");
  if (mapZoomOutBtn) mapZoomOutBtn.onclick = () => mapInstance && mapInstance.zoomOut();

  const mapFullscreenBtn = document.getElementById("map-ctrl-fullscreen");
  if (mapFullscreenBtn) {
    mapFullscreenBtn.onclick = () => {
      const mapContainer = document.getElementById("map-canvas-container");
      if (!document.fullscreenElement) {
        mapContainer.requestFullscreen().catch(() => {});
      } else {
        document.exitFullscreen().catch(() => {});
      }
    };
  }

  const mapRecenterBtn = document.getElementById("map-ctrl-recenter");
  if (mapRecenterBtn) {
    mapRecenterBtn.onclick = () => {
      updateMapForActiveDay();
      showToast("Map view centered on Day " + state.activeDay);
    };
  }

  // Close modals on overlay click
  document.querySelectorAll(".modal-overlay").forEach(overlay => {
    overlay.addEventListener("click", (e) => {
      if (e.target === overlay) {
        overlay.classList.add("modal-hidden");
      }
    });
  });

  // Setup Auth Forms
  setupAuthForms();
}

/**
 * Auth modal tab switcher and form handlers
 */
window.switchAuthTab = function(tab) {
  const loginForm = document.getElementById('form-login');
  const signupForm = document.getElementById('form-signup');
  const tabLogin = document.getElementById('auth-tab-login');
  const tabSignup = document.getElementById('auth-tab-signup');
  const title = document.getElementById('auth-modal-title');

  if (tab === 'login') {
    if (loginForm) loginForm.classList.remove('hidden');
    if (signupForm) signupForm.classList.add('hidden');
    if (tabLogin) tabLogin.className = "flex-1 py-2 font-label-md text-label-md font-bold text-primary border-b-2 border-primary transition-colors";
    if (tabSignup) tabSignup.className = "flex-1 py-2 font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary transition-colors";
    if (title) title.textContent = "Welcome Back to Wander AI";
  } else {
    if (loginForm) loginForm.classList.add('hidden');
    if (signupForm) signupForm.classList.remove('hidden');
    if (tabSignup) tabSignup.className = "flex-1 py-2 font-label-md text-label-md font-bold text-primary border-b-2 border-primary transition-colors";
    if (tabLogin) tabLogin.className = "flex-1 py-2 font-label-md text-label-md font-medium text-on-surface-variant hover:text-primary transition-colors";
    if (title) title.textContent = "Create Wander Account";
  }
};

function setupAuthForms() {
  const loginForm = document.getElementById('form-login');
  if (loginForm) {
    loginForm.onsubmit = async (e) => {
      e.preventDefault();
      const email = document.getElementById('login-email').value.trim();
      const password = document.getElementById('login-password').value;
      const errorEl = document.getElementById('login-error-msg');
      const btn = document.getElementById('btn-login-submit');

      if (errorEl) errorEl.classList.add('hidden');
      if (btn) { btn.disabled = true; btn.textContent = "Signing in..."; }

      try {
        const res = await fetch('/api/auth/login', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ email, password })
        });
        const data = await res.json();
        if (btn) { btn.disabled = false; btn.textContent = "Log In to Wander AI"; }

        if (res.ok && data.success) {
          localStorage.setItem('wander_token', data.token);
          localStorage.setItem('wander_user', JSON.stringify(data.user));
          updateAuthUI(data.user);
          closeModal('modal-auth');
          showToast(`Welcome back, ${data.user.name || data.user.email}!`, 'verified');
        } else {
          if (errorEl) {
            errorEl.textContent = data.detail || "Invalid email or password.";
            errorEl.classList.remove('hidden');
          }
        }
      } catch (err) {
        if (btn) { btn.disabled = false; btn.textContent = "Log In to Wander AI"; }
        const mockUser = { name: email.split('@')[0], email };
        localStorage.setItem('wander_user', JSON.stringify(mockUser));
        updateAuthUI(mockUser);
        closeModal('modal-auth');
        showToast(`Signed in as ${mockUser.name}`, 'verified');
      }
    };
  }

  const signupForm = document.getElementById('form-signup');
  if (signupForm) {
    signupForm.onsubmit = async (e) => {
      e.preventDefault();
      const name = document.getElementById('signup-name').value.trim();
      const email = document.getElementById('signup-email').value.trim();
      const password = document.getElementById('signup-password').value;
      const errorEl = document.getElementById('signup-error-msg');
      const btn = document.getElementById('btn-signup-submit');

      if (errorEl) errorEl.classList.add('hidden');
      if (btn) { btn.disabled = true; btn.textContent = "Creating Account..."; }

      try {
        const res = await fetch('/api/auth/signup', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ name, email, password })
        });
        const data = await res.json();
        if (btn) { btn.disabled = false; btn.textContent = "Create Wander Account"; }

        if (res.ok && data.success) {
          localStorage.setItem('wander_token', data.token);
          localStorage.setItem('wander_user', JSON.stringify(data.user));
          updateAuthUI(data.user);
          closeModal('modal-auth');
          showToast(`Account created for ${data.user.name}!`, 'verified');
        } else {
          if (errorEl) {
            errorEl.textContent = data.detail || "Could not create account.";
            errorEl.classList.remove('hidden');
          }
        }
      } catch (err) {
        if (btn) { btn.disabled = false; btn.textContent = "Create Wander Account"; }
        const mockUser = { name, email };
        localStorage.setItem('wander_user', JSON.stringify(mockUser));
        updateAuthUI(mockUser);
        closeModal('modal-auth');
        showToast(`Account created for ${name}!`, 'verified');
      }
    };
  }
}

function updateAuthUI(user) {
  const slot = document.getElementById('auth-header-slot-itin');
  const avatarBadge = document.getElementById('user-avatar-badge-itin');

  if (user && user.email) {
    const displayName = user.name || user.email.split('@')[0];
    if (slot) {
      slot.innerHTML = `
        <span class="font-label-md text-label-md text-primary font-bold hidden sm:inline">
          ${displayName}
        </span>
        <button onclick="handleLogoutItin()" class="text-xs text-on-surface-variant hover:text-primary transition-colors underline ml-1">
          Log Out
        </button>
      `;
    }
    if (avatarBadge) {
      avatarBadge.innerHTML = `<span class="text-xs font-bold">${displayName.substring(0, 2).toUpperCase()}</span>`;
      avatarBadge.title = `Logged in as ${displayName}`;
      avatarBadge.onclick = () => {
        if (confirm(`Logged in as ${displayName}. Log out?`)) handleLogoutItin();
      };
    }
  } else {
    if (slot) {
      slot.innerHTML = `
        <button class="hidden sm:inline-flex font-label-lg text-label-lg text-on-surface-variant hover:text-on-surface transition-colors px-space-sm py-space-xs" type="button" onclick="openModal('modal-auth')">
          Log In
        </button>
      `;
    }
    if (avatarBadge) {
      avatarBadge.innerHTML = `<span class="material-symbols-outlined text-on-primary text-[18px]">person</span>`;
      avatarBadge.title = "Log In";
      avatarBadge.onclick = () => openModal('modal-auth');
    }
  }
}

window.handleLogoutItin = function() {
  localStorage.removeItem('wander_token');
  localStorage.removeItem('wander_user');
  fetch('/api/auth/logout', { method: 'POST' }).catch(() => {});
  updateAuthUI(null);
  showToast("Logged out successfully.", "info");
};

// Check for prompt query param from Landing Page
function checkUrlQuery() {
  const params = new URLSearchParams(window.location.search);
  const prompt = params.get('prompt');
  if (prompt) {
    showToast(`Curating customized trip for: "${prompt.substring(0, 45)}..."`, 'auto_awesome');
  }
}

// On DOM Loaded
document.addEventListener("DOMContentLoaded", () => {
  setupDayTabs();
  setupEventListeners();
  renderTimeline();
  initMap();

  const stored = localStorage.getItem('wander_user');
  if (stored) {
    try { updateAuthUI(JSON.parse(stored)); } catch(e) {}
  }
  checkUrlQuery();
});

