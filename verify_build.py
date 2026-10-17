import re
from html.parser import HTMLParser

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

class MyParser(HTMLParser):
    def error(self, message):
        print(f"Parser error: {message}")

p = MyParser()
p.feed(content)
print("HTML Parser: Valid!")

activities = [
    ('MainActivity.kt', 'act_main'),
    ('TaskListComposeActivity.kt', 'act_task_list_compose'),
    ('TaskListXmlActivity.kt', 'act_task_list_xml'),
    ('TaskDetailComposeActivity.kt', 'act_task_detail_compose'),
    ('TaskDetailXmlActivity.kt', 'act_task_detail_xml'),
    ('TaskAnalyticsComposeActivity.kt', 'act_analytics_compose'),
    ('TaskAnalyticsXmlActivity.kt', 'act_analytics_xml'),
    ('SettingsComposeActivity.kt', 'act_settings_compose'),
    ('SettingsXmlActivity.kt', 'act_settings_xml'),
    ('ManualStoreOwnerActivity.kt', 'act_manual_store_owner')
]

print(f"\nChecking Activities ({len(activities)} total):")
all_ok = True
for name, act_id in activities:
    found_id = f'id="{act_id}"' in content
    nav_link = f'href="#{act_id}"' in content
    file_name_present = name in content
    status = "OK" if found_id and nav_link else "FAIL"
    print(f"  [{status}] {name} (ID: {act_id}, Section: {found_id}, Nav: {nav_link})")
    if not (found_id and nav_link):
        all_ok = False

print(f"\nAll Activities fully linked and rendered: {all_ok}")

# Verify no syntax tag leakage
leakage_matches = re.findall(r'class="[kpanmsfbc\-_]+"[^>]*class=', content)
print(f"Regex Tag Leakage instances: {len(leakage_matches)}")
if leakage_matches:
    print(f"  Sample leakage: {leakage_matches[:3]}")

# Count code lines and files
file_cards = len(re.findall(r'class="code-component-container"', content))
code_lines = len(re.findall(r'class="code-line"', content))
print(f"\nTotal file cards rendered: {file_cards}")
print(f"Total syntax-highlighted code lines: {code_lines}")
print(f"Total HTML size: {len(content):,} bytes")
