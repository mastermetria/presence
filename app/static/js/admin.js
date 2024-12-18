
async function fetchAutomations() {
    try {
        const response = await fetch("/api/automations");
        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const automations = await response.json();
        displayAutomations(automations);
    } catch (error) {
        console.error("Error fetching automations:", error);
        document.getElementById("automations-container").innerHTML = "<p>Error fetching automatisations.</p>";
    }
}

function displayAutomations(automations) {
    const container = document.getElementById("automations-container");
    container.innerHTML = "";

    if (automations.length === 0) {
        container.innerHTML = "<p>No automatisations found.</p>";
        return;
    }

    automations.forEach(automation => {
        const div = document.createElement("div");
        div.className = "automation";
        div.innerHTML = `
    <h3>${automation.name} (ID: ${automation.id})</h3>
    <textarea id="params-${automation.id}">${JSON.stringify(automation.params, null, 2)}</textarea>
    <button class="saveButton" onclick="saveParams(${automation.id})">Save Changes</button>
    `;
        container.appendChild(div);
    });
}

async function saveParams(automationId) {
    const textarea = document.getElementById(`params-${automationId}`);
    const newParams = textarea.value;

    try {
        const response = await fetch(`/api/automation/${automationId}/update-params`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ params: JSON.parse(newParams) })
        });

        if (!response.ok) {
            throw new Error(`HTTP error! Status: ${response.status}`);
        }

        const result = await response.json();
        alert(`Params for Automation ${automationId} updated successfully!`);
        console.log(result);
    } catch (error) {
        console.error("Error updating params:", error);
        alert(`Failed to update params for Automation ${automationId}.`);
    }
}

// Charger toutes les automatisations au chargement de la page
fetchAutomations();
