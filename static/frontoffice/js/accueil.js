document.addEventListener('DOMContentLoaded', function() {
      // Load restaurant images for infinite carousel
      function loadCarouselImages() {
        fetch('/api/all_restaurants/')
          .then(response => response.json())
          .then(data => {
            const carouselTrack = document.getElementById('carousel-track');

            // Clear existing slides
            carouselTrack.innerHTML = '';

            // Filter restaurants that have images
            const restaurantsWithImages = data.features.filter(restaurant =>
              restaurant.properties.image_url
            );

            if (restaurantsWithImages.length > 0) {
              // Create slides from restaurant images (duplicate for infinite effect)
              const slides = [];
              restaurantsWithImages.forEach(restaurant => {
                slides.push(`
                  <div class="slide">
                    <img src="/static/frontoffice/img/restologo/${ restaurant.properties.image_url }" alt="${ restaurant.properties.nom }" />
                  </div>
                `);
              });

              // Duplicate slides for infinite scroll effect
              carouselTrack.innerHTML = slides.join('') + slides.join('');
            } else {
              // Fallback to default images if no restaurant images available
              const defaultSlides = [
                '<div class="slide"><img src="assets/img/img1.jpg" alt="" /></div>',
                '<div class="slide"><img src="assets/img/img2.jpg" alt="" /></div>',
                '<div class="slide"><img src="assets/img/img3.jpg" alt="" /></div>',
                '<div class="slide"><img src="assets/img/img4.jpg" alt="" /></div>',
                '<div class="slide"><img src="assets/img/img5.jpg" alt="" /></div>',
                '<div class="slide"><img src="assets/img/img6.jpg" alt="" /></div>'
              ];
              carouselTrack.innerHTML = defaultSlides.join('') + defaultSlides.join('');
            }
          })
          .catch(error => {
            console.error('Error loading carousel images:', error);
            // Fallback to default images on error
            const carouselTrack = document.getElementById('carousel-track');
            const defaultSlides = [
              '<div class="slide"><img src="assets/img/img1.jpg" alt="" /></div>',
              '<div class="slide"><img src="assets/img/img2.jpg" alt="" /></div>',
              '<div class="slide"><img src="assets/img/img3.jpg" alt="" /></div>',
              '<div class="slide"><img src="assets/img/img4.jpg" alt="" /></div>',
              '<div class="slide"><img src="assets/img/img5.jpg" alt="" /></div>',
              '<div class="slide"><img src="assets/img/img6.jpg" alt="" /></div>'
            ];
            carouselTrack.innerHTML = defaultSlides.join('') + defaultSlides.join('');
          });
      }

      // Load carousel images first
      loadCarouselImages();

      // Initialize Swiper
      const swiper = new Swiper('.mySwiper', {
        loop: true,
        slidesPerView: 3,
        spaceBetween: 30,
        centeredSlides: true,
        autoplay: {
          delay: 3000,
          disableOnInteraction: false,
        },
        pagination: {
          el: '.swiper-pagination',
          clickable: true,
        },
        navigation: {
          nextEl: '.swiper-button-next',
          prevEl: '.swiper-button-prev',
        },
        breakpoints: {
          320: {
            slidesPerView: 1,
            spaceBetween: 20
          },
          768: {
            slidesPerView: 2,
            spaceBetween: 30
          },
          1024: {
            slidesPerView: 3,
            spaceBetween: 40
          }
        }
      });

      // Hamburger menu toggle
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

      // Map and API functionality from accueil.html
      const map = L.map('map-container').setView([-18.8792, 47.5079], 13);

      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors',
        maxZoom: 19
      }).addTo(map);

      // Load restaurants for Swiper
      fetch('/api/all_restaurants/')
        .then(response => response.json())
        .then(data => {
          const swiperWrapper = document.querySelector('.swiper-wrapper');

          data.features.forEach(restaurant => {
            const slide = document.createElement('div');
            slide.className = 'swiper-slide';

            slide.innerHTML = `
              <div class="restaurant-item">
                ${restaurant.properties.image_url ?
                  `<img src="/static/frontoffice/img/restologo/${ restaurant.properties.image_url }" alt="${ restaurant.properties.nom }" class="restaurant-image" />` :
                  '<div class="restaurant-image placeholder"></div>'}
                <h2 class="restaurant-name">${restaurant.properties.nom}</h2>
                <p class="restaurant-description">${restaurant.properties.description}</p>
              </div>
            `;

            swiperWrapper.appendChild(slide);
          });

          // Update Swiper after adding slides
          swiper.update();
        })
        .catch(error => {
          console.error('Error fetching restaurants:', error);
        });

      // Map selector functionality
      const viewSelector = document.getElementById('view-selector');

      viewSelector.addEventListener('change', function() {
        const selectedOption = this.value;

        if (selectedOption === 'restaurants') {
          loadRestaurants();
        } else if (selectedOption === 'pickup-points') {
          loadPickupPoints();
        }
      });

      function loadRestaurants() {
        map.eachLayer(layer => {
          if (layer instanceof L.Marker) {
            map.removeLayer(layer);
          }
        });

        fetch('/api/all_restaurants/')
          .then(response => response.json())
          .then(data => {
            const bounds = [];
            data.features && data.features.forEach(restaurant => {
              if (restaurant.geometry?.coordinates) {
                const [lng, lat] = restaurant.geometry.coordinates;
                const marker = L.marker([lat, lng]).addTo(map);
                marker.bindPopup(`<b>${restaurant.properties.nom}</b><br>${restaurant.properties.description}`);
                bounds.push([lat, lng]);
              }
            });
            if (bounds.length > 0) {
              map.fitBounds(bounds, {padding: [50, 50]});
            }
          });
      }

      function loadPickupPoints() {
        map.eachLayer(layer => {
          if (layer instanceof L.Marker) {
            map.removeLayer(layer);
          }
        });

        fetch('/api/points_de_recuperation/')
          .then(response => response.json())
          .then(data => {
            const bounds = [];
            data.features && data.features.forEach(point => {
              if (point.geometry?.coordinates) {
                const [lng, lat] = point.geometry.coordinates;
                const marker = L.marker([lat, lng]).addTo(map);
                marker.bindPopup(`<b>${point.properties.nom}</b>`);
                bounds.push([lat, lng]);
              }
            });
            if (bounds.length > 0) {
              map.fitBounds(bounds, {padding: [50, 50]});
            }
          })
          .catch(error => {
            console.error('Error fetching pickup points:', error);
          });
      }

      // Load pickup points by default
      loadPickupPoints();
    });