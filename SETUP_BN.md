# StudentBridge v4 setup

সম্পূর্ণ updated নির্দেশনা: [DEVELOPER_GUIDE_BN.md](DEVELOPER_GUIDE_BN.md)।

প্রথমবার: Python 3.12 → Supabase project → Groq key → `first_setup_windows.bat` → public schema SQL → generated private SQL → pilot accounts → `run_windows.bat`।

পরেরবার: `run_windows.bat` → sign in। SQL/account/dependencies প্রতিদিন নতুন করে লাগবে না।

Recommended cloud setup-এ `.env`-এর `STUDENTBRIDGE_BACKEND=supabase` থাকবে। API key, master key ও `runtime/` GitHub-এ দেবেন না।

শুধু account ছাড়াই local preview চাইলে setup wizard-এ `local` নির্বাচন করুন; সেটি cloud persistence বা Supabase login যাচাই করে না।
