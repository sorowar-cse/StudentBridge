# StudentBridge v4 — Developer Guide (বাংলা)

এই guide Sorowar Mahabub ও দ্বিতীয় team member-এর জন্য। এটি installation, account/key setup, database, প্রতিদিন run, GitHub, deployment, security evidence এবং পরবর্তী expansion এক জায়গায় ব্যাখ্যা করে। VS Code-এ file খুলে `Ctrl+Shift+V` চাপলে সুন্দর preview দেখা যাবে।

## 1. আপনার জন্য নির্ধারিত setup

**Python 3.12 + Streamlit + Groq + Frankfurter + hosted Supabase Auth/PostgreSQL।**

আপনার PC-তে PostgreSQL server, Docker, Node.js বা LLM model download প্রয়োজন নেই। Python app PC-তে চলবে; login ও saved data Supabase-এ থাকবে। Internet প্রয়োজন। Node.js শুধু optional SQL developer tests-এর জন্য।

সর্বোচ্চ **১৫টি enrolled pilot account** database-এ enforce করা আছে। প্রথমে ২টি দিয়ে setup যাচাই করুন, তারপর ১০–১৫টি করুন। এটি capacity/load benchmark নয়; ১৫ জনকে একই সঙ্গে unlimited AI request দেওয়ার প্রতিশ্রুতি নয়।

- Supabase: password login, persistent records, own-account access।
- Groq: দুই model-এর মাধ্যমে পরিকল্পনা/পর্যালোচনা। PC-তে model নামবে না।
- Frankfurter: latest published reference rates; account/key লাগে না।
- Streamlit: user interface; Community Cloud-এ deploy করা যাবে।
- Payments ও wallet: simulation; কোনো bank বা বাস্তব payment integration নেই।

Free plans দিয়ে controlled evaluation করার জন্য design করা হয়েছে। Provider quota, sleeping/paused projects ও service changes প্রযোজ্য। Paid upgrade স্বয়ংক্রিয়ভাবে হয় না; প্রয়োজনে account owner নিজে plan বেছে নেবেন।

## 2. কাজের সঠিক ক্রম

1. ZIP extract ও Python 3.12 নিশ্চিত করুন।
2. Supabase free project তৈরি করুন; public signup বন্ধ করুন।
3. Groq account ও API key নিন।
4. `first_setup_windows.bat` চালান; wizard-এ URL/key দিন।
5. Supabase SQL Editor-এ `supabase/schema.sql` চালান।
6. একই Editor-এ generated `runtime/setup_private.sql` চালান।
7. Supabase dashboard থেকে ২টি confirmed pilot account তৈরি করুন।
8. `run_windows.bat` দিয়ে app চালিয়ে login ও profile save করুন।
9. Connection/security checks করুন; পরে আরও test accounts যোগ করুন।
10. Secret ছাড়া source GitHub-এ দিন।
11. Streamlit Cloud-এ deploy করে generated secrets paste করুন।
12. Local ও online—দুই জায়গায় একই account-এর saved profile যাচাই করুন।

## 3. ZIP কোথায় রাখবেন

ZIP extract করে যেমন `D:\Projects\StudentBridge_v4` folder রাখুন। এই folder-এর ভেতর সরাসরি `app.py` থাকতে হবে। OneDrive/shared/public folder-এর বদলে নিজের private project folder ব্যবহার করুন। v3 আলাদা রাখুন।

| File / folder | কাজ | GitHub-এ যাবে? |
|---|---|---|
| `app.py`, `studentbridge/` | Application | হ্যাঁ |
| `supabase/schema.sql` | Public database schema ও security rules | হ্যাঁ |
| `requirements.txt` | Python dependencies | হ্যাঁ |
| `.env.example` | খালি configuration template | হ্যাঁ |
| `.streamlit/config.toml` | Theme, XSRF/CORS settings | হ্যাঁ |
| `.streamlit/secrets.example.toml` | খালি cloud template | হ্যাঁ |
| `.env` | নিজের keys ও master key | **না** |
| `runtime/setup_private.sql` | Database-এর private signing/audit subkeys | **না** |
| `runtime/cloud_secrets.toml` | Cloud-এ paste করার আসল secrets | **না** |
| `runtime/` | Local private files | **না** |
| `.venv/`, `node_modules/` | Installed dependencies | **না** |
| `data/`, `assets/`, `tests/`, `scripts/` | Public references, team assets, tests | ব্যক্তিগত data না থাকলে হ্যাঁ |
| ব্যক্তিগত PDF, backups, screenshots | User financial information | **না** |

## 4. Python ও VS Code

1. Python 3.12 install করুন; Windows installer-এ Python launcher ও PATH option রাখুন।
2. VS Code → File → Open Folder → `StudentBridge_v4`।
3. Terminal → New Terminal।
4. Check করুন:

```powershell
py -3.12 --version
```

এরপর সবচেয়ে সহজ উপায়: Explorer থেকে `first_setup_windows.bat` double-click করুন। প্রথমবার dependencies install হতে কিছু সময় লাগবে।

Manual equivalent:

```powershell
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe scripts\setup_local.py
```

Virtual environment activate করা বাধ্যতামূলক নয়; উপরের commands সরাসরি সঠিক interpreter ব্যবহার করে। VS Code-এর Python interpreter হিসেবে `.venv\Scripts\python.exe` নির্বাচন করুন।

Mac/Linux equivalent:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python scripts/setup_local.py
.venv/bin/python -m streamlit run app.py --server.address 127.0.0.1
```

## 5. Supabase account ও project

Official site: https://supabase.com/dashboard

1. Sign up/sign in করুন; GitHub দিয়ে করা সহজ।
2. একটি organization এবং নতুন project তৈরি করুন। Free plan নির্বাচন করুন।
3. Project name দিন, যেমন `studentbridge-pilot`।
4. একটি শক্ত database password দিন এবং নিজের password manager-এ রাখুন। App-এ এই database password দিতে হবে না।
5. কাছে available region বেছে project তৈরি হওয়া পর্যন্ত অপেক্ষা করুন।
6. Project-এর **Connect** dialog বা **Settings → API Keys** থেকে নিন:
   - Project URL: `https://YOURPROJECT.supabase.co`
   - **Publishable key**: `sb_publishable_...`
7. **Secret key / service_role key ব্যবহার করবেন না।** App সেগুলো reject করে, কারণ এগুলো RLS bypass করতে পারে। Legacy anon key supported হলেও নতুন publishable key-ই ব্যবহার করুন।
8. **Authentication → Sign In / Providers** বা Authentication settings-এ **Allow new users to sign up / Enable sign ups** বন্ধ করুন। Dashboard-এর menu label বদলালে সংশ্লিষ্ট Auth setting খুঁজুন।
9. Email/password provider enabled রাখুন।

এই pilot-এ account টিম তৈরি করবে। তাই user signup email, magic link, redirect callback বা custom SMTP প্রয়োজন নেই। Dashboard দিয়ে confirmed account তৈরি করা email ownership-এর স্বাধীন যাচাই নয়; এগুলো নিয়ন্ত্রিত test accounts।

Supabase-এর default email service arbitrary ১৫টি email-এর production mail solution নয়। ভবিষ্যতে public signup/password-email চালু করলে custom SMTP, verification, CAPTCHA ও recovery flow যোগ করতে হবে। শুধু signup toggle খুলে দেওয়া যথেষ্ট নয়।

## 6. Groq account, key এবং models

1. https://console.groq.com/ এ sign up/sign in করুন।
2. https://console.groq.com/keys → Create API Key।
3. নাম দিন `StudentBridge-local`। Key privately copy করুন।
4. Console-এর Limits ও Usage দেখুন। প্রথমে paid upgrade প্রয়োজন ধরে নেবেন না।
5. Setup wizard যখন চাইবে তখন key paste করুন। Hidden input-এ টাইপ/paste দেখা না যাওয়াটা স্বাভাবিক; paste করে Enter দিন।

Default models:

```text
Planner:  openai/gpt-oss-20b
Reviewer: openai/gpt-oss-120b
```

এগুলো Groq-hosted model IDs। OpenAI account/key বা local model download প্রয়োজন নেই। উপলব্ধ model ও structured-output support provider-এর হাতে; Guide-এর **List available models** দিয়ে নিজের account-এ যাচাই করুন।

একটি reviewed AI task দুইটি model call করতে পারে। StudentBridge-এর cloud allowance: প্রতি user ২০টি task/day, সব user মিলিয়ে ১০০টি task/day এবং সব user মিলিয়ে সর্বোচ্চ ৩টি task/minute। এগুলো UTC day ধরে এবং failed attempts-ও count করে। Groq-এর limits আরও কম হতে পারে। Quota শেষ হলে অপেক্ষা করুন অথবা built-in assistant/calculators ব্যবহার করুন। কোনো paid fallback নেই।

## 7. Setup wizard কী তৈরি করে

Run করুন `first_setup_windows.bat`, অথবা:

```powershell
.\.venv\Scripts\python.exe scripts\setup_local.py
```

- Backend প্রশ্নে Supabase-এর জন্য Enter দিন।
- Supabase URL দিন।
- Publishable key দিন; hidden input।
- Groq key দিন; hidden input। এখন না দিলে পরে যোগ করা যাবে।

Wizard তৈরি করবে:

1. `.env`: PC-র configuration।
2. `runtime/setup_private.sql`: signing/audit subkeys database-এ বসানোর SQL।
3. `runtime/cloud_secrets.toml`: online deployment-এর ready-to-paste configuration।

**Master key একবার তৈরি হয়। একই key PC, database configuration এবং cloud app-এর জন্য সংরক্ষণ করতে হবে।** Setup আবার চালালে existing `.env` থাকলে Enter দিয়ে আগের values রাখা যায়; master key অপরিবর্তিত থাকে। `.env` মুছে নতুন wizard চালিয়ে আগের encrypted data উদ্ধার করা যাবে না।

Master key server-side AES encryption-এর জন্য ব্যবহৃত হয়। Private SQL-এ পুরো master/encryption key যায় না; শুধু আলাদা signing ও audit subkeys যায়। তিনটি generated file private। Project/PC বদলানোর আগে `.env`-এর নিরাপদ backup রাখুন।

পরে শুধু Groq key বদলালে `.env` এবং `runtime/cloud_secrets.toml`-এ একই পরিবর্তন করুন, অথবা wizard-এ নতুন Groq key দিয়ে Enter দিয়ে অন্য fields রাখুন। Cloud dashboard-এর Secrets আলাদাভাবে update করতে হবে।

## 8. Database setup: দুইটি SQL, সঠিক ক্রমে

Supabase project → **SQL Editor → New query**।

### প্রথম SQL

VS Code-এ `supabase/schema.sql` খুলে পুরো content copy → SQL Editor-এ paste → **Run**।

এটি tables, RLS policies, bounded RPCs, ১৫-account cap, atomic simulated ledger এবং AI allowance তৈরি করে। নিজে কোনো RLS policy বন্ধ করবেন না। App-এর RPC security-definer functions owner privileges ব্যবহার করে; সেগুলোর ভেতরে user ID, roles ও limits enforce করা আছে।

### দ্বিতীয় SQL

নিজের generated `runtime/setup_private.sql` খুলে পুরো content copy → নতুন query → **Run**।

এই file অন্য কাউকে দেবেন না এবং public repository-তে রাখবেন না। Supabase SQL Editor history-তেও এটি sensitive administrative configuration হিসেবে বিবেচিত হবে।

ভুল project-এ SQL চালিয়েছেন কি না নিশ্চিত করুন। `schema.sql` পুনরায় চালানো data মুছে দেয় না। Private SQL অন্য existing key পেলে ইচ্ছাকৃতভাবে বন্ধ হবে; matching original `.env` ফেরত আনুন। Working database-এর key জোর করে replace করবেন না।

## 9. ২টি থেকে ১৫টি pilot account তৈরি

Supabase → **Authentication → Users → Add user → Create new user**। UI label সামান্য বদলাতে পারে।

প্রতি account-এর জন্য:

1. আলাদা email দিন—নিজেদের controlled email ব্যবহার করুন।
2. আলাদা ১২+ অক্ষরের temporary password দিন।
3. **Auto Confirm User / Email confirmed** option থাকলে enable করুন।
4. Create করুন। Invitation email পাঠানোর option প্রয়োজন নেই।
5. Password privately সংশ্লিষ্ট tester-কে দিন। Repository, issue, shared screenshot বা public chat-এ দেবেন না।

App-এ first successful sign-in-এর সময় account enroll হবে। **সর্বোচ্চ ১৫টি enrolled member**। Auth dashboard-এ অতিরিক্ত account থাকলেও cap পূর্ণ হলে নতুন enrollment হবে না। নতুন account-এর default role `executor`: শুধু simulated transfer execute করতে পারে।

Permission tiers দেখাতে user একবার sign in করার পর SQL Editor-এ role বদলাতে পারেন:

```sql
update public.sb_members
set role = 'viewer'
where user_id = 'PASTE_THE_USERS_UUID_HERE';
```

অন্য values: `planner`, `executor`।

- Viewer: read, calculate, নিজের profile; executable quote/transfer/top-up নয়।
- Planner: উপরের সঙ্গে signed quote তৈরি; transfer/top-up নয়।
- Executor: উপরের সঙ্গে explicit confirmation দিয়ে sandbox transfer ও simulated top-up।

Role user profile/metadata থেকে নেওয়া হয় না; user নিজে database role বদলাতে পারে না।

Password ভুলে গেলে এই controlled pilot-এ owner Supabase Users dashboard থেকে reset/update করবেন। Dashboard-এ সরাসরি password update action না থাকলে নিচের owner-only utility ব্যবহার করুন; public recovery email flow এই সংস্করণে নেই। নতুন password দিয়ে sign in-এর পরে Account & Privacy থেকে current password যাচাই করে password বদলানো যায়। সম্পূর্ণ account delete করতে Auth Users dashboard-এর delete action ব্যবহার করুন; foreign keys সংশ্লিষ্ট app records cascade delete করে। আগে প্রয়োজনীয় নিজের evidence export করুন।

### Email ছাড়াই owner-এর create/reset utility

Dashboard থেকে account তৈরি করাই প্রথম পছন্দ। Password reset-এর জন্য PC-তে এই command দিন:

```powershell
.\.venv\Scripts\python.exe scripts\cloud_account_admin.py reset-password
```

- Supabase **Settings → API Keys** থেকে owner-এর **secret key** নিন। এটি app-এর publishable key থেকে আলাদা।
- শুধু এই local terminal-এর hidden prompt-এ secret key দিন। `.env`, generated SQL/TOML, Streamlit Secrets, GitHub বা chat-এ এটি রাখবেন না। Utility key সংরক্ষণ করে না এবং app এটি import করে না।
- Authentication → Users থেকে target user-এর UUID দিন। Script email দেখাবে; সঠিক person কি না মিলিয়ে নিন।
- নতুন ১২+ অক্ষরের password দুইবার দিন।
- Target email লিখে action confirm করুন। এরপর user-কে নতুন password privately দিন।

Dashboard account creation unavailable হলে একই utility-তে:

```powershell
.\.venv\Scripts\python.exe scripts\cloud_account_admin.py create
```

এতে owner-confirmed test account তৈরি হবে, email পাঠানো হবে না। এটি সাধারণ app ব্যবহারকারীর feature নয়। Privileged key app runtime-এর বাইরে রাখার জন্য utility আলাদা করা হয়েছে। Supabase Auth API owner action-এর authority দেয়; direct `auth.users` table edit করা হয় না। Network error হলে dashboard দেখে নিন—দ্বিতীয়বার create চাপার আগে প্রথমটি সফল হয়েছিল কি না যাচাই করুন।

## 10. প্রথমবার app চালিয়ে যাচাই

`run_windows.bat` double-click করুন। অথবা:

```powershell
.\.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Browser-এ terminal-এর local URL খুলুন; সাধারণত http://localhost:8501 ।

1. Sidebar-এ **Cloud storage · Supabase** দেখুন।
2. Supabase-এ তৈরি email/password দিয়ে sign in করুন।
3. **My Student Profile** খুলুন। University/department/programme/location লিখুন।
4. নিজের invoice-এর প্রযোজ্য tax-সহ tuition total ও currency, **পরবর্তী unpaid due date**, actual billing interval দিন। Personal forecast আলাদা tax হিসাব করে না।
5. মাসিক rent/food/transport/utilities/other, savings, confirmed income/funding দিন।
6. Planning start ও months দিন। Buffer, living-cost growth ও FX stress নিজের assumptions অনুযায়ী দিন।
7. Confirmation tick → Save my profile।
8. **My Forecast → Calculate from my saved profile**।
9. Total, funding gap, monthly table এবং largest monthly cash shortfall দেখুন।
10. Sign out করে পুনরায় sign in করুন; profile ফিরেছে কি না দেখুন।

University name ইত্যাদি English-এ দিলে English PDF-এ typography সবচেয়ে নির্ভরযোগ্য। UI চার ভাষায় আছে; user-entered text automatic translation হয় না।

### Groq চালু করা

Guide for User → Connections & calculation settings:

- Exchange-rate source: **Published reference rates**।
- AI engine: **Groq · cloud**।
- Models: উপরের default IDs, নিজের account-এ available হলে।
- Cloud consent পড়ে tick দিন।

Profile-based AI priority review শুধু numeric summary ও generic study context পাঠায়; email, university name, department, private note বাদ থাকে। অন্য প্রশ্নে নিজে sensitive data লিখবেন না। Session নতুন হলে consent আবার দিতে হবে।

## 11. দ্বিতীয়বার বা পরের দিন চালানোর নিয়ম

প্রতিবার account তৈরি, SQL run, model download বা dependencies install করতে হবে না।

1. Internet চালু করুন।
2. Supabase project paused থাকলে dashboard থেকে resume করুন।
3. `StudentBridge_v4` folder-এর `run_windows.bat` double-click করুন।
4. আগের account দিয়ে sign in করুন।
5. প্রয়োজন হলে Guide-এ Groq consent দিন।
6. কাজ শেষ হলে sign out; terminal-এ `Ctrl+C`।

Online deploy হয়ে গেলে শুধু app URL খুললেই হবে; আপনার PC-তে terminal চালু রাখতে হবে না। Free hosting sleep করলে wake হতে সময় লাগতে পারে।

## 12. Connection ও security checks

প্রথমে read-oriented connection check:

```powershell
.\.venv\Scripts\python.exe scripts\doctor.py
```

নিজের test account দিয়ে membership/RPC-ও check করতে:

```powershell
.\.venv\Scripts\python.exe scripts\doctor.py --login
```

এই দ্বিতীয় command first login হলে pilot account enroll করতে পারে। Password command argument-এ যায় না; prompt-এ hidden input দিন। Doctor model catalogue দেখে, paid inference call চালায় না।

Python regression tests:

```powershell
.\.venv\Scripts\python.exe -m pytest -q
```

Offline synthetic benchmark:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py --provider offline
```

Live FX check:

```powershell
.\.venv\Scripts\python.exe scripts\smoke_live_fx.py
```

Groq evaluation প্রথমে ছোট রাখুন; এটি real API quota ব্যবহার করে এবং app-এর interactive task allowance-এর বাইরে developer-controlled calls:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate.py --provider groq --allow-cloud --max-cases 3 --pause 30
```

তিনটি task-এ সর্বোচ্চ দুই model করে ছয়টি call হতে পারে; quota এখনও provider অনুযায়ী। Errors-কে accuracy হিসেবে লুকানো হবে না।

### নিজের hosted Supabase-এর isolation পরীক্ষা

দুটি **নতুন, blank, dedicated synthetic test account** তৈরি করুন। এগুলোও ১৫-member cap-এর মধ্যে পড়বে।

```powershell
.\.venv\Scripts\python.exe scripts\check_cloud_security.py
```

Script-এর সতর্কতা পড়ে `SYNTHETIC` লিখুন। এটি A-র একটি synthetic marker save করে B/anonymous read এবং direct role update denial পরীক্ষা করে, শেষে marker মুছে দেয়। Existing saved profile/plan পেলে শুরু করবে না। Output: `evaluation/cloud_security_private.json`—নিজে দেখে sanitized copy প্রয়োজনে evidence হিসেবে দিন। Emails/passwords/tokens output-এ রাখা হয় না।

### ১০–১৫ account-এর জন্য ready synthetic profile inputs

`data/profile_test_cases.json`-এ P01–P15 এবং `data/profile_test_expected.csv`-এ expected totals আছে। Institution নাম reference catalogue থেকে এসেছে, কিন্তু **সব amount বানানো test data**; official tuition বলে ব্যবহার করবেন না।

নিজের blank dedicated test account-এ একটি case বসাতে:

```powershell
.\.venv\Scripts\python.exe scripts\load_pilot_profile.py --case P01
```

Warning পড়ে `SYNTHETIC` লিখুন, তারপর সেই account-এর email/password দিন। Existing saved profile/plan থাকলে overwrite করবে না। App-এ ওই account দিয়ে My Forecast খুলে Calculate করুন এবং CSV-এর expected total/resources/gap মিলিয়ে দেখুন। পরের account-এ P02, তারপর P03 ইত্যাদি ব্যবহার করতে পারেন। এগুলোও ১৫-account cap-এর মধ্যে থাকবে।

Test set আবার generate করতে:

```powershell
.\.venv\Scripts\python.exe scripts\generate_profile_cases.py
```

এতে কোনো cloud account তৈরি বা LLM training হয় না। পুরোনো conversion/adversarial test set-এর জন্য `scripts/generate_test_set.py`-ও রাখা আছে।

### Optional: database rules-এর local developer test

এটি app চালানোর জন্য প্রয়োজন নেই। Node.js install করা থাকলে project root-এ:

```powershell
npm ci
npm run test:sql
```

এতে WASM PostgreSQL + pgcrypto দিয়ে আসল SQL/RLS functions পরীক্ষা হয়; Supabase Auth token validation-এর বদলে test claim stub থাকে। Hosted Supabase, internet authentication বা true multi-process load test হিসেবে এই ফল দাবি করবেন না।

## 13. GitHub upload

GitHub account ও GitHub Desktop:

- https://github.com/signup
- https://desktop.github.com/download/

1. GitHub Desktop-এ sign in করুন।
2. File → New repository → `studentbridge` তৈরি করুন।
3. Repository-এর local folder-এ project-এর **ভেতরের source files** কপি করুন। Root-এ `app.py` থাকবে। `.gitignore`-ও কপি করবেন।
4. Change list-এ `.env`, `runtime/`, database, real PDFs, secrets, `.venv/`, `node_modules/` নেই নিশ্চিত করুন। Git ignore Windows Explorer copy-তে file আটকায় না; Git-এর change list থেকে যাচাই করুন।
5. `Add StudentBridge v4` message দিয়ে Commit to main।
6. Publish repository। প্রথমে private রাখতে পারেন। Judges/source sharing-এর জন্য public করলে শুধু sanitized source দিন।
7. পরের update: Commit → Push origin।

একটি secret accidental commit হলে key revoke/rotate করুন; শুধু latest file delete করলে Git history থেকে যায় না। Master key leak হলে existing encrypted profile data exposure-ও বিবেচনা করতে হবে; এটি সাধারণ Groq key rotation-এর মতো নয়।

## 14. Streamlit Community Cloud deployment

Official deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy

1. GitHub-এ source push হয়েছে নিশ্চিত করুন।
2. https://share.streamlit.io/ এ GitHub দিয়ে sign in/connect করুন।
3. Create app → repository → branch `main`।
4. Main file path: `app.py`।
5. Advanced settings → Python **3.12** নির্বাচন করুন।
6. নিজের generated `runtime/cloud_secrets.toml` খুলুন। এর content **Streamlit-এর Secrets box-এ** paste করুন। File GitHub-এ দেবেন না।
7. এতে `STUDENTBRIDGE_BACKEND="supabase"` ও `STUDENTBRIDGE_DEPLOYMENT="cloud"` থাকবে। Master key local setup-এর সঙ্গে **একই** হবে। Values root level-এ থাকবে; `[groq]`/`[supabase]` section বানাবেন না।
8. App subdomain available হলে নির্বাচন করুন → Deploy।
9. Build logs দেখুন; dependencies install হতে সময় লাগতে পারে।
10. Deployed URL খুলে নিজের pilot account দিয়ে login করুন। Sidebar-এ Cloud storage নিশ্চিত করুন।
11. PC-তে saved profile online-এ দেখা যাচ্ছে কি না দেখুন। Online-এ ছোট পরিবর্তন save করে PC-তে sign in করেও মিলিয়ে নিন।
12. Browser-এর আলাদা private/incognito session-এ B account দিয়ে A-র profile, budget ও wallet দেখা যাচ্ছে না নিশ্চিত করুন।
13. Streamlit reboot/redeploy-এর পরও profile Supabase-এ থাকবে। একটি browser/session refresh হলে পুনরায় sign in লাগতে পারে; browser refresh-এর পর permanent login cookie এই সংস্করণে নেই।

Cloud mode-এ local fallback নেই। Supabase বা master key ভুল হলে configuration/connection error দেখাবে; খালি local database তৈরি করে সফল login দেখাবে না। Community Cloud-এর local disk-এ user data স্থায়ীভাবে রাখার ওপর নির্ভর করা হয়নি।

Cloud-এ নিজের PC-র Ollama ব্যবহার করবেন না। এই configuration-এ cloud UI Ollama option সরায়। Groq ব্যবহার করুন।

### Live link GitHub-এ দেখানো

Deploy হওয়ার পরে আসল URL দিয়ে README-তে যোগ করুন:

```markdown
## Live application
[Open StudentBridge](https://YOUR-APP-NAME.streamlit.app)
```

GitHub repository-এর About → Website-এ একই URL দিন। GitHub Pages এই Python app চালাবে না; Streamlit Cloud app চালাবে।

### পরবর্তী online update

1. Local code edit করুন।
2. Tests চালান।
3. GitHub Desktop-এ Commit → Push origin।
4. Streamlit app update/rebuild হচ্ছে কি না দেখুন।
5. শুধু key/config বদলালে Streamlit Settings → Secrets update করে reboot দিন। Code-এ আসল key লিখবেন না।
6. Schema change হলে reviewed migration SQL আলাদাভাবে Supabase-এ চালাতে হবে; Git push SQL নিজে চালায় না।

## 15. Competition walkthrough ও evidence

`docs/COMPETITION_ALIGNMENT.md` এবং `docs/SECURITY_DESIGN.md` পড়ুন।

একটি practical session:

1. A account → profile → forecast → source/date → PDF।
2. B account → A-র data না থাকা দেখান।
3. Converter-এ BDT→CNY এবং CNY→MYR published reference।
4. Wallet-এ explicit simulated funds যোগ করুন।
5. Transfers-এ ছোট amount compare → signed quote → approval checkbox ও final six characters → execute।
6. একই quote আবার execute করলে original receipt ও replay flag আসে; দ্বিতীয় debit হয় না।
7. Viewer account থেকে execute/top-up unavailable দেখান।
8. SQL security tests দিয়ে expiry, tampering, limits ও audit checks-এর evidence দেখান।
9. Wallet & Audit থেকে PDF statement export করুন।
10. Groq enabled থাকলে একটি reviewed AI question এবং একটি profile priority review দেখান।

Video/presentation/report পরে final project review-এর পর তৈরি হবে। এখনকার docs operational documentation; এগুলো পূর্ণ final submission report নয়। Competition brief-এ সাধারণ demo video optional বলা হলেও non-on-chain execution evidence-এ sandbox logs ও demo video-র উল্লেখ আছে; নিরাপদ প্রস্তুতি হিসেবে পরবর্তীতে পাঁচ মিনিটের মধ্যে video রাখুন।

## 16. সাধারণ সমস্যা ও সমাধান

| সমস্যা | কী করবেন |
|---|---|
| `py` command নেই | Python 3.12 ও launcher install করে terminal নতুন করে খুলুন |
| `ModuleNotFoundError` | `.venv` interpreter দিয়ে requirements install করেছেন কি না দেখুন |
| Hidden key input-এ কিছু দেখা যায় না | স্বাভাবিক; paste করে Enter দিন |
| Configuration incomplete | URL/publishable key/master key যাচাই; wizard সম্পন্ন করুন |
| Login হচ্ছে না | Auth user তৈরি, confirmed, password, schema ও private SQL, project paused কি না, cap পূর্ণ কি না দেখুন |
| Supabase-এ user আছে, app-এ নেই | First successful login-এ member enroll হয়; key SQL ও cap check করুন |
| Profile integrity failed | Local/cloud master key একই করুন; নতুন random key দিয়ে আগের data খোলা যাবে না |
| Quote signature mismatch | `.env`-এর master key ও private SQL-এর signing subkey একই setup-এর কি না দেখুন |
| Groq `401` | Key ভুল/revoked; `.env` বা Cloud Secrets update ও restart |
| Groq `429` / app allowance | অপেক্ষা করুন; built-in mode-এ calculations চালান |
| Model unavailable | Model list ও structured-output support দেখুন |
| FX unavailable | Internet/provider retry; নিজে Guide থেকে illustrative offline mode বেছে নিতে পারেন; সেটিকে current market rate বলবেন না |
| FX observations have different dates | Composite quote/forecast বন্ধ থাকবে; পরে retry বা একই budget currency-র scenario ব্যবহার করুন |
| Cloud entry file পাওয়া যাচ্ছে না | Repo root-এ `app.py`, ZIP upload নয়; nested হলে সঠিক path দিন |
| Cloud data empty | একই Supabase project ও account ব্যবহার করছেন কি না দেখুন; local preview-র data cloud-এ auto migrate হয় না |
| App ঘুমিয়ে আছে/slow start | Free hosting wake হওয়া পর্যন্ত অপেক্ষা করুন; presentation-এর আগে open/check করুন |
| Database paused | Supabase dashboard-এ resume করুন |
| SQL relation not found | প্রথমে public schema.sql, এরপর private setup SQL চালান |
| Account profile delete-এর পর receipt আছে | এটি intended scope; পুরো account delete owner dashboard থেকে করতে হবে |

## 17. v3 থেকে কীভাবে যাবেন

v3 working folder ও runtime-এর private backup আলাদা রাখুন। v4 ZIP নতুন folder-এ extract করুন। v3-এর `.env` অন্ধভাবে overwrite/copy করবেন না; v4 wizard দিয়ে Supabase fields যোগ করুন।

Supabase account IDs এবং পুরোনো SQLite user IDs আলাদা। **v3 local data cloud-এ auto migrate হয় না।** এই ছোট pilot-এর জন্য নতুন cloud accounts-এ নিজের profile পুনরায় দেওয়া সহজ ও নিরাপদ। v4 local-preview mode পুরোনো local Store schema পড়তে পারে, কিন্তু এটিকে cloud migration বলে দাবি করবেন না।

## 18. পরে Pro plan ও বেশি users

Provider plan upgrade application scale test-এর বিকল্প নয়। পরে এই ক্রমে কাজ করবেন:

1. Supabase/Groq/hosting-এর বর্তমান quota ও billing দেখে প্রয়োজনীয় plan নিন।
2. Reviewed SQL দিয়ে `sb_private.settings.member_limit` বাড়ান। উদাহরণ:

```sql
update sb_private.settings
set member_limit = 100,
    ai_user_daily = 50,
    ai_global_daily = 1000,
    ai_global_minute = 10
where singleton;
```

এটি শুধু configuration example; provider quota যাচাই ছাড়া সরাসরি বেশি limit দেবেন না।

3. Public signup চাইলে SMTP, verified email flow, abuse controls, CAPTCHA, password recovery ও প্রয়োজনীয় migrations তৈরি করুন। এই pilot-এর signup closed রাখুন যতক্ষণ তা হয়নি।
4. Backup/restore, monitoring, retention, support ও incident handling যোগ করুন। Free plan-এ automatic backups অন্তর্ভুক্ত ধরে নেবেন না।
5. Realistic concurrent users দিয়ে latency, memory, rate-limit ও database transaction test করুন। Heavy work-এর জন্য job queue/worker এবং প্রয়োজন হলে Streamlit-এর বাইরে API service বিবেচনা করুন।
6. বাস্তব remittance/payments যোগ করার আগে licensed provider integration ও সংশ্লিষ্ট operational/legal requirements আলাদাভাবে নির্ধারণ করুন।

## 19. Official references

Setup checks: 16 October 2026. Provider UI/limits পরে বদলাতে পারে।

- Supabase API keys: https://supabase.com/docs/guides/getting-started/api-keys
- Supabase password auth: https://supabase.com/docs/guides/auth/passwords
- Supabase RLS: https://supabase.com/docs/guides/database/postgres/row-level-security
- Supabase SMTP limitations: https://supabase.com/docs/guides/auth/auth-smtp
- Supabase plan limits: https://supabase.com/pricing
- Groq quickstart: https://console.groq.com/docs/quickstart
- Groq models: https://console.groq.com/docs/models
- Groq limits: https://console.groq.com/docs/rate-limits
- Frankfurter: https://frankfurter.dev/
- Streamlit deployment: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/deploy
- Streamlit secrets: https://docs.streamlit.io/deploy/streamlit-community-cloud/deploy-your-app/secrets-management
- Streamlit local-file persistence: https://docs.streamlit.io/develop/concepts/connections/connecting-to-data
- GitHub Desktop: https://docs.github.com/en/desktop/overview/creating-your-first-repository-using-github-desktop
- Competition announcement: https://ird.oou.cmu.ac.th/2026-shenzhen-international-fintech-competition/
- Detailed brief linked by CMU: https://drive.scmc.cmu.ac.th/s/2jKErkTJpFmcxYF
