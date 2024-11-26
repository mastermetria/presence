document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('update-interval-form');
    const taskId = form.getAttribute('data-task-id'); // Récupérer l'ID de la tâche depuis l'attribut HTML

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
