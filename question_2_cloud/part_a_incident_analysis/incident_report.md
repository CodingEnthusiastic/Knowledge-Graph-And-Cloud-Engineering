# Question 2 — Part A: The Padlock Has Broken (Incident Root Cause Analysis)

**Author:** Cloud & Infrastructure Engineering Candidate  
**Date of Incident Analysis:** October 2026  
**System Under Investigation:** Production AI App (`app.example.in`) on On-Premises Ubuntu Server  

---

## 1. Real Cause of the Problem (Step-by-Step Root Cause Analysis)

### Executive Summary
The browser warning **"Your connection is not private"** (`NET::ERR_CERT_DATE_INVALID`) is caused by an **expired TLS certificate** that expired on **Monday, October 12, 2026 at 09:12:02 GMT**. 

Caddy was unable to automatically renew the certificate because the **new broadband router installed in early September hijacked incoming HTTP port 80 traffic**. When Let's Encrypt / ZeroSSL attempted to validate domain ownership via the ACME HTTP-01 challenge, the router's web management interface intercepted the requests and returned an `HTTP 401 Unauthorized` response rather than forwarding the traffic to Caddy on the Ubuntu server.

---

### Step-by-Step Evidence Mapping from Diagnostic Checks

| Diagnostic Check | Result Observed | Engineering Deduction |
|---|---|---|
| **Check 1: DNS Resolution**<br>`dig +short app.example.in` | `203.0.113.24` | **DNS is correct.** Public DNS accurately points to the office's public WAN IP address. There is no DNS misconfiguration or spoofing. |
| **Check 2: Application Health**<br>`curl -s http://localhost:8000/health` | `{"status":"ok"}` | **Backend is fully functional.** FastAPI / Python backend, PostgreSQL, and workers are running without internal faults. |
| **Check 3: Reverse Proxy Status**<br>`systemctl status caddy` | `Active: active (running) since Wed 2026-09-30 11:02:17 IST` | **Caddy daemon is operational.** The process has been continuously running since September 30. |
| **Check 4: Active Certificate Dates**<br>`openssl s_client ... openssl x509 -noout -dates` | `notBefore=Jul 14 09:12:03 2026 GMT`<br>`notAfter=Oct 12 09:12:02 2026 GMT` | **CERTIFICATE EXPIRED.** Let's Encrypt certificates are valid for 90 days. The certificate expired on **Oct 12, 2026**. Visitors are receiving an expired certificate. |
| **Check 5: Caddy Error Logs**<br>`journalctl -u caddy ...` | `error: 403 :: urn:ietf:params:acme:error:unauthorized :: Invalid response from http://app.example.in/.well-known/acme-challenge/...: 401` | **ACME HTTP-01 Validation Failure.** Caddy begins renewal attempts 30 days before expiration (~September 12). The CA verification bot received an HTTP 401 Unauthorized response instead of the ACME cryptographic token. |
| **Check 6: External WAN Probe**<br>`curl -sI http://app.example.in` | `HTTP/1.1 401 Unauthorized`<br>`Server: micro_httpd`<br>`WWW-Authenticate: Basic realm="Broadband Router"` | **THE SMOKING GUN.** External HTTP traffic reaches `micro_httpd` (embedded web server of the new office router) rather than Caddy. |

---

### The Causal Chain of Failure
1. **July 14, 2026:** Caddy successfully issues a 90-day certificate for `app.example.in`, valid through October 12, 2026.
2. **Early September 2026:** The Internet Service Provider (ISP) replaces the office broadband router. The technician installs a router with factory-default configuration:
   - Port forwarding rules for port 80 (HTTP) and port 443 (HTTPS) to the Ubuntu computer's LAN IP were **erased / not re-created**.
   - The router has **Remote Web Management enabled on WAN port 80**, handled by `micro_httpd` with HTTP Basic Authentication.
3. **Mid-September 2026 (~Sept 12–14):** Caddy enters its automated 30-day renewal window and issues an ACME HTTP-01 challenge. Let's Encrypt sends a GET request to `http://app.example.in/.well-known/acme-challenge/<TOKEN>`.
4. **The Interception:** Because port 80 is not forwarded, the router answers the request with `HTTP/1.1 401 Unauthorized` (`Server: micro_httpd`). Let's Encrypt fails the challenge with error 403/401. Caddy logs the error and retries with exponential backoff.
5. **October 12, 2026 (09:12 GMT):** The existing certificate expires.
6. **Monday Morning:** Users visit `app.example.in` and browsers block access with the warning: *"Your connection is not private"*.

---

## 2. Immediate Resolution Plan (Step-by-Step)

### Step 1: Log in to the Router Admin Console (LAN-Only)
Connect a workstation to the office local network and navigate to the default gateway (typically `http://192.168.1.1` or `http://192.168.0.1`). Log in using the router's administrative credentials.

### Step 2: Disable Remote Management on WAN (Critical Security Fix)
Navigate to **Administration / Security / Remote Management**:
- **Disable** "Remote Web Access / WAN Management" on port 80 and port 443.
- Set router administration to be accessible **only from the LAN / internal IP range**.
- If WAN administration is mandatory, change its port to an obscure high port (e.g., `8443`) and restrict access to a specific trusted source IP.

### Step 3: Establish Static DHCP Reservation for the Ubuntu Server
Navigate to **Network / DHCP Server / Static IP Lease**:
- Locate the Ubuntu server's MAC address and assign a permanent private IP (e.g., `192.168.1.100`).
- Ensure the server never receives a different local IP upon reboot.

### Step 4: Configure Virtual Server / Port Forwarding
Navigate to **Port Forwarding / NAT Rules** and configure the following mapping:
- **Rule 1 (HTTP for ACME & Redirects):**  
  External Port: `80` $\to$ Internal IP: `192.168.1.100` $\to$ Internal Port: `80` (Protocol: TCP)
- **Rule 2 (HTTPS for Secure Application Traffic):**  
  External Port: `443` $\to$ Internal IP: `192.168.1.100` $\to$ Internal Port: `443` (Protocol: TCP)
- Save and apply router settings.

### Step 5: Verify External Forwarding from Outside Network
From a mobile connection or external test terminal, verify that the router header is gone:
```bash
curl -sI http://app.example.in
```
*Expected response:* Caddy's HTTP 308 redirect to HTTPS (`Location: https://app.example.in/`), **not** `micro_httpd 401`.

### Step 6: Force Caddy Certificate Renewal
On the Ubuntu server terminal:
```bash
sudo systemctl reload caddy
# Or force restart if necessary:
sudo systemctl restart caddy
```
Caddy will instantly retry the pending ACME challenge, validate the token over port 80, and write the newly issued certificate to `/var/lib/caddy/.local/share/caddy/certificates/...`.

### Step 7: Confirm Certificate Validity and Production Restoration
```bash
echo | openssl s_client -connect app.example.in:443 -servername app.example.in 2>/dev/null | openssl x509 -noout -dates
```
*Verification:* Confirm `notAfter` now displays a date **90 days in the future** (January 2027). Refresh the browser to verify the secure green padlock.

---

### Alternative Solutions Evaluated

| Alternative | Mechanism | Pros | Cons & Why Rejected for Immediate Fix |
|---|---|---|---|
| **ACME DNS-01 Challenge** | Caddy verifies domain control via DNS TXT records (e.g., Cloudflare API) without needing port 80 open. | Works even if port 80 is blocked by ISP. | Requires installing custom Caddy build with DNS plugin (`xcaddy`), adding DNS API tokens, and does not fix the dangerous exposed router management interface on port 80! |
| **Self-Signed Certificate** | Generate snakeoil cert with OpenSSL. | Fast local testing. | Browsers will still display security warnings; completely unacceptable for 20 production users. |

**Chosen Approach:** Port forwarding + WAN management lockdown is selected because it directly solves the operational issue AND eliminates a dangerous network vulnerability.

---

## 3. Preventive Architecture: Never Surprised Again

To guarantee the engineering team is notified **weeks before** certificate expiration rather than discovering it on Monday morning through user complaints:

### 1. External Blackbox Expiry Probing (Uptime Kuma / Prometheus)
Deploy an external probe (e.g., a free Uptime Kuma instance on a cheap VPS or a scheduled GitHub Action / Cloudflare Worker) that executes TLS handshake checks every 6 hours:
- **Threshold 1 (Warning at 21 days):** Slack / Discord / WhatsApp webhook alert to team lead.
- **Threshold 2 (Urgent at 14 days):** SMS / PagerDuty alert to on-call engineer.
- **Threshold 3 (Critical at 7 days):** Daily escalation notification.

### 2. Dual-Verification ACME Architecture (DNS-01 Fallback)
Configure Caddy to use the **DNS-01 challenge** via Cloudflare / Route53 DNS plugin as an automatic fallback if HTTP-01 challenge fails. DNS-01 does not rely on incoming ports or local router state, providing resilience against future router replacements.

### 3. Change Management Runbook for Office Hardware
Create a mandatory operational SOP:
- Whenever office network equipment is serviced or replaced, the network technician must complete a sign-off checklist verifying port forwarding (80, 443), static IP reservation, and WAN lockdown.
- Store a sanitized backup of the router configuration file on an encrypted internal vault.

---

## 4. Other Critical Security and Operational Worries

Beyond the certificate error, the diagnostic results reveal three alarming vulnerabilities:

### 1. Severe Security Risk: Router Management Exposed on WAN
- `Server: micro_httpd` with `Basic realm="Broadband Router"` on public port 80 means **the router's administrative login is accessible to anyone on the internet**.
- `micro_httpd` is an ancient, minimal web server notorious for memory corruption, buffer overflows, and authentication bypass vulnerabilities.
- Automated internet scanners (Shodan, Censys) continuously crawl public IP ranges targeting consumer routers. An attacker brute-forcing default credentials (e.g., `admin/admin`) could modify DNS settings (DNS hijacking), poison traffic, or install botnet malware (e.g., Mirai).

### 2. Regulatory & Privacy Hazard: Sensitive Case Notes on an Unhardened Network
- The prompt explicitly notes: *"It stores private case notes about the people it helps, so security is important."*
- If an attacker gains access to the office router, they share the broadcast domain with the server hosting the PostgreSQL database.
- Housing sensitive personal/legal case notes on an office computer without DMZ isolation, network segmentation, or zero-trust access exposes the organization to massive data breach liability under privacy regulations (e.g., Digital Personal Data Protection Act / DPDP).

### 3. High Availability Single Point of Failure (SPOF)
- The entire application depends on a residential/office broadband line and building power.
- If the office experiences a power cut, an ISP fiber cut, or a dynamic IP reassignment, the application goes down with zero automated failover.
