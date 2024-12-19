document.addEventListener('DOMContentLoaded', async () => {
    const form = document.getElementById('update-interval-form');

    // Fonction pour récupérer les jours depuis l'API et les afficher
    const fetchTaskInterval = async () => {
        try {
            const response = await fetch(`/scheduler/jobs/${taskId}`);
            if (!response.ok) {
                throw new Error('Erreur lors de la récupération des informations du scheduler');
            }

            const data = await response.json();
            const intervalSpan = document.getElementById('task_interval');

            if (intervalSpan) {
                let intervalParts = [];

                if (data.days && data.days > 0) {
                    intervalParts.push(`${data.days} jour${data.days > 1 ? 's' : ''}`);
                    console.log(data.days);
                }

                if (data.hours && data.hours > 0) {
                    intervalParts.push(`${data.hours} heure${data.hours > 1 ? 's' : ''}`);
                    console.log(data.hours);
                }

                if (data.minutes && data.minutes > 0) {
                    intervalParts.push(`${data.minutes} minute${data.minutes > 1 ? 's' : ''}`);
                    console.log(data.minutes);
                }

                let intervalText = intervalParts.length > 0 ? intervalParts.join(' et ') : 'Intervalle non spécifié';

                intervalSpan.textContent = intervalText;
            }

        } catch (error) {
            console.error('Erreur:', error);
        }
    };


    // Appel de la fonction au chargement de la page
    await fetchTaskInterval();

    form.addEventListener('submit', async function (event) {
        event.preventDefault();
        console.log("update interval NOW")
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
