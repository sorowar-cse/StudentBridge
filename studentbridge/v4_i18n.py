"""Complete rows for the v4 profile/account workflow; no translation API."""

EXTRA_ROWS = """
account_enrolled|Pilot account enrolled|Test account যুক্ত হয়েছে|测试账户已加入|Akaun rintis didaftarkan
student_profile_saved|Student profile saved|শিক্ষার্থী profile সংরক্ষিত|学生资料已保存|Profil pelajar disimpan
personal_profiles_deleted|Saved profiles deleted|Saved profile মুছে গেছে|已删除保存的资料|Profil tersimpan dipadam
profile|My Student Profile|আমার শিক্ষার্থী প্রোফাইল|我的学生资料|Profil pelajar saya
forecast|My Forecast|আমার ভবিষ্যৎ বাজেট|我的预算预测|Unjuran saya
account|Account & Privacy|অ্যাকাউন্ট ও গোপনীয়তা|账户与隐私|Akaun & privasi
email_login|Account email|অ্যাকাউন্টের ইমেইল|账户邮箱|E-mel akaun
pilot_login|Sign in with the pilot account created by the team. Public registration is closed.|টিমের তৈরি test account দিয়ে sign in করুন। Public registration বন্ধ।|请使用团队创建的测试账户登录。暂不开放公众注册。|Log masuk dengan akaun rintis yang dicipta oleh pasukan. Pendaftaran awam ditutup.
cloud_storage|Cloud storage · Supabase|ক্লাউড স্টোরেজ · Supabase|云存储 · Supabase|Storan awan · Supabase
local_storage|Local storage · this computer only|লোকাল স্টোরেজ · শুধু এই কম্পিউটারে|本地存储 · 仅此电脑|Storan setempat · komputer ini sahaja
profile_intro|Enter your actual unpaid tuition, billing dates and monthly expenses. Inputs are private and user provided; they are not independently verified.|নিজের অপরিশোধিত tuition, বিলের তারিখ ও মাসিক খরচ দিন। তথ্য ব্যক্তিগত ও আপনার দেওয়া; স্বাধীনভাবে যাচাইকৃত নয়।|填写实际未付学费、账单日期及每月支出。资料属于用户自报，未经独立核实。|Masukkan yuran belum dibayar, tarikh bil dan perbelanjaan bulanan sebenar. Data peribadi ini dilaporkan pengguna dan tidak disahkan secara bebas.
profile_required|Set up My Student Profile to calculate your personal forecast. Other tools remain available.|ব্যক্তিগত forecast-এর জন্য আমার শিক্ষার্থী প্রোফাইল পূরণ করুন। অন্য tools ব্যবহার করা যাবে।|请先设置学生资料，再计算个人预算预测。其他工具仍可使用。|Lengkapkan Profil pelajar saya untuk mengira unjuran peribadi. Alat lain masih tersedia.
profile_save|Save my profile|আমার প্রোফাইল সংরক্ষণ|保存我的资料|Simpan profil saya
department|Department / faculty|বিভাগ / অনুষদ|院系|Jabatan / fakulti
campus|Campus|ক্যাম্পাস|校区|Kampus
city_input|Study city|পড়াশোনার শহর|就读城市|Bandar pengajian
study_mode|Study mode / degree|পড়াশোনার ধরন / ডিগ্রি|学习形式 / 学位|Mod pengajian / ijazah
start_date|Planning start date|পরিকল্পনা শুরুর তারিখ|规划开始日期|Tarikh mula perancangan
next_tuition|Next unpaid tuition due date|পরবর্তী অপরিশোধিত tuition-এর তারিখ|下一笔未付学费到期日|Tarikh yuran belum dibayar seterusnya
billing_interval|Actual billing interval (months)|প্রকৃত বিলের ব্যবধান (মাস)|实际账单间隔（月）|Selang bil sebenar (bulan)
billing_help|Set the interval from your invoice. A semester is not assumed to have a universal duration. Programme total/invoice is counted once.|Invoice অনুযায়ী ব্যবধান দিন। সব semester-এর সময় এক ধরা হয় না। Programme total/invoice একবার গণনা হবে।|请按账单填写间隔，不假设所有学期长度一致。项目总额或单次账单仅计算一次。|Tetapkan selang mengikut invois. Tempoh semester tidak dianggap sama untuk semua. Jumlah program/invois dikira sekali.
tuition_currency|Tuition currency|Tuition-এর মুদ্রা|学费币种|Mata wang yuran
living_currency|Monthly living-cost currency|মাসিক জীবনযাত্রার খরচের মুদ্রা|每月生活费币种|Mata wang kos sara hidup bulanan
budget_currency|Budget/report currency|বাজেট / রিপোর্টের মুদ্রা|预算 / 报告币种|Mata wang belanjawan/laporan
resources_currency|Savings, income and funding currency|Savings, income ও funding-এর মুদ্রা|储蓄、收入及资助币种|Mata wang simpanan, pendapatan dan dana
oneoff_currency|One-time expense currency|এককালীন খরচের মুদ্রা|一次性费用币种|Mata wang perbelanjaan sekali
source_note|Fee reference / private note|Fee reference / ব্যক্তিগত নোট|费用依据 / 私人备注|Rujukan yuran / nota peribadi
confirm_profile|I checked these amounts, unpaid due dates and billing periods. Funding entered is confirmed.|আমি এই অঙ্ক, অপরিশোধিত বিলের তারিখ ও সময়কাল যাচাই করেছি। দেওয়া funding নিশ্চিত।|我已核对金额、未付账单日期及收费周期，所填资助已确认。|Saya telah menyemak amaun, tarikh bil belum dibayar dan tempoh bil. Dana yang dimasukkan telah disahkan.
forecast_run|Calculate from my saved profile|আমার সংরক্ষিত প্রোফাইল থেকে হিসাব|根据已保存资料计算|Kira daripada profil tersimpan
forecast_intro|Scenario estimates use your saved inputs and the latest available reference rates. Future fees and exchange rates are unknown.|আপনার saved input ও সর্বশেষ প্রকাশিত rate দিয়ে scenario হিসাব হয়। ভবিষ্যতের fee ও rate জানা নেই।|情景估算使用已保存资料及最新可用参考汇率，未来学费和汇率未知。|Anggaran senario menggunakan input tersimpan dan kadar rujukan terkini yang tersedia. Yuran dan kadar masa depan tidak diketahui.
cost_growth|Annual living-cost growth assumption (%)|বার্ষিক living-cost বৃদ্ধির অনুমান (%)|年度生活费增长假设（%）|Andaian pertumbuhan kos sara hidup tahunan (%)
fx_stress|Extra cost of foreign expenses (%)|বিদেশি মুদ্রার খরচ বাড়ার অনুমান (%)|外币支出额外成本（%）|Kos tambahan perbelanjaan mata wang asing (%)
stress_help|FX stress applies to expenses whose currency differs from the budget currency. It is an assumption, not an exchange-rate prediction.|Budget currency থেকে আলাদা মুদ্রার খরচে FX stress প্রযোজ্য। এটি অনুমান; rate prediction নয়।|汇率压力仅适用于币种不同于预算币种的支出。这是假设，并非汇率预测。|Tekanan FX dikenakan pada perbelanjaan yang berbeza mata wang daripada belanjawan. Ini andaian, bukan ramalan kadar.
timing_gap|Largest monthly cash shortfall|মাসভিত্তিক সর্বোচ্চ অর্থঘাটতি|最大月度资金缺口|Kekurangan tunai bulanan terbesar
first_shortfall|First shortfall period|প্রথম ঘাটতির সময়কাল|首次资金不足期间|Tempoh kekurangan pertama
monthly_cashflow|Monthly cash flow|মাসভিত্তিক অর্থপ্রবাহ|每月现金流|Aliran tunai bulanan
month_start|Period starts|সময়কাল শুরু|期间开始|Tempoh bermula
closing_balance|Closing balance|সমাপনী ব্যালান্স|期末余额|Baki penutup
total_cost|Total cost|মোট খরচ|总费用|Jumlah kos
due_dates|Tuition due dates|Tuition-এর তারিখ|学费到期日|Tarikh yuran perlu dibayar
forecast_pdf|Download forecast PDF|Forecast PDF ডাউনলোড|下载预算预测 PDF|Muat turun PDF unjuran
profile_pdf|Download my profile summary PDF|আমার প্রোফাইল সারাংশ PDF|下载个人资料摘要 PDF|Muat turun ringkasan profil PDF
profile_assistant|Use my profile budget|আমার প্রোফাইলের বাজেট দেখুন|使用我的资料预算|Gunakan belanjawan profil saya
profile_ai|Review my forecast priorities with AI|AI দিয়ে forecast-এর করণীয় পর্যালোচনা|用 AI 审查预算优先事项|Semak keutamaan unjuran dengan AI
profile_ai_note|Only numeric forecast totals and generic study context are sent. Your university name, department, email and private note are excluded.|শুধু সংখ্যাগত forecast totals ও সাধারণ study context পাঠানো হবে। University নাম, department, email ও private note পাঠানো হবে না।|仅发送预算数值及通用学习背景，不发送大学名称、院系、邮箱或私人备注。|Hanya jumlah angka unjuran dan konteks pengajian umum dihantar. Nama universiti, jabatan, e-mel dan nota peribadi tidak dihantar.
profile_updated|Profile updated: {date}|প্রোফাইল আপডেট: {date}|资料更新：{date}|Profil dikemas kini: {date}
private_data|Saved student profiles and plans are encrypted. Cloud access is restricted to your authenticated account. Operators controlling the app secrets remain trusted.|Saved student profile ও plan encrypted। Cloud data শুধু আপনার authenticated account-এর জন্য। App secrets নিয়ন্ত্রণকারী operator বিশ্বস্ত হিসেবে বিবেচিত।|已保存的资料和计划已加密，云端访问仅限本人已认证账户。控制应用密钥的运营者仍属于受信任方。|Profil dan pelan tersimpan disulitkan. Akses awan terhad kepada akaun anda yang disahkan. Pengendali rahsia aplikasi masih dipercayai.
delete_profiles|Delete my saved profiles and plan|আমার saved profile ও plan মুছুন|删除我的资料和计划|Padam profil dan pelan tersimpan saya
delete_note|This removes saved profile/plan documents. Sandbox balances, operation logs and your login account remain. Ask the team for full account erasure.|এতে saved profile/plan মুছবে। Sandbox balance, logs ও login account থাকবে। পুরো account মুছতে টিমের সহায়তা নিন।|这将删除资料和计划文件，模拟余额、操作日志及登录账户仍保留。完整账户删除请联系团队。|Ini memadam dokumen profil/pelan. Baki simulasi, log operasi dan akaun log masuk kekal. Hubungi pasukan untuk pemadaman akaun penuh.
delete_confirm|I want to delete my saved profiles and plan.|আমি আমার saved profile ও plan মুছতে চাই।|我确认删除已保存的资料和计划。|Saya mahu memadam profil dan pelan tersimpan saya.
deleted_profiles|Saved profiles and plan deleted.|Saved profile ও plan মুছে গেছে।|已删除资料和计划。|Profil dan pelan tersimpan dipadam.
change_password|Change password|পাসওয়ার্ড পরিবর্তন|修改密码|Tukar kata laluan
current_password|Current password|বর্তমান পাসওয়ার্ড|当前密码|Kata laluan semasa
password_changed|Password changed. Sign in again with the new password.|Password পরিবর্তিত হয়েছে। নতুন password দিয়ে sign in করুন।|密码已修改，请使用新密码重新登录。|Kata laluan ditukar. Log masuk semula menggunakan kata laluan baharu.
reset_help|Forgot your password? Ask the team to reset your controlled pilot account in the Supabase dashboard.|Password ভুলে গেলে টিমকে Supabase dashboard থেকে আপনার test account reset করতে বলুন।|忘记密码？请联系团队在 Supabase 控制台重置测试账户。|Lupa kata laluan? Minta pasukan menetapkan semula akaun rintis anda dalam papan pemuka Supabase.
guide_v4_title|Profiles, forecasts and account access|প্রোফাইল, forecast ও account access|资料、预算预测及账户访问|Profil, unjuran dan akses akaun
guide_v4_body|1. Sign in with your assigned account. 2. Save My Student Profile with real amounts and unpaid dates. 3. Open My Forecast and calculate. 4. Check source dates and assumptions. 5. Review a quote before any sandbox transfer. 6. Download PDFs and sign out. Personal profiles are optional for the standalone converter and university reference planner.|১. দেওয়া account দিয়ে sign in করুন। ২. প্রকৃত অঙ্ক ও unpaid dates দিয়ে profile save করুন। ৩. Forecast খুলে হিসাব করুন। ৪. Source date ও assumptions দেখুন। ৫. Sandbox transfer-এর আগে quote যাচাই করুন। ৬. PDF নামিয়ে sign out করুন। Converter ও university reference planner profile ছাড়াও চলবে।|1. 使用指定账户登录。2. 保存实际金额和未付日期。3. 打开预算预测并计算。4. 核对来源日期及假设。5. 模拟转账前审查报价。6. 下载 PDF 并退出。独立换汇和大学参考规划工具无需个人资料。|1. Log masuk dengan akaun diberi. 2. Simpan profil dengan amaun sebenar dan tarikh belum dibayar. 3. Buka Unjuran saya dan kira. 4. Semak tarikh sumber dan andaian. 5. Semak sebut harga sebelum pemindahan simulasi. 6. Muat turun PDF dan log keluar. Penukar dan perancang rujukan universiti tidak memerlukan profil peribadi.
guide_ai_limits|Cloud AI requests are limited to protect the shared allowance. One reviewed task can use two model calls. Provider limits may be lower. Calculators still work without an LLM.|Shared allowance সুরক্ষায় cloud AI request সীমিত। একটি reviewed task-এ দুই model call হতে পারে। Provider limit আরও কম হতে পারে। LLM ছাড়াও calculator চলবে।|云端 AI 请求设有限额，一项双模型审核任务可能调用模型两次。供应商限额可能更低。计算工具无需 LLM 也可使用。|Permintaan AI awan dihadkan untuk melindungi kuota bersama. Satu tugas disemak boleh menggunakan dua panggilan model. Had pembekal mungkin lebih rendah. Kalkulator boleh berjalan tanpa LLM.
guide_developer_file|For installation, account creation, keys, SQL setup and deployment, open DEVELOPER_GUIDE_BN.md included in the project. API keys are never entered into this public guide.|Install, account, key, SQL setup ও deploy-এর জন্য project-এর DEVELOPER_GUIDE_BN.md খুলুন। এই public guide-এ API key দিতে হয় না।|安装、账户、密钥、SQL 设置及部署请参阅项目内 DEVELOPER_GUIDE_BN.md。此公开指南不收集 API 密钥。|Untuk pemasangan, akaun, kunci, SQL dan penggunaan awan, buka DEVELOPER_GUIDE_BN.md dalam projek. Panduan awam ini tidak menerima kunci API.
setup_missing|Configuration incomplete. Follow the Developer Guide; no local fallback was used.|Configuration অসম্পূর্ণ। Developer Guide অনুসরণ করুন; local fallback ব্যবহার হয়নি।|配置不完整，请参阅开发者指南；未切换至本地存储。|Konfigurasi belum lengkap. Ikuti Panduan Pembangun; tiada sandaran setempat digunakan.
same_currency_note|No external rate was needed: all amounts use the budget currency.|সব অঙ্ক budget currency-তে; বাইরের rate লাগেনি।|所有金额均使用预算币种，无需外部汇率。|Semua amaun menggunakan mata wang belanjawan; kadar luaran tidak diperlukan.
profile_pdf_note|Financial PDFs use English labels. Use English institution/programme names for consistent PDF typography.|Financial PDF-এর label ইংরেজি। PDF-এ সঠিকভাবে দেখাতে institution/programme-এর ইংরেজি নাম ব্যবহার করুন।|财务 PDF 标签使用英语。建议院校及专业名称使用英文，以确保 PDF 字体显示一致。|Label PDF kewangan menggunakan bahasa Inggeris. Gunakan nama institusi/program bahasa Inggeris untuk paparan PDF yang konsisten.
"""
