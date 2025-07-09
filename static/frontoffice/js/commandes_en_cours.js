let commandeAAnuller = null;

        function confirmerAnnulation(commandeId) {
            commandeAAnuller = commandeId;
            const modal = new bootstrap.Modal(document.getElementById('modalAnnulation'));
            modal.show();
        }

        document.getElementById('btnConfirmerAnnulation').addEventListener('click', function() {
            if (commandeAAnuller) {
                annulerCommande(commandeAAnuller);
            }
        });

        async function annulerCommande(commandeId) {
            try {
                const response = await fetch(`/annuler-commande/${commandeId}/`, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || ''
                    }
                });

                const data = await response.json();

                if (data.success) {
                    // Masquer le modal
                    bootstrap.Modal.getInstance(document.getElementById('modalAnnulation')).hide();

                    // Afficher un message de succès
                    showAlert('success', 'Commande annulée avec succès !');

                    // Recharger la page après 1 seconde
                    setTimeout(() => {
                        window.location.reload();
                    }, 1000);
                } else {
                    showAlert('danger', data.message || 'Erreur lors de l\'annulation');
                }
            } catch (error) {
                console.error('Erreur:', error);
                showAlert('danger', 'Erreur de connexion');
            }
        }

        function showAlert(type, message) {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const container = document.querySelector('.container');
            container.insertBefore(alertDiv, container.firstChild);

            // Auto-dismiss après 5 secondes
            setTimeout(() => {
                if (alertDiv.parentNode) {
                    alertDiv.remove();
                }
            }, 5000);
        }