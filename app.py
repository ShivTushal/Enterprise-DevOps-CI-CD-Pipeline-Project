from flask import Flask, jsonify
import socket
import urllib.request

app = Flask(__name__)

# ==========================================
# SERVER IP FUNCTIONS
# ==========================================

def get_private_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "Unavailable"


def get_public_ip():
    try:
        with urllib.request.urlopen("https://api.ipify.org", timeout=5) as res:
            return res.read().decode("utf-8").strip()
    except Exception:
        return "Unavailable"


# Cache IPs on startup
SERVER_PRIVATE_IP = get_private_ip()
SERVER_PUBLIC_IP = get_public_ip()

print(f"[Server] Private IP : {SERVER_PRIVATE_IP}")
print(f"[Server] Public  IP : {SERVER_PUBLIC_IP}")


# ==========================================
# API ROUTES
# ==========================================

@app.route('/api/server-info')
def server_info():
    return jsonify({
        "private_ip": SERVER_PRIVATE_IP,
        "public_ip": SERVER_PUBLIC_IP
    })


# ==========================================
# HEALTH CHECK ROUTE
# ==========================================

@app.route('/health')
def health():
    return jsonify({
        "status": "healthy"
    }), 200


# ==========================================
# MAIN WEBSITE ROUTE
# ==========================================

@app.route('/')
def home():
    html = (
        get_html()
        .replace('__PRIVATE_IP__', SERVER_PRIVATE_IP)
        .replace('__PUBLIC_IP__', SERVER_PUBLIC_IP)
    )
    return html


# ==========================================
# HTML PAGE
# ==========================================

def get_html():
    return """<!DOCTYPE html>
<html lang="en" data-theme="dark">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Year Converter</title>
    <link href="https://fonts.googleapis.com/css2?family=Playfair+Display:wght@400;700;900&family=DM+Mono:wght@300;400;500&display=swap" rel="stylesheet">
    <style>
        *, *::before, *::after {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }

        /* =====================
           DARK MODE — Deep Navy Indigo
        ===================== */
        :root,
        [data-theme="dark"] {
            --bg: #0d1b2a;
            --surface: #112236;
            --gold: #f4a738;
            --gold-light: #ffd07a;
            --gold-dim: #a06818;
            --cream: #e8f4fd;
            --glass: rgba(244, 167, 56, 0.07);
            --border: rgba(244, 167, 56, 0.22);
            --text: #cde8ff;
            --muted: #6a8faa;
            --input-bg: rgba(8, 28, 48, 0.65);
            --result-bg: rgba(8, 28, 48, 0.55);
            --card-shadow: 0 40px 80px rgba(5, 15, 30, 0.7);
            --grid-line: rgba(244,167,56,0.05);
            --radial: rgba(100,160,255,0.10);
            --jenkins-bg: rgba(10, 22, 38, 0.94);
            --star-opacity: 1;
        }

        /* =====================
           LIGHT MODE — Soft Teal Mint
        ===================== */
        [data-theme="light"] {
            --bg: #e6f4f1;
            --surface: #d0ece7;
            --gold: #d97706;
            --gold-light: #b45309;
            --gold-dim: #f59e42;
            --cream: #134e4a;
            --glass: rgba(13, 148, 136, 0.08);
            --border: rgba(13, 148, 136, 0.28);
            --text: #134e4a;
            --muted: #4d8a83;
            --input-bg: rgba(200, 240, 235, 0.75);
            --result-bg: rgba(200, 240, 235, 0.65);
            --card-shadow: 0 40px 80px rgba(10, 80, 70, 0.13);
            --grid-line: rgba(13,148,136,0.07);
            --radial: rgba(13,148,136,0.09);
            --jenkins-bg: rgba(220, 245, 242, 0.95);
            --star-opacity: 0;
        }

        /* =====================
           GLOBAL TRANSITIONS
        ===================== */
        html {
            transition: background 0.45s ease, color 0.45s ease;
        }

        body, .card, input[type="text"], .jenkins-badge, .result-box, .theme-toggle {
            transition:
                background 0.45s ease,
                border-color 0.45s ease,
                color 0.45s ease,
                box-shadow 0.45s ease;
        }

        html, body {
            height: 100%;
            background: var(--bg);
            color: var(--text);
            font-family: 'DM Mono', monospace;
            overflow-x: hidden;
        }

        /* === BACKGROUND GRID === */
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image:
                linear-gradient(var(--grid-line) 1px, transparent 1px),
                linear-gradient(90deg, var(--grid-line) 1px, transparent 1px);
            background-size: 48px 48px;
            pointer-events: none;
            z-index: 0;
        }

        body::after {
            content: '';
            position: fixed;
            inset: 0;
            background: radial-gradient(ellipse 80% 60% at 50% 10%, var(--radial) 0%, transparent 70%);
            pointer-events: none;
            z-index: 0;
        }

        /* === STARS (hidden in light mode via opacity) === */
        .stars {
            position: fixed;
            inset: 0;
            pointer-events: none;
            z-index: 0;
            overflow: hidden;
            opacity: var(--star-opacity);
            transition: opacity 0.6s ease;
        }

        .star {
            position: absolute;
            width: 2px;
            height: 2px;
            border-radius: 50%;
            background: var(--gold-light);
            animation: twinkle var(--dur, 4s) ease-in-out infinite var(--delay, 0s);
            opacity: 0;
        }

        @keyframes twinkle {
            0%, 100% { opacity: 0; transform: scale(0.5); }
            50% { opacity: var(--bright, 0.6); transform: scale(1.2); }
        }

        /* === THEME TOGGLE === */
        .theme-toggle {
            position: fixed;
            top: 24px;
            right: 28px;
            z-index: 200;
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 999px;
            padding: 8px 14px 8px 10px;
            cursor: pointer;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            animation: fadeSlideDown 1s cubic-bezier(0.22,1,0.36,1) 0.4s both;
            user-select: none;
        }

        .theme-toggle:hover {
            border-color: var(--gold);
            box-shadow: 0 4px 24px rgba(0,0,0,0.2), 0 0 16px rgba(201,168,76,0.15);
        }

        /* pill track */
        .toggle-track {
            width: 36px;
            height: 20px;
            background: var(--border);
            border-radius: 999px;
            position: relative;
            border: 1px solid var(--border);
            transition: background 0.4s ease;
            flex-shrink: 0;
        }

        [data-theme="light"] .toggle-track {
            background: var(--gold);
            border-color: var(--gold);
        }

        /* sliding knob */
        .toggle-knob {
            position: absolute;
            top: 2px;
            left: 2px;
            width: 14px;
            height: 14px;
            border-radius: 50%;
            background: var(--gold);
            transition: transform 0.4s cubic-bezier(0.34,1.56,0.64,1), background 0.4s ease;
        }

        [data-theme="light"] .toggle-knob {
            transform: translateX(16px);
            background: #fff;
        }

        .icon-moon, .icon-sun { font-size: 13px; line-height: 1; }
        .icon-sun  { display: none; }
        [data-theme="light"] .icon-moon { display: none; }
        [data-theme="light"] .icon-sun  { display: inline; }

        .toggle-label {
            font-family: 'DM Mono', monospace;
            font-size: 9px;
            letter-spacing: 0.3em;
            text-transform: uppercase;
            color: var(--muted);
            white-space: nowrap;
            transition: color 0.45s ease;
        }

        /* === LAYOUT === */
        .main-wrap {
            position: relative;
            z-index: 1;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            padding: 60px 24px 120px;
        }

        /* === HEADER === */
        .site-header {
            text-align: center;
            margin-bottom: 64px;
            animation: fadeSlideDown 0.9s cubic-bezier(0.22, 1, 0.36, 1) both;
        }

        .eyebrow {
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            letter-spacing: 0.4em;
            text-transform: uppercase;
            color: var(--gold);
            margin-bottom: 18px;
            opacity: 0.8;
        }

        .eyebrow::before, .eyebrow::after {
            content: '—';
            margin: 0 12px;
            opacity: 0.5;
        }

        h1 {
            font-family: 'Playfair Display', serif;
            font-size: clamp(3rem, 8vw, 6rem);
            font-weight: 900;
            line-height: 0.95;
            letter-spacing: -0.02em;
            background: linear-gradient(135deg, var(--gold-light) 0%, var(--gold) 40%, #cde8ff 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 20px;
        }

        [data-theme="light"] h1 {
            background: linear-gradient(135deg, #b45309 0%, #d97706 45%, #134e4a 100%);
            -webkit-background-clip: text;
            background-clip: text;
        }

        .subtitle {
            font-size: 12px;
            letter-spacing: 0.15em;
            color: var(--muted);
            text-transform: uppercase;
        }

        /* === CARD === */
        .card {
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 2px;
            padding: 56px 52px;
            width: 100%;
            max-width: 520px;
            position: relative;
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            animation: fadeSlideUp 1s cubic-bezier(0.22, 1, 0.36, 1) 0.2s both;
            box-shadow:
                0 0 0 1px rgba(201,168,76,0.05),
                var(--card-shadow),
                inset 0 1px 0 rgba(201,168,76,0.12);
        }

        .card::before, .card::after {
            content: '';
            position: absolute;
            width: 24px;
            height: 24px;
            border-color: var(--gold);
            border-style: solid;
            opacity: 0.5;
        }

        .card::before { top: -1px; left: -1px; border-width: 2px 0 0 2px; }
        .card::after  { bottom: -1px; right: -1px; border-width: 0 2px 2px 0; }

        .card-inner-corner-tl, .card-inner-corner-br {
            position: absolute;
            width: 24px;
            height: 24px;
            border-color: var(--gold);
            border-style: solid;
            opacity: 0.5;
        }

        .card-inner-corner-tl { top: -1px; right: -1px; border-width: 2px 2px 0 0; }
        .card-inner-corner-br { bottom: -1px; left: -1px; border-width: 0 0 2px 2px; }

        .card-label {
            font-size: 9px;
            letter-spacing: 0.5em;
            text-transform: uppercase;
            color: var(--gold);
            margin-bottom: 36px;
            display: flex;
            align-items: center;
            gap: 12px;
            opacity: 0.7;
        }

        .card-label::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, var(--gold-dim), transparent);
        }

        /* === FORM === */
        .input-group { margin-bottom: 28px; }

        .input-label {
            display: block;
            font-size: 9px;
            letter-spacing: 0.35em;
            text-transform: uppercase;
            color: var(--gold);
            margin-bottom: 10px;
            opacity: 0.75;
        }

        .input-wrap { position: relative; }

        .input-wrap::before {
            content: '◈';
            position: absolute;
            left: 16px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--gold-dim);
            font-size: 14px;
            pointer-events: none;
            transition: color 0.3s;
        }

        .input-wrap:focus-within::before { color: var(--gold); }

        input[type="text"] {
            width: 100%;
            background: var(--input-bg);
            border: 1px solid var(--border);
            border-radius: 1px;
            padding: 16px 16px 16px 44px;
            font-family: 'DM Mono', monospace;
            font-size: 18px;
            font-weight: 500;
            color: var(--text);
            outline: none;
            transition: border-color 0.3s, box-shadow 0.3s, background 0.45s, color 0.45s;
            letter-spacing: 0.05em;
        }

        input[type="text"]::placeholder {
            color: var(--muted);
            font-size: 13px;
            letter-spacing: 0.1em;
        }

        input[type="text"]:focus {
            border-color: var(--gold);
            background: rgba(201,168,76,0.04);
            box-shadow: 0 0 0 3px rgba(201,168,76,0.08), 0 0 20px rgba(201,168,76,0.1);
        }

        /* === BUTTON === */
        .btn-submit {
            width: 100%;
            background: transparent;
            border: 1px solid var(--gold);
            border-radius: 1px;
            padding: 17px 24px;
            font-family: 'DM Mono', monospace;
            font-size: 10px;
            font-weight: 500;
            letter-spacing: 0.5em;
            text-transform: uppercase;
            color: var(--gold);
            cursor: pointer;
            position: relative;
            overflow: hidden;
            transition: color 0.4s, box-shadow 0.4s, border-color 0.45s;
        }

        .btn-submit::before {
            content: '';
            position: absolute;
            inset: 0;
            background: var(--gold);
            transform: translateX(-101%);
            transition: transform 0.4s cubic-bezier(0.76, 0, 0.24, 1);
        }

        .btn-submit:hover { color: var(--bg); box-shadow: 0 0 30px rgba(201,168,76,0.3); }
        .btn-submit:hover::before { transform: translateX(0); }
        .btn-submit:active { transform: scale(0.98); }

        .btn-text {
            position: relative;
            z-index: 1;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 12px;
        }

        .btn-icon { font-size: 14px; transition: transform 0.4s; }
        .btn-submit:hover .btn-icon { transform: rotate(90deg); }

        /* === RESULT BOX === */
        .result-box {
            margin-top: 28px;
            padding: 20px 24px;
            background: var(--result-bg);
            border: 1px solid var(--border);
            border-left: 3px solid var(--gold);
            border-radius: 1px;
            font-size: 13px;
            color: var(--text);
            line-height: 1.7;
            display: none;
            animation: fadeSlideUp 0.5s cubic-bezier(0.22,1,0.36,1) both;
            word-break: break-all;
        }

        .result-box.show { display: block; }

        .result-box .result-label {
            font-size: 9px;
            letter-spacing: 0.4em;
            text-transform: uppercase;
            color: var(--gold);
            margin-bottom: 10px;
            opacity: 0.7;
        }

        .result-box .result-value {
            font-size: 15px;
            font-weight: 500;
            color: var(--gold);
        }

        .loading-dots { display: inline-flex; gap: 4px; }

        .loading-dots span {
            width: 4px; height: 4px;
            border-radius: 50%;
            background: var(--gold);
            animation: dot-pulse 1.4s ease-in-out infinite;
        }

        .loading-dots span:nth-child(2) { animation-delay: 0.2s; }
        .loading-dots span:nth-child(3) { animation-delay: 0.4s; }

        @keyframes dot-pulse {
            0%, 80%, 100% { transform: scale(0.6); opacity: 0.3; }
            40% { transform: scale(1); opacity: 1; }
        }

        /* === ORNAMENT === */
        .ornament {
            display: flex;
            align-items: center;
            gap: 16px;
            color: var(--gold-dim);
            font-size: 14px;
            margin: 32px 0 0;
            opacity: 0.5;
        }

        .ornament::before, .ornament::after {
            content: '';
            flex: 1;
            height: 1px;
            background: linear-gradient(90deg, transparent, var(--gold-dim));
        }

        .ornament::after { background: linear-gradient(90deg, var(--gold-dim), transparent); }

        /* === JENKINS BADGE === */
        .jenkins-badge {
            position: fixed;
            bottom: 28px;
            right: 28px;
            z-index: 100;
            display: flex;
            align-items: center;
            gap: 10px;
            background: var(--jenkins-bg);
            border: 1px solid var(--border);
            border-radius: 2px;
            padding: 10px 16px;
            backdrop-filter: blur(16px);
            box-shadow: 0 8px 32px rgba(0,0,0,0.15);
            animation: fadeSlideUp 1.2s cubic-bezier(0.22,1,0.36,1) 0.5s both;
        }

        .jenkins-badge:hover {
            border-color: var(--gold);
            box-shadow: 0 8px 32px rgba(0,0,0,0.2), 0 0 20px rgba(201,168,76,0.1);
        }

        .jenkins-dot {
            width: 7px; height: 7px;
            border-radius: 50%;
            background: #2ecc71;
            box-shadow: 0 0 8px #2ecc71;
            flex-shrink: 0;
            animation: pulse-dot 2s ease-in-out infinite;
        }

        @keyframes pulse-dot {
            0%, 100% { box-shadow: 0 0 6px #2ecc71; opacity: 1; }
            50%       { box-shadow: 0 0 12px #2ecc71, 0 0 20px rgba(46,204,113,0.4); opacity: 0.8; }
        }

        .jenkins-text {
            font-family: 'DM Mono', monospace;
            font-size: 9px;
            letter-spacing: 0.25em;
            text-transform: uppercase;
            color: var(--muted);
        }

        .jenkins-text strong {
            display: block;
            color: var(--text);
            font-size: 10px;
            letter-spacing: 0.1em;
        }

        /* === ANIMATIONS === */
        @keyframes fadeSlideDown {
            from { opacity: 0; transform: translateY(-30px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        @keyframes fadeSlideUp {
            from { opacity: 0; transform: translateY(24px); }
            to   { opacity: 1; transform: translateY(0); }
        }

        /* === GLOW BAND === */
        .glow-band {
            position: fixed;
            bottom: 0; left: 0; right: 0;
            height: 1px;
            background: linear-gradient(90deg, transparent 0%, var(--gold) 40%, var(--gold-light) 50%, var(--gold) 60%, transparent 100%);
            opacity: 0.3;
            z-index: 1;
        }

        /* === IP BADGE === */
        .ip-badge {
            position: fixed;
            top: 24px;
            left: 28px;
            z-index: 200;
            background: var(--glass);
            border: 1px solid var(--border);
            border-radius: 2px;
            padding: 10px 16px;
            backdrop-filter: blur(16px);
            -webkit-backdrop-filter: blur(16px);
            box-shadow: 0 4px 20px rgba(0,0,0,0.15);
            animation: fadeSlideDown 1s cubic-bezier(0.22,1,0.36,1) 0.3s both;
            min-width: 190px;
        }

        .ip-badge:hover {
            border-color: var(--gold);
            box-shadow: 0 4px 24px rgba(0,0,0,0.2), 0 0 16px rgba(244,167,56,0.12);
        }

        .ip-row {
            display: flex;
            align-items: center;
            gap: 8px;
            padding: 3px 0;
        }

        .ip-row + .ip-row {
            margin-top: 6px;
            padding-top: 6px;
            border-top: 1px solid var(--border);
        }

        .ip-dot {
            width: 6px;
            height: 6px;
            border-radius: 50%;
            flex-shrink: 0;
        }

        .ip-dot.private { background: #38bdf8; box-shadow: 0 0 6px #38bdf8; }
        .ip-dot.public  { background: #a78bfa; box-shadow: 0 0 6px #a78bfa; }

        .ip-info {
            font-family: 'DM Mono', monospace;
        }

        .ip-info .ip-type {
            font-size: 8px;
            letter-spacing: 0.35em;
            text-transform: uppercase;
            color: var(--muted);
            display: block;
            line-height: 1;
            margin-bottom: 2px;
        }

        .ip-info .ip-value {
            font-size: 11px;
            font-weight: 500;
            color: var(--text);
            letter-spacing: 0.05em;
        }

        /* === RESPONSIVE === */
        @media (max-width: 560px) {
            .card { padding: 36px 24px; }
            h1 { font-size: 2.8rem; }
            .theme-toggle { top: 16px; right: 16px; }
            .ip-badge { top: 16px; left: 16px; min-width: 160px; }
        }
    </style>
</head>
<body>

<!-- Twinkling stars -->
<div class="stars" id="stars"></div>

<!-- IP Address Badge -->
<div class="ip-badge">
    <div class="ip-row">
        <div class="ip-dot private"></div>
        <div class="ip-info">
            <span class="ip-type">Private IP</span>
            <span class="ip-value">__PRIVATE_IP__</span>
        </div>
    </div>
    <div class="ip-row">
        <div class="ip-dot public"></div>
        <div class="ip-info">
            <span class="ip-type">Public IP</span>
            <span class="ip-value" id="public-ip">__PUBLIC_IP__</span>
        </div>
    </div>
</div>

<!-- Theme Toggle -->
<button class="theme-toggle" onclick="toggleTheme()" aria-label="Toggle light/dark mode">
    <div class="toggle-track">
        <div class="toggle-knob"></div>
    </div>
    <span class="icon-moon">🌙</span>
    <span class="icon-sun">☀️</span>
    <span class="toggle-label" id="toggle-label">Dark</span>
</button>

<div class="main-wrap">
    <header class="site-header">
        <p class="eyebrow">Temporal Tools</p>
        <h1>Year<br>Converter</h1>
        <p class="subtitle">Transform any year across calendars &amp; eras</p>
    </header>

    <div class="card">
        <div class="card-inner-corner-tl"></div>
        <div class="card-inner-corner-br"></div>

        <p class="card-label">Input</p>

        <div class="input-group">
            <label class="input-label" for="year">Enter a year</label>
            <div class="input-wrap">
                <input type="text" id="year" placeholder="e.g. 2024" autocomplete="off" />
            </div>
        </div>

        <button class="btn-submit" onclick="sendData()">
            <span class="btn-text">
                <span>Convert Year</span>
                <span class="btn-icon">✦</span>
            </span>
        </button>

        <div class="result-box" id="result-box">
            <p class="result-label">Result</p>
            <div class="result-value" id="result-value"></div>
        </div>

        <div class="ornament">◆</div>
    </div>
</div>

<!-- Jenkins CI/CD Badge -->
<div class="jenkins-badge">
    <div class="jenkins-dot"></div>
    <div class="jenkins-text">
        <strong>Jenkins CI/CD</strong>
        Working
    </div>
</div>

<div class="glow-band"></div>

<script>
    /* === STAR GENERATOR === */
    (function () {
        const container = document.getElementById('stars');
        for (let i = 0; i < 80; i++) {
            const star = document.createElement('div');
            star.className = 'star';
            star.style.cssText = [
                `left:${Math.random() * 100}%`,
                `top:${Math.random() * 100}%`,
                `--dur:${3 + Math.random() * 5}s`,
                `--delay:${Math.random() * 6}s`,
                `--bright:${0.3 + Math.random() * 0.7}`,
                `width:${1 + Math.random() * 2}px`,
                `height:${1 + Math.random() * 2}px`
            ].join(';');
            container.appendChild(star);
        }
    })();

    /* === THEME TOGGLE === */
    function toggleTheme() {
        const html = document.documentElement;
        const isDark = html.getAttribute('data-theme') === 'dark';
        const next = isDark ? 'light' : 'dark';
        html.setAttribute('data-theme', next);
        document.getElementById('toggle-label').textContent =
            next.charAt(0).toUpperCase() + next.slice(1);
        try { localStorage.setItem('theme', next); } catch(e) {}
    }

    /* Restore saved preference on load */
    (function () {
        try {
            const saved = localStorage.getItem('theme');
            if (saved === 'light' || saved === 'dark') {
                document.documentElement.setAttribute('data-theme', saved);
                document.getElementById('toggle-label').textContent =
                    saved.charAt(0).toUpperCase() + saved.slice(1);
            }
        } catch(e) {}
    })();

    /* === YEAR CONVERTER === */
    async function sendData() {
        const year = document.getElementById("year").value.trim();
        const resultBox = document.getElementById("result-box");
        const resultValue = document.getElementById("result-value");

        if (!year) {
            resultBox.classList.add('show');
            resultValue.innerHTML = '<span style="color:#e05c2a">&#9888; Please enter a year first.</span>';
            return;
        }

        resultBox.classList.add('show');
        resultValue.innerHTML = '<span class="loading-dots"><span></span><span></span><span></span></span>';

        try {
            const response = await fetch(
                "https://1gpfd6q15f.execute-api.ap-south-1.amazonaws.com/test/year",
                {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ year: year })
                }
            );

            const data = await response.json();
            const formatted = JSON.stringify(data, null, 2)
                .replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
            resultValue.innerHTML = '<pre style="white-space:pre-wrap;font-size:12px;line-height:1.8">' + formatted + '</pre>';

        } catch (err) {
            resultValue.innerHTML = '<span style="color:#e05c2a">&#10005; Error: ' + err.message + '</span>';
        }
    }

    /* === ENTER KEY === */
    document.getElementById("year").addEventListener("keydown", function (e) {
        if (e.key === "Enter") sendData();
    });
</script>
</body>
</html>"""

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)