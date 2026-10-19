# StudentBridge — team details update (Step 13/15, part A)

Requires the v4 UI refresh already applied and checked.

## Apply

1. Close the local app with Ctrl+C if it is running.
2. Keep a backup of `app.py` and `data/team.json` outside the repository.
3. Unzip this package and merge its files into the repository root (where
   `app.py` is located). Replace the included existing files; retain all other files.
4. If you have the second member's photo, save a real PNG as
   `assets/team/member2/profile.png`. The filename must be exactly lowercase
   `profile.png`. Convert/export to PNG; do not only rename a JPG extension.
   Without a photo, the app displays HH from the member's name.
5. Run from the repository root in PowerShell:

   ```powershell
   .\.venv\Scripts\python.exe -m streamlit run app.py
   ```

6. Open Developers and confirm the two names, academic details, email, phone
   and photos. The leader's existing metadata and image path are retained.
7. In GitHub Desktop, review `app.py`, `data/team.json`, `tests/test_app.py`,
   this instruction file, and the optional `assets/team/member2/profile.png`. Commit with
   `Update team member details`, then Push origin.
8. Refresh the live app and check Developers again.

## Included professional details

- Dr. Hasniza bt Hambali
- PhD · Year 3
- Faculty of Engineering & Built Environment (FKAB)
- Universiti Kebangsaan Malaysia (UKM)
- p145746@siswa.ukm.edu.my
- +60 12-305 5841

No age, gender or separate student-ID field is added. No WhatsApp capability is
assumed for this member. Her supplied phone number is shown as contact text.

## Changes

- `data/team.json`: replaces the second member's placeholder metadata.
- `app.py`: derives photo-fallback initials from the member's name, with HTML
  escaping. The existing UI refresh and application logic are retained.
- `tests/test_app.py`: the existing public developer-page check reads the
  configured member names instead of requiring the old XXXXYYYY placeholder.
- `docs/TEAM_UPDATE.md`: this guide.

There are no dependency, secret, account, database, model or calculation changes.
Keep `.env`, `.venv`, `runtime`, `.streamlit/secrets.toml`, private evidence,
databases, keys and backup files out of GitHub as before.

## Validation

Full existing test suite on the updated local source: **227 passed in 30.25s**.
These tests use synthetic/local fixtures, not new calls to the hosted accounts.
