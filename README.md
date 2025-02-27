# Style Transfer Webshop 🎨

## Introduction 📝

Welcome to the Style Transfer Webshop—a unique online store for style transfer merchandise! This project was developed as part of the "AI Project" course at the Deggendorf Institute of Technology. 🏫

---

## Development 🛠️

To ensure consistent dependency management, we use [Poetry](https://python-poetry.org/). Install it with `pip install poetry` if you don’t already have it.

### Requirements ✅

- [Python 3.10.*](https://www.python.org/)  
- [Poetry](https://python-poetry.org/)  
- [Docker](https://www.docker.com/)  
- [Docker Compose](https://docs.docker.com/compose/)  

### Setup Local ⚙️

1. Clone the repository:  
   `git clone https://mygit.th-deg.de/me04536/style-transfer-webshop.git`  
2. Open a terminal in the root directory of the repository.  
3. Install dependencies:  
   `poetry install`  
   - If the Python version doesn’t match but the correct version is installed, set it manually with:  
     `poetry env use /path/to/preferred/python/version`  
4. Activate the virtual environment:  
   `poetry shell`  

### Setup with Compose 🐳

1. Clone the repository:  
   `git clone https://mygit.th-deg.de/me04536/style-transfer-webshop.git`  
2. Open a terminal in the root directory of the repository.  
3. Build and run the services:  
   `docker-compose up --build`  

### Compose for Local Development 💻

For development, you can run services individually:  
- Start a specific service with:  
  `docker-compose up --build <service>`  
- Recommended: Run the database and AI service in Docker containers, then run the web service locally with:  
  `python -m sts`  

### Adding Dependencies 📦

- Add a runtime dependency:  
  `poetry add <dependency>`  
- Add a development dependency:  
  `poetry add --dev <dependency>`  
- **Note**: Avoid using `pip` to install dependencies, as it won’t update the `pyproject.toml` file.

### Linting 🧹

Before committing, ensure code quality with:  
- Format code (auto-fixes errors):  
  `black src`  
- Check for type errors:  
  `mypy src`  
- **Warning**: Unresolved errors will block your commit! 🚫

---

## Authors 👥

- **[Moritz Enderle](https://mygit.th-deg.de/me04536)**  
  - Project Owner  
  - Lead Developer  
  - Backend Development  
  - Project Maintenance  
  - Deployment  
  - UI Design  
- **[Florian Eder](https://mygit.th-deg.de/fe02174)**  
  - AI Development  
  - Backend Development  
  - Streamlit Development  
- **[Amelie Kammerer](https://mygit.th-deg.de/ak23131)**  
  - Streamlit Development  
  - User Area  
  - Checkout Process  
- **[Quirin Joshua Groszeibl](https://mygit.th-deg.de/qg23320)**  
  - Streamlit Development  
  - Lead Design  
  - Product Design Process  

---

Happy coding and shopping! 🎉
