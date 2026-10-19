# StudentBridge v4 — UI refresh

This update improves the existing Streamlit interface. It adds warm ivory input
surfaces, visible borders, a slow red/gold border animation on the active field,
clearer cards and buttons, and placeholders in English, Bangla, Chinese and Malay.
The visitor's reduced-motion preference disables the animation.

## Step 12/15 — প্রথমে PC-তে update দিন

1. VS Code-এর terminal-এ app চললে **Ctrl+C** দিয়ে বন্ধ করুন।
2. Repository-এর বাইরে একটি backup folder-এ বর্তমান নিচের তিনটি ফাইল কপি রাখুন:
   `app.py`, `assets/theme.css`, `studentbridge/profile_ui.py`।
3. `StudentBridge_v4_UI_Refresh.zip` unzip করুন। ZIP-এর ফাইলগুলো আপনার
   **StudentBridge repository root**-এ merge/copy করুন। Windows replace করতে
   বললে ওই ফাইলগুলো replace করুন। নতুন `StudentBridge_v4_UI_Refresh` নামে
   nested folder বানিয়ে তার মধ্যে app রাখবেন না।
4. Repository root-এ এই structure মিলিয়ে নিন:

   ```text
   StudentBridge/
     app.py
     assets/theme.css
     studentbridge/profile_ui.py
     studentbridge/ui_hints.py
     docs/UI_REFRESH.md
   ```

   `ui_hints.py` নতুন ফাইল; সেটিও অবশ্যই কপি করতে হবে। Folder merge করবেন;
   পুরো `assets` বা `studentbridge` folder মুছে replace করবেন না।

5. VS Code-এ repository root-এর PowerShell terminal থেকে চালান:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

   নতুন package install করার প্রয়োজন নেই। `.env`, Cloud Secrets, database বা
   encryption key পরিবর্তন করার প্রয়োজন নেই।

6. Browser-এ local app খুলে দেখুন:

   - Login-এর ঘরগুলোর border ও background স্পষ্ট দেখা যায়।
   - কোনো ঘরে click করলে red/gold focus border দেখা যায়। Tab key দিয়েও focus
     পরিষ্কার থাকে। OS-এ reduced motion চালু থাকলে animation বন্ধ থাকবে।
   - Login করে আপনার আগের saved profile দেখা যায়; তথ্য নিজে থেকে বদলায় না।
   - খালি profile field-এ example দেখা যায়। Filled field-এ নিজের তথ্যই থাকে।
   - Currency converter-এ খালি amount field-এ `e.g. 100` দেখা যায়।
   - Dropdown, date, number এবং note field ব্যবহার করা যায়।
   - Language বদলালে খালি field-এর placeholder-ও বদলায়।
   - `Convert 100 MYR to CNY`, forecast ও PDF download আগের মতো কাজ করে।
   - Browser-এর সরু window/phone view-এ form ব্যবহারযোগ্য থাকে।

## Local check ঠিক হলে GitHub ও live app update

1. GitHub Desktop-এ **StudentBridge** repository খুলুন। এই update-এ বদলানোর
   ফাইল মাত্র পাঁচটি: উপরের tree-এর ফাইলগুলো। অন্য uncommitted পরিবর্তন
   থাকলে আলাদা করে review করুন।
2. `.env`, `.venv`, `runtime`, `.streamlit/secrets.toml`, private cloud evidence,
   database, private keys বা backup file select/commit করবেন না। Gitignore-এর
   আগের protection রাখুন।
3. Summary লিখতে পারেন: `Polish input fields and add multilingual placeholders`।
4. **Commit to main**, তারপর **Push origin** করুন।
5. Streamlit deployment-এ একই `main` branch ও root `app.py` ব্যবহৃত হলে নতুন
   code থেকে app update হওয়ার কথা। Deploy শেষ হলে live app refresh করুন।
   পুরোনো styling দেখালে browser-এ **Ctrl+F5** দিন। প্রয়োজন হলে নিজের
   Streamlit dashboard থেকে app-এর status/log দেখে **Reboot app** করুন।
6. Live app-এ login, saved profile, converter, forecast এবং PDF আবার একবার
   check করুন। Unsaved form text থাকলে refresh/reboot-এর আগে save করুন।

Live address: https://studentbridge.streamlit.app/

## Scope and verification

- Changed files: the five files in the tree above. There are no new dependencies.
- Account data, member metadata, keys, fees, model configuration, calculations,
  permissions, approval checks and database schema are outside this update.
- Existing widget keys and values were retained. Placeholders are display-only
  examples; they are never financial defaults and never save themselves.
- Existing test suite: **227 passed in 30.79 seconds** on the local synthetic
  test environment, including the existing four-language UI workflows.
- Python AST comparison confirmed that the existing application logic matches
  the previous corrected v4 after excluding presentation-only additions.
- Widget wrappers were checked against the deployed login/settings DOM and
  installed Streamlit 1.65 frontend source. CSS uses stable widget identifiers.
- A real browser rendering of the patched app could not be completed in the
  build environment. Local/phone appearance and the final deployed rendering
  still need the visual checks above. These tests do not represent a new live
  Groq, Supabase or FX connection test.

## Roll back if needed

Restore the three backed-up files, remove the new `studentbridge/ui_hints.py`
only if nothing else imports it, and run the app again. To roll back online,
commit and push the restored files, or revert the UI commit in GitHub Desktop.
Leave account secrets and encryption keys as they are.
