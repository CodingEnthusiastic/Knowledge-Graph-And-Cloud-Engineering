# Incident Investigation: The Broken HTTPS Padlock

**Target Assessment:** Question 2 — Part A: Finding the Padlock Failure  
**Target Audience:** Engineering Leadership & Technical Interview Panel  
**Author:** AI Knowledge Graph & Cloud Engineering Intern Candidate  
**Date:** October 2026  
**Document Format:** Markdown for ChatGPT Executive PDF Generation  

---

## Executive Summary

On Monday morning, users accessing `app.example.in` encountered browser privacy warnings (`NET::ERR_CERT_DATE_INVALID`). An emergency audit revealed that the TLS certificate expired on **October 12, 2026**. 

The root cause was not an application bug or Caddy crash; rather, a replacement router installed by the ISP in early September erased previous port forwarding rules and exposed its internal web management server (`micro_httpd`) directly to the public internet on port 80. Consequently, Let's Encrypt's automated ACME HTTP-01 renewal challenges received an `HTTP 401 Unauthorized` response from the router instead of reaching Caddy.

This report documents the diagnostic evidence, the ordered remediation workflow, automated alert strategies, and critical security vulnerabilities exposed by this incident.

---

## 1. Root Cause Breakdown & Diagnostic Proof

The investigation examined six system checks. The synthesis of evidence is mapped below:

```
                  ┌──────────────────────────────────────────────┐
                  │ 1. DNS points correctly to 203.0.113.24     │
                  │ 2. Backend API healthy (localhost:8000)      │
                  │ 3. Caddy process active & running            │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 4. Check 4 shows Certificate EXPIRED on:     │
                  │    notAfter = Oct 12 09:12:02 2026 GMT       │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 5. Caddy Journalctl: ACME HTTP-01 renewal     │
                  │    failed with HTTP 401 Unauthorized         │
                  └──────────────────────┬───────────────────────┘
                                         ▼
                  ┌──────────────────────────────────────────────┐
                  │ 6. External curl reveals smoking gun:        │
                  │    HTTP/1.1 401 Unauthorized                 │
                  │    Server: micro_httpd                       │
                  │    WWW-Authenticate: Basic realm="Router"    │
                  └──────────────────────────────────────────────┘
```

### The Chain of Events:
1. **July 14, 2026:** Caddy acquired a standard 90-day Let's Encrypt TLS certificate.
2. **Early September 2026:** The ISP replaced the office broadband router. The new router was placed into service with default settings:
   - Port forwarding to internal server (`192.168.1.100`) was lost.
   - Remote router web administration was enabled on WAN port 80.
3. **Mid-September 2026:** Caddy initiated automated background renewal (standard at 30 days remaining). Let's Encrypt contacted `http://app.example.in/.well-known/acme-challenge/...`.
4. **The Interception:** Traffic hit the router's embedded `micro_httpd` server, which demanded Basic Auth credentials. Renewal failed repeatedly.
5. **October 12, 2026:** The 90-day validity period elapsed.
6. **Monday Morning:** First business day after expiration; users were locked out by browser security banners.

---

## 2. Immediate Remediation Runbook

Follow these steps sequentially to restore production within 15 minutes:

### Phase 1: Router Hardening & Port Forwarding
1. **Access Router Admin (Local LAN Only):** Connect to `http://192.168.1.1` from within the office.
2. **Disable WAN Remote Management:** Turn off external web administration on ports 80/443. This closes the router exploit surface and releases port 80.
3. **Set Static DHCP Lease:** Bind the Ubuntu server's MAC address to a fixed IP (e.g., `192.168.1.100`).
4. **Configure Port Forwarding:**
   - Map external TCP `80` $\to$ `192.168.1.100:80` (Required for ACME challenge & HTTP $\to$ HTTPS redirection).
   - Map external TCP `443` $\to$ `192.168.1.100:443` (Required for TLS application traffic).

### Phase 2: Verification & Certificate Issuance
5. **Verify External Routing:**
   ```bash
   curl -sI http://app.example.in
   ```
   *Expected:* HTTP 308 permanent redirect from Caddy, confirming router interception has ceased.
6. **Force Caddy Renewal:**
   ```bash
   sudo systemctl restart caddy
   ```
7. **Verify New Certificate Expiry:**
   ```bash
   echo | openssl s_client -connect app.example.in:443 -servername app.example.in 2>/dev/null | openssl x509 -noout -dates
   ```
   *Verification:* Ensure `notAfter` displays a valid expiration date in January 2027.

---

## 3. Long-Term Preventive Architecture

To ensure the team is never blindsided again:

| Prevention Layer | Implementation Mechanism | Notification Threshold |
|---|---|---|
| **External Synthetics** | Uptime Kuma / Prometheus Blackbox running on external cloud VPS | Alert at 21, 14, and 7 days prior to cert expiry via Telegram/Slack |
| **DNS-01 ACME Validation** | Enable Caddy Cloudflare/Route53 DNS-01 plugin | Independent of incoming port 80; functions even if router settings reset |
| **Hardware Change SOP** | Infrastructure change log & router backup configuration file stored in vault | Mandatory post-maintenance checklist before technician leaves office |

---

## 4. Critical Security & Privacy Findings

The audit reveals significant secondary hazards that demand immediate attention:

1. **Active Router Exposure (`micro_httpd`):**  
   The office router had administrative authentication open to the entire internet. Many implementations of `micro_httpd` suffer from known CVEs and buffer overflow flaws. Any script kiddie or botnet scanning `203.0.113.24` could brute-force the router and seize network control.
2. **Confidential Case Notes at Risk:**  
   The application stores private case notes about vulnerable individuals. Hosting this data on a desktop machine on a flat office network with exposed perimeter hardware represents extreme compliance and legal liability under data privacy laws.
3. **Single Point of Failure (SPOF):**  
   Reliance on a single physical computer, an office broadband connection, and municipal power creates unavoidable operational instability.

---

## Conclusion & Transition to Cloud
Part A proves that running production enterprise software—especially apps processing private case notes—on an office workstation behind consumer network hardware is fundamentally unsafe and operationally brittle. Part B details the cloud migration strategy to eliminate these vulnerabilities permanently.
