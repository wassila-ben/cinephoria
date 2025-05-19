const { ipcRenderer } = require('electron');
const fs = require('fs');
const path = require('path');

document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
        const res = await fetch('http://localhost:8000/api/token-auth/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ username: email, password })
        });

        const data = await res.json();

        if (res.ok) {
        // Stocke le token dans un fichier temporaire
        const tokenPath = path.join(__dirname, 'token.txt');
        fs.writeFileSync(tokenPath, data.token);

        // Redirige vers l’interface employé
        window.location.href = 'dashboard.html';
        } else {
        document.getElementById('error').textContent = 'Identifiants incorrects';
        }
    } catch (err) {
        console.error(err);
        document.getElementById('error').textContent = 'Erreur de connexion au serveur';
    }
});

