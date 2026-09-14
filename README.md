# SupOptique Agenda Auto-Sync (Synapses)

Ce dépôt permet de récupérer automatiquement votre emploi du temps de **SupOptique** (géré via **Synapses**) et de l'importer dans des applications de calendrier comme **Google Calendar** ou **Apple Calendar** avec un nettoyage complet et une gestion de couleurs par type de cours.

---

## 🌟 Intérêts principaux du script

* **Nettoyage et lisibilité des cours :** Les intitulés bruts de Synapses (ex: `5N-025-PHO (Cours magistral)`) sont automatiquement convertis en titres clairs et explicites (ex: `Optique physique (CM)`, `Anglais (TD)`).
* **Noms d'agendas automatiques :** Les calendriers intègrent la métadonnée standard `X-WR-CALNAME` (`Cours Magistraux`, `Travaux Dirigés`, etc.) pour s'intituler proprement dès l'importation.
* **Raccourcissement mobile (Alias) :** Les matières à noms à rallonge (comme *Outils Numériques pour l'Ingénieur·e en Physique - 1*) sont automatiquement abrégées (ex: `ONIP 1`) pour ne pas être tronquées sur écran de smartphone ou widget.
* **Localisation précise :** Les salles sont automatiquement extraites et assignées directement au champ **Lieu** (`LOCATION`) de l'événement.
* **Fusion des doublons multi-salles :** Si plusieurs salles sont réservées pour une même session (ex: semaine intensive d'anglais), les salles sont fusionnées proprement sur un créneau unique (`Salle S2.8, Salle S2.10`) plutôt que de créer des blocs superposés.
* **Code couleur par type de séance :** L'emploi du temps est découpé en plusieurs fichiers distincts (`CM`, `TD`, `TP`, `EXAM`, `AUTRE`). En important chaque fichier séparément, vous pouvez leur attribuer des couleurs différentes dans Google ou Apple Calendar. Un fichier global `SO_ALL.ics` est également disponible.
* **Description enrichie :** Chaque événement contient dans sa description le nom complet officiel de la matière, le code du module, le groupe, les intervenants et la salle.

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

#### Option A (Recommandée pour masquer votre token si le dépôt est public) :
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

### 4. Personnalisation optionnelle

Au début du fichier `export_supoptique.py`, vous pouvez personnaliser :

* **Activer / Désactiver les emojis :**
  ```python
  USE_EMOJIS = False  # Mettez True si vous souhaitez activer des emojis devant les titres
  ```
* **Ajouter des alias de matières :**
  ```python
  ALIASES = {
      "Outils Numériques pour l'Ingénieur·e en Physique - 1": "ONIP 1",
      # Ajoutez d'autres raccourcis ici si besoin
  }
  ```
* **Filtrer des options non suivies (`BLACKLIST`) :**
  ```python
  BLACKLIST = [
      # "NOM_OPTION_A_IGNORER",
  ]
  ```

---

### 5. Activer l'automatisation GitHub Actions
1. Allez dans l'onglet **Actions** de votre dépôt GitHub.
2. Le workflow `Update SupOptique Calendars` s'exécutera automatiquement **toutes les 2 heures**.
3. Vous pouvez aussi le lancer manuellement à tout moment via le bouton **Run workflow**.

---

## 📅 Importer dans Google Calendar ou Apple Calendar

Le script génère les calendriers suivants à la racine du dépôt :
* `SO_CM.ics` : Cours Magistraux (`CM`)
* `SO_TD.ics` : Travaux Dirigés (`TD`)
* `SO_TP.ics` : Travaux Pratiques (`TP`)
* `SO_EXAM.ics` : Examens, Partiels, Contrôles continus (`Exam`)
* `SO_AUTRE.ics` : Autres créneaux éventuels
* `SO_ALL.ics` : Calendrier complet réunissant tous les cours

### Procédure d'importation :
1. Dans Google Calendar, à gauche à côté de **Autres agendas**, cliquez sur **+** puis **À partir de l'URL**.
2. Collez l'URL Raw correspondant au type de cours, par exemple :
   ```
   https://raw.githubusercontent.com/Endou999/supoptique-agenda/main/SO_CM.ics
   ```
3. Cliquez sur **Ajouter un agenda**.
4. Dans la liste à gauche, cliquez sur les trois points `⋮` à côté du calendrier ajouté pour lui attribuer la couleur de votre choix.
5. Répétez pour les autres fichiers (`SO_TD.ics`, `SO_TP.ics`, `SO_EXAM.ics`).

> [!TIP]
> **Délai de rafraîchissement Google Calendar :**  
> Google Calendar interroge les flux externes toutes les 8h à 24h. Si vous avez une modification de dernière minute sur Synapses et souhaitez forcer Google Calendar à recharger immédiatement votre calendrier, ajoutez simplement un paramètre à la fin du lien dans Google Calendar (ex : `.../SO_CM.ics?v=2`).
