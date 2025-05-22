document.addEventListener('DOMContentLoaded', () => {
  console.log("💡 Script JS chargé !");

  const { ipcRenderer } = require('electron');
  const fs = require('fs');
  const path = require('path');

  document.getElementById('login-form').addEventListener('submit', async (e) => {
    e.preventDefault();
    console.log("🧪 Formulaire soumis !");

    const email = document.getElementById('email').value;
    const password = document.getElementById('password').value;

    try {
      const res = await fetch('http://localhost:8000/api/token-auth/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, password })
      });

      const data = await res.json();
      console.log("🔍 Réponse brute :", data);

      if (res.ok) {
        const tokenPath = path.join(__dirname, 'token.txt');
        fs.writeFileSync(tokenPath, data.token);
        console.log("📦 TOKEN ÉCRIT :", data.token);
        console.log("📂 Chemin :", tokenPath);
        window.location.href = 'dashboard.html';
      } else {
        document.getElementById('error').textContent = 'Identifiants incorrects';
      }
    } catch (err) {
      console.error(err);
      document.getElementById('error').textContent = 'Erreur de connexion au serveur';
    }
  });
});
