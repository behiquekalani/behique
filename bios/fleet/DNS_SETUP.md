# DNS Setup -- behike.store & behike.co

Naboria local IP: `192.168.0.152`
Web server port: `8080`
Both domains on Namecheap.

---

## Option A: Cloudflare Tunnel (recommended)

Free. No port forwarding. Hides your home IP. DDoS protection + free SSL included.

### 1. Create Cloudflare account

Go to https://dash.cloudflare.com/sign-up (free plan).

### 2. Add domains to Cloudflare

Add both `behike.store` and `behike.co` to your Cloudflare account. Cloudflare will give you two nameservers (something like `anna.ns.cloudflare.com` and `bob.ns.cloudflare.com`).

### 3. Change nameservers on Namecheap

For each domain on Namecheap:
1. Go to Domain List > click domain > Nameservers
2. Select "Custom DNS"
3. Paste Cloudflare's two nameservers
4. Save

Wait 5-30 min for propagation (can take up to 48h, usually fast).

### 4. Install cloudflared on Naboria (Windows)

Open PowerShell as Admin:

```powershell
winget install --id Cloudflare.cloudflared -e
```

Or download from: https://github.com/cloudflare/cloudflared/releases/latest (grab the windows-amd64.msi)

### 5. Authenticate

```powershell
cloudflared tunnel login
```

This opens a browser. Pick your Cloudflare account and authorize.

### 6. Create the tunnel

```powershell
cloudflared tunnel create behike
```

This generates a tunnel ID and credentials file. Note the tunnel UUID.

### 7. Create config file

Create `C:\Users\<your-user>\.cloudflared\config.yml`:

```yaml
tunnel: behike
credentials-file: C:\Users\<your-user>\.cloudflared\<TUNNEL-UUID>.json

ingress:
  - hostname: behike.co
    service: http://localhost:8080
  - hostname: behike.store
    service: http://localhost:8080
  - hostname: "*.behike.co"
    service: http://localhost:8080
  - service: http_status:404
```

Replace `<your-user>` and `<TUNNEL-UUID>` with your actual values.

### 8. Route DNS

```powershell
cloudflared tunnel route dns behike behike.co
cloudflared tunnel route dns behike behike.store
```

This creates CNAME records in Cloudflare automatically.

### 9. Run the tunnel

```powershell
cloudflared tunnel run behike
```

### 10. Install as Windows service (so it runs on boot)

```powershell
cloudflared service install
```

Then start it:

```powershell
net start cloudflared
```

### Verify

Visit https://behike.co and https://behike.store. Both should hit Naboria's web server on port 8080 with full SSL.

---

## Option B: Ngrok (quick testing)

Good for temporary URLs before committing to Cloudflare.

### Install

```powershell
winget install --id Ngrok.Ngrok -e
```

### Auth (free account at https://ngrok.com)

```powershell
ngrok config add-authtoken YOUR_TOKEN
```

### Run

```powershell
ngrok http 8080
```

Gives you a temporary public URL like `https://abc123.ngrok-free.app`. Use it for testing. Free tier has random URLs that change on restart.

For custom domains, ngrok requires a paid plan. Use Cloudflare instead.

---

## Security Checklist

- [ ] **Never expose home IP directly.** Always proxy through Cloudflare. Never create A records pointing to your public IP.
- [ ] **Cloudflare proxy enabled.** In DNS settings, make sure the orange cloud icon is ON for all records (proxied, not DNS-only).
- [ ] **SSL/TLS mode set to Full (Strict).** Cloudflare dashboard > SSL/TLS > set to "Full (Strict)". Free cert, zero config.
- [ ] **Rate limiting.** Cloudflare dashboard > Security > WAF > Rate limiting rules. Start with: block IPs that hit more than 100 requests/min.
- [ ] **WAF rules.** Cloudflare dashboard > Security > WAF. Enable managed rules (free tier includes basic protection). Add custom rule to block known bad countries if needed.
- [ ] **Bot protection.** Cloudflare dashboard > Security > Bots. Enable "Bot Fight Mode" (free).
- [ ] **Firewall on Naboria.** Windows Firewall should NOT have port 8080 open to the internet. Only localhost and LAN access. Cloudflare Tunnel connects outbound, so no inbound ports needed.
- [ ] **Keep cloudflared updated.** `winget upgrade Cloudflare.cloudflared`

---

## Quick Reference

| What | Value |
|------|-------|
| behike.co | Namecheap, NS pointed to Cloudflare |
| behike.store | Namecheap, NS pointed to Cloudflare |
| Tunnel name | behike |
| Naboria local IP | 192.168.0.152 |
| Web server | http://localhost:8080 |
| Config file | C:\Users\<user>\.cloudflared\config.yml |
| SSL | Cloudflare (free, automatic) |
