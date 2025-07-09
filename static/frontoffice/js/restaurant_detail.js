// Category filter buttons
        const buttons = document.querySelectorAll('.category-btn');
        buttons.forEach(button => {
            button.addEventListener('click', () => {
                buttons.forEach(btn => btn.classList.remove('active'));
                button.classList.add('active');
            });
        });

        // Add to cart function using add_to_panier endpoint
        function addToCart(mealId) {
            fetch("/api/panier/ajouter/", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "X-CSRFToken": "{{ csrf_token }}"
                },
                body: JSON.stringify({ repas_id: mealId })
            })
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    alert("Ajouté au panier !");
                } else {
                    alert(data.message || "Erreur lors de l'ajout au panier.");
                }
            })
            .catch(error => {
                alert("Erreur réseau lors de l'ajout au panier.");
                console.error(error);
            });
        }

        document.addEventListener('DOMContentLoaded', function() {
            const menuToggle = document.getElementById('menu-toggle');
            const hamburgerMenu = document.getElementById('hamburger-menu');
            const submenuParents = document.querySelectorAll('.has-submenu');

            menuToggle.addEventListener('click', function(e) {
                e.stopPropagation();
                hamburgerMenu.classList.toggle('active');
            });

            document.addEventListener('click', function(e) {
                if (!hamburgerMenu.contains(e.target) && e.target !== menuToggle) {
                    hamburgerMenu.classList.remove('active');
                }
            });

            submenuParents.forEach(function(parent) {
                parent.addEventListener('click', function(e) {
                    e.stopPropagation();
                    parent.classList.toggle('open');
                });
            });
        });