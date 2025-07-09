// Password toggle function
    function togglePassword() {
      const passwordField = document.getElementById("password-field");
      passwordField.type = passwordField.type === "password" ? "text" : "password";
    }

    // JavaScript pour gérer l'ouverture et la fermeture du popup
    const openDeliveryPopupButton = document.getElementById('open-delivery-popup');
    const deliveryPopup = document.getElementById('delivery-popup');
    const closePopupButton = document.querySelector('.close-popup');
    const verifyZonesCheckbox = document.getElementById('verify-zones-checkbox');
    const continueDeliveryButton = document.querySelector('.btn-delivery-continue');

    if (openDeliveryPopupButton) {
      openDeliveryPopupButton.addEventListener('click', function(event) {
        event.preventDefault();
        deliveryPopup.classList.add('active');
      });
    }

    if (closePopupButton) {
      closePopupButton.addEventListener('click', function() {
        deliveryPopup.classList.remove('active');
      });
    }

    if (deliveryPopup) {
      deliveryPopup.addEventListener('click', function(event) {
        if (event.target === deliveryPopup) {
          deliveryPopup.classList.remove('active');
        }
      });
    }

    if (verifyZonesCheckbox) {
      verifyZonesCheckbox.addEventListener('change', function() {
        continueDeliveryButton.disabled = !this.checked;
      });
    }