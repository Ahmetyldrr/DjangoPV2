# DjangoPV2

Django project for apphane.com.tr

🚀 **Status: Production Ready with CI/CD!**

## 🌐 Live Site
- **URL**: https://apphane.com.tr
- **Admin**: https://apphane.com.tr/admin/
- **Health Check**: https://apphane.com.tr/health/
- **Direct Django**: http://165.227.130.23:9000 (Backend only)

## 🔧 Quick Commands

### Manual Deployment:
```bash
ssh root@165.227.130.23
cd /var/www/apphane
./deploy_script.sh
```

### Quick Test:
```bash
./quick_test.sh
```

### Logs:
```bash
docker-compose logs -f
```

## 📋 CI/CD Pipeline
- **Trigger**: Push to main branch
- **Tests**: Automatic Django tests
- **Deploy**: Zero-downtime deployment with HTTPS
- **SSL**: Auto-managed certificates
- **Static Files**: Auto-sync for Nginx compatibility  
- **Health Check**: Multiple verification layers
- **Nginx**: Auto-restart and 502 error prevention

## ✅ Fixed Issues
1. ✅ Dockerfile gunicorn command simplified
2. ✅ Docker-compose health checks fixed
3. ✅ Nginx dependency issues resolved
4. ✅ SSL complexity removed for stability
5. ✅ CI/CD pipeline optimized

## 🏗️ Architecture
- **Web**: Django + Gunicorn (Port 80)
- **Database**: PostgreSQL (External)
- **Cache**: Redis (Port 9379)
- **Deploy**: Docker Compose + GitHub Actions

---

**Last Update**: 24 Ağustos 2025  
**Environment**: Production Ready

