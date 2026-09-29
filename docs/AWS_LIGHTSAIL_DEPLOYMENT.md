# AWS Lightsail Deployment Guide — E-Green Quanta

This guide details the complete, step-by-step procedure to deploy the **E-Green Quanta Traffic Route Optimization System** on **AWS Lightsail**.

---

## 1. Architecture on AWS Lightsail

```
                      [ User Web Browser ]
                               │
                               ▼ Port 80 / 443
                   ┌───────────────────────────────┐
                   │  AWS Lightsail Ubuntu Server   │
                   │                               │
                   │       Nginx Reverse Proxy     │
                   │     (SSL / Port 80 & 443)     │
                   └───────┬───────────────┬───────┘
                           │               │
                 Route /   │               │ Route /api/
                           ▼               ▼
                   ┌──────────────┐ ┌──────────────┐
                   │   Frontend   │ │   Backend    │
                   │ Next.js (14) │ │ FastAPI /    │
                   │  Port: 3000  │ │ Uvicorn:8000 │
                   └──────────────┘ └──────┬───────┘
                                           │
                                           ▼
                                    ┌──────────────┐
                                    │ SQLite / PG  │
                                    │ egreen_quanta│
                                    └──────────────┘
```

* **Client Browser:** Communicates through standard HTTP/HTTPS (Port 80/443).
* **Nginx:** Routes web dashboard requests (`/`) to the Next.js frontend, and API/WebSocket requests (`/api/`, `/docs`) to FastAPI.
* **Backend:** FastAPI optimization engine with SQLite database (or optional managed PostgreSQL).

---

## 2. Choosing Your AWS Lightsail Instance

1. Log into your [AWS Lightsail Console](https://lightsail.aws.amazon.com/).
2. Click **Create instance**.
3. Select your instance location (choose the AWS region closest to your users, e.g., *Mumbai (ap-south-1)*, *Virginia*, or *Frankfurt*).
4. Select platform and blueprint:
   * **Platform:** Linux/Unix
   * **Blueprint:** **OS Only** -> **Ubuntu 22.04 LTS** (or Ubuntu 24.04 LTS)
5. Choose your instance plan:
   * **Recommended:** **$10/month plan** (2 GB RAM, 1 or 2 vCPUs, 60 GB SSD, 3 TB transfer).
   * **Budget:** **$5/month plan** (1 GB RAM, 1 vCPU) — *Requires configuring a swap file (detailed in Step 4 below) to prevent out-of-memory during Next.js builds.*
6. Identify your instance (e.g., `egreen-quanta-server`) and click **Create instance**.

---

## 3. Configure Lightsail Firewall & Static IP

### A. Attach a Static IP (Free on AWS Lightsail)
*By default, Lightsail changes your public IP whenever you stop/start the server. A static IP ensures your IP remains permanent.*
1. In the Lightsail console, go to the **Networking** tab.
2. Click **Create static IP**.
3. Select your instance (`egreen-quanta-server`) and click **Create**.
4. Note your newly assigned Static IP address (e.g., `54.xxx.xxx.xxx`).

### B. Open Firewall Ports
1. Click on your instance name and go to the **IPv4 Firewall** section under the **Networking** tab.
2. Ensure the following rules are added:
   * **SSH:** Port `22` (TCP)
   * **HTTP:** Port `80` (TCP)
   * **HTTPS:** Port `443` (TCP)
3. Click **Save**.

---

## 4. Server Initialization & Swap Setup

Connect to your instance either via the **"Connect using SSH"** button in the Lightsail browser console, or from your local terminal:

```bash
ssh -i /path/to/LightsailKey.pem ubuntu@<YOUR_STATIC_IP>
```

### A. Update Packages & Enable Swap Memory (Crucial)
A 2GB swap file ensures smooth compilation of Node.js and Python packages without out-of-memory crashes:

```bash
# 1. Update system packages
sudo apt update && sudo apt upgrade -y

# 2. Create and enable 2GB swap space
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make swap permanent across reboots
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# Verify memory and swap
free -h
```

---

## 5. Deployment Method 1: Docker Compose (Recommended)

Docker Compose encapsulates the frontend, backend, and Nginx reverse proxy into isolated containers that automatically restart if the server reboots.

### A. Install Docker and Docker Compose Plugin
Run the following on your Lightsail Ubuntu server:

```bash
# Install Docker
sudo apt install -y ca-certificates curl gnupg lsb-release
sudo install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg
sudo chmod a+r /etc/apt/keyrings/docker.gpg

echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin

# Allow running docker without sudo
sudo usermod -aG docker $USER
newgrp docker
```

### B. Clone or Transfer the Codebase
Clone your repository onto the server:

```bash
cd ~
git clone <YOUR_GIT_REPO_URL> egreen-quanta
cd egreen-quanta
```

*(Alternatively, if copying from your local machine, use `scp`:)*
```bash
scp -i /path/to/LightsailKey.pem -r . ubuntu@<YOUR_STATIC_IP>:~/egreen-quanta
```

### C. Build and Start All Services
From the root of the project (`~/egreen-quanta`):

```bash
docker compose up -d --build
```

### D. Verify Deployment
Check the running containers:

```bash
docker compose ps
```
You should see:
* `egreen_backend` (Up, port 8000 exposed internally)
* `egreen_frontend` (Up, port 3000 exposed internally)
* `egreen_nginx` (Up, port 0.0.0.0:80->80/tcp)

Now open your browser and navigate to:
```
http://<YOUR_STATIC_IP>
```
You will be greeted by the **E-Green Quanta Admin Login Gate**!
* **Default Username:** `admin`
* **Default Password:** `admin123`

FastAPI Swagger Documentation will be accessible at:
```
http://<YOUR_STATIC_IP>/docs
```

---

## 6. Deployment Method 2: Native Bare-Metal (PM2 + Systemd + Nginx)

If you prefer running services directly on the host without Docker:

### A. Install Node.js, Python, and Nginx
```bash
# Python 3, venv, and build tools
sudo apt install -y python3 python3-pip python3-venv nginx git

# Node.js 20 LTS
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

### B. Setup Backend Service (Systemd)
```bash
cd ~/egreen-quanta/backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
```

Create a systemd unit file for FastAPI:
```bash
sudo tee /etc/systemd/system/egreen-backend.service > /dev/null <<EOF
[Unit]
Description=E-Green Quanta FastAPI Service
After=network.target

[Service]
User=ubuntu
WorkingDirectory=/home/ubuntu/egreen-quanta/backend
Environment="PYTHONPATH=/home/ubuntu/egreen-quanta/backend:/home/ubuntu/egreen-quanta"
ExecStart=/home/ubuntu/egreen-quanta/backend/venv/bin/uvicorn api:app --host 127.0.0.1 --port 8000 --workers 2
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now egreen-backend
sudo systemctl status egreen-backend
```

### C. Setup Frontend Service (PM2)
```bash
cd ~/egreen-quanta/frontend
npm install
npm run build

# Start Next.js production server with PM2
pm2 start npm --name "egreen-frontend" -- start
pm2 save
pm2 startup
# (Run the generated sudo env command printed by pm2 startup)
```

### D. Configure Host Nginx
Replace `/etc/nginx/sites-available/default` with:
```bash
sudo tee /etc/nginx/sites-available/default > /dev/null <<'EOF'
server {
    listen 80 default_server;
    server_name _;

    client_max_body_size 50M;

    # Backend API & WebSockets
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_read_timeout 300s;
    }

    location ~ ^/(docs|redoc|openapi.json) {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }

    # Frontend Dashboard
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    }
}
EOF

sudo nginx -t
sudo systemctl restart nginx
```

---

## 7. Adding a Custom Domain & Free SSL (HTTPS)

Once your domain's DNS A-Record points to your Lightsail Static IP:

```bash
# Install Certbot
sudo apt install -y certbot python3-certbot-nginx

# Obtain and configure SSL certificate automatically
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com
```
Certbot automatically installs the SSL certificate, modifies Nginx configuration, and configures an auto-renewing cron job.

---

## 8. Maintenance & Operational Commands

### Docker Compose Commands (Method 1)
```bash
# View live application logs
docker compose logs -f

# View backend only logs
docker compose logs -f backend

# Restart services
docker compose restart

# Rebuild after code updates
git pull
docker compose up -d --build

# Stop all services
docker compose down
```

### Native Server Commands (Method 2)
```bash
# Backend status & logs
sudo systemctl status egreen-backend
journalctl -u egreen-backend -f

# Frontend status & logs
pm2 status
pm2 logs egreen-frontend

# Nginx test & reload
sudo nginx -t && sudo systemctl reload nginx
```

### Database Backup
Your historical optimization runs are saved in SQLite database `egreen_quanta.db`. To take a manual backup:
```bash
# Create timestamped backup
cp egreen_quanta.db egreen_quanta_backup_$(date +%F).db
```
