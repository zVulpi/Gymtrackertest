import re

with open('gym_tracker_website.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Find and remove duplicate timer block
pattern = r"// =======================================================\s*// TIMER LOGIC\s*// =======================================================\s*let timerInt = null;.*?document\.getElementById\('btn-timer-close'\)\.onclick = \(\) => \{\s*clearInterval\(timerInt\); document\.getElementById\('timer-bar'\)\.classList\.remove\('active'\);\s*\};\s*"

new_content = re.sub(pattern, "", content, flags=re.DOTALL)

with open('gym_tracker_website.html', 'w', encoding='utf-8') as f:
    f.write(new_content)

print("Duplicate timer logic removed.")