"""Local, deterministic UI translations. No external translation API or user data.

Stable message IDs keep language changes separate from financial logic. Names,
ISO currency codes, model IDs and official programme titles stay unchanged.
"""

from babel.numbers import get_currency_name
from .v4_i18n import EXTRA_ROWS

LANGUAGES = {"en": "English", "bn": "বাংলা", "zh": "中文", "ms": "Bahasa Melayu"}
LOCALES = {"en": "en", "bn": "bn", "zh": "zh_CN", "ms": "ms"}

# Each row is: key | English | Bangla | Simplified Chinese | Bahasa Melayu.
# Keeping complete rows makes missing translations visible during review/tests.
_ROWS = """
language|Language|ভাষা|语言|Bahasa
navigation|Workspace|ওয়ার্কস্পেস|工作区|Ruang kerja
dashboard|Dashboard|ড্যাশবোর্ড|总览|Papan pemuka
assistant|AI Assistant|AI সহায়ক|AI 助手|Pembantu AI
converter|Currency Converter|মুদ্রা রূপান্তর|货币兑换|Penukar mata wang
planner|University Planner|বিশ্ববিদ্যালয় পরিকল্পনা|大学费用规划|Perancang universiti
transfers|Transfers|লেনদেন|转账|Pemindahan
wallet|Wallet & Audit|ওয়ালেট ও অডিট|钱包与审计|Dompet & audit
developer|Developer|ডেভেলপার|开发团队|Pembangun
guide|Guide for User|ব্যবহার নির্দেশিকা|用户指南|Panduan pengguna
brand_line|STUDENT FINANCE · CONNECTED ACROSS BORDERS|শিক্ষার্থী অর্থব্যবস্থা · সীমান্ত পেরিয়ে সংযোগ|学生财务 · 跨境互联|KEWANGAN PELAJAR · MERENTASI SEMPADAN
hero|Your next chapter, financially clear.|শিক্ষাজীবনের পরবর্তী ধাপের আর্থিক পরিকল্পনা স্পষ্ট করুন।|让下一段求学之旅，财务更清晰。|Rancang kewangan untuk langkah pengajian seterusnya.
hero_sub|Plan university costs, understand currency conversion and review every transfer.|বিশ্ববিদ্যালয়ের খরচ পরিকল্পনা, মুদ্রা রূপান্তর ও প্রতিটি লেনদেন যাচাই করুন।|规划大学费用，了解汇率，并核对每笔转账。|Rancang kos universiti, fahami pertukaran mata wang dan semak setiap pemindahan.
release|Version 3.0|সংস্করণ ৩.০|版本 3.0|Versi 3.0
simulation|Simulation environment · no real money moves|সিমুলেশন পরিবেশ · বাস্তব টাকা পাঠানো হয় না|模拟环境 · 不涉及真实资金|Persekitaran simulasi · tiada wang sebenar dipindahkan
setup_title|Create your StudentBridge account|StudentBridge অ্যাকাউন্ট তৈরি করুন|创建 StudentBridge 账户|Cipta akaun StudentBridge anda
setup_text|Set up your private workspace with a password of at least 12 characters.|অন্তত ১২ অক্ষরের password দিয়ে ব্যক্তিগত ওয়ার্কস্পেস তৈরি করুন।|使用至少 12 个字符的密码，设置您的私人工作区。|Sediakan ruang kerja peribadi dengan kata laluan sekurang-kurangnya 12 aksara.
username|Username|ব্যবহারকারীর নাম|用户名|Nama pengguna
password|Password|পাসওয়ার্ড|密码|Kata laluan
choose_password|Choose a password (12+ characters)|পাসওয়ার্ড দিন (অন্তত ১২ অক্ষর)|设置密码（至少 12 个字符）|Tetapkan kata laluan (12+ aksara)
repeat_password|Repeat password|পাসওয়ার্ড আবার দিন|再次输入密码|Ulang kata laluan
create_account|Create account|অ্যাকাউন্ট তৈরি করুন|创建账户|Cipta akaun
login_title|Welcome back|আবার স্বাগতম|欢迎回来|Selamat kembali
login_sub|Sign in to continue your financial planning.|আর্থিক পরিকল্পনা চালিয়ে যেতে সাইন ইন করুন।|登录以继续您的财务规划。|Log masuk untuk meneruskan perancangan kewangan anda.
sign_in|Sign in|সাইন ইন|登录|Log masuk
sign_out|Sign out|সাইন আউট|退出登录|Log keluar
signed_in|Signed in as {name} · {role}|{name} হিসেবে সাইন ইন · {role}|已登录：{name} · {role}|Log masuk sebagai {name} · {role}
session_note|Your session expires after 30 minutes.|আপনার সেশন ৩০ মিনিট পরে শেষ হবে।|会话将在 30 分钟后过期。|Sesi anda tamat selepas 30 minit.
login_failed|Sign-in failed or temporarily locked. After five failed attempts, wait five minutes.|সাইন ইন ব্যর্থ বা সাময়িকভাবে লক হয়েছে। পাঁচবার ব্যর্থ হলে পাঁচ মিনিট অপেক্ষা করুন।|登录失败或账户暂时锁定。连续失败五次后，请等待五分钟。|Log masuk gagal atau dikunci sementara. Selepas lima percubaan gagal, tunggu lima minit.
password_mismatch|Passwords do not match.|দুটি পাসওয়ার্ড মিলছে না।|两次输入的密码不一致。|Kata laluan tidak sepadan.
storage_error|Your workspace could not be opened. Check folder permissions and the matching server key backup.|ওয়ার্কস্পেস খোলা যায়নি। folder permission ও সঠিক server key backup দেখুন।|无法打开工作区。请检查文件夹权限及匹配的服务器密钥备份。|Ruang kerja tidak dapat dibuka. Semak kebenaran folder dan sandaran kunci pelayan yang sepadan.
account_help|Account and password help is available in Guide for User.|অ্যাকাউন্ট ও পাসওয়ার্ডের সহায়তা ব্যবহার নির্দেশিকায় পাবেন।|账户与密码帮助请参阅用户指南。|Bantuan akaun dan kata laluan tersedia dalam Panduan pengguna.
planner_metric|Universities in catalogue|ক্যাটালগে বিশ্ববিদ্যালয়|目录中的大学|Universiti dalam katalog
programme_metric|Programme references|প্রোগ্রামের তথ্যসূত্র|专业费用参考|Rujukan program
balance_metric|Wallet currencies|ওয়ালেটের মুদ্রা|钱包币种|Mata wang dalam dompet
reference_metric|Reference source|রেটের উৎস|汇率来源|Sumber rujukan
live|Published reference rates|প্রকাশিত reference rate|已公布的参考汇率|Kadar rujukan diterbitkan
offline|Illustrative reference rates|উদাহরণভিত্তিক reference rate|示例参考汇率|Kadar rujukan ilustrasi
ready|Ready to plan|পরিকল্পনার জন্য প্রস্তুত|准备开始规划|Sedia untuk merancang
overview_title|Your financial overview|আপনার আর্থিক সারসংক্ষেপ|您的财务概览|Gambaran kewangan anda
overview_sub|A clear view of tuition, funding and your latest activity.|টিউশন, অর্থায়ন ও সাম্প্রতিক কার্যক্রমের স্পষ্ট চিত্র।|清晰查看学费、资金和最近活动。|Lihat yuran, pembiayaan dan aktiviti terkini dengan jelas.
no_budget|No budget calculated yet|এখনও বাজেট হিসাব করা হয়নি|尚未计算预算|Belum ada belanjawan dikira
no_activity|No completed transfers yet|এখনও কোনো লেনদেন সম্পন্ন হয়নি|尚无已完成的转账|Belum ada pemindahan selesai
recent_activity|Recent activity|সাম্প্রতিক কার্যক্রম|最近活动|Aktiviti terkini
quick_actions|Your workspace|আপনার ওয়ার্কস্পেস|您的工作区|Ruang kerja anda
open_planner|Open University Planner|বিশ্ববিদ্যালয় পরিকল্পনা খুলুন|打开大学费用规划|Buka perancang universiti
open_converter|Open Currency Converter|মুদ্রা রূপান্তর খুলুন|打开货币兑换|Buka penukar mata wang
open_transfers|Open Transfers|লেনদেন খুলুন|打开转账|Buka pemindahan
open_guide|Open Guide for User|ব্যবহার নির্দেশিকা খুলুন|打开用户指南|Buka panduan pengguna
last_budget|Latest budget|সর্বশেষ বাজেট|最近预算|Belanjawan terkini
estimated_cost|Estimated cost|আনুমানিক খরচ|预计费用|Anggaran kos
resources|Confirmed resources|নিশ্চিত অর্থায়ন|已确认资金|Sumber disahkan
gap|Funding gap|অর্থের ঘাটতি|资金缺口|Jurang pembiayaan
ask_title|Ask with clarity. Calculate with confidence.|প্রশ্ন করুন স্পষ্টভাবে, হিসাব দেখুন নির্ভরযোগ্যভাবে।|清晰提问，可靠计算。|Tanya dengan jelas. Kira dengan yakin.
question|Your question|আপনার প্রশ্ন|您的问题|Soalan anda
question_placeholder|Enter a currency or university finance question|মুদ্রা বা বিশ্ববিদ্যালয়ের খরচ নিয়ে প্রশ্ন লিখুন|输入货币或大学费用问题|Masukkan soalan mata wang atau kewangan universiti
run_assistant|Run assistant|সহায়ক চালান|运行助手|Jalankan pembantu
processing|Checking your request and calculating…|প্রশ্ন যাচাই ও হিসাব করা হচ্ছে…|正在核对请求并计算…|Menyemak permintaan dan mengira…
question_required|Enter a question to continue.|চালিয়ে যেতে প্রশ্ন লিখুন।|请输入问题以继续。|Masukkan soalan untuk meneruskan.
clarify|Please clarify the amount, currency direction or programme in your question.|প্রশ্নে অর্থের পরিমাণ, মুদ্রার দিক বা প্রোগ্রাম স্পষ্ট করুন।|请明确金额、兑换方向或专业信息。|Sila jelaskan amaun, arah mata wang atau program dalam soalan anda.
blocked|This request requires a security override and cannot be processed.|এই প্রশ্নে নিরাপত্তা নিয়ম অগ্রাহ্য করতে বলা হয়েছে; এটি প্রক্রিয়া করা যাবে না।|此请求要求绕过安全规则，无法处理。|Permintaan ini memerlukan pintasan keselamatan dan tidak boleh diproses.
use_planner|Use University Planner to enter your tuition, living costs and confirmed funding.|টিউশন, জীবনযাত্রার খরচ ও নিশ্চিত অর্থায়ন বিশ্ববিদ্যালয় পরিকল্পনায় দিন।|请在大学费用规划中填写学费、生活费及已确认资金。|Gunakan Perancang universiti untuk memasukkan yuran, kos sara hidup dan pembiayaan disahkan.
result|Calculation result|হিসাবের ফল|计算结果|Hasil pengiraan
verified_calculation|Calculated from validated inputs and reference data.|যাচাইকৃত input ও reference data থেকে হিসাব করা হয়েছে।|根据已验证输入和参考数据计算。|Dikira daripada input dan data rujukan yang disahkan.
from|From|যে মুদ্রা থেকে|原币种|Daripada
to|To|যে মুদ্রায়|目标币种|Kepada
amount|Amount|পরিমাণ|金额|Amaun
source_amount|Amount in source currency|উৎস মুদ্রায় পরিমাণ|原币种金额|Amaun mata wang asal
reverse|Reverse direction|উল্টো দিকে রূপান্তর|反向兑换|Songsangkan arah
calculate_conversion|Calculate conversion|রূপান্তর হিসাব করুন|计算兑换|Kira pertukaran
converted|Converted reference amount|রূপান্তরিত reference পরিমাণ|换算参考金额|Amaun rujukan ditukar
rate|Reference rate|Reference rate|参考汇率|Kadar rujukan
reference_date|Observation date|রেট প্রকাশের তারিখ|汇率日期|Tarikh pemerhatian
rate_source|Rate source|রেটের উৎস|汇率来源|Sumber kadar
reference_note|Reference rates support planning; payment providers may charge different rates and fees.|Reference rate পরিকল্পনার জন্য; payment provider-এর rate ও fee আলাদা হতে পারে।|参考汇率仅用于规划；支付服务商的汇率和费用可能不同。|Kadar rujukan untuk perancangan; penyedia pembayaran mungkin mengenakan kadar dan fi berbeza.
illustrative_note|This calculation uses an illustrative dataset, not market rates.|এই হিসাবে উদাহরণভিত্তিক dataset ব্যবহৃত হয়েছে, market rate নয়।|此计算使用示例数据，并非市场汇率。|Pengiraan ini menggunakan set data ilustrasi, bukan kadar pasaran.
sensitivity|Exchange-rate sensitivity|রেট পরিবর্তনের প্রভাব|汇率敏感性|Kepekaan kadar pertukaran
movement|Rate movement assumption|রেট পরিবর্তনের অনুমান|汇率变动假设|Andaian perubahan kadar
received|Received amount|প্রাপ্ত পরিমাণ|到账金额|Amaun diterima
sensitivity_note|These are planning scenarios, not predictions. Payment fees are excluded.|এগুলো পরিকল্পনার scenario, পূর্বাভাস নয়। Payment fee অন্তর্ভুক্ত নেই।|这些是规划情景，并非预测，且不含支付费用。|Ini senario perancangan, bukan ramalan. Fi pembayaran tidak disertakan.
loading_currencies|Loading available currencies…|উপলব্ধ মুদ্রা লোড হচ্ছে…|正在加载可用币种…|Memuatkan mata wang tersedia…
fx_unavailable|The reference-rate service is temporarily unavailable. Retry or review connection settings in Guide for User.|Reference-rate service সাময়িকভাবে পাওয়া যাচ্ছে না। Retry করুন বা নির্দেশিকায় connection settings দেখুন।|参考汇率服务暂时不可用。请重试，或在用户指南中检查连接设置。|Perkhidmatan kadar rujukan tidak tersedia buat sementara. Cuba semula atau semak tetapan sambungan dalam Panduan pengguna.
retry|Retry|আবার চেষ্টা করুন|重试|Cuba semula
country|Country|দেশ|国家|Negara
level|Degree level|ডিগ্রির স্তর|学位层次|Tahap pengajian
all|All|সব|全部|Semua
Malaysia|Malaysia|মালয়েশিয়া|马来西亚|Malaysia
Bangladesh|Bangladesh|বাংলাদেশ|孟加拉国|Bangladesh
China|China|চীন|中国|China
Bachelor|Bachelor|স্নাতক|本科|Sarjana muda
Master|Master|স্নাতকোত্তর|硕士|Sarjana
programme|University programme|বিশ্ববিদ্যালয়ের প্রোগ্রাম|大学专业|Program universiti
no_programme|No programme reference matches these filters.|এই filter-এ কোনো প্রোগ্রামের তথ্য নেই।|没有符合筛选条件的专业参考。|Tiada rujukan program sepadan dengan penapis ini.
official_reference|Official programme reference|প্রোগ্রামের অফিসিয়াল তথ্যসূত্র|官方专业参考|Rujukan program rasmi
reference_fee|Published fee reference|প্রকাশিত fee reference|已公布费用参考|Rujukan yuran diterbitkan
source_year|Source year|তথ্যের বছর|资料年份|Tahun sumber
checked|Checked|যাচাইয়ের তারিখ|核查日期|Disemak
source_link|Open official source|অফিসিয়াল উৎস খুলুন|打开官方来源|Buka sumber rasmi
original_source|Original source notes (English)|মূল উৎসের বিবরণ (English)|原始来源说明（英文）|Nota sumber asal (bahasa Inggeris)
manual_fee|Use your current invoice or verified fee sheet for this programme.|এই প্রোগ্রামের বর্তমান invoice বা যাচাইকৃত fee sheet ব্যবহার করুন।|请使用该专业的当前账单或已核实费用表。|Gunakan invois semasa atau jadual yuran disahkan untuk program ini.
living_note|Living costs are editable planning assumptions. Replace them with your expected expenses.|জীবনযাত্রার খরচ পরিবর্তনযোগ্য অনুমান। নিজের প্রত্যাশিত খরচ দিয়ে বদলান।|生活费为可编辑的规划假设，请替换为您的预计开支。|Kos sara hidup ialah andaian boleh ubah. Gantikan dengan perbelanjaan jangkaan anda.
load_saved|Load my saved plan|সংরক্ষিত পরিকল্পনা ব্যবহার করুন|加载已保存计划|Muatkan pelan disimpan
inputs_currency|Enter all amounts below in {currency}.|নিচের সব পরিমাণ {currency}-এ দিন।|以下金额均以 {currency} 输入。|Masukkan semua amaun berikut dalam {currency}.
tuition_fee|Fee per selected period|নির্বাচিত মেয়াদের fee|每个所选周期的费用|Yuran bagi tempoh dipilih
fee_period|Fee period|Fee-এর মেয়াদ|费用周期|Tempoh yuran
programme_period|Whole programme|সম্পূর্ণ প্রোগ্রাম|整个专业|Keseluruhan program
year|Year|বছর|年|Tahun
semester|Semester|সেমিস্টার|学期|Semester
trimester|Trimester|ট্রাইমেস্টার|三学期制学期|Trimester
invoice|Invoice|ইনভয়েস|账单|Invois
unknown|Confirmation required|নিশ্চিত করা প্রয়োজন|需要确认|Perlu pengesahan
months|Planning horizon (months)|পরিকল্পনার মেয়াদ (মাস)|规划期限（月）|Tempoh perancangan (bulan)
fee_count|Number of tuition periods|টিউশন মেয়াদের সংখ্যা|学费周期数量|Bilangan tempoh yuran
fee_count_help|Count a whole-programme total or invoice once. Count annual/semester bills explicitly.|সম্পূর্ণ প্রোগ্রাম বা invoice একবার ধরুন। বছর/সেমিস্টারের bill-এর সংখ্যা আলাদা করে দিন।|整个专业总额或单张账单仅计一次。年度或学期账单须明确填写次数。|Kira jumlah keseluruhan program atau satu invois sekali sahaja. Nyatakan bilangan bil tahunan/semester.
rent|Monthly rent|মাসিক ভাড়া|每月房租|Sewa bulanan
food|Monthly food|মাসিক খাবার|每月餐饮|Makanan bulanan
transport|Monthly transport|মাসিক যাতায়াত|每月交通|Pengangkutan bulanan
utilities|Monthly utilities|মাসিক utility|每月水电等费用|Utiliti bulanan
other|Other monthly expenses|অন্যান্য মাসিক খরচ|其他每月开支|Perbelanjaan bulanan lain
one_off|One-off charges|এককালীন খরচ|一次性费用|Caj sekali sahaja
tax|Tax assumption (%)|করের অনুমান (%)|税费假设（%）|Andaian cukai (%)
contingency|Contingency (%)|জরুরি সংরক্ষণ (%)|预备金（%）|Kontingensi (%)
savings|Available savings|ব্যবহারযোগ্য সঞ্চয়|可用储蓄|Simpanan tersedia
income|Confirmed monthly support/income|নিশ্চিত মাসিক সহায়তা/আয়|已确认每月资助或收入|Sokongan/pendapatan bulanan disahkan
funding|Confirmed one-off funding|নিশ্চিত এককালীন অর্থায়ন|已确认一次性资助|Pembiayaan sekali sahaja disahkan
confirm_fee|I confirm the fee amount, period and applicable student classification|আমি fee-এর পরিমাণ, মেয়াদ ও প্রযোজ্য শিক্ষার্থী শ্রেণি নিশ্চিত করছি|我确认费用金额、周期及适用学生类别|Saya mengesahkan amaun, tempoh yuran dan kategori pelajar berkenaan
save_plan|Save this plan securely|পরিকল্পনাটি নিরাপদে সংরক্ষণ করুন|安全保存此计划|Simpan pelan ini dengan selamat
calculate_budget|Calculate my student budget|শিক্ষার বাজেট হিসাব করুন|计算学生预算|Kira belanjawan pengajian
confirm_required|Confirm the amount and fee period before calculating.|হিসাবের আগে পরিমাণ ও fee-এর মেয়াদ নিশ্চিত করুন।|计算前请确认金额和费用周期。|Sahkan amaun dan tempoh yuran sebelum mengira.
category|Category|খাত|类别|Kategori
tuition|Tuition|টিউশন|学费|Yuran pengajian
tax_amount|Tax assumption|করের অনুমান|税费假设|Andaian cukai
living|Living costs|জীবনযাত্রার খরচ|生活费|Kos sara hidup
buffer|Contingency|জরুরি সংরক্ষণ|预备金|Kontingensi
budget_actions|Recommended planning actions|প্রস্তাবিত পরিকল্পনার পদক্ষেপ|建议规划行动|Tindakan perancangan disyorkan
verify_fee_advice|Confirm your applicable programme fee and bill period with the university.|বিশ্ববিদ্যালয়ের সঙ্গে নিজের প্রযোজ্য programme fee ও bill-এর মেয়াদ নিশ্চিত করুন।|请向大学确认适用专业费用及账单周期。|Sahkan yuran program dan tempoh bil berkenaan dengan universiti.
housing_advice|Review housing and living expenses for {city}; update the assumptions with your own estimates.|{city}-এর বাসা ও জীবনযাত্রার খরচ যাচাই করে নিজের অনুমান বসান।|核对 {city} 的住宿与生活费用，并更新为您自己的估算。|Semak kos perumahan dan sara hidup di {city}; kemas kini dengan anggaran anda.
gap_advice|Your funding gap is {amount} {currency}; spreading it over {months} months requires {monthly} extra per month.|অর্থের ঘাটতি {amount} {currency}; {months} মাসে পূরণ করতে মাসে অতিরিক্ত {monthly} লাগবে।|资金缺口为 {amount} {currency}；若分摊至 {months} 个月，每月需额外准备 {monthly}。|Jurang pembiayaan ialah {amount} {currency}; untuk {months} bulan, tambahan {monthly} diperlukan setiap bulan.
covered_advice|Your declared resources cover this plan. Keep the contingency available for changes.|ঘোষিত অর্থায়ন এই পরিকল্পনার জন্য যথেষ্ট। পরিবর্তনের জন্য জরুরি সংরক্ষণ রাখুন।|已申报资金可覆盖此计划，请保留预备金应对变化。|Sumber dinyatakan mencukupi untuk pelan ini. Kekalkan kontingensi untuk perubahan.
funding_advice|Check official funding or instalment options; include an award only after confirmation.|অফিসিয়াল funding বা কিস্তির সুযোগ দেখুন; award নিশ্চিত হওয়ার পরই যোগ করুন।|查看官方资助或分期选项，获确认后才计入奖助金。|Semak pilihan pembiayaan atau ansuran rasmi; masukkan anugerah hanya selepas disahkan.
prioritize|Ask both models to prioritize actions|দুটি model দিয়ে অগ্রাধিকার বাছুন|请两个模型排列行动优先级|Minta kedua-dua model utamakan tindakan
advice_processing|Reviewing the numeric scenario independently…|সংখ্যাভিত্তিক পরিকল্পনা আলাদাভাবে পর্যালোচনা হচ্ছে…|正在独立审核数值规划…|Menyemak senario berangka secara berasingan…
model_agreed|Both models agreed on these actions; amounts come from the calculation.|দুটি model এই পদক্ষেপে একমত; পরিমাণগুলো হিসাব থেকে এসেছে।|两个模型对此行动达成一致；金额来自计算结果。|Kedua-dua model bersetuju dengan tindakan ini; amaun daripada pengiraan.
home_currency|View total in another currency|অন্য মুদ্রায় মোট দেখুন|以其他货币查看总额|Lihat jumlah dalam mata wang lain
convert_total|Convert total|মোট রূপান্তর করুন|换算总额|Tukar jumlah
due_title|Next tuition bill|পরবর্তী টিউশন bill|下一笔学费账单|Bil yuran seterusnya
due_amount|Next bill amount|পরবর্তী bill-এর পরিমাণ|下一笔账单金额|Amaun bil seterusnya
due_available|Already set aside|আগে থেকে রাখা অর্থ|已预留金额|Amaun telah diasingkan
due_months|Months until due|পরিশোধ পর্যন্ত মাস|距离到期月数|Bulan sehingga perlu dibayar
due_calculate|Calculate monthly saving target|মাসিক সঞ্চয়ের লক্ষ্য হিসাব করুন|计算每月储蓄目标|Kira sasaran simpanan bulanan
due_result|Set aside {amount} {currency} per month for {months} months.|{months} মাস ধরে মাসে {amount} {currency} আলাদা রাখুন।|连续 {months} 个月，每月预留 {amount} {currency}。|Asingkan {amount} {currency} sebulan selama {months} bulan.
transfer_title|Compare options. Review before you confirm.|বিকল্প তুলনা করুন। নিশ্চিত করার আগে যাচাই করুন।|比较选项，确认前先核对。|Bandingkan pilihan. Semak sebelum sahkan.
transfer_note|Providers, fees, balances and transfers are simulated. Reference FX may use live published rates.|Provider, fee, balance ও transfer সিমুলেটেড। FX-এ প্রকাশিত live reference rate ব্যবহার হতে পারে।|服务商、费用、余额及转账均为模拟。汇率可使用实时获取的公布参考值。|Penyedia, fi, baki dan pemindahan adalah simulasi. FX boleh menggunakan kadar rujukan diterbitkan yang diambil secara langsung.
spend_currency|Spend currency|খরচের মুদ্রা|支出币种|Mata wang dibelanjakan
receive_currency|Receive currency|প্রাপ্তির মুদ্রা|收款币种|Mata wang diterima
spend_budget|Total spend budget · includes fee|মোট খরচের সীমা · fee-সহ|总支出预算 · 含费用|Jumlah belanjawan dibelanjakan · termasuk fi
new_recipient|Unfamiliar recipient|অপরিচিত প্রাপক|不熟悉的收款人|Penerima baharu
compare|Compare providers|Provider তুলনা করুন|比较服务商|Bandingkan penyedia
provider|Simulation provider|সিমুলেশন provider|模拟服务商|Penyedia simulasi
fee_included|Fee included|অন্তর্ভুক্ত fee|已含费用|Fi disertakan
spend|Total spend|মোট খরচ|总支出|Jumlah dibelanjakan
minutes_estimate|Estimated minutes|আনুমানিক মিনিট|预计分钟数|Anggaran minit
select_provider|Provider for this quote|এই quote-এর provider|此报价的服务商|Penyedia untuk sebut harga ini
create_quote|Create signed quote|স্বাক্ষরিত quote তৈরি করুন|创建签名报价|Cipta sebut harga bertandatangan
review_quote|Review your quote|Quote যাচাই করুন|核对报价|Semak sebut harga anda
quote_summary|Spend {spend} {source}, including {fee} fee. Receive {received} {target} through {provider}.|{fee} fee-সহ {spend} {source} খরচ হবে। {provider}-এর মাধ্যমে {received} {target} পাবেন।|支出 {spend} {source}，含费用 {fee}。通过 {provider} 收到 {received} {target}。|Belanjakan {spend} {source}, termasuk fi {fee}. Terima {received} {target} melalui {provider}.
quote_expiry|Quote {id} · approximately {seconds} seconds remaining|Quote {id} · আনুমানিক {seconds} সেকেন্ড বাকি|报价 {id} · 约剩余 {seconds} 秒|Sebutan harga {id} · baki kira-kira {seconds} saat
risk_blocked|This quote requires risk review and cannot be executed.|এই quote-এর risk review প্রয়োজন; চালানো যাবে না।|此报价需要风险审核，无法执行。|Sebutan harga ini memerlukan semakan risiko dan tidak boleh dilaksanakan.
risk_passed|Current quote passed the configured checks.|বর্তমান quote নির্ধারিত যাচাইয়ে উত্তীর্ণ।|当前报价已通过所配置的检查。|Sebutan harga semasa lulus semakan ditetapkan.
approve|I reviewed this quote and approve the simulated balance change|আমি quote যাচাই করে সিমুলেটেড balance পরিবর্তনের অনুমতি দিচ্ছি|我已核对报价并同意模拟余额变更|Saya telah menyemak sebut harga dan meluluskan perubahan baki simulasi
confirmation|Enter the quote's final six characters: {code}|Quote-এর শেষ ছয়টি অক্ষর লিখুন: {code}|输入报价编号的最后六个字符：{code}|Masukkan enam aksara terakhir sebut harga: {code}
execute|Confirm transfer|লেনদেন নিশ্চিত করুন|确认转账|Sahkan pemindahan
transfer_completed|Transfer simulation completed. No real money moved.|লেনদেনের সিমুলেশন সম্পন্ন। বাস্তব টাকা পাঠানো হয়নি।|转账模拟已完成，未转移真实资金。|Simulasi pemindahan selesai. Tiada wang sebenar dipindahkan.
replay|Previous receipt returned; no second debit.|আগের receipt ফেরত দেওয়া হয়েছে; দ্বিতীয়বার debit হয়নি।|已返回原收据，未重复扣款。|Resit terdahulu dikembalikan; tiada debit kedua.
receipt_details|Receipt details|রসিদের বিবরণ|收据详情|Butiran resit
receipt_id|Receipt reference|রসিদের reference|收据编号|Rujukan resit
wallet_title|Your wallet|আপনার ওয়ালেট|您的钱包|Dompet anda
currency|Currency|মুদ্রা|币种|Mata wang
balance|Balance|ব্যালেন্স|余额|Baki
wallet_empty|Your wallet is empty.|আপনার ওয়ালেট খালি।|您的钱包为空。|Dompet anda kosong.
add_funds_title|Add simulated funds|সিমুলেটেড অর্থ যোগ করুন|添加模拟资金|Tambah dana simulasi
fund_currency|Funding currency|অর্থ যোগের মুদ্রা|入账币种|Mata wang pembiayaan
fund_amount|Amount to add|যোগ করার পরিমাণ|添加金额|Amaun untuk ditambah
add_funds|Add funds|অর্থ যোগ করুন|添加资金|Tambah dana
wallet_note|Funds added here are simulated and recorded in the audit history.|এখানে যোগ করা অর্থ সিমুলেটেড এবং audit history-তে সংরক্ষিত।|此处添加的资金为模拟资金，并记录于审计历史。|Dana yang ditambah di sini adalah simulasi dan direkodkan dalam sejarah audit.
audit_title|Audit integrity|অডিটের অখণ্ডতা|审计完整性|Integriti audit
audit_verified|Audit chain verified · {count} events|Audit chain যাচাই হয়েছে · {count}টি ঘটনা|审计链已验证 · {count} 个事件|Rantaian audit disahkan · {count} peristiwa
audit_failed|Audit verification failed. Transfer execution is disabled.|Audit যাচাই ব্যর্থ। লেনদেন চালানো বন্ধ আছে।|审计验证失败，转账执行已禁用。|Pengesahan audit gagal. Pelaksanaan pemindahan dinyahdayakan.
audit_history|Your activity history|আপনার কার্যক্রমের ইতিহাস|您的活动历史|Sejarah aktiviti anda
event|Event|ঘটনা|事件|Peristiwa
time|Time (UTC)|সময় (UTC)|时间（UTC）|Masa (UTC)
seq|Sequence|ক্রম|序号|Urutan
no_events|No events available.|কোনো ঘটনা নেই।|暂无事件。|Tiada peristiwa tersedia.
pdf_receipt|Download receipt (PDF)|রসিদ ডাউনলোড (PDF)|下载收据（PDF）|Muat turun resit (PDF)
pdf_invoice|Download planning invoice (PDF)|পরিকল্পনার invoice ডাউনলোড (PDF)|下载规划账单（PDF）|Muat turun invois perancangan (PDF)
pdf_statement|Download statement (PDF)|বিবরণী ডাউনলোড (PDF)|下载报表（PDF）|Muat turun penyata (PDF)
pdf_summary|Download summary (PDF)|সারসংক্ষেপ ডাউনলোড (PDF)|下载摘要（PDF）|Muat turun ringkasan (PDF)
pdf_note|Financial documents are issued in English with unchanged currency codes and amounts.|মুদ্রার code ও পরিমাণ অপরিবর্তিত রেখে আর্থিক document English-এ তৈরি হয়।|财务文件以英文出具，币种代码和金额保持不变。|Dokumen kewangan dikeluarkan dalam bahasa Inggeris dengan kod mata wang dan amaun dikekalkan.
team_title|The people behind StudentBridge|StudentBridge-এর নির্মাতা দল|StudentBridge 开发团队|Pasukan di sebalik StudentBridge
team_intro|A student-led team building clearer cross-border financial planning.|সীমান্ত পেরিয়ে আর্থিক পরিকল্পনা সহজ করতে কাজ করা শিক্ষার্থী দল।|由学生组成的团队，致力于更清晰的跨境财务规划。|Pasukan diterajui pelajar untuk perancangan kewangan rentas sempadan yang lebih jelas.
team_leader|Team Leader|দলনেতা|团队负责人|Ketua pasukan
team_member|Team Member|দলের সদস্য|团队成员|Ahli pasukan
pursuing|Pursuing|অধ্যয়নরত|在读|Sedang mengikuti pengajian
degree|Degree|ডিগ্রি|学位|Ijazah
faculty|Faculty|অনুষদ|学院|Fakulti
university|University|বিশ্ববিদ্যালয়|大学|Universiti
email|Email|ইমেইল|电子邮件|E-mel
phone|Phone|ফোন|电话|Telefon
whatsapp_only|WhatsApp ONLY|শুধু WhatsApp|仅限 WhatsApp|WhatsApp SAHAJA
email_member|Email member|ইমেইল করুন|发送邮件|E-mel ahli
whatsapp_member|Contact on WhatsApp|WhatsApp-এ যোগাযোগ|通过 WhatsApp 联系|Hubungi melalui WhatsApp
placeholder_member|Second-member details will be updated.|দ্বিতীয় সদস্যের তথ্য পরে যোগ হবে।|第二位成员资料将稍后更新。|Butiran ahli kedua akan dikemas kini.
photo_help|Profile images are managed in the team's local image folders.|Profile image দলের নির্দিষ্ট local image folder-এ রাখা হয়।|头像由团队本地图片文件夹管理。|Gambar profil diurus dalam folder imej setempat pasukan.
guide_intro|Everything you need to use StudentBridge, in one place.|StudentBridge ব্যবহারের সব নির্দেশনা এক জায়গায়।|使用 StudentBridge 所需的全部说明，集中于此。|Semua panduan penggunaan StudentBridge di satu tempat.
guide_start|Getting started|শুরু করার পদ্ধতি|开始使用|Bermula
guide_start_body|Choose a university programme, confirm your fee period and calculate your budget. Convert the total into your home currency. Review a signed quote before confirming a simulated transfer.|বিশ্ববিদ্যালয়ের programme বাছুন, fee-এর মেয়াদ নিশ্চিত করে budget হিসাব করুন। নিজের মুদ্রায় মোট দেখুন। সিমুলেটেড transfer নিশ্চিত করার আগে signed quote যাচাই করুন।|选择大学专业，确认费用周期并计算预算。将总额换算为本国货币，确认模拟转账前先核对签名报价。|Pilih program universiti, sahkan tempoh yuran dan kira belanjawan. Tukar jumlah kepada mata wang negara anda. Semak sebut harga bertandatangan sebelum mengesahkan pemindahan simulasi.
guide_questions|Example questions for AI Assistant|AI সহায়কের জন্য উদাহরণ প্রশ্ন|AI 助手示例问题|Contoh soalan untuk Pembantu AI
guide_question_note|Use one amount and explicit SOURCE to TARGET currency codes. Unclear or reversed wording may require clarification.|একটি পরিমাণ ও SOURCE to TARGET currency code লিখুন। অস্পষ্ট বা উল্টোভাবে লেখা প্রশ্নে clarification লাগতে পারে।|使用单个金额及明确的 SOURCE to TARGET 币种代码。含糊或反向表述可能需要进一步澄清。|Gunakan satu amaun dan kod mata wang SOURCE to TARGET yang jelas. Ayat kabur atau terbalik mungkin memerlukan penjelasan.
guide_fees|Tuition and living costs|টিউশন ও জীবনযাত্রার খরচ|学费与生活费|Yuran dan kos sara hidup
guide_fees_body|Programme references are not your payable invoice. Confirm university, programme, student classification, intake and fee period. Living costs are illustrative assumptions. Include only confirmed funding. Unknown UKM fee periods and current IIUC CSE fees require your own verified information.|Programme reference আপনার পরিশোধযোগ্য invoice নয়। বিশ্ববিদ্যালয়, programme, শিক্ষার্থী শ্রেণি, intake ও fee-এর মেয়াদ নিশ্চিত করুন। জীবনযাত্রার খরচ উদাহরণভিত্তিক অনুমান। কেবল নিশ্চিত অর্থায়ন যোগ করুন। UKM-এর অস্পষ্ট fee period ও IIUC CSE-এর current fee নিজের যাচাইকৃত তথ্য দিয়ে দিন।|专业费用参考并非您的应付账单。请确认大学、专业、学生类别、入学批次及费用周期。生活费为示例假设，仅计入已确认资金。UKM 未明确的费用周期和 IIUC CSE 当前费用须由您提供已核实资料。|Rujukan program bukan invois perlu bayar anda. Sahkan universiti, program, kategori pelajar, ambilan dan tempoh yuran. Kos sara hidup ialah andaian ilustrasi. Masukkan pembiayaan disahkan sahaja. Tempoh yuran UKM yang tidak jelas dan yuran CSE IIUC semasa memerlukan maklumat disahkan anda.
guide_transfer|Transfers, confirmations and receipts|লেনদেন, confirmation ও রসিদ|转账、确认与收据|Pemindahan, pengesahan dan resit
guide_transfer_body|All providers, fees and wallet transfers are simulated; no real payment service is connected. Add simulated wallet funds, compare providers, generate a quote and confirm its last six characters. Quotes expire after three minutes. Repeating a completed quote returns its original receipt without a second debit.|সব provider, fee ও wallet transfer সিমুলেটেড; কোনো real payment service যুক্ত নেই। Wallet-এ সিমুলেটেড অর্থ যোগ করে provider তুলনা করুন, quote তৈরি করে শেষ ছয় অক্ষর নিশ্চিত করুন। Quote তিন মিনিট পরে শেষ হয়। সম্পন্ন quote আবার চালালে আগের receipt ফেরত আসে, দ্বিতীয়বার debit হয় না।|所有服务商、费用及钱包转账均为模拟，未连接真实支付服务。添加模拟资金、比较服务商、生成报价并确认最后六个字符。报价三分钟后到期。重复执行已完成报价会返回原收据，不重复扣款。|Semua penyedia, fi dan pemindahan dompet adalah simulasi; tiada perkhidmatan pembayaran sebenar disambungkan. Tambah dana simulasi, bandingkan penyedia, jana sebut harga dan sahkan enam aksara terakhir. Sebut harga tamat selepas tiga minit. Ulangan sebut harga selesai mengembalikan resit asal tanpa debit kedua.
guide_pdf|PDF receipts and planning invoices|PDF রসিদ ও planning invoice|PDF 收据及规划账单|Resit PDF dan invois perancangan
guide_pdf_body|Every document has a StudentBridge header and the requested computer-generated footer. Receipts confirm simulated activity only. Planning invoices are unpaid estimates based on your inputs, not official university bills or proof of payment.|প্রতিটি document-এ StudentBridge header ও computer-generated footer থাকে। Receipt কেবল simulated activity নিশ্চিত করে। Planning invoice নিজের input অনুযায়ী unpaid estimate, বিশ্ববিদ্যালয়ের official bill বা payment proof নয়।|每份文件均含 StudentBridge 页眉及所要求的计算机生成页脚。收据仅确认模拟活动。规划账单是基于输入的未支付估算，并非大学官方账单或付款凭证。|Setiap dokumen mempunyai pengepala StudentBridge dan pengaki dijana komputer yang diminta. Resit mengesahkan aktiviti simulasi sahaja. Invois perancangan ialah anggaran belum dibayar berdasarkan input anda, bukan bil rasmi universiti atau bukti pembayaran.
connections|Connections & calculation settings|সংযোগ ও হিসাবের settings|连接与计算设置|Tetapan sambungan & pengiraan
fx_source|Exchange-rate source|Exchange rate-এর উৎস|汇率来源|Sumber kadar pertukaran
fx_settings_help|Live references need internet. The offline reference contains invented rates for practice and must not be treated as market data.|Live reference-এর জন্য internet দরকার। Offline reference-এ practice-এর জন্য বানানো rate আছে; market data হিসেবে ব্যবহার করবেন না।|实时获取参考汇率需要网络。离线参考包含练习用的虚构汇率，不可当作市场数据。|Rujukan langsung memerlukan internet. Rujukan luar talian mengandungi kadar rekaan untuk latihan dan bukan data pasaran.
ai_engine|AI engine|AI engine|AI 引擎|Enjin AI
offline_engine|Built-in assistant|অন্তর্নির্মিত সহায়ক|内置助手|Pembantu terbina dalam
groq_engine|Groq · cloud|Groq · cloud|Groq · 云端|Groq · awan
ollama_engine|Ollama · local|Ollama · local|Ollama · 本地|Ollama · setempat
planner_model|Planner model|পরিকল্পনাকারী model|规划模型|Model perancang
reviewer_model|Reviewer model|যাচাইকারী model|审核模型|Model penyemak
model_list|List available models|উপলব্ধ model দেখুন|列出可用模型|Senaraikan model tersedia
models_unavailable|Could not load models. Check your local key or Ollama connection.|Model লোড হয়নি। Local key বা Ollama connection দেখুন।|无法加载模型，请检查本地密钥或 Ollama 连接。|Model tidak dapat dimuatkan. Semak kunci setempat atau sambungan Ollama.
cloud_consent|Allow masked questions / numeric budgets and public sources to Groq|Masked question / সংখ্যাভিত্তিক budget ও public source Groq-এ পাঠাতে সম্মতি|允许向 Groq 发送脱敏问题、数值预算及公开资料|Benarkan soalan bertopeng / belanjawan berangka dan sumber awam dihantar ke Groq
engine_help|The built-in assistant needs no key and does not use an LLM. Groq needs a local API key and free-plan quotas apply. Ollama runs downloaded models on your PC. Two-model review may abstain when outputs disagree.|অন্তর্নির্মিত সহায়কে key বা LLM লাগে না। Groq-এর local API key লাগে এবং free quota সীমিত। Ollama PC-তে downloaded model চালায়। দুটি model একমত না হলে ফল আটকে দিতে পারে।|内置助手无需密钥，也不使用 LLM。Groq 需要本地 API 密钥，且受免费额度限制。Ollama 在您的电脑上运行已下载模型。双模型输出不一致时可能拒绝给出结果。|Pembantu terbina dalam tidak memerlukan kunci dan tidak menggunakan LLM. Groq memerlukan kunci API setempat dan tertakluk pada kuota percuma. Ollama menjalankan model dimuat turun pada PC anda. Semakan dua model boleh berhenti apabila output bercanggah.
security_guide|Security & algorithm|নিরাপত্তা ও algorithm|安全与算法|Keselamatan & algoritma
security_body|SAGE-FX combines source retrieval, two-model checks, exact Decimal calculations, anomaly screening, signed quotes with atomic execution, and protected audit/storage. Server permissions, expiry, explicit confirmation and replay protection remain enforced in every language. This integration does not establish research novelty by itself.|SAGE-FX-এ source retrieval, two-model check, Decimal হিসাব, anomaly screening, atomic execution-সহ signed quote ও protected audit/storage আছে। সব ভাষাতেই server permission, expiry, confirmation ও replay protection কার্যকর থাকে। কেবল এই সমন্বয় research novelty প্রমাণ করে না।|SAGE-FX 结合来源检索、双模型核对、精确 Decimal 计算、异常筛查、签名报价与原子执行，以及受保护的审计与存储。任何语言下均执行权限、过期、明确确认与防重复规则。此集成本身不构成研究创新的证明。|SAGE-FX menggabungkan carian sumber, semakan dua model, pengiraan Decimal tepat, saringan anomali, sebut harga bertandatangan dengan pelaksanaan atomik dan audit/storan dilindungi. Kebenaran pelayan, tamat tempoh, pengesahan jelas dan perlindungan ulangan dikuatkuasakan dalam semua bahasa. Integrasi ini sahaja tidak membuktikan kebaharuan penyelidikan.
privacy_body|Keep passwords, API keys, bank identifiers and passports out of questions. Saved plans and audit payloads are encrypted locally. A compromised PC or copied database/key requires stronger external protection; keep a matching runtime backup and exported audit head separately.|প্রশ্নে password, API key, bank identifier বা passport দেবেন না। Saved plan ও audit payload local-এ encrypted থাকে। PC compromise বা database/key copy-এর বিরুদ্ধে বাইরের সুরক্ষা দরকার; matching runtime backup ও exported audit head আলাদা রাখুন।|请勿在问题中输入密码、API 密钥、银行标识或护照信息。保存的计划与审计内容在本地加密。电脑被入侵或数据库及密钥被复制时，需要更强的外部保护；请分别保管匹配的运行数据备份及导出的审计头。|Jangan masukkan kata laluan, kunci API, pengenal bank atau pasport dalam soalan. Pelan dan kandungan audit disulitkan secara setempat. PC terjejas atau pangkalan data/kunci disalin memerlukan perlindungan luar yang lebih kukuh; simpan sandaran runtime sepadan dan kepala audit dieksport secara berasingan.
setup_guide|Setup, accounts & troubleshooting|Setup, অ্যাকাউন্ট ও সমস্যার সমাধান|设置、账户与故障排查|Persediaan, akaun & penyelesaian masalah
setup_guide_body|Install requirements using your virtual environment and run Streamlit. Configure cloud keys only in your local .env file, then restart. For additional accounts or a password reset, use the local account script. Detailed commands are in README.md and SETUP_BN.md.|Virtual environment দিয়ে requirements install করে Streamlit চালান। Cloud key শুধু local .env file-এ দিয়ে restart করুন। নতুন account বা password reset-এর জন্য local account script চালান। বিস্তারিত command README.md ও SETUP_BN.md-তে আছে।|使用虚拟环境安装依赖并运行 Streamlit。云端密钥仅配置在本地 .env 文件中，然后重启。新增账户或重置密码请使用本地账户脚本。详细命令见 README.md 和 SETUP_BN.md。|Pasang keperluan menggunakan persekitaran maya dan jalankan Streamlit. Konfigurasi kunci awan hanya dalam fail .env setempat, kemudian mula semula. Gunakan skrip akaun setempat untuk akaun tambahan atau tetapan semula kata laluan. Arahan terperinci dalam README.md dan SETUP_BN.md.
technical_details|Technical details (original language)|কারিগরি বিবরণ (মূল ভাষা)|技术详情（原文）|Butiran teknikal (bahasa asal)
generic_error|This request could not be completed. Check the entered values or connection settings.|কাজটি সম্পন্ন হয়নি। দেওয়া তথ্য বা connection settings দেখুন।|无法完成此请求，请检查输入值或连接设置。|Permintaan ini tidak dapat diselesaikan. Semak nilai dimasukkan atau tetapan sambungan.
amount_error|Enter a valid positive amount using the currency's allowed decimal places.|মুদ্রার অনুমোদিত দশমিক অনুযায়ী সঠিক ধনাত্মক পরিমাণ দিন।|请输入有效正金额，并遵守该币种的小数位要求。|Masukkan amaun positif yang sah mengikut bilangan tempat perpuluhan mata wang.
expiry_error|This quote has expired. Create a fresh quote.|Quote-এর মেয়াদ শেষ। নতুন quote তৈরি করুন।|此报价已过期，请重新创建。|Sebutan harga tamat tempoh. Cipta yang baharu.
approval_error|Review the quote, tick approval and enter the correct final six characters.|Quote যাচাই করে approval দিন ও সঠিক শেষ ছয় অক্ষর লিখুন।|请核对报价、勾选同意并输入正确的最后六个字符。|Semak sebut harga, tandakan kelulusan dan masukkan enam aksara terakhir yang betul.
funds_error|Insufficient simulated funds. Add funds in Wallet & Audit.|সিমুলেটেড অর্থ যথেষ্ট নেই। ওয়ালেট ও অডিটে অর্থ যোগ করুন।|模拟资金不足，请在钱包与审计中添加资金。|Dana simulasi tidak mencukupi. Tambah dana dalam Dompet & audit.
permission_error|This account does not have permission for that action.|এই অ্যাকাউন্টে কাজটির অনুমতি নেই।|此账户无权执行该操作。|Akaun ini tiada kebenaran untuk tindakan tersebut.
password_error|Use a password of 12–128 characters.|১২–১২৮ অক্ষরের password ব্যবহার করুন।|请使用 12 至 128 个字符的密码。|Gunakan kata laluan 12–128 aksara.
cloud_error|Enable cloud consent in Guide for User before using Groq.|Groq ব্যবহারের আগে ব্যবহার নির্দেশিকায় cloud consent দিন।|使用 Groq 前，请在用户指南中启用云端同意。|Aktifkan persetujuan awan dalam Panduan pengguna sebelum menggunakan Groq.
mode_changed|Rate settings changed. Compare providers again before creating a quote.|Rate settings বদলেছে। Quote তৈরির আগে আবার provider তুলনা করুন।|汇率设置已更改，请重新比较服务商后再创建报价。|Tetapan kadar berubah. Bandingkan penyedia sekali lagi sebelum mencipta sebut harga.
Local|Local|স্থানীয়|本地学生|Tempatan
International|International|আন্তর্জাতিক|国际学生|Antarabangsa
Verify fee eligibility|Verify fee eligibility|প্রযোজ্য fee যাচাই করুন|核实费用适用资格|Sahkan kelayakan yuran
viewer|Viewer|দর্শক|查看者|Pemerhati
planner_role|Planner|পরিকল্পনাকারী|规划者|Perancang
executor|Executor|লেনদেনকারী|执行者|Pelaksana
account_created|Account created|অ্যাকাউন্ট তৈরি|账户已创建|Akaun dicipta
login_event|Signed in|সাইন ইন|已登录|Log masuk
sandbox_top_up|Simulated funds added|সিমুলেটেড অর্থ যোগ|已添加模拟资金|Dana simulasi ditambah
quote_created|Quote created|Quote তৈরি|报价已创建|Sebutan harga dicipta
sandbox_transfer_completed|Transfer simulation completed|লেনদেন সিমুলেশন সম্পন্ন|转账模拟已完成|Simulasi pemindahan selesai
execution_denied|Action declined|কার্যক্রম আটকে দেওয়া হয়েছে|操作已拒绝|Tindakan ditolak
profile_saved|Plan saved|পরিকল্পনা সংরক্ষিত|计划已保存|Pelan disimpan
password_reset|Password reset|Password পরিবর্তন|密码已重置|Kata laluan ditetapkan semula
source_original_note|Official names and source text retain their original language.|অফিসিয়াল নাম ও উৎসের লেখা মূল ভাষায় রাখা হয়েছে।|官方名称及来源文本保留原语言。|Nama rasmi dan teks sumber dikekalkan dalam bahasa asal.
"""

_ROWS = _ROWS.strip() + "\n" + EXTRA_ROWS.strip()
_ROWS = _ROWS.replace(
    "Version 3.0|সংস্করণ ৩.০|版本 3.0|Versi 3.0", "Version 4.0|সংস্করণ ৪.০|版本 4.0|Versi 4.0"
)
CATALOG = {language: {} for language in LANGUAGES}
for row in _ROWS.strip().splitlines():
    parts = row.split("|")
    if len(parts) != 5:
        raise RuntimeError(f"Translation row has {len(parts)} columns: {parts[0]}")
    key, *values = parts
    if key in CATALOG["en"]:
        raise RuntimeError(f"Duplicate translation key: {key}")
    for language, value in zip(LANGUAGES, values):
        CATALOG[language][key] = value


class Translator:
    def __init__(self, language="en"):
        self.language = language if language in LANGUAGES else "en"

    def __call__(self, key, **values):
        return CATALOG[self.language][key].format(**values)

    def currency_label(self, code):
        if code == "CNH":
            names = {
                "en": "Offshore yuan",
                "bn": "অফশোর ইউয়ান",
                "zh": "离岸人民币",
                "ms": "Yuan luar pesisir",
            }
            name = names[self.language]
        else:
            name = get_currency_name(code, locale=LOCALES[self.language])
        return f"{code} · {name}" + (" (RMB)" if code == "CNY" else "")

    def error(self, exc):
        message = str(exc).lower()
        if "12–128" in message or "12-128" in message:
            return self("password_error")
        if "insufficient" in message:
            return self("funds_error")
        if "quote expired" in message:
            return self("expiry_error")
        if "tick approval" in message:
            return self("approval_error")
        if "cloud consent" in message:
            return self("cloud_error")
        if "session expired" in message or "please sign in" in message:
            return self("login_title") + ". " + self("sign_in")
        if (
            "cannot execute" in message
            or "only an executor" in message
            or "viewer accounts" in message
        ):
            return self("permission_error")
        if any(
            part in message
            for part in (
                "plain number",
                "decimal places",
                "must be positive",
                "cannot be negative",
                "invalid amount",
            )
        ):
            return self("amount_error")
        if "live fx unavailable" in message:
            return self("fx_unavailable")
        return self("generic_error")
