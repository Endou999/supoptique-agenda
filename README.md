# SupOptique Agenda Auto-Sync (Synapses)

Ce dépôt permet de récupérer automatiquement votre emploi du temps de **SupOptique** (géré via **Synapses**) et de l'importer dans des applications de calendrier comme **Google Calendar** ou **Apple Calendar** avec un nettoyage complet et une gestion de couleurs par type de cours.

---

## 🌟 Intérêts principaux du script

* **Nettoyage et lisibilité des cours :** Les intitulés bruts de Synapses (ex: `5N-025-PHO (Cours magistral)`) sont automatiquement convertis en titres clairs et explicites (ex: `Optique physique (CM)`, `Anglais (TD)`).
* **Localisation précise :** Les salles sont automatiquement extraites et assignées directement au champ **Lieu** (`LOCATION`) de l'événement.
* **Fusion des doublons multi-salles :** Si plusieurs salles sont réservées pour une même session (ex: semaine intensive d'anglais), les salles sont fusionnées proprement sur un créneau unique plutôt que de créer des blocs superposés.
* **Code couleur par type de séance :** L'emploi du temps est découpé en plusieurs fichiers distincts (`CM`, `TD`, `TP`, `EXAM`, `AUTRE`). En important chaque fichier séparément, vous pouvez leur attribuer des couleurs différentes dans Google ou Apple Calendar. Un fichier global `SO_ALL.ics` est également disponible.
* **Description enrichie :** Chaque événement contient dans sa description le code du module, le groupe, les intervenants et la salle.

---

## 🚀 Installation et Configuration

### 1. Cloner ou Forker le projet
Si ce n'est pas déjà fait, forkez ou clonez ce dépôt sur votre compte GitHub.

### 2. Récupérer votre lien iCal Synapses
1. Rendez-vous sur **Synapses** : [synapses.institutoptique.fr](https://synapses.institutoptique.fr).
2. Accédez à votre calendrier personnel / emploi du temps.
3. Copiez le lien d'exportation iCal (qui ressemble à : `https://synapses.institutoptique.fr/calendar/ical/<votre_token>`).

### 3. Configurer votre lien dans le dépôt

Deux méthodes sont possibles :

#### Option A (Recommandée pour garder votre lien secret si le dépôt est public) :
1. Allez dans les **Settings** de votre dépôt GitHub.
2. Cliquez sur **Secrets and variables** > **Actions** > **New repository secret**.
3. Nom : `ICAL_URL`
4. Valeur : Collez votre lien iCal Synapses complet.
5. Validez avec **Add secret**.

#### Option B (Directement dans le code) :
Dans `export_supoptique.py`, mettez à jour la variable `DEFAULT_ICAL_URL` :
```python
DEFAULT_ICAL_URL = "https://synapses.institutoptique.fr/calendar/ical/VOTRE_TOKEN"
```

---

### 4. (Optionnel) Filtrer des options via la `BLACKLIST`
Si vous êtes inscrit à une option ou un module que vous ne suivez pas, ajoutez son mot-clé dans la liste `BLACKLIST` au début de `export_supoptique.py` :

```python
BLACKLIST = [
    # "NOM_OPTION_A_IGNORER",
]
```

---

### 5. Activer l'automatisation GitHub Actions
1. Allez dans l'onglet **Actions** de votre dépôt GitHub.
2. Autorisez l'exécution des workflows si demandé.
3. Le workflow `Update SupOptique Calendars` s'exécutera automatiquement **toutes les 2 heures**.
4. Vous pouvez aussi le lancer manuellement à tout moment via le bouton **Run workflow**.

---

## 📅 Importer dans Google Calendar ou Apple Calendar

Le script génère les calendriers suivants à la racine du dépôt :
* `SO_CM.ics` : Cours Magistraux
* `SO_TD.ics` : Travaux Dirigés
* `SO_TP.ics` : Travaux Pratiques
* `SO_EXAM.ics` : Examens, Partiels, Contrôles continus
* `SO_AUTRE.ics` : Autres créneaux éventuels
* `SO_ALL.ics` : Calendrier complet réunissant tous les cours

### Procédure d'importation :
1. Sur GitHub, ouvrez l'un des fichiers `.ics` (ex: `SO_CM.ics`).
2. Cliquez sur le bouton **Raw** en haut à droite.
3. Copiez l'URL de votre navigateur. Le lien doit avoir la forme suivante :
   ```
   https://raw.githubusercontent.com/Endou999/supoptique-agenda/main/SO_CM.ics
   ```
4. Dans **Google Calendar** :
   - Dans le volet gauche, à côté de *Autres agendas*, cliquez sur **+** puis **À partir de l'URL**.
   - Collez le lien direct.
   - Cliquez sur **Ajouter un agenda**.
   - Personnalisez la couleur de cet agenda selon vos préférences (ex: bleu pour les CM, vert pour les TD, jaune pour les TP, rouge pour les examens).
5. Répétez l'opération pour les autres types (`SO_TD.ics`, `SO_TP.ics`, etc.).
