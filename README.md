<div align="center">

<img width="140" height="140" src="docs/logo.png" alt="logo">

# Aniweb

Aniweb is a personal streaming website for watching anime with Russian voice acting.

English | [Russian](RU_README.md)

</div>

# Overview

Aniweb is a personal streaming website for watching anime with Russian voice acting from [AniLiberty](https://aniliberty.top/). The AniLiberty API is used to retrieve information about anime. The interface is made with love and specifically for those who used to watch anime on jut.su. The project is intended for local or self-hosted use.

# Features

* **External APIs**: uses the [AniLiberty API](https://api.anilibria.app/api/docs/v1/) to fetch information
* **Home page**: shows the latest updated releases
* **Release catalog**: you can find interesting anime using filters: you can find interesting anime using filters
* **Top search bar**: searches anime by query
* **Favorite releases**: you can add a selected release to your favorites. To see all your favorite releases, go to the favorites section on the top panel
* **Player**: the player is not very convenient at the moment, but it will be improved in the future
* **Mobile support**: currently very poor support, but it partially exists
* **Marked watched episodes**: when you finish watching an episode, the current episode is marked as watched

# Tech Stack

**Backend**:

* Python
* FastAPI
* uvicorn
* Jinja2
* SQLite

**Frontend**:

* HTML
* CSS
* JavaScript
* HLS.js
* Plyr.js

# Installation

Requirements: Python 3.11+

```bash
git clone https://github.com/ixieanais/aniweb.git
cd aniweb

pip install -r requirements.txt
```

# Running

```bash
python main.py
```

# Contributing

If you want to contribute to the project, I would be happy to see any interesting contributions!

1. Fork the repository
2. Create a branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

# License

Copyright © 2025 [ixieanais](https://github.com/ixieanais).<br>
Aniweb is [MIT](https://choosealicense.com/licenses/mit) licensed.