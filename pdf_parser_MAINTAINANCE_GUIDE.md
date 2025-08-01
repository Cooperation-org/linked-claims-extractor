# LINKEDTRUST AI PDF Extractor - Maintenance & Updates Guide

## Overview

This document provides comprehensive instructions for maintaining, updating, and troubleshooting the AI PDF Extractor production deployment. Follow these procedures to ensure smooth operation and proper deployment of code changes.

## Server Access

### Obtaining SSH Access

The SSH private key is stored in the secure vault:

**🔐 Vault URL**: https://vault.whatscookin.us/app/passwords/view/d787768d-fe85-4d60-b839-91c7d3843c45

### Connecting to Production Server

1. **Download the SSH key** from the vault
2. **Save and secure the key**:
   ```bash
   # Save the key (replace 'extract_key.pem' with your preferred name)
   nano extract_key.pem
   # Paste the private key content
   
   # Set correct permissions
   chmod 400 extract_key.pem
   ```

3. **Connect to the server**:
   ```bash
   ssh -i extract_key.pem root@24.144.88.199
   # or
   ssh -i extract_key.pem root@extract.linkedtrust.us
   ```

4. **Navigate to the application directory**:
   ```bash
   cd /root/ext/linked-claims-extractor
   ```

## Code Updates & Deployment

### Pulling Latest Changes from GitHub

```bash
# 1. Connect to the server
ssh -i extract_key.pem root@extract.linkedtrust.us

# 2. Navigate to application directory
cd /root/ext/linked-claims-extractor

# 3. Activate virtual environment
cd /root/ext
source venv/bin/activate

# 4. Stop the service before updating
sudo systemctl stop ai-pdf-extractor.service

# 5. Backup current code (optional but recommended)
cp -r /root/ext/linked-claims-extractor /root/ext/linked-claims-extractor.backup.$(date +%Y%m%d_%H%M%S)

# 6. Pull latest changes
cd /root/ext/linked-claims-extractor
git pull origin main

# 7. Update Python dependencies if requirements.txt changed
cd /root/ext
source venv/bin/activate
pip install -r linked-claims-extractor/requirements.txt

# 8. Install any new NLTK data if needed
python -c "import nltk; nltk.download('punkt_tab'); nltk.download('punkt')"

# 9. Download spaCy models if needed
python -m spacy download en_core_web_sm

# 10. Restart the service
sudo systemctl start ai-pdf-extractor.service

# 11. Verify the service is running
sudo systemctl status ai-pdf-extractor.service
```

### Step-by-Step Deployment Checklist

- [ ] **Connect to server** using SSH key from vault
- [ ] **Stop the service**: `sudo systemctl stop ai-pdf-extractor.service`
- [ ] **Backup current code** (if making major changes)
- [ ] **Pull latest code**: `git pull origin main`
- [ ] **Update dependencies**: `pip install -r requirements.txt`
- [ ] **Update environment variables** (if `.env` changes)
- [ ] **Restart service**: `sudo systemctl start ai-pdf-extractor.service`
- [ ] **Check service status**: `sudo systemctl status ai-pdf-extractor.service`
- [ ] **Test application**: `curl -I https://extract.linkedtrust.us`
- [ ] **Monitor logs** for any errors

### Handling Environment Variables

If environment variables need to be updated:

```bash
# Edit the .env file
cd /root/ext/linked-claims-extractor
nano .env

# Ensure proper permissions
chmod 600 .env

# Restart service to load new variables
sudo systemctl restart ai-pdf-extractor.service
```

## Log Management & Monitoring

### Log File Locations

| Service | Log Type | Location | Purpose |
|---------|----------|----------|---------|
| **Gunicorn** | Access | `/var/log/gunicorn/access.log` | HTTP requests |
| **Gunicorn** | Error | `/var/log/gunicorn/error.log` | Application errors |
| **Nginx** | Access | `/var/log/nginx/access.log` | Web server requests |
| **Nginx** | Error | `/var/log/nginx/error.log` | Web server errors |
| **Systemd** | Service | `journalctl -u ai-pdf-extractor.service` | Service status/errors |

### Viewing Logs in Real-Time

```bash
# Monitor application errors (most important)
sudo tail -f /var/log/gunicorn/error.log

# Monitor HTTP requests
sudo tail -f /var/log/gunicorn/access.log

# Monitor system service logs
sudo journalctl -u ai-pdf-extractor.service -f

# Monitor nginx errors
sudo tail -f /var/log/nginx/error.log

# View all logs together
sudo multitail /var/log/gunicorn/error.log /var/log/gunicorn/access.log
```

### Log Analysis Commands

```bash
# Check recent errors in application
sudo tail -100 /var/log/gunicorn/error.log | grep -i error

# Check service restart history
sudo journalctl -u ai-pdf-extractor.service --since "1 hour ago"

# Find high memory usage events
sudo journalctl -u ai-pdf-extractor.service | grep -i "memory\|killed\|oom"

# Check recent HTTP 500 errors
sudo grep "500" /var/log/nginx/access.log | tail -20

# Monitor disk space
df -h
du -sh /var/log/*
```

### Log Rotation

Logs are automatically rotated by the system. Manual cleanup if needed:

```bash
# Clear old logs (be careful!)
sudo truncate -s 0 /var/log/gunicorn/error.log
sudo truncate -s 0 /var/log/gunicorn/access.log

# Or remove old rotated logs
sudo find /var/log -name "*.log.*" -mtime +30 -delete
```

## Troubleshooting Common Issues

### Service Won't Start

```bash
# 1. Check detailed error messages
sudo journalctl -u ai-pdf-extractor.service --no-pager

# 2. Test application manually
cd /root/ext
source venv/bin/activate
cd linked-claims-extractor/pdf_parser/src
python app.py

# 3. Test gunicorn manually
gunicorn --bind 127.0.0.1:5050 --workers 1 app:app

# 4. Check if port is already in use
sudo netstat -tlnp | grep :5050

# 5. Check virtual environment
source /root/ext/venv/bin/activate
python -c "import torch, transformers, anthropic; print('Dependencies OK')"
```

### High Memory Usage

```bash
# Monitor memory in real-time
htop

# Check service memory usage
sudo systemctl status ai-pdf-extractor.service

# Restart service to clear memory
sudo systemctl restart ai-pdf-extractor.service

# Check for memory leaks
sudo journalctl -u ai-pdf-extractor.service | grep -i "memory\|leak"
```

### Application Errors

```bash
# Check Python import errors
cd /root/ext
source venv/bin/activate
cd linked-claims-extractor/pdf_parser/src
python -c "from pdf_parser import DocumentManager; print('Imports OK')"

# Check missing dependencies
pip check

# Re-install problematic packages
pip install --force-reinstall transformers sentence-transformers
```

### SSL Certificate Issues

```bash
# Check certificate status
sudo certbot certificates

# Test certificate renewal
sudo certbot renew --dry-run

# Force renewal if needed
sudo certbot renew --force-renewal

# Restart nginx after certificate changes
sudo systemctl restart nginx
```

## Performance Monitoring

### System Resource Monitoring

```bash
# Real-time system monitoring
htop

# Check CPU usage
top -p $(pgrep -f gunicorn)

# Memory usage breakdown
free -h
cat /proc/meminfo

# Disk I/O monitoring
iotop

# Network connections
sudo netstat -tulnp | grep :5050
```

### Application Performance

```bash
# Check response times
curl -w "@curl-format.txt" -o /dev/null -s https://extract.linkedtrust.us

# Where curl-format.txt contains:
#     time_namelookup:  %{time_namelookup}\n
#     time_connect:     %{time_connect}\n
#     time_appconnect:  %{time_appconnect}\n
#     time_pretransfer: %{time_pretransfer}\n
#     time_redirect:    %{time_redirect}\n
#     time_starttransfer: %{time_starttransfer}\n
#     time_total:       %{time_total}\n

# Monitor active connections
sudo ss -tuln | grep :5050
```

## Emergency Procedures

### Service Recovery

```bash
# Emergency restart
sudo systemctl restart ai-pdf-extractor.service
sudo systemctl restart nginx

# If service is completely broken, manual start
cd /root/ext
source venv/bin/activate
cd linked-claims-extractor/pdf_parser/src
nohup python app.py > /tmp/app.log 2>&1 &
```

### Rollback to Previous Version

```bash
# If you have a backup
sudo systemctl stop ai-pdf-extractor.service
cd /root/ext
mv linked-claims-extractor linked-claims-extractor.broken
mv linked-claims-extractor.backup.YYYYMMDD_HHMMSS linked-claims-extractor
sudo systemctl start ai-pdf-extractor.service
```

### Complete System Reset

```bash
# Nuclear option - complete reinstall
cd /root/ext
sudo systemctl stop ai-pdf-extractor.service
rm -rf venv linked-claims-extractor

# Clone fresh copy
git clone https://github.com/your-org/linked-claims-extractor.git
python3 -m venv venv
source venv/bin/activate
pip install -r linked-claims-extractor/requirements.txt

# Download required models
python -m spacy download en_core_web_sm
python -c "import nltk; nltk.download('punkt_tab')"

# Restart service
sudo systemctl start ai-pdf-extractor.service
```

## Maintenance Schedule

### Daily Checks
- [ ] Verify service is running: `sudo systemctl status ai-pdf-extractor.service`
- [ ] Check application response: `curl -I https://extract.linkedtrust.us`
- [ ] Monitor error logs: `sudo tail -50 /var/log/gunicorn/error.log`

### Weekly Maintenance  
- [ ] Review system resource usage
- [ ] Check log file sizes and clean if necessary
- [ ] Verify SSL certificate expiry date
- [ ] Update system packages: `sudo apt update && sudo apt upgrade`

### Monthly Tasks
- [ ] Pull latest code updates from GitHub
- [ ] Update Python dependencies if needed
- [ ] Review and rotate old log files
- [ ] Check backup integrity (if backups are implemented)

## Contact & Escalation

### Quick Reference
- **Server IP**: 24.144.88.199
- **Domain**: extract.linkedtrust.us
- **SSH Key Vault): https://vault.whatscookin.us/app/passwords/view/d787768d-fe85-4d60-b839-91c7d3843c45

### Emergency Contacts
- For urgent production issues, follow your organization's escalation procedures
- Include relevant log snippets and error messages in any support requests
- Always specify the timestamp when issues occurred for easier log correlation

## Best Practices

1. **Always backup before major changes**
2. **Test in staging environment first** (if available)
3. **Monitor logs during and after deployments**
4. **Keep the vault SSH key secure and access controlled**
5. **Document any configuration changes made**
6. **Use descriptive commit messages for code changes**
7. **Verify service health after every update**