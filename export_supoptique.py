#!/usr/bin/env python3
"""
Synchronisation et nettoyage de l'emploi du temps de SupOptique (Synapses)
pour affichage et colorisation dans Google Calendar, Apple Calendar, etc.
"""

import os
import re
import requests
import ics
from collections import defaultdict

# --- CONFIGURATION ---

# URL de l'export iCal personnel fourni par Synapses (SupOptique)
# Peut être surchargée par une variable d'environnement ou un Secret GitHub "ICAL_URL"
DEFAULT_ICAL_URL = "https://synapses.institutoptique.fr/calendar/ical/65698bc78b16954139a67a7b303a851d8296e61895fcfee4586b9d3d05a4a83d"
_env_ical = os.environ.get("ICAL_URL", "").strip()
ICAL_URL = _env_ical if _env_ical else DEFAULT_ICAL_URL

# Préfixe pour les noms de fichiers générés (ex: SO_CM.ics)
FILE_PREFIX = "SO_"

# Activer ou désactiver les emojis dans les titres (True / False)
USE_EMOJIS = True

# Emojis par type de cours
EMOJIS = {
    "CM": "🎓",
    "TD": "✏️",
    "TP": "🔬",
    "EXAM": "📝",
    "AUTRE": "📌"
}

# Dictionnaire d'abréviations / alias pour raccourcir les noms trop longs sur mobile
ALIASES = {
    "Outils Numériques pour l'Ingénieur·e en Physique - 1": "ONIP 1",
    "Outils Numériques pour l'Ingénieur·e en Physique": "ONIP",
    "Mathématiques & signal 1": "Maths & Signal 1",
}

# Noms d'affichage des calendriers dans Google / Apple Calendar (X-WR-CALNAME)
CALENDAR_NAMES = {
    "CM": "Cours Magistraux",
    "TD": "Travaux Dirigés",
    "TP": "Travaux Pratiques",
    "EXAM": "Examens",
    "AUTRE": "Divers",
    "ALL": "Emploi du temps"
}

# Liste des mots-clés à exclure (en majuscules).
# Si un intitulé ou une description contient l'un de ces mots, l'événement est ignoré.
BLACKLIST = [
    # "EXEMPLE_OPTION_NON_CHOISIE"
]

# Types de cours supportés et leurs fichiers associés
CATEGORIES = ["CM", "TD", "TP", "EXAM", "AUTRE"]


def init_calendar(name):
    """
    Initialise un calendrier avec les métadonnées de nom et fuseau horaire.
    """
    cal = ics.Calendar()
    cal.extra.append(ics.grammar.parse.ContentLine(name="X-WR-CALNAME", value=name))
    cal.extra.append(ics.grammar.parse.ContentLine(name="X-WR-TIMEZONE", value="Europe/Paris"))
    return cal


def determine_category_and_type(raw_type, raw_summary, full_desc):
    """
    Identifie la catégorie de calendrier et le label court du cours.
    """
    combined = f"{raw_type} {raw_summary} {full_desc}".upper()

    # 1. Examens, contrôles, partiels, soutenances
    exam_keywords = [
        "EXAMEN", "EXAM", "CONTRÔLE", "CONTROLE", "PARTIEL",
        "EVALUATION", "ÉVALUATION", "DS", "TEST", "SOUTENANCE"
    ]
    if any(k in combined for k in exam_keywords):
        return "EXAM", "Exam"

    # 2. Travaux Pratiques (TP)
    if "TRAVAUX PRATIQUE" in combined or " TP" in combined or raw_type.upper().startswith("TP"):
        return "TP", "TP"

    # 3. Travaux Dirigés (TD)
    if "TRAVAUX DIRIG" in combined or " TD" in combined or raw_type.upper().startswith("TD"):
        return "TD", "TD"

    # 4. Cours Magistraux (CM)
    if "COURS MAGISTRAL" in combined or "COURS" in combined or " CM" in combined or "AMPHI" in combined:
        return "CM", "CM"

    # 5. Autre événement
    short_type = raw_type.strip() if raw_type.strip() else "Autre"
    return "AUTRE", short_type


def clean_subject_name(subjects, cat, code):
    """
    Nettoie et sélectionne l'intitulé le plus pertinent parmi les lignes de sujet.
    """
    if not subjects:
        return code or "Cours"

    if len(subjects) == 1:
        subject = subjects[0].strip()
    else:
        # Si une ligne est contenue dans une autre plus précise (ex: 'TP OPTIQUE' et 'TP Optique physique')
        s0, s1 = subjects[0].strip(), subjects[1].strip()
        if s0.lower() in s1.lower():
            subject = s1
        elif s1.lower() in s0.lower():
            subject = s0
        else:
            subject = " - ".join(subjects)

    # Si c'est un TP, on retire un éventuel préfixe redondant "TP " dans le titre
    if cat == "TP":
        subject = re.sub(r"^TP\s+", "", subject, flags=re.IGNORECASE)

    # Nettoyage de la ponctuation parasite au début/fin
    subject = subject.strip(" :.-")
    return subject if subject else (code or "Cours")


def parse_event_details(event):
    """
    Extrait les informations détaillées d'un VEVENT SupOptique.
    """
    desc = (event.description or "").replace(r"\n", "\n")
    lines = [l.strip() for l in desc.split("\n") if l.strip()]

    code = ""
    raw_type = ""
    subjects = []
    group = ""
    teachers = ""
    rooms = ""

    # Ligne 0 : code du module (ex: 5N-025-PHO)
    if lines and re.match(r"^\w+-\w+-\w+$", lines[0]):
        code = lines[0]
        remaining = lines[1:]
    else:
        remaining = lines

    # Ligne 1 : Type de séance (ex: Cours magistral, Travaux dirigés)
    if remaining:
        raw_type = remaining[0]
        remaining = remaining[1:]

    # Lignes restantes : Sujet, Groupe, Intervenants, Salles
    for line in remaining:
        if line.startswith("Groupe :"):
            group = line.replace("Groupe :", "").strip()
        elif line.startswith("Intervenants :"):
            teachers = line.replace("Intervenants :", "").strip()
        elif line.startswith("Salles :"):
            rooms = line.replace("Salles :", "").strip()
        else:
            subjects.append(line)

    cat, short_type = determine_category_and_type(raw_type, event.name or "", desc)
    subject = clean_subject_name(subjects, cat, code)

    # Alias / Raccourci pour l'affichage si configuré
    display_subject = ALIASES.get(subject, subject)

    # Ajout d'emoji si activé
    prefix_emoji = f"{EMOJIS.get(cat, '📌')} " if USE_EMOJIS else ""
    title = f"{prefix_emoji}{display_subject} ({short_type})"

    # Lieu : priorité à la localisation de l'événement, sinon la salle dans la description
    location = (event.location or rooms or "").strip()

    # Description nettoyée et enrichie (garde le nom complet officiel)
    desc_parts = [
        f"Matière : {subject}",
        f"Type : {raw_type or short_type}",
    ]
    if code:
        desc_parts.append(f"Code : {code}")
    if group:
        desc_parts.append(f"Groupe : {group}")
    if teachers:
        desc_parts.append(f"Intervenant(s) : {teachers}")
    if location:
        desc_parts.append(f"Salle(s) : {location}")

    clean_description = "\n".join(desc_parts)

    return {
        "title": title,
        "subject": subject,
        "display_subject": display_subject,
        "cat": cat,
        "short_type": short_type,
        "code": code,
        "group": group,
        "teachers": teachers,
        "location": location,
        "clean_description": clean_description,
        "raw_desc": desc
    }


def should_blacklist(info):
    """
    Vérifie si l'événement correspond à un mot-clé de la liste noire.
    """
    if not BLACKLIST:
        return False
    search_space = f"{info['title']} {info['raw_desc']}".upper()
    for word in BLACKLIST:
        if word.upper() in search_space:
            return True
    return False


def get_edt():
    print(f"=== Synchronisation de l'Emploi du Temps SupOptique ===")
    print(f"Téléchargement du flux iCal depuis Synapses...")

    if not ICAL_URL or "VOTRE_TOKEN" in ICAL_URL:
        raise ValueError("Erreur : L'URL de l'agenda Synapses n'est pas configurée.")

    headers = {
        "User-Agent": "Mozilla/5.0 (SupOptique-Agenda-Sync)"
    }
    response = requests.get(ICAL_URL, headers=headers, timeout=30)
    response.raise_for_status()

    content = response.text
    # Isoler la partie VCALENDAR
    cal_start = content.find("BEGIN:VCALENDAR")
    cal_end = content.rfind("END:VCALENDAR")
    if cal_start != -1 and cal_end != -1:
        content = content[cal_start : cal_end + len("END:VCALENDAR")]

    source_cal = ics.Calendar(content)
    total_events = len(source_cal.events)
    print(f"-> {total_events} événements récupérés dans le flux brut.")

    # Regroupement pour fusion / déduplication des créneaux identiques multi-salles
    # Clé de fusion : (heure_debut, heure_fin, matiere, categorie)
    grouped_events = defaultdict(list)
    skipped_blacklist = 0

    for ev in source_cal.events:
        info = parse_event_details(ev)
        if should_blacklist(info):
            skipped_blacklist += 1
            continue

        key = (ev.begin, ev.end, info["subject"], info["cat"])
        grouped_events[key].append((ev, info))

    if skipped_blacklist > 0:
        print(f"-> {skipped_blacklist} événements ignorés via la BLACKLIST.")

    # Création des calendriers par catégorie et d'un calendrier global complet
    cals = {cat: init_calendar(CALENDAR_NAMES.get(cat, cat)) for cat in CATEGORIES}
    cal_all = init_calendar(CALENDAR_NAMES.get("ALL", "Emploi du temps"))

    total_kept = 0
    for key, items in grouped_events.items():
        total_kept += 1
        first_ev, first_info = items[0]

        # Fusion des salles si plusieurs créneaux au même moment (ex: plusieurs salles réservées)
        all_rooms = []
        for _, info in items:
            loc = info["location"]
            if loc and loc not in all_rooms:
                all_rooms.append(loc)
        merged_location = ", ".join(all_rooms) if all_rooms else first_info["location"]

        # Création du nouvel événement nettoyé
        clean_ev = ics.Event()
        clean_ev.name = first_info["title"]
        clean_ev.begin = first_ev.begin
        clean_ev.end = first_ev.end
        clean_ev.location = merged_location
        clean_ev.uid = first_ev.uid

        # Mise à jour de la description avec les salles fusionnées si nécessaire
        final_desc = first_info["clean_description"]
        if len(all_rooms) > 1:
            # Remplacement de la ligne Salle(s)
            lines = [l for l in final_desc.split("\n") if not l.startswith("Salle(s) :")]
            lines.append(f"Salle(s) : {merged_location}")
            final_desc = "\n".join(lines)
        clean_ev.description = final_desc

        # Ajout dans le calendrier correspondant et dans le global
        cat = first_info["cat"]
        cals[cat].events.add(clean_ev)
        cal_all.events.add(clean_ev)

    # Écriture des fichiers .ics
    files_generated = []
    print("\n--- Répartition des événements générés ---")
    for cat in CATEGORIES:
        cal_obj = cals[cat]
        filename = f"{FILE_PREFIX}{cat}.ics"
        with open(filename, "w", encoding="utf-8") as f:
            f.writelines(cal_obj.serialize_iter())
        count = len(cal_obj.events)
        print(f"  * {filename:<16} : {count:3d} cours")
        files_generated.append(filename)

    # Fichier combiné ALL
    all_filename = f"{FILE_PREFIX}ALL.ics"
    with open(all_filename, "w", encoding="utf-8") as f:
        f.writelines(cal_all.serialize_iter())
    print(f"  * {all_filename:<16} : {len(cal_all.events):3d} cours (Total)")
    files_generated.append(all_filename)

    print(f"\nSynchronisation terminée avec succès ({total_kept} cours uniques enregistrés).")
    return files_generated


if __name__ == "__main__":
    get_edt()
