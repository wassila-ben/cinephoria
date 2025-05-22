console.log("💡 Script JS chargé !");

const fs = require('fs');
const path = require('path');
const tokenPath = path.join(__dirname, 'token.txt');
const token = fs.readFileSync(tokenPath, 'utf-8').trim();

// Initialisation quand la page est chargée
document.addEventListener('DOMContentLoaded', () => {
    fetchIncidents();
    fetchSalles();
});

// Récupérer les incidents
async function fetchIncidents() {
    const list = document.getElementById('incident-list');
    list.innerHTML = '<p style="color: #ccc;">⏳ Chargement en cours...</p>';

    try {
        const res = await fetch('http://localhost:8000/api/incidents/', {
            headers: {
                'Authorization': `Token ${token}` 
            }
        });

        const data = await res.json();

        if (!Array.isArray(data)) {
            list.innerHTML = '<p style="color: red;">Erreur API</p>';
            return;
        }

        if (!data || data.length === 0) {
            list.innerHTML ='<div class="no-incidents"><p style="color: #aaa; font-style: italic;">Aucun incident signalé.</p></div>';
            return;
}


        list.innerHTML = '<ul>' +
            data.map(i => `
                <li class="${i.statut === 'Résolu' ? 'resolu' : ''}">
                    <span>${i.type_incident} – ${i.description} (${i.statut})</span>
                    ${i.statut !== 'Résolu' ? `<button onclick="resolveIncident(${i.id})">Traité</button>` : ''}
                </li>`
            ).join('') +
            '</ul>';

    } catch (error) {
        console.error("Erreur fetchIncidents :", error);
        list.innerHTML = '<p style="color: red;">Erreur lors du chargement des incidents.</p>';
    }
}

// Récupérer la liste des salles
async function fetchSalles() {
    try {
        const res = await fetch('http://localhost:8000/api/salles/', {
            headers: {
                'Authorization': `Token ${token}`
            }
        });

        const salles = await res.json();
        const select = document.getElementById('salle-id');

        salles.forEach(s => {
            const option = document.createElement('option');
            option.value = s.id;
            option.textContent = s.nom;
            select.appendChild(option);
        });
    } catch (err) {
        console.error("Erreur fetchSalles:", err);
        const select = document.getElementById('salle-id');
        select.innerHTML = '<option value="">Erreur de chargement des salles</option>';
    }
}

// Soumission du formulaire d’incident
document.getElementById('incident-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const salle = document.getElementById('salle-id').value;
    const siege = document.getElementById('siege-id').value;
    const type_materiel = document.getElementById('type-materiel').value;
    const type_incident = document.getElementById('type-incident').value;
    const description = document.getElementById('description').value;

    const payload = {
        salle,
        type_materiel,
        type_incident,
        description,
    };

    if (siege.trim() !== '') {
        payload.siege = siege;
    }

    try {
        const res = await fetch('http://localhost:8000/api/incidents/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Token ${token}`
            },
            body: JSON.stringify(payload)
        });

        if (res.ok) {
            document.getElementById('incident-response').textContent = 'Incident signalé';
            document.getElementById('incident-form').reset();
            fetchIncidents();
        } else {
            const errorData = await res.json();
            document.getElementById('incident-response').textContent = 'Erreur : ' + (errorData.detail || 'déclaration impossible');
        }
    } catch (err) {
        console.error(err);
        document.getElementById('incident-response').textContent = 'Erreur réseau';
    }
});

// Marquer un incident comme traité
async function resolveIncident(id) {
    try {
        const res = await fetch(`http://localhost:8000/api/incidents/${id}/resolve/`, {
            method: 'PATCH',
            headers: {
                'Authorization': `Token ${token}`
            }
        });

        if (res.ok) {
            fetchIncidents();
        }
    } catch (err) {
        console.error("Erreur resolveIncident:", err);
    }
}
