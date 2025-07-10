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
      const paymentMethodElement = document.querySelector('input[name="payment-method"]:checked');
      const pickupPointElement = document.getElementById('point_recuperation');

      if (!pickupPointElement) {
        alert('Élément point de récupération non trouvé');
        return;
      }

      if (!paymentMethodElement) {
        alert('Veuillez sélectionner une méthode de paiement');
        return;
      }

      const paymentMethod = paymentMethodElement.value;
      const pickupPoint = pickupPointElement.value;

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
          alert('Commande validée avec succès ! Votre commande est maintenant en cours de traitement.');
          // Recharger la page du panier pour afficher l'état vide
          location.reload();
        } else {
          alert('Erreur lors de la commande: ' + data.message);
        }
      });
    }
    document.addEventListener('DOMContentLoaded', function() {
        // Charger dynamiquement les modes de paiement seulement si le conteneur existe
        const paymentContainer = document.getElementById('payment-methods-container');
        if (paymentContainer) {
            fetch('/api/panier/modes-paiement/')
                .then(response => response.json())
                .then(data => {
                if (data.success && Array.isArray(data.modes)) {
                    paymentContainer.innerHTML = '';
                    data.modes.forEach((mode, idx) => {
                    const id = `mode-paiement-${mode.id}`;
                    const checked = idx === 0 ? 'checked' : '';
                    paymentContainer.innerHTML += `
                        <div class="payment-option">
                        <input type="radio" id="${id}" name="payment-method" value="${mode.id}" ${checked}>
                        <label for="${id}">
                            <span>${mode.nom}</span>
                        </label>
                        </div>
                    `;
                    });
                } else {
                    paymentContainer.innerHTML = '<div style="color:red;">Aucun mode de paiement disponible</div>';
                }
                })
                .catch(() => {
                paymentContainer.innerHTML = '<div style="color:red;">Erreur lors du chargement des modes de paiement</div>';
                });
        }
        });
    // Hamburger menu functionality
    const menuToggle = document.getElementById('menu-toggle');
    if (menuToggle) {
        menuToggle.addEventListener('click', function(e) {
          e.stopPropagation();
          const menu = document.getElementById('hamburger-menu');
          if (menu) {
            menu.classList.toggle('active');
          }
        });
    }

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
