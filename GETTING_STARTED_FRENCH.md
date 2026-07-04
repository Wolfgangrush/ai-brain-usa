# Bienvenue, Maître — votre AI Brain commence ici

Vous n'avez pas besoin d'être programmeur. Vous avez besoin d'un ordinateur portable (Mac ou Windows), d'une connexion internet pour l'installation, et de 30 minutes. Si vous savez copier-coller, vous pouvez utiliser ceci.

> **English:** [GETTING_STARTED.md](GETTING_STARTED.md)

---

## Ce que c'est, en un paragraphe

Un outil gratuit qui transforme votre ordinateur portable en un petit assistant de cabinet juridique privé. Il se souvient de vos dossiers (chaque fichier, chaque partie, chaque ordonnance, chaque date d'audience). Il valide les citations Bluebook. Il vous indique quel tribunal fédéral est compétent. Il signale les risques liés à la Règle modèle 7 de l'ABA et les problèmes de conformité CCPA. Il fonctionne **sur votre propre ordinateur** — pas de cloud, pas de téléchargement, aucun tiers ne lit les données de vos clients. Sous licence MIT. Vous possédez tout ce que vous y mettez.

## Pourquoi un avocat indépendant aux États-Unis devrait s'y intéresser

Les grands cabinets ont des armées de collaborateurs pour vérifier les citations, gérer les dossiers et rédiger. Vous avez vous-même et un ordinateur portable. Voici votre deuxième cerveau.

- **Vous oubliez moins.** Le contexte des dossiers vieux de plusieurs mois revient instantanément.
- **Vous manquez moins de délais.** Les dates d'audience, les délais de dépôt et les prescriptions sont suivis automatiquement.
- **Vous restez conforme à l'ABA.** Le pare-feu intégré signale les risques de publicité (Règle 7), les problèmes de pratique multijuridictionnelle (MR 5.5) et les problèmes de confidentialité (MR 1.6).
- **Vous économisez de l'argent.** Westlaw/PACER/LexisNexis coûtent des milliers par an. Cet outil coûte 0 $.
- **Vos données restent privées.** Les dossiers de vos clients ne quittent JAMAIS votre ordinateur portable.
- **Vous pouvez évoluer.** Lorsque vous embauchez votre premier collaborateur, passez du mode indépendant au mode cabinet — même outil, mêmes données.

## Ce qu'il y a dedans

7 spécialistes qui vivent dans votre terminal :

1. **Le Réceptionniste (le cerveau)** — comprend ce dont vous avez besoin et vous oriente vers le bon spécialiste.
2. **Le Greffier aux citations** — valide les citations Bluebook (SCOTUS, F.3d, F.Supp.3d, U.S.C., C.F.R.).
3. **Le Greffier du tribunal** — connaît les tribunaux fédéraux : SCOTUS, 13 circuits, 94 districts, faillites, fiscalité.
4. **Le Gestionnaire de dossiers** — conserve vos dossiers actifs (parties, audiences, ordonnances, délais).
5. **L'Assistant de rédaction** — se connecte aux plugins de rédaction wolfgang_rush (v0.2+).
6. **Le Responsable conformité** — Règles ABA 7, 5.5, 1.6, Avis formel 512 (éthique de l'IA), CCPA/CPRA, FinCEN CTA.
7. **Le Suivi des délais** — prescriptions, délais de dépôt, dates d'audience (calcul des délais selon FRCP Règle 6).

## Installation rapide

```bash
pip install git+https://github.com/Wolfgangrush/ai-law-firm-usa.git
ailawfirm_usa
```

## Essayer

```bash
ailawfirm_usa court "scotus"
ailawfirm_usa cite "347 U.S. 483 (1954)"
ailawfirm_usa cite "42 U.S.C. § 1983"
```

## Portée

La v0.1 est **axée sur le fédéral.** Elle couvre SCOTUS, les tribunaux fédéraux de circuit/district, FRCP/FRCrP/FRE, les Règles modèles de l'ABA et les citations Bluebook. Les modules spécifiques aux États (CA CRC, NY CPLR, règles des barreaux d'État) arrivent en v0.2+. Les 50 États sont énumérés comme espaces réservés.

## Confidentialité

Tout fonctionne en local. Les dossiers de vos clients, les fichiers et les données de calendrier restent sur votre ordinateur portable. Pas de téléchargement cloud. Pas d'accès tiers. Pas de télémétrie.
