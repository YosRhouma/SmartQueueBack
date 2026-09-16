# SmartQueue Backend

SmartQueue est une application backend Django conçue pour faciliter la prise de tickets virtuels à distance afin d'éviter les longues files d'attente dans les administrations publiques et privées telles que les banques, les postes et les institutions de service.

## Description du projet

Ce backend gère :

- les comptes utilisateurs avec différents rôles (`citizen`, `institution`);
- les institutions et les services offerts;
- la création, la gestion et le suivi des tickets virtuels;
- les notifications utilisateurs.

## Structure du projet

```text
smartqueue-backend/
├── apps/
│   ├── users/
│   ├── institutions/
│   ├── tickets/
│   └── notifications/
├── config/
├── db.sqlite3
├── manage.py
└── requirements.txt
```

## Pré-requis

- Python 3.10+
- pip
- virtualenv ou venv

## Installation

1. Cloner le projet :

```bash
git clone <url-du-repo>
cd SQback
```

2. Créer un environnement virtuel :

```bash
python -m venv venv
source venv/bin/activate   # Linux/macOS
venv\Scripts\activate      # Windows
```

3. Installer les dépendances :

```bash
pip install -r requirements.txt
```

4. Configurer la base de données :

```bash
python manage.py migrate
```

5. Créer un superutilisateur :

```bash
python manage.py createsuperuser
```

6. Lancer le serveur de développement :

```bash
python manage.py runserver
```

## Applications Django

- `apps.users` : gestion des utilisateurs et des rôles.
- `apps.institutions` : gestion des institutions et services.
- `apps.tickets` : gestion des tickets virtuels.
- `apps.notifications` : gestion des notifications liées aux tickets.

## Variables d'environnement

Le projet utilise les fichiers Django par défaut pour l'instant. Pour éviter de stocker des secrets dans le code, il est conseillé d'ajouter un fichier `.env` local et d'utiliser la librairie `python-decouple` si nécessaire.

## Licence

swagger
http://127.0.0.1:8000/api/docs/

## nouvelle commande d'execution 
daphne -p 8000 config.asgi:application