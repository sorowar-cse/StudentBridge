# Third-party components and data

StudentBridge integrates existing components; it does not claim to have invented their underlying algorithms or trained the hosted LLMs.

- Streamlit: https://github.com/streamlit/streamlit
- Supabase Auth/PostgreSQL and documented REST APIs: https://supabase.com/docs
- Groq hosted models/API: https://console.groq.com/docs; service/model terms apply to use.
- Frankfurter reference data/API: https://frankfurter.dev/; observations are attributed in the application.
- scikit-learn Isolation Forest, TF-IDF and similarity: https://scikit-learn.org/
- Python dependencies are declared in `requirements.txt`; retain their upstream licenses when redistributing binaries/vendor packages.
- DejaVu fonts are bundled in `assets/fonts/` with their original license file.
- Optional SQL verification uses PGlite PostgreSQL/pgcrypto: https://github.com/electric-sql/pglite, pinned in `package-lock.json`. Node modules are not bundled.
- University reference records include original official-source URLs and checked dates in `data/universities.json`. Fee applicability must be verified for the student's actual programme/status.
- `data/demo_fx.json`, generated conversion questions and `data/profile_test_cases.json` use synthetic testing values. They are not market rates or official fees.
- Team photographs/contact details are supplied/replaceable by the team. Obtain the appropriate permission before publishing them.

The top-level project LICENSE applies to the original application code; it does not replace upstream licenses or service terms. All model/provider names are attribution, not endorsement.
