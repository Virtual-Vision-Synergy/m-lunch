let panierModifications = {};

    function changeQuantity(itemId, delta) {
      const quantiteElement = document.getElementById(`quantite-${itemId}`);
      let currentQuantity = parseInt(quantiteElement.textContent);
      let newQuantity = currentQuantity + delta;
      if (newQuantity < 1) newQuantity = 1;

      quantiteElement.textContent = newQuantity;
      panierModifications[itemId] = newQuantity;

      // Update the cart via AJAX
      updateCart();
    }

    function removeFromPanier(itemId) {
      // AJAX call to remove item
      fetch(`/api/panier/supprimer/${itemId}/`, {
        method: 'POST',
        headers: {
          'X-CSRFToken': '{{ csrf_token }}',
          'Content-Type': 'application/json'
        }
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          location.reload(); // Refresh to show updated cart
        }
      });
    }

    function updateCart() {
    // Pour chaque modification de quantité, on appelle l'endpoint update_quantity
        const updates = Object.entries(panierModifications).map(([itemId, quantite]) => {
            return fetch(`/api/panier/update/${itemId}/`, {
            method: 'POST',
            headers: {
                'X-CSRFToken': '{{ csrf_token }}',
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ quantite: quantite })
            })
            .then(response => response.json());
        });

        Promise.all(updates).then(results => {
            // Si au moins une mise à jour a réussi, on rafraîchit la page ou on met à jour les totaux
            let success = results.some(r => r.success);
            if (success) {
            location.reload(); // Ou tu peux mettre à jour les totaux dynamiquement ici
            } else {
            alert('Erreur lors de la mise à jour du panier.');
            }
        });
    }

    function submitOrder() {
      const paymentMethod = document.querySelector('input[name="payment-method"]:checked').value;
      const pickupPoint = document.getElementById('point_recuperation').value;

      if (!pickupPoint) {
        alert('Veuillez sélectionner un point de récupération');
        return;
      }
      if (!paymentMethod) {
        alert('Veuillez sélectionner un méthode de paiement');
        return;
      }
      // AJAX call to finalize the order
      fetch('/api/panier/valider/', {
        method: 'POST',
        headers: {
          'X-CSRFToken': '{{ csrf_token }}',
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          mode_paiement_id: paymentMethod,
          point_recup_id: pickupPoint
        })
      })
      .then(response => response.json())
      .then(data => {
        if (data.success) {
          window.location.href = '/panier/';
        } else {
          alert('Erreur lors de la commande: ' + data.message);
        }
      });
    }
    document.addEventListener('DOMContentLoaded', function() {
        // Charger dynamiquement les modes de paiement
        fetch('/api/panier/modes-paiement/')
            .then(response => response.json())
            .then(data => {
            if (data.success && Array.isArray(data.modes)) {
                const container = document.getElementById('payment-methods-container');
                container.innerHTML = '';
                data.modes.forEach((mode, idx) => {
                const id = `mode-paiement-${mode.id}`;
                const checked = idx === 0 ? 'checked' : '';
                container.innerHTML += `
                    <div class="payment-option">
                    <input type="radio" id="${id}" name="payment-method" value="${mode.id}" ${checked}>
                    <label for="${id}">
                        <span>${mode.nom}</span>
                    </label>
                    </div>
                `;
                });
            } else {
                document.getElementById('payment-methods-container').innerHTML = '<div style="color:red;">Aucun mode de paiement disponible</div>';
            }
            })
            .catch(() => {
            document.getElementById('payment-methods-container').innerHTML = '<div style="color:red;">Erreur lors du chargement des modes de paiement</div>';
            });
        });
    // Hamburger menu functionality
    document.getElementById('menu-toggle').addEventListener('click', function(e) {
      e.stopPropagation();
      const menu = document.getElementById('hamburger-menu');
      menu.classList.toggle('active');
    });

    document.querySelectorAll('.has-submenu').forEach(item => {
      item.addEventListener('click', function(e) {
        if (e.target === this || e.target.classList.contains('arrow')) {
          this.classList.toggle('open');
          e.preventDefault();
        }
      });
    });

    document.addEventListener('click', function(e) {
      const menu = document.getElementById('hamburger-menu');
      if (menu && menu.classList.contains('active')) {
        if (!menu.contains(e.target) && e.target.id !== 'menu-toggle') {
          menu.classList.remove('active');
        }
      }

      document.querySelectorAll('.has-submenu.open').forEach(function(item) {
        if (!item.contains(e.target)) {
          item.classList.remove('open');
        }
      });
    });
