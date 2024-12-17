document.addEventListener("DOMContentLoaded", function() {
  // Fonction pour récupérer les notes des burgers dynamiquement
  function fetchBurgerRatings() {
    const burgerElements = document.querySelectorAll('[id^="rating-"]');

    burgerElements.forEach(ratingElement => {
      const burgerId = ratingElement.id.split('-')[1];

      // Requête AJAX pour récupérer la note de l'utilisateur
      fetch(`/rate_burger/${burgerId}`)
        .then(response => response.json())
        .then(data => {
          if (data.user_rating !== null) {
            // Si une note existe, cochez l'étoile correspondante
            const starInput = document.querySelector(`#star${data.user_rating}-${burgerId}`);
            if (starInput) {
              starInput.checked = true;
            }
          }
        })
        .catch(err => console.error("Erreur lors de la récupération de la note :", err));
    });

    document.querySelectorAll('.rate-form').forEach(form => {
      form.querySelectorAll('.rating input').forEach(input => {
        input.addEventListener('change', (event) => {
          form.submit()
        });
      });
    });
  }

  // Appel initial lors du chargement de la page
  fetchBurgerRatings();

  // Appel supplémentaire après mise à jour AJAX
  document.getElementById('search-input').addEventListener('input', function() {
    const query = this.value;

    fetch(`/filter_burgers?q=${query}`)
      .then(response => response.text())
      .then(html => {
        document.getElementById('burger-list').innerHTML = html;

        // Ré-exécuter les appels AJAX pour les étoiles
        fetchBurgerRatings();
      })
      .catch(error => console.error('Erreur lors du filtrage :', error));
  });
});
