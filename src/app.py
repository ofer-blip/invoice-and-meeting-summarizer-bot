import os
import sys
import json
from flask import Flask, request, jsonify, redirect, url_for, session, render_template_string, send_from_directory
from google.oauth2 import id_token
from google.auth.transport import requests
import drive_meeting_sync
import google_auth

app = Flask(__name__)
app.secret_key = os.environ.get("FLASK_SECRET_KEY", "d-dialog-meeting-bot-secret-key-2026")

HTML_TEMPLATE = """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2224%22 fill=%22%230f172a%22/><path d=%22M30 25 h20 c25 0,35 15,35 25 s-10 25,-35 25 h-20 v-50%22 fill=%22none%22 stroke=%22url(%23g)%22 stroke-width=%2212%22 stroke-linecap=%22round%22/><circle cx=%2275%22 cy=%2275%22 r=%228%22 fill=%22%232DD4BF%22/><defs><linearGradient id=%22g%22 x1=%220%22 y1=%220%22 x2=%221%22 y2=%221%22><stop offset=%220%25%22 stop-color=%22%233B82F6%22/><stop offset=%22100%25%22 stop-color=%22%232DD4BF%22/></linearGradient></defs></svg>">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D-Dialog | AI Meeting Assistant</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0B0F19;
            --surface: #141C2F;
            --surface-hover: #1A243C;
            --primary: #3B82F6;
            --primary-hover: #60A5FA;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border: #1E293B;
            --accent: #2DD4BF; /* Teal/Neon */
        }
        * { box-sizing: border-box; font-family: 'Heebo', sans-serif; }
        body { 
            background-color: var(--bg-base); 
            color: var(--text-main); 
            margin: 0; padding: 20px; 
            display: flex; flex-direction: column; align-items: center; 
            min-height: 100vh;
            background-image: radial-gradient(circle at top, #14203a 0%, transparent 40%);
        }
        
        .top-bar {
            width: 100%; max-width: 600px;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 40px; margin-top: 10px;
        }
        .logo { font-weight: 800; font-size: 1.8rem; color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 10px; letter-spacing: -0.5px; }
        .logo span { color: var(--primary); }
        .contact-pill {
            background: rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 50px;
            border: 1px solid var(--border); font-size: 0.95rem;
            color: var(--text-muted); display: flex; align-items: center; gap: 8px;
            backdrop-filter: blur(10px);
        }
        .contact-pill a { color: var(--accent); font-weight: 600; text-decoration: none; transition: 0.3s; }
        .contact-pill a:hover { color: #fff; }

        .container { 
            width: 100%; max-width: 600px; 
            background: var(--surface); padding: 50px 40px; 
            border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
            border: 1px solid var(--border);
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1); 
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
        
        h1 { margin-top: 0; font-size: 2.2rem; font-weight: 700; text-align: center; color: var(--text-main); line-height: 1.2; letter-spacing: -0.5px; margin-bottom: 15px; }
        p { color: var(--text-muted); font-size: 1.15rem; line-height: 1.6; text-align: center; margin-bottom: 40px; font-weight: 400; }
        
        .btn { 
            display: inline-block; padding: 16px 32px; 
            background: linear-gradient(135deg, var(--primary), #2563EB); 
            color: white; text-decoration: none; border-radius: 50px; 
            font-weight: 600; font-size: 1.1rem; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
            border: none; cursor: pointer; width: 100%; 
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4); 
            text-align: center;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 25px -5px rgba(59, 130, 246, 0.5); filter: brightness(1.1); }
        .btn-secondary { 
            background: transparent; color: var(--text-main); 
            border: 1px solid var(--border); box-shadow: none; 
        }
        .btn-secondary:hover { background: rgba(255,255,255,0.05); transform: translateY(-2px); box-shadow: 0 10px 20px rgba(0,0,0,0.2); }
        .btn-logout { color: #F87171; border-color: rgba(248, 113, 113, 0.2); }
        .btn-logout:hover { background: rgba(248, 113, 113, 0.1); border-color: rgba(248, 113, 113, 0.4); }
        
        .success-box { 
            background: rgba(45, 212, 191, 0.1); border: 1px solid rgba(45, 212, 191, 0.2); 
            padding: 20px; border-radius: 16px; margin-bottom: 35px; 
            display: flex; flex-direction: column; align-items: center;
        }
        .success-box h3 { margin: 0 0 5px 0; color: var(--accent); font-weight: 600; }
        
        .video-section { margin-top: 50px; padding-top: 35px; border-top: 1px solid var(--border); }
        .video-section h2 { font-size: 1.2rem; margin-bottom: 20px; color: var(--text-main); font-weight: 600; }
        .video-card { 
            background: rgba(255,255,255,0.03); border: 1px solid var(--border); 
            border-radius: 16px; padding: 20px; display: flex; align-items: center; gap: 20px; 
            cursor: pointer; transition: 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
        }
        .video-card:hover { background: rgba(255,255,255,0.06); transform: translateX(-5px); border-color: rgba(255,255,255,0.1); }
        .play-icon { width: 50px; height: 50px; background: rgba(59, 130, 246, 0.1); color: var(--primary); border: 1px solid rgba(59, 130, 246, 0.2); border-radius: 50%; display: flex; justify-content: center; align-items: center; font-size: 18px; padding-left: 4px; transition: 0.3s; }
        .video-card:hover .play-icon { background: var(--primary); color: #fff; }
        
        .action-buttons { display: flex; flex-direction: column; gap: 15px; margin-top: 25px; }
</style>
</head>
<body>
    <div class="top-bar">
        <a href="/" class="logo">D-Dialog<span>.</span></a>
        <div class="contact-pill">
            לסיוע ותמיכה (עופר): <a href="tel:052-6947202">052-6947202</a>
        </div>
    </div>
    
    <div class="container">
        <h1>תמלול וסיכום אוטומטי<br>לפגישות שלך</h1>
        
        {% if email %}
            <div class="success-box">
                <h3>מחובר בהצלחה</h3>
                <p style="margin: 0; font-size: 0.95rem;">החשבון הפעיל: <strong>{{ email }}</strong></p>
            </div>
            
            <p>פשוט גרור קבצי שמע לתיקיית <strong>"הקלטות לפענוח"</strong> ב-Drive. <br>אנחנו נתמלל, נסכם, ונארגן את הכל בתיקיית <strong>"סיכומים"</strong> - ישירות למייל שלך.</p>
            
            <style>
                .sync-btn-home {
                    background: linear-gradient(135deg, #3B82F6 0%, #2DD4BF 100%);
                    color: white; border: none; padding: 20px 30px; border-radius: 16px;
                    font-size: 1.2rem; font-weight: 700; cursor: pointer;
                    width: 100%; max-width: 400px; margin: 20px auto;
                    display: flex; align-items: center; justify-content: center;
                    gap: 12px; box-shadow: 0 10px 25px rgba(45,212,191,0.3);
                    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
                }
                .sync-btn-home:hover { transform: translateY(-3px); box-shadow: 0 15px 30px rgba(45,212,191,0.4); }
                .sync-btn-home:disabled { opacity: 0.7; transform: none; cursor: not-allowed; }
                .spinner-home {
                    width: 24px; height: 24px; border: 3px solid rgba(255,255,255,0.3);
                    border-top: 3px solid #fff; border-radius: 50%; animation: spin 1s linear infinite;
                }
                .folders-list {
                    background: #1E293B; border-radius: 12px; padding: 15px; margin-bottom: 20px;
                    display: flex; flex-wrap: wrap; gap: 8px; justify-content: center;
                }
                .folder-badge {
                    background: #0F172A; border: 1px solid #334155; padding: 6px 12px;
                    border-radius: 20px; font-size: 0.85rem; color: #94A3B8;
                }
            </style>

            <button id="sync-btn-home" class="sync-btn-home" onclick="runSyncHome()">
                ✨ סנכרן וסכם פגישות עכשיו
            </button>
            <p style="font-size: 0.85rem; color: #64748B; text-align: center; margin-top: -10px; margin-bottom: 20px;">הסיכומים ישלחו למייל וימוינו אוטומטית לתיקיות בדרייב</p>

            <div class="folders-list" id="folders-list">
                <div style="width: 100%; text-align: center; margin-bottom: 10px; color: #fff; font-weight: 500;">התיקיות הפעילות שלך:</div>
                <!-- Folders will be injected here via JS -->
            </div>

            <script>
            function runSyncHome() {
                const btn = document.getElementById('sync-btn-home');
                btn.innerHTML = '<div class="spinner-home"></div> מסנכרן ומעבד...';
                btn.disabled = true;
                
                fetch('/sync')
                    .then(res => res.json())
                    .then(data => {
                        btn.innerHTML = '✅ הסיכומים נשלחו למייל!';
                        setTimeout(() => {
                            btn.innerHTML = '✨ סנכרן וסכם פגישות עכשיו';
                            btn.disabled = false;
                        }, 5000);
                    })
                    .catch(err => {
                        btn.innerHTML = '❌ שגיאה בסנכרון. נסה שוב.';
                        setTimeout(() => {
                            btn.innerHTML = '✨ סנכרן וסכם פגישות עכשיו';
                            btn.disabled = false;
                        }, 5000);
                    });
            }

            // Fetch and display categories dynamically
            fetch('/sync?api=categories')
                .then(res => res.json())
                .then(data => {
                    if (data && data.success && data.categories) {
                        const container = document.getElementById('folders-list');
                        if (data.categories.length === 0) {
                            container.innerHTML += '<div class="folder-badge">לא הוגדרו תיקיות (סיווג כללי)</div>';
                            return;
                        }
                        data.categories.forEach(cat => {
                            let icon = '📁';
                            if (cat.includes('עסק')) icon = '🏢';
                            else if (cat.includes('גפ') || cat.includes('חינוך')) icon = '🏫';
                            else if (cat.includes('פיתוח')) icon = '💻';
                            
                            const badge = document.createElement('div');
                            badge.className = 'folder-badge';
                            badge.textContent = icon + ' ' + cat;
                            container.appendChild(badge);
                        });
                    }
                });
            </script>

            <div class="action-buttons">
                <a href="/dashboard" class="btn btn-secondary">ניהול תיקיות מתקדם</a>
                <a href="/logout" class="btn btn-secondary btn-logout">התנתקות</a>
            </div>
        {% else %}
            <p>הענק למערכת הרשאות קריאה לדרייב וקבל סיכומים אוטומטיים ישירות למייל, ממוינים ומסווגים לפי הצרכים המדויקים שלך.</p>
            <a href="/login" class="btn">התחבר עם Google</a>
        {% endif %}
    </div>
</body>
</html>"""

LOGIN_TEMPLATE = """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2224%22 fill=%22%230f172a%22/><path d=%22M30 25 h20 c25 0,35 15,35 25 s-10 25,-35 25 h-20 v-50%22 fill=%22none%22 stroke=%22url(%23g)%22 stroke-width=%2212%22 stroke-linecap=%22round%22/><circle cx=%2275%22 cy=%2275%22 r=%228%22 fill=%22%232DD4BF%22/><defs><linearGradient id=%22g%22 x1=%220%22 y1=%220%22 x2=%221%22 y2=%221%22><stop offset=%220%25%22 stop-color=%22%233B82F6%22/><stop offset=%22100%25%22 stop-color=%22%232DD4BF%22/></linearGradient></defs></svg>">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D-Dialog | התחברות</title>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;800&display=swap" rel="stylesheet">
    <style>
        :root {
            --primary: #3B82F6;
            --primary-hover: #2563EB;
            --accent: #2DD4BF;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
        }
        * { box-sizing: border-box; font-family: 'Heebo', sans-serif; }
        body { 
            margin: 0; padding: 0; height: 100vh;
            background-color: #030712;
            background-image: 
                radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.12), transparent 40%),
                radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.12), transparent 40%);
            display: flex; justify-content: center; align-items: center; 
        }
        
        .login-card {
            background: linear-gradient(180deg, rgba(30, 41, 59, 0.4) 0%, rgba(15, 23, 42, 0.6) 100%);
            backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
            border-radius: 24px; padding: 60px 50px; 
            border: 1px solid rgba(255, 255, 255, 0.08);
            box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.1);
            width: 100%; max-width: 450px; text-align: center;
            animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px); } to { opacity: 1; transform: translateY(0); } }
        
        .logo { font-weight: 800; font-size: 2.2rem; color: var(--text-main); margin-bottom: 20px; letter-spacing: -0.5px; }
        .logo span { color: var(--primary); }
        
        h1 { margin: 0 0 10px 0; font-size: 1.5rem; font-weight: 600; color: var(--text-main); }
        p { color: var(--text-muted); font-size: 1rem; line-height: 1.5; margin-bottom: 40px; }
        
        .google-btn {
            display: flex; align-items: center; justify-content: center; gap: 12px;
            background: white; color: #3f3f3f; text-decoration: none;
            padding: 14px 24px; border-radius: 12px; font-weight: 600; font-size: 1.05rem;
            transition: 0.3s; box-shadow: 0 4px 10px rgba(0,0,0,0.1);
            width: 100%; border: none; cursor: pointer;
        }
        .google-btn:hover { background: #f8f9fa; transform: translateY(-2px); box-shadow: 0 6px 15px rgba(0,0,0,0.15); }
        .google-icon { width: 24px; height: 24px; }
        
        .privacy-note {
            margin-top: 30px; font-size: 0.85rem; color: #64748B; line-height: 1.5;
            display: flex; align-items: center; justify-content: center; gap: 8px;
        }
        .lock-icon { font-size: 14px; }
</style>
</head>
<body>
    <div class="login-card">
        <div class="logo">D-Dialog<span>.</span></div>
        <h1>ברוכים הבאים</h1>
        <p>כדי לסנכרן אוטומטית את תיקיות ההקלטות והסיכומים, עליך להתחבר עם חשבון ה-Google שלך.</p>
        
        <a href="/auth/google" class="google-btn">
            <svg class="google-icon" viewBox="0 0 24 24">
                <path d="M22.56 12.25c0-.78-.07-1.53-.2-2.25H12v4.26h5.92c-.26 1.37-1.04 2.53-2.21 3.31v2.77h3.57c2.08-1.92 3.28-4.74 3.28-8.09z" fill="#4285F4"/>
                <path d="M12 23c2.97 0 5.46-.98 7.28-2.66l-3.57-2.77c-.98.66-2.23 1.06-3.71 1.06-2.86 0-5.29-1.93-6.16-4.53H2.18v2.84C3.99 20.53 7.7 23 12 23z" fill="#34A853"/>
                <path d="M5.84 14.09c-.22-.66-.35-1.36-.35-2.09s.13-1.43.35-2.09V7.07H2.18C1.43 8.55 1 10.22 1 12s.43 3.45 1.18 4.93l2.85-2.22.81-.62z" fill="#FBBC05"/>
                <path d="M12 5.38c1.62 0 3.06.56 4.21 1.64l3.15-3.15C17.45 2.09 14.97 1 12 1 7.7 1 3.99 3.47 2.18 7.07l3.66 2.84c.87-2.6 3.3-4.53 6.16-4.53z" fill="#EA4335"/>
            </svg>
            המשך עם Google
        </a>
        
        <div class="privacy-note">
            <span class="lock-icon">🔒</span>
            אנו דורשים גישה ל-Drive אך ורק כדי ליצור עבורך את תיקיות המערכת ולשמור את הסיכומים.
        </div>
    </div>
</body>
</html>"""

DASHBOARD_TEMPLATE = """<!DOCTYPE html>
<html dir="rtl" lang="he">
<head>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2224%22 fill=%22%230f172a%22/><path d=%22M30 25 h20 c25 0,35 15,35 25 s-10 25,-35 25 h-20 v-50%22 fill=%22none%22 stroke=%22url(%23g)%22 stroke-width=%2212%22 stroke-linecap=%22round%22/><circle cx=%2275%22 cy=%2275%22 r=%228%22 fill=%22%232DD4BF%22/><defs><linearGradient id=%22g%22 x1=%220%22 y1=%220%22 x2=%221%22 y2=%221%22><stop offset=%220%25%22 stop-color=%22%233B82F6%22/><stop offset=%22100%25%22 stop-color=%22%232DD4BF%22/></linearGradient></defs></svg>">
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>D-Dialog | הגדרות ותיקיות</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;600;700&display=swap" rel="stylesheet">
    <style>
        :root {
            --bg-base: #0B0F19;
            --surface: #141C2F;
            --surface-hover: #1A243C;
            --primary: #3B82F6;
            --primary-hover: #60A5FA;
            --text-main: #F8FAFC;
            --text-muted: #94A3B8;
            --border: #1E293B;
            --accent: #2DD4BF;
        }
        * { box-sizing: border-box; font-family: 'Heebo', sans-serif; }
        body { 
            background-color: var(--bg-base); 
            color: var(--text-main); 
            margin: 0; padding: 20px; 
            display: flex; flex-direction: column; align-items: center; 
            min-height: 100vh;
            background-image: radial-gradient(circle at top, #14203a 0%, transparent 40%);
        }
        
        .top-bar {
            width: 100%; max-width: 700px;
            display: flex; justify-content: space-between; align-items: center;
            margin-bottom: 40px; margin-top: 10px;
        }
        .logo { font-weight: 800; font-size: 1.8rem; color: var(--text-main); text-decoration: none; display: flex; align-items: center; gap: 10px; letter-spacing: -0.5px; }
        .logo span { color: var(--primary); }
        .contact-pill {
            background: rgba(255,255,255,0.05); padding: 8px 16px; border-radius: 50px;
            border: 1px solid var(--border); font-size: 0.95rem;
            color: var(--text-muted); display: flex; align-items: center; gap: 8px;
            backdrop-filter: blur(10px);
        }
        .contact-pill a { color: var(--accent); font-weight: 600; text-decoration: none; transition: 0.3s; }
        .contact-pill a:hover { color: #fff; }

        .container { 
            width: 100%; max-width: 700px; 
            background: var(--surface); padding: 50px 40px; 
            border-radius: 24px; box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5); 
            border: 1px solid var(--border);
            animation: fadeIn 0.6s cubic-bezier(0.16, 1, 0.3, 1); 
        }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(20px) scale(0.98); } to { opacity: 1; transform: translateY(0) scale(1); } }
        
        h1 { margin-top: 0; font-size: 2rem; font-weight: 700; text-align: center; color: var(--text-main); letter-spacing: -0.5px; margin-bottom: 10px; }
        p { color: var(--text-muted); font-size: 1.1rem; line-height: 1.6; text-align: center; margin-bottom: 40px; font-weight: 400; }
        
        .btn { 
            display: inline-block; padding: 16px 32px; 
            background: linear-gradient(135deg, var(--primary), #2563EB); 
            color: white; text-decoration: none; border-radius: 50px; 
            font-weight: 600; font-size: 1.1rem; transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1); 
            border: none; cursor: pointer; width: 100%; 
            box-shadow: 0 10px 20px -5px rgba(59, 130, 246, 0.4); 
            text-align: center;
        }
        .btn:hover { transform: translateY(-3px); box-shadow: 0 15px 25px -5px rgba(59, 130, 246, 0.5); filter: brightness(1.1); }
        
        .btn-link { display: block; text-align: center; margin-top: 25px; color: var(--text-muted); text-decoration: none; font-weight: 500; transition: 0.3s; }
        .btn-link:hover { color: var(--text-main); }
        
        .category-item { 
            background: rgba(0,0,0,0.2); border: 1px solid var(--border); 
            border-radius: 16px; padding: 24px; margin-bottom: 20px; 
            animation: slideIn 0.3s ease-out; position: relative; 
            transition: border-color 0.3s;
        }
        .category-item:focus-within { border-color: rgba(59, 130, 246, 0.5); }
        
        .category-row { display: flex; gap: 12px; margin-bottom: 15px; }
        @keyframes slideIn { from { opacity: 0; transform: translateY(15px); } to { opacity: 1; transform: translateY(0); } }
        
        input[type="text"] { 
            flex-grow: 1; padding: 14px 20px; font-size: 1.05rem; 
            background: var(--surface); color: var(--text-main);
            border: 1px solid var(--border); border-radius: 12px; 
            transition: all 0.3s; outline: none; font-family: 'Heebo', sans-serif; 
        }
        input[type="text"]:focus, textarea:focus { border-color: var(--primary); box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1); }
        input[type="text"]::placeholder, textarea::placeholder { color: #475569; }
        
        textarea { 
            width: 100%; padding: 16px 20px; font-size: 1rem; 
            background: var(--surface); color: var(--text-main);
            border: 1px solid var(--border); border-radius: 12px; 
            resize: vertical; min-height: 100px; font-family: 'Heebo', sans-serif; 
            transition: all 0.3s; outline: none; line-height: 1.5;
        }
        
        .btn-remove { 
            background: rgba(248, 113, 113, 0.1); color: #F87171; 
            border: 1px solid rgba(248, 113, 113, 0.2); padding: 0 20px; 
            border-radius: 12px; cursor: pointer; font-weight: 600; 
            transition: 0.3s; font-family: sans-serif;
        }
        .btn-remove:hover { background: rgba(248, 113, 113, 0.2); }
        
        .btn-add { 
            background: transparent; color: var(--primary); 
            border: 2px dashed rgba(59, 130, 246, 0.3); padding: 16px; 
            border-radius: 16px; cursor: pointer; font-weight: 600; font-size: 1.05rem;
            width: 100%; margin-bottom: 35px; transition: 0.3s; font-family: 'Heebo', sans-serif; 
        }
        .btn-add:hover { background: rgba(59, 130, 246, 0.05); border-color: var(--primary); }
        
        .success { background: rgba(45, 212, 191, 0.1); color: var(--accent); padding: 15px; border-radius: 12px; text-align: center; font-weight: 600; border: 1px solid rgba(45, 212, 191, 0.2); margin-bottom: 30px; }
        
        /* Custom Checkbox */
        .checkbox-row { margin-top: 15px; display: flex; align-items: center; gap: 10px; padding: 10px 15px; background: rgba(255,255,255,0.02); border-radius: 10px; border: 1px solid rgba(255,255,255,0.05); }
        .checkbox-row label { font-size: 0.95rem; color: var(--text-muted); cursor: pointer; user-select: none; transition: 0.2s; }
        .checkbox-row:hover label { color: var(--text-main); }
        
        input[type="checkbox"] {
            appearance: none; -webkit-appearance: none;
            width: 20px; height: 20px; border-radius: 6px;
            background: var(--surface); border: 1px solid var(--border);
            cursor: pointer; display: flex; justify-content: center; align-items: center;
            transition: 0.2s;
        }
        input[type="checkbox"]:checked { background: var(--primary); border-color: var(--primary); }
        input[type="checkbox"]:checked::after { content: '✓'; color: white; font-size: 14px; font-weight: bold; }

        .sync-btn {
            background: linear-gradient(135deg, #3B82F6 0%, #2DD4BF 100%);
            color: #fff;
            border: none;
            border-radius: 12px;
            padding: 16px;
            width: 100%;
            font-size: 1.1rem;
            font-weight: 700;
            cursor: pointer;
            margin-bottom: 24px;
            display: flex;
            align-items: center;
            justify-content: center;
            gap: 10px;
            box-shadow: 0 4px 15px rgba(59, 130, 246, 0.4);
            transition: transform 0.2s, box-shadow 0.2s;
        }
        .sync-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(59, 130, 246, 0.6);
        }
        .sync-btn:disabled {
            opacity: 0.7;
            cursor: not-allowed;
            transform: none;
        }
        .spinner {
            width: 20px;
            height: 20px;
            border: 3px solid rgba(255,255,255,0.3);
            border-top: 3px solid #fff;
            border-radius: 50%;
            animation: spin 1s linear infinite;
        }
        @keyframes spin { 0% { transform: rotate(0deg); } 100% { transform: rotate(360deg); } }

</style>
</head>
<body>
    <div class="top-bar">
        <a href="/" class="logo">D-Dialog<span>.</span></a>
        <div class="contact-pill">
            לסיוע ותמיכה: <a href="tel:052-6947202">052-6947202</a>
        </div>
    </div>

    <div class="container">
        <h1>ההגדרות והתיקיות שלי</h1>
        <p>כאן תוכל לארגן את הקטגוריות שלך ולהגדיר <strong>הנחיות AI מותאמות אישית</strong>. המערכת תבצע בדיוק מה שתבקש לכל סוג פגישה.</p>
        
        {% if message %}
            <div class="success">{{ message }}</div>
        {% endif %}

        
        <button id="sync-btn" class="sync-btn" onclick="runSync()">
            ✨ סנכרן וסכם פגישות עכשיו
        </button>

        <script>
        function runSync() {
            const btn = document.getElementById('sync-btn');
            btn.innerHTML = '<div class="spinner"></div> מתחבר לדרייב ומסכם...';
            btn.disabled = true;
            
            fetch('/sync')
                .then(res => res.json())
                .then(data => {
                    btn.innerHTML = '✅ הסיכומים מוכנים בדרייב!';
                    setTimeout(() => {
                        btn.innerHTML = '✨ סנכרן וסכם פגישות עכשיו';
                        btn.disabled = false;
                    }, 5000);
                })
                .catch(err => {
                    btn.innerHTML = '❌ שגיאה בסנכרון. נסה שוב.';
                    setTimeout(() => {
                        btn.innerHTML = '✨ סנכרן וסכם פגישות עכשיו';
                        btn.disabled = false;
                    }, 5000);
                });
        }
        </script>

        <form method="POST" action="/dashboard">
            <div id="categoryList">
                {% for cat in categories %}
                <div class="category-item">
                    <div class="category-row">
                        <input type="text" name="category_name" value="{{ cat.name }}" placeholder="שם התיקייה (למשל: סיכומי דירקטוריון)">
                        <button type="button" class="btn-remove" onclick="this.closest('.category-item').remove()" title="הסר תיקייה">✕</button>
                    </div>
                    <textarea name="category_prompt" placeholder="הנחיות AI למנוע (אופציונלי). למשל: סכם רק את ההחלטות העסקיות כרשימת בולטים...">{{ cat.prompt }}</textarea>
                    
                    <div class="checkbox-row">
                        <input type="hidden" name="category_transcribe" value="{{ 'on' if cat.transcribe else 'off' }}">
                        <input type="checkbox" onchange="this.previousElementSibling.value = this.checked ? 'on' : 'off'" {% if cat.transcribe %}checked{% endif %}>
                        <label onclick="this.previousElementSibling.click()">הפק בנוסף תמלול מלא מדויק מילה-במילה (Deepgram Nova-2)</label>
                    </div>
                </div>
                {% endfor %}
            </div>
            <button type="button" class="btn-add" onclick="addCategory()">+ הוסף תיקייה חדשה</button>
            
            <button type="submit" class="btn">שמור הגדרות מערכת</button>
            <a href="/" class="btn-link">חזרה לראשי</a>
        </form>
    </div>

    <script>
        function addCategory() {
            const div = document.createElement('div');
            div.className = 'category-item';
            div.innerHTML = `
                <div class="category-row">
                    <input type="text" name="category_name" placeholder="שם התיקייה חדשה" autofocus>
                    <button type="button" class="btn-remove" onclick="this.closest('.category-item').remove()" title="הסר תיקייה">✕</button>
                </div>
                <textarea name="category_prompt" placeholder="הנחיות AI למנוע (אופציונלי). למשל: סכם רק את ההחלטות..."></textarea>
                <div class="checkbox-row">
                    <input type="hidden" name="category_transcribe" value="off">
                    <input type="checkbox" onchange="this.previousElementSibling.value = this.checked ? 'on' : 'off'">
                    <label onclick="this.previousElementSibling.click()">הפק בנוסף תמלול מלא מדויק מילה-במילה (Deepgram Nova-2)</label>
                </div>
            `;
            document.getElementById('categoryList').appendChild(div);
        }
    </script>
</body>
</html>"""

@app.route('/')
def index():
    # Serve the original PWA index.html
    return send_from_directory('docs', 'index.html')

@app.route('/<path:filename>')
def serve_docs(filename):
    import os
    if os.path.exists(os.path.join('docs', filename)):
        return send_from_directory('docs', filename)
    return "Not found", 404

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    email = session.get('user_email')
    if not email:
        return redirect(url_for('login'))
    
    message = ""
    if request.method == 'POST':
        names = request.form.getlist('category_name')
        prompts = request.form.getlist('category_prompt')
        transcribes = request.form.getlist('category_transcribe')
        
        categories = []
        for i in range(len(names)):
            name = names[i].strip()
            prompt = prompts[i].strip() if i < len(prompts) else ""
            transcribe = transcribes[i] == 'on' if i < len(transcribes) else False
            
            if name:
                categories.append({
                    "name": name, 
                    "prompt": prompt,
                    "transcribe": transcribe
                })
                
        if not categories:
            categories = [{"name": "כללי", "prompt": "", "transcribe": False}]
            
        google_auth.update_user_categories(email, categories)
        message = "ההגדרות נשמרו בהצלחה!"
    
    current_categories = google_auth.get_user_categories(email)
    if not current_categories:
        current_categories = [{"name": "כללי", "prompt": ""}]
    return render_template_string(DASHBOARD_TEMPLATE, categories=current_categories, message=message)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))

@app.route('/login')
def login():
    if session.get('user_email'):
        return redirect(url_for('index'))
    return render_template_string(LOGIN_TEMPLATE)

@app.route('/auth/google')
def auth_google():
    flow = google_auth.get_flow()
    flow.redirect_uri = url_for('oauth2callback', _external=True, _scheme='https')
    authorization_url, state = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        prompt='consent'
    )
    session['state'] = state
    if getattr(flow, 'code_verifier', None):
        session['code_verifier'] = flow.code_verifier
    return redirect(authorization_url)

@app.route('/oauth2callback')
def oauth2callback():
    state = session.get('state')
    flow = google_auth.get_flow()
    flow.redirect_uri = url_for('oauth2callback', _external=True, _scheme='https')
    
    # Restore the PKCE code verifier if it was generated
    if session.get('code_verifier'):
        flow.code_verifier = session.get('code_verifier')
    
    # In production, require HTTPS.
    flow.fetch_token(authorization_response=request.url.replace('http://', 'https://'))
    creds = flow.credentials
    
    # Get user email
    request_session = requests.Request()
    id_info = id_token.verify_oauth2_token(
        creds.id_token, request_session
    )
    email = id_info.get('email')
    
    if email:
        google_auth.save_credentials_for_user(email, creds)
        session['user_email'] = email
        
        # Optionally, create the default folders for the new user immediately
        try:
            from googleapiclient.discovery import build
            drive_svc = build('drive', 'v3', credentials=creds)
            import drive_meeting_sync
            import config
            # Just touch the folders to ensure they exist
            input_folder_id = drive_meeting_sync.find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_INPUT_FOLDER)
            output_folder_id = drive_meeting_sync.find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_OUTPUT_FOLDER)
            archive_folder_id = drive_meeting_sync.find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_ARCHIVE_FOLDER)
        except Exception as e:
            print(f"Error creating folders for new user {email}: {e}")
            
    return redirect(url_for('index'))

@app.route('/sync', methods=['GET', 'POST', 'OPTIONS'])
def sync_meetings():
    if request.method == 'OPTIONS':
        response = jsonify({})
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
        response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
        return response

    # Ignore automatic executions from Cloud Scheduler / PubSub
    if request.headers.get('X-CloudScheduler') or 'pubsub' in request.headers.get('User-Agent', '').lower():
        print("Ignoring automatic scheduled execution.")
        response = jsonify({"success": True, "message": "Ignored automatic trigger"})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

    if request.args.get('api') == 'categories':
        categories = set()
        try:
            import google_auth
            import config
            import drive_meeting_sync
            from googleapiclient.discovery import build
            
            active_users = google_auth.get_all_active_users()
            for email in active_users:
                creds = google_auth.get_credentials_for_user(email)
                if creds:
                    drive_svc = build('drive', 'v3', credentials=creds)
                    input_folder_id = drive_meeting_sync.find_or_create_root_folder(drive_svc, config.DRIVE_MEETINGS_INPUT_FOLDER)
                    
                    query = f"'{input_folder_id}' in parents and mimeType = 'application/vnd.google-apps.folder' and trashed = false"
                    results = drive_svc.files().list(q=query, fields="files(id, name)").execute()
                    
                    for f in results.get('files', []):
                        categories.add(f.get('name'))
        except Exception as e:
            print("Error fetching categories from Drive:", e)
            
        response = jsonify({"success": True, "categories": list(categories)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200

    try:
        force_category = request.args.get('category')
        # Prevent timeout issues by checking if it's a pub/sub or scheduler ping
        # Cloud Run allows up to 60 mins execution if configured, but default is 5 mins.
        import drive_meeting_sync
        found, processed = drive_meeting_sync.sync_all_users(force_category=force_category)
        if found == 0:
            msg = "לא נמצאו הקלטות חדשות בתיקיות."
        elif processed == 0:
            msg = f"נמצאו {found} הקלטות, אך כולן דולגו (ייתכן עקב חריגת מכסה או שגיאה)."
        else:
            msg = f"הסנכרון הושלם בהצלחה! נמצאו {found} קבצים, מתוכם עובדו {processed} הקלטות."
            
        response = jsonify({"success": True, "message": msg})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 200
    except Exception as e:
        import traceback
        traceback.print_exc()
        response = jsonify({"success": False, "error": str(e)})
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))

@app.route('/admin', methods=['GET', 'POST'])
def admin_panel():
    email = session.get('user_email')
    # Hardcoded admin check
    if email != 'ofer@ddialog.co.il':
        return "Access Denied. You are not an administrator.", 403
        
    message = ""
    if request.method == 'POST':
        target_email = request.form.get('target_email')
        new_limit = request.form.get('minutes_limit')
        is_active = request.form.get('is_active') == 'on'
        
        if target_email and new_limit is not None:
            google_auth.update_user_billing(target_email, int(new_limit), is_active)
            message = f"עודכן בהצלחה המשתמש: {target_email}"
            
    users = google_auth.get_all_users_admin()
    
    html = f'''
    <!DOCTYPE html>
    <html lang="he" dir="rtl">
    <head>
    <link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><rect width=%22100%22 height=%22100%22 rx=%2224%22 fill=%22%230f172a%22/><path d=%22M30 25 h20 c25 0,35 15,35 25 s-10 25,-35 25 h-20 v-50%22 fill=%22none%22 stroke=%22url(%23g)%22 stroke-width=%2212%22 stroke-linecap=%22round%22/><circle cx=%2275%22 cy=%2275%22 r=%228%22 fill=%22%232DD4BF%22/><defs><linearGradient id=%22g%22 x1=%220%22 y1=%220%22 x2=%221%22 y2=%221%22><stop offset=%220%25%22 stop-color=%22%233B82F6%22/><stop offset=%22100%25%22 stop-color=%22%232DD4BF%22/></linearGradient></defs></svg>">
        <meta charset="UTF-8">
        <title>ניהול לקוחות - D-Dialog</title>
        <link href="https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;600;700;800&display=swap" rel="stylesheet">
        <style>
            :root {{
                --primary: #3B82F6;
                --primary-hover: #2563EB;
                --accent: #2DD4BF;
                --text-main: #F8FAFC;
                --text-muted: #94A3B8;
            }}
            * {{ box-sizing: border-box; font-family: 'Heebo', sans-serif; }}
            
            body {{ 
                margin: 0; padding: 0; min-height: 100vh;
                background-color: #030712;
                background-image: 
                    radial-gradient(circle at 15% 50%, rgba(59, 130, 246, 0.12), transparent 40%),
                    radial-gradient(circle at 85% 30%, rgba(139, 92, 246, 0.12), transparent 40%),
                    radial-gradient(circle at 50% 100%, rgba(45, 212, 191, 0.08), transparent 50%);
                background-attachment: fixed;
                color: var(--text-main); 
                display: flex; flex-direction: column; align-items: center; 
            }}
            
            .navbar {{
                position: fixed; top: 0; left: 0; width: 100%; height: 72px;
                background: rgba(3, 7, 18, 0.65);
                backdrop-filter: blur(16px); -webkit-backdrop-filter: blur(16px);
                border-bottom: 1px solid rgba(255, 255, 255, 0.05);
                display: flex; justify-content: space-between; align-items: center;
                padding: 0 5%; z-index: 1000;
            }}
            
            .logo {{ 
                font-weight: 800; font-size: 1.6rem; color: var(--text-main); 
                text-decoration: none; letter-spacing: -0.5px; 
                display: flex; align-items: center; gap: 4px;
            }}
            .logo span {{ color: var(--primary); }}
            
            .page-wrapper {{ margin-top: 120px; width: 100%; display: flex; justify-content: center; padding: 0 20px; margin-bottom: 60px; }}

            .container {{ 
                width: 100%; max-width: 1000px; 
                background: linear-gradient(180deg, rgba(30, 41, 59, 0.3) 0%, rgba(15, 23, 42, 0.5) 100%);
                backdrop-filter: blur(24px); -webkit-backdrop-filter: blur(24px);
                border-radius: 24px; padding: 50px 40px; 
                border: 1px solid rgba(255, 255, 255, 0.08);
                box-shadow: 0 30px 60px -15px rgba(0, 0, 0, 0.8), inset 0 1px 1px rgba(255, 255, 255, 0.1);
                animation: fadeIn 0.8s cubic-bezier(0.16, 1, 0.3, 1) forwards;
                opacity: 0;
            }}
            
            @keyframes fadeIn {{ from {{ opacity: 0; transform: translateY(20px); }} to {{ opacity: 1; transform: translateY(0); }} }}
            
            h1 {{ margin-top:0; font-size: 2.2rem; font-weight: 700; color: var(--text-main); border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 20px; margin-bottom: 30px; letter-spacing: -0.5px; }}
            
            table {{ width: 100%; border-collapse: collapse; margin-top: 20px; background: rgba(3, 7, 18, 0.4); border-radius: 16px; overflow: hidden; border: 1px solid rgba(255,255,255,0.05); }}
            th, td {{ padding: 20px; text-align: right; border-bottom: 1px solid rgba(255,255,255,0.03); }}
            th {{ background: rgba(255,255,255,0.02); color: var(--text-muted); font-weight: 600; font-size: 0.95rem; text-transform: uppercase; letter-spacing: 0.5px; }}
            tr:hover td {{ background: rgba(255,255,255,0.02); }}
            
            input[type="number"] {{ 
                width: 100px; padding: 10px 14px; 
                background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.1); 
                border-radius: 8px; color: var(--text-main); font-family: monospace; font-size: 1.05rem;
                outline: none; transition: 0.3s;
            }}
            input[type="number"]:focus {{ border-color: var(--primary); box-shadow: 0 0 0 2px rgba(59, 130, 246, 0.2); }}
            
            input[type="checkbox"] {{
                appearance: none; -webkit-appearance: none;
                width: 24px; height: 24px; border-radius: 6px;
                background: rgba(0,0,0,0.3); border: 1px solid rgba(255,255,255,0.15);
                cursor: pointer; display: flex; justify-content: center; align-items: center;
                transition: 0.2s;
            }}
            input[type="checkbox"]:checked {{ background: linear-gradient(135deg, var(--primary), #2563EB); border-color: transparent; }}
            input[type="checkbox"]:checked::after {{ content: '✓'; color: white; font-size: 16px; font-weight: bold; }}
            
            button {{ 
                background: linear-gradient(135deg, var(--primary), #2563EB); 
                color: white; border: none; padding: 10px 20px; border-radius: 8px; 
                cursor: pointer; font-weight: 600; transition: 0.3s; 
                box-shadow: 0 4px 10px rgba(59, 130, 246, 0.3), inset 0 1px 1px rgba(255,255,255,0.2);
            }}
            button:hover {{ transform: translateY(-1px); box-shadow: 0 6px 15px rgba(59, 130, 246, 0.5); filter: brightness(1.1); }}
            
            .success {{ 
                background: linear-gradient(180deg, rgba(45, 212, 191, 0.1) 0%, rgba(45, 212, 191, 0.02) 100%);
                color: var(--accent); padding: 16px 20px; border-radius: 12px; font-weight: 600; 
                border: 1px solid rgba(45, 212, 191, 0.2); margin-bottom: 25px; 
            }}
</style>
    </head>
    <body>
        <nav class="navbar">
            <a href="/" class="logo">D-Dialog<span>.</span></a>
            <div style="color: var(--text-muted); font-size: 0.95rem;">ממשק ניהול בכיר</div>
        </nav>
        
        <div class="page-wrapper">
            <div class="container">
                <h1>ניהול לקוחות, מכסות וחיובים</h1>
                {"<div class='success'>" + message + "</div>" if message else ""}
                <table>
                    <tr>
                        <th>מייל לקוח</th>
                        <th>מספר שימושים</th>
                            <th>דקות שנוצלו</th>
                        <th>מכסת דקות</th>
                        <th>חשבון פעיל?</th>
                        <th>פעולות</th>
                    </tr>
    '''
    
    for u in users:
        html += f'''
                    <tr>
                        <form method="POST" action="/admin">
                            <input type="hidden" name="target_email" value="{u['email']}">
                            <td style="font-family: monospace; font-size:1rem; color: #E2E8F0;">{u['email']}</td>
                            <td style="color: var(--accent); font-weight:700; font-size:1.05rem;">{u['minutes_used']:.1f} דק'</td>
                            <td><input type="number" name="minutes_limit" value="{u['minutes_limit']}"></td>
                            <td><div style="display:flex; justify-content:flex-end;"><input type="checkbox" name="is_active" {'checked' if u['is_active'] else ''}></div></td>
                            <td><button type="submit">עדכן לקוח</button></td>
                        </form>
                    </tr>
        '''
        
    html += '''
                </table>
            </div>
        </div>
    </body>
    </html>
    '''
    return html

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
