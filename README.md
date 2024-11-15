# WellNest

## Prerequisites
Before you start, make sure you have:
1. A computer with Windows, Mac, or Linux operating system
2. [Python](https://www.python.org/downloads/) installed (version 3.8 or higher)
3. [Docker Desktop](https://www.docker.com/products/docker-desktop/) (optional, for database)
4. A text editor (like [VS Code](https://code.visualstudio.com/))

## Initial Setup

### Step 1: Get the Required API Keys
1. Get an OpenAI API key:
   - Go to [OpenAI's website](https://platform.openai.com/api-keys)
   - Sign up/Login
   - Create a new API key
   - Save it somewhere safe

### Step 2: Set Up Environment Variables
1. Find the file named `.env.example` in the project folder
2. Make a copy of it and rename it to `.env.local`
3. Open `.env.local` in your text editor
4. Generate a random key for authentication:
   - Open your terminal/command prompt
   - Copy and paste this command:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - Copy the output and paste it as your auth key in `.env.local`
5. Add your OpenAI API key to `.env.local`

### Step 3: Install Required Software

#### Option A: Easy Setup (Recommended for Beginners)
1. Open your terminal/command prompt
2. Navigate to your project folder
3. Run these commands one by one:
```bash
python -m venv .venv                  # Creates a virtual environment
.venv/Scripts/activate                # Windows
# OR
source .venv/bin/activate            # Mac/Linux
pip install -r requirements.txt       # Installs required packages
```

#### Option B: Advanced Setup (Faster but more complex)
Follow these steps if you want to use the faster `uv` package manager:

For Windows:
1. Open PowerShell as administrator
2. Run:
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

For Mac/Linux:
1. Open terminal
2. Run:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then run:
```bash
uv venv
.venv/Scripts/activate                # Windows
# OR
source .venv/bin/activate            # Mac/Linux
uv pip install -r requirements.txt
```

### Step 4: Database Setup
Choose one of these options:

#### Option A: Local Database (Using Docker)
1. Make sure Docker Desktop is running
2. Create a file named `docker-compose.yml` with:
```yaml
services:
  db:
    image: postgres:16
    environment:
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
    ports:
      - 5432:5432
```
3. Run:
```bash
docker compose --env-file .env.local up -d
```

#### Option B: Cloud Database
Use [Supabase](https://supabase.com) for a free hosted database (follow their setup guide)

### Step 5: Initialize Database
Run these commands in order:
```bash
dotenv -f .env.local run -- prisma db push    # Creates database tables
python seed.py                                # Adds initial data
```

## Running the Application
1. Start the app:
```bash
dotenv -f .env.local run -- streamlit run main.py
```
2. Your default web browser should open automatically with the application

## Optional Tools
- View/edit database content:
```bash
dotenv -f .env.local run -- prisma studio
```

## Configuration
- To limit who can register, edit `models/config.yaml`
- Add allowed email domains in the `mail_whitelist` section