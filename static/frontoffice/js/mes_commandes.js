 // Hamburger menu functionality
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