document.addEventListener('DOMContentLoaded', function() {
    // Password toggle
    document.querySelectorAll('.toggle-password').forEach(icon => {
      icon.addEventListener('click', function() {
        const input = this.parentElement.querySelector('input');
        const isPassword = input.type === 'password';
        input.type = isPassword ? 'text' : 'password';
        this.classList.toggle('fa-eye-slash');
        this.classList.toggle('fa-eye');
      });
    });

    // Initialize map - wait a moment to ensure container is rendered
    setTimeout(() => {
      const map = L.map('map', {
        preferCanvas: true
      }).setView([-18.8792, 47.5079], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; OpenStreetMap contributors'
      }).addTo(map);

      // Add geocoder control
      L.Control.geocoder({
        defaultMarkGeocode: false
      }).on('markgeocode', function(e) {
        map.setView(e.geocode.center, 15);
        updateSector(e.geocode.center.lat, e.geocode.center.lng);
      }).addTo(map);

      let marker;
      map.on('click', function(e) {
        updateSector(e.latlng.lat, e.latlng.lng);
      });

      function updateSector(lat, lng) {
        if (marker) map.removeLayer(marker);
        marker = L.marker([lat, lng]).addTo(map);

        fetch(`/api/zone-from-coord/?lat=${lat}&lon=${lng}`)
          .then(response => response.json())
          .then(data => {
            const secteurInput = document.getElementById('secteur');
            if (data.success) {
              secteurInput.value = data.nom;
              showToast(`Zone sélectionnée : ${data.nom}`, 'success');
            } else {
              secteurInput.value = '';
              showToast("Aucune zone de livraison à proximité", 'danger');
            }
          });
      }
    }, 100);

    function showToast(message, type) {
      const toast = document.createElement('div');
      toast.className = `toast-message toast-${type}`;
      toast.textContent = message;
      document.body.appendChild(toast);
      setTimeout(() => toast.remove(), 3000);
    }
  });