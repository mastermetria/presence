
async function fetchLogs() {
    try {
        const response = await fetch(`/logs/${automation_index}`);
        if (!response.ok) {
            console.error(`Erreur : ${response.status}`);
            return;
        }

        const logs = await response.json();
        console.log(logs)
        const terminal = document.getElementById('terminal');
        terminal.innerHTML = ''; // Efface les anciens logs

        logs.forEach(log => {
            // Divise la ligne en deux parties : avant et après le ` - `
            const match = log.match(/^(.*?) - (.*)$/);
            if (match) {
                const timestamp = match[1]; // Partie avant le ` - `
                const message = match[2];  // Partie après le ` - `

                // Crée un élément <p> avec les deux parties
                const p = document.createElement('p');
                p.innerHTML = `<span style="color: red;">${timestamp}</span> - ${message}`;
                terminal.appendChild(p);
            }
        });
    } catch (error) {
        console.error('Erreur lors du chargement des logs :', error);
    }
}

// Recharge les logs toutes les 2 secondes
setInterval(fetchLogs, 60000);
fetchLogs(); // Chargement initial