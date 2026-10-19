# Upgrade from v3 to v4

Keep v3 and its private runtime backup separate. Extract v4 into a new folder. Use the v4 setup wizard; do not overwrite its configuration with an unchanged v3 `.env`.

Supabase accounts use different identities from local SQLite accounts. No automatic local-to-cloud account/profile migration is claimed. For the small competition pilot, create fresh controlled cloud accounts and re-enter confirmed profile data.

The local storage format remains compatible with v3, and new student-profile tables are created when local mode opens an existing Store. Only point local mode at a private COPY of an old runtime directory; cloud mode does not use that directory.

Preserve the generated v4 master key for every later local/cloud run. Model/FX settings, profile/forecast workflow and Cloud Secrets instructions are documented in `DEVELOPER_GUIDE_BN.md`.
