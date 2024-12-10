document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('update-interval-form');

    // Fonction pour récupérer les jours depuis l'API et les afficher
    const fetchTaskInterval = async () => {
        try {
            const response = await fetch(`/scheduler/jobs/${taskId}`);
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des jours');
            }

            const data = await response.json();
            const days = data.days;
            const intervalSpan = document.getElementById('task_interval');

            if (intervalSpan) {
                intervalSpan.textContent = `${days} jours`;
            }
        } catch (error) {
            console.error('Erreur:', error);
        }
    };

    // Appel de la fonction au chargement de la page
    await fetchTaskInterval();

    form.addEventListener('submit', async function (event) {
        event.preventDefault();

        const formData = new FormData(this);
        const hours = formData.get('interval'); // Récupérer la valeur sélectionnée (en heures)
        const intervalInSeconds = parseInt(hours) * 3600; // Convertir les heures en secondes

        try {
            const response = await fetch(`/scheduler/jobs/${taskId}`, {
                method: 'PATCH',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    trigger: 'interval',
                    seconds: intervalInSeconds, // Utiliser les secondes
                }),
            });

            const result = await response.json();
            const messageDiv = document.getElementById('response-message');

            if (response.ok) {
                messageDiv.textContent = "Intervalle mis à jour avec succès.";
                messageDiv.style.color = "green";
                setTimeout(() => location.reload(), 1000);
            } else {
                messageDiv.textContent = result.message || "Une erreur est survenue.";
                messageDiv.style.color = "red";
            }
        } catch (error) {
            const messageDiv = document.getElementById('response-message');
            messageDiv.textContent = "Erreur lors de la mise à jour : " + error.message;
            messageDiv.style.color = "red";
        }
    });
});
