// Initialize the map with restaurant functionality
    const map = L.map('map').setView([-18.8792, 47.5204], 13);
    let restaurantCount = 0;

    // Hide loading spinner once map is ready
    map.on('load', function() {
      document.getElementById('loading-spinner').style.display = 'none';
    });

    L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      attribution: '© OpenStreetMap contributors'
    }).addTo(map);

    // Custom marker styling with better design
    const restaurantIcon = L.divIcon({
      className: 'restaurant-marker',
      html: `<div style="
        background: linear-gradient(45deg, #ff6b35, #f7931e);
        border-radius: 50%;
        width: 30px;
        height: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        color: white;
        font-size: 16px;
        box-shadow: 0 4px 12px rgba(255, 107, 53, 0.4);
        border: 3px solid white;
      ">🍽️</div>`,
      iconSize: [36, 36],
      iconAnchor: [18, 18]
    });

    // Map control functions
    function centerMap() {
      map.setView([-18.8792, 47.5204], 13);
    }

    function toggleFullscreen() {
      const mapElement = document.getElementById('map');
      if (!document.fullscreenElement) {
        mapElement.requestFullscreen().then(() => {
          setTimeout(() => map.invalidateSize(), 100);
        });
      } else {
        document.exitFullscreen().then(() => {
          setTimeout(() => map.invalidateSize(), 100);
        });
      }
    }

    // Load restaurants in GeoJSON format with enhanced popup
fetch('/api/restaurants/')
  .then(response => {
    console.log('Fetch /api/restaurants/ response:', response);
    return response.json();
  })
  .then(data => {
    console.log('Fetched restaurant data:', data);
    document.getElementById('loading-spinner').style.display = 'none';
    restaurantCount = data.features.length;
    document.getElementById('restaurant-count').textContent = restaurantCount;
    L.geoJSON(data, {
      onEachFeature: function (feature, layer) {
        const props = feature.properties;
        // Debug horaires for each restaurant
        console.log('Restaurant:', props.nom, 'Horaires:', props.horaires);
        // Get opening and closing times (first slot if exists)
        let horaireText = 'Horaire non renseigné';
        if (props.horaires && props.horaires.length > 0) {
          const h = props.horaires[0];
          horaireText = `🕒 ${h.horaire_debut} - ${h.horaire_fin}`;
        }
        const popupContent = `
          <div class="restaurant-popup">
            <strong>${props.nom}</strong>
            <div class="rating">${horaireText}</div>
            ${props.image_url ? `<img src="/media/restaurants/${props.image_url}" alt="${props.nom}">` : ''}
            <div style="margin: 10px 0; color: #666; font-size: 14px;">
              <!--📍 ${props.adresse || 'Adresse non disponible'}-->
            </div>
            <a href="/menu/${props.id}/"><button class="menu-button">Voir le menu</button></a>
          </div>
        `;
        layer.bindPopup(popupContent, {
          maxWidth: 250,
          className: 'custom-popup'
        });
        layer.bindTooltip(props.nom, {
          direction: 'top',
          offset: [0, -20]
        });
      },
      pointToLayer: function (feature, latlng) {
        return L.marker(latlng, {
          icon: restaurantIcon
        });
      }
    }).addTo(map);
  })
      .catch(error => {
        console.error('Error loading restaurants:', error);
        document.getElementById('loading-spinner').style.display = 'none';
        document.getElementById('restaurant-count').textContent = '⚠️';

        // Fallback marker if API fails
        const marker = L.marker([-18.8792, 47.5204], {
          icon: restaurantIcon
        }).addTo(map);
        marker.bindPopup(`
          <div class="restaurant-popup">
            <strong>Erreur de chargement</strong><br>
            <div style="color: #666; margin: 10px 0;">
              Impossible de charger les restaurants. Veuillez réessayer plus tard.
            </div>
            <button class="menu-button" onclick="location.reload()">Réessayer</button>
          </div>
        `).openPopup();
      });

    // Enhanced hamburger menu functionality
    document.addEventListener('DOMContentLoaded', function() {
      const menuToggle = document.getElementById('menu-toggle');
      const hamburgerMenu = document.getElementById('hamburger-menu');
      const submenuParents = document.querySelectorAll('.has-submenu');

      // Open/close hamburger menu
      menuToggle.addEventListener('click', function(e) {
        e.stopPropagation();
        hamburgerMenu.classList.toggle('active');
      });

      // Close menu when clicking elsewhere
      document.addEventListener('click', function(e) {
        if (!hamburgerMenu.contains(e.target) && e.target !== menuToggle) {
          hamburgerMenu.classList.remove('active');
        }
      });

      // Submenu handling
      submenuParents.forEach(function(parent) {
        parent.addEventListener('click', function(e) {
          e.stopPropagation();
          parent.classList.toggle('open');
        });
      });

      // Search clear functionality
      const clearSearch = document.querySelector('.group');
      if (clearSearch) {
        clearSearch.addEventListener('click', function() {
          document.querySelector('.search-input').value = '';
        });
      }

      // Add smooth scroll to map when page loads
      setTimeout(() => {
        document.querySelector('.map-wrapper').scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        });
      }, 500);
    });