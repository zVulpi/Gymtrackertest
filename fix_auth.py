import re

with open('gym_tracker_website.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Replace API_URL and authToken
content = content.replace("const API_URL = 'http://localhost:3000/api';", "const API_URL_CLOUD = 'http://localhost:3001/api';")
content = content.replace("let authToken = localStorage.getItem('gtrk_token') || null;", "window.authToken = localStorage.getItem('gtrk_token') || null;")

# Fix fetch call
content = content.replace("await fetch(API_URL + endpoint", "await fetch(API_URL_CLOUD + endpoint")

# Fix authToken usage globally
content = content.replace("if (authToken)", "if (window.authToken)")
content = content.replace("if (!authToken)", "if (!window.authToken)")
content = content.replace("authToken = res.token;", "window.authToken = res.token;")
content = content.replace("authToken = null;", "window.authToken = null;")
content = content.replace("localStorage.setItem('gtrk_token', authToken);", "localStorage.setItem('gtrk_token', window.authToken);")

# Fix null references in UI checks
content = content.replace("document.querySelector('.bnav').style.display = 'none';", "const nav = document.querySelector('.bnav');\n      if(nav) nav.style.display = 'none';")

content = content.replace("document.getElementById('btn-sync-now').style.display = 'block';", "if(document.getElementById('btn-sync-now')) document.getElementById('btn-sync-now').style.display = 'block';")
content = content.replace("document.getElementById('btn-logout').style.display = 'block';", "if(document.getElementById('btn-logout')) document.getElementById('btn-logout').style.display = 'block';")

content = content.replace("document.getElementById('btn-sync-now').style.display = 'none';", "if(document.getElementById('btn-sync-now')) document.getElementById('btn-sync-now').style.display = 'none';")
content = content.replace("document.getElementById('btn-logout').style.display = 'none';", "if(document.getElementById('btn-logout')) document.getElementById('btn-logout').style.display = 'none';")

content = content.replace("document.getElementById('btn-goto-reg').onclick", "if(document.getElementById('btn-goto-reg')) document.getElementById('btn-goto-reg').onclick")
content = content.replace("document.getElementById('btn-goto-log').onclick", "if(document.getElementById('btn-goto-log')) document.getElementById('btn-goto-log').onclick")
content = content.replace("document.getElementById('btn-reg').onclick", "if(document.getElementById('btn-reg')) document.getElementById('btn-reg').onclick")
content = content.replace("document.getElementById('btn-verify').onclick", "if(document.getElementById('btn-verify')) document.getElementById('btn-verify').onclick")
content = content.replace("document.getElementById('btn-login').onclick", "if(document.getElementById('btn-login')) document.getElementById('btn-login').onclick")
content = content.replace("document.getElementById('btn-logout').onclick", "if(document.getElementById('btn-logout')) document.getElementById('btn-logout').onclick")
content = content.replace("document.getElementById('btn-sync-now').onclick", "if(document.getElementById('btn-sync-now')) document.getElementById('btn-sync-now').onclick")

with open('gym_tracker_website.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Auth fixes applied.")