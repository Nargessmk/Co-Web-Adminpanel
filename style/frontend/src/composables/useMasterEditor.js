import { ref } from 'vue'
import { useQuasar } from 'quasar'
import api from 'src/services/api'
import { useHomeContent } from 'src/composables/useHomeContent'
import { useSiteContent } from 'src/composables/useSiteContent'

const STORAGE_KEY = 'cloudland_master_content_v1'

// Default Service Items (6 cards matching index.html)
export const DEFAULT_SERVICES = [
  {
    title: 'رایانش ابری و Edge',
    text: 'پیاده‌سازی شبکه‌های توزیع‌شده با پاسخ‌دهی نزدیک به کاربر، لتنسی زیر ۱۵ میلی‌ثانیه و بدون قطعی.',
    iconSrc: '/uploads/icons3d/cloud.svg',
    features: ['اتصال به ۱۶۰+ نود جهانی', 'توزیع هوشمند بار (Anycast)'],
  },
  {
    title: 'معماری میکروسرویس',
    text: 'طراحی سیستم‌های ماژولار سازمانی با مقیاس‌پذیری خودکار، ایزولاسیون کامل کانتینرها و بازیابی آنی.',
    iconSrc: '/uploads/icons3d/microservices.svg',
    features: ['کلاسترهای کانتینری مدیریت‌شده', 'اتوماسیون استقرار CI/CD'],
  },
  {
    title: 'هوش مصنوعی و یادگیری ماشین',
    text: 'یکپارچه‌سازی مدل‌های زبانی (LLM) و خطوط پردازش داده‌های حجیم بر روی شتاب‌دهنده‌های پیشرفته گرافیکی.',
    iconSrc: '/uploads/icons3d/ai.svg',
    features: ['خطوط پردازش بلادرنگ NLP', 'بهینه‌سازی مدل‌ها برای استقرار محلی'],
  },
  {
    title: 'طراحی محصول و تجربه کاربری',
    text: 'خلق رابط‌های کاربری چشم‌نواز با هویت بصری اختصاصی، سیستم دیزاین یکپارچه و رعایت ارگونومی تعاملی.',
    iconSrc: '/uploads/icons3d/ux.svg',
    features: ['سیستم دیزاین‌های مقیاس‌پذیر', 'تست کاربردپذیری و دسترسی‌پذیری'],
  },
  {
    title: 'امنیت ابری و Zero-Trust',
    text: 'حفاظت چندسطحی از داده‌های حساس سازمانی، رمزنگاری AES-256 و ایزولاسیون کامل ترافیک درون‌سازمانی.',
    iconSrc: '/uploads/icons3d/security.svg',
    features: ['انطباق با استانداردهای ISO 27001', 'احراز هویت بیومتریک و توکن‌های سخت‌افزاری'],
  },
  {
    title: 'مهندسی و تحلیل کلان‌داده',
    text: 'استخراج ارزش از جریان داده‌ها با دریاچه‌های داده پرسرعت، ساختارهای انبار مدرن و داشبوردهای پایش لحظه‌ای.',
    iconSrc: '/uploads/icons3d/bigdata.svg',
    features: ['خطوط انتقال Kafka و Spark', 'مدل‌سازی پیش‌بینانه رفتار کاربران'],
  },
]

// Default Projects (3 showcase cards)
export const DEFAULT_PROJECTS = [
  {
    num: '۰۱',
    category: 'زیرساخت ابری و لجستیک',
    title: 'سامانه جامع هوشمند لجستیک و انبارداری توزیع‌شده',
    description: 'پلتفرم توزیع‌شده با قابلیت پردازش و رهگیری همزمان میلیون‌ها مرسوله در کشور، مسیریابی خودکار با الگوریتم ژنتیک و پاسخ‌دهی پایدار به کلاینت‌های لبه شبکه بدون قطعی.',
    metrics: [
      { val: '۱.۸M+', lbl: 'تراکنش روزانه' },
      { val: '۱۲ms', lbl: 'لتنسی نودها' },
      { val: '۹۹.۹۹۹%', lbl: 'SLA پایداری' },
    ],
    tags: ['Kafka', 'Golang Core', 'Kubernetes', 'Redis Cluster'],
    image: '/uploads/home/contact-datacenter.jpg',
    badge: 'استقرار فعال در ۲۶ استان کشور',
    link: '/contact',
  },
  {
    num: '۰۲',
    category: 'فین‌تک و سامانه‌های مالی',
    title: 'هسته بانکداری باز و درگاه تسویه آنی بین‌بانکی',
    description: 'معماری میکروسرویس فوق‌امن بر پایه استانداردهای مالی ISO 8583 با ماژول رمزنگاری سخت‌افزاری HSM، ایزولاسیون کامل کانتینرها و تسویه آنی تراکنش‌های بین‌بانکی با تاخیر زیر ۸ میلی‌ثانیه.',
    metrics: [
      { val: '۸ms', lbl: 'تاخیر پردازش تراکنش' },
      { val: 'Zero-Trust', lbl: 'رمزنگاری سخت‌افزاری' },
      { val: 'ISO 8583', lbl: 'استاندارد بانکی' },
    ],
    tags: ['Rust Async', 'mTLS 1.3', 'PostgreSQL Sharded', 'Vault'],
    image: '/uploads/home/hero-corporate.jpg',
    badge: 'امنیت بانکی Zero-Trust و HSM',
    link: '/contact',
  },
  {
    num: '۰۳',
    category: 'هوش مصنوعی و لبه',
    title: 'موتور بلادرنگ تبدیل صوت به متن فارسی در لبه',
    description: 'فشرده‌سازی و بهینه‌سازی مدل‌های یادگیری عمیق Conformer برای استقرار مستقیم بر روی چیپ‌های سخت‌افزاری Edge، با پیاده‌سازی مصوبات اداری بدون نیاز به اینترنت و بدون ارسال داده به سرور خارجی.',
    metrics: [
      { val: '۹۸.۵٪', lbl: 'دقت بازشناسی کلمات' },
      { val: '<۲۵۰MB', lbl: 'مصرف حافظه رم' },
      { val: 'Realtime', lbl: 'پردازش صوت آفلاین' },
    ],
    tags: ['PyTorch C++', 'ONNX Runtime', 'Edge TPU', 'FastAPI'],
    image: '/uploads/home/contact-programming.jpg',
    badge: 'پردازش کاملاً آفلاین و ایزوله',
    link: '/contact',
  },
]

// Default About Section & Full Page Data
export const DEFAULT_ABOUT = {
  badge: 'درباره کهکشان هوشمند',
  title: 'اصالت مهندسی، انضباط سازمانی',
  desc: 'ما یک استودیوی پیشرو در معماری نرم‌افزارهای تجاری و زیرساخت‌های ابری هستیم که دقت فنی را با استانداردهای بین‌المللی سازمانی تلفیق می‌کنیم. رویکرد ما در مهندسی نرم‌افزار متکی بر شفافیت کد منبع، کاهش ریسک‌های عملیاتی و ایزولاسیون امنیتی Zero-Trust بنا شده است.',
  button_text: 'آشنایی بیشتر با کهکشان هوشمند',
  button_link: '/about',
  image: '/Modern 3D Tech Dashboard Illustration(1).png',
  chip1_label: 'معماری امنیتی',
  chip1_val: 'Zero-Trust Isolated',
  chip2_label: 'لتنسی لبه شبکه',
  chip2_val: '< ۱۵ms Anycast',
  chip3_label: 'تضمین پایداری کتبی',
  chip3_val: 'SLA ۹۹.۹۹٪ رسمی',
  statementTitle: 'پیشگام در مهندسی سیستم‌های توزیع‌شده با قابلیت اتکای سازمانی',
  statementP1: 'کهکشان هوشمند متشکل از معماران ارشد سیستم، مهندسان زیرساخت ابری و متخصصان داده با سابقه طراحی و اجرای سیستم‌های پرترافیک سازمانی است. رویکرد ما در مهندسی نرم‌افزار متکی بر شفافیت کد منبع، کاهش ریسک‌های عملیاتی و ایزولاسیون امنیتی Zero-Trust بنا شده است.',
  statementP2: 'ما پیچیدگی‌های فنی را به معماری‌های ساده، آزمون‌پذیر و پایدار تبدیل می‌کنیم تا تصمیم‌گیرندگان تجاری بتوانند با آرامش کامل و بدون دغدغه قطعی سرور یا گلوگاه‌های ترافیکی، مسیر رشد کسب‌وکار خود را دنبال کنند.',
  metrics: [
    { val: '+۸۵', title: 'سامانه سازمانی استقراریافته', desc: 'پروژه‌های موفق ملی و تجاری با پایداری کامل' },
    { val: '۹۹.۹۹٪', title: 'تضمین قرارداد سطح خدمات (SLA)', desc: 'پایداری زیرساخت بدون قطعی و وقفه ناخواسته' },
    { val: '< ۱۵ms', title: 'لتنسی شبکه در نقاط لبه Anycast', desc: 'پاسخ‌دهی آنی درخواست‌ها در لبه شبکه ابری' },
    { val: '۲۰+', title: 'متخصصان و معماران ارشد', desc: 'تیم تخصصی با مدارک معتبر بین‌المللی ابری' },
  ],
  values: [
    {
      title: 'معماری تاب‌آور و Zero-Downtime',
      desc: 'تمامی سرویس‌ها با منطق توزیع جغرافیایی، Failover خودکار و ایزولاسیون پردازش طراحی می‌شوند تا حتی در بحرانی‌ترین شرایط ترافیکی بدون وقفه به کار خود ادامه دهند.',
      icon: 'dns',
    },
    {
      title: 'امنیت چندسطحی Zero-Trust',
      desc: 'هیچ درخواستی بدون احراز هویت و رمزنگاری سراسری پذیرفته نمی‌شود. انطباق با استاندارد ISO 27001 و تفکیک لایه‌های دسترسی، امضای امنیتی پروژه‌های ماست.',
      icon: 'security',
    },
    {
      title: 'شفافیت فنی و مالکیت کامل کارفرما',
      desc: 'کد تمیز، مستندسازی RFC استاندارد و تحویل کامل تمام کدهای منبع، کانتینرها و خطوط پایپ‌لاین CI/CD به کارفرما بدون هیچ‌گونه قفل‌شدگی به ارائه‌دهنده خاص.',
      icon: 'code',
    },
    {
      title: 'وسواس در کارایی و لتنسی میلی‌ثانیه‌ای',
      desc: 'پایش مستمر پروفایلینگ مصرف رم و پردازنده و بهینه‌سازی لایه‌های داده با کش‌های توزیع‌شده Redis Cluster برای دستیابی به کمترین زمان پاسخ‌دهی ممکن.',
      icon: 'speed',
    },
  ],
  milestones: [
    { year: '۱۳۹۸', title: 'آغاز فعالیت هسته مهندسی', desc: 'تأسیس کهکشان هوشمند با تمرکز بر مشاوره معماری سیستم‌های توزیع‌شده و پردازش ابری.' },
    { year: '۱۴۰۰', title: 'توسعه پلتفرم ابری Anycast', desc: 'راه‌اندازی زیرساخت لبه با بیش از ۳۰ نقطه حضور (PoP) در سراسر کشور و اتصال مستقیم به IXP.' },
    { year: '۱۴۰۲', title: 'ورود به حوزه مدل‌های پردازش هوش مصنوعی در لبه', desc: 'ارائه راهکارهای فشرده‌سازی و استقرار مدل‌های LLM و پردازش صوت به صورت آفلاین بر روی چیپ‌های Edge.' },
    { year: '۱۴۰۴', title: 'تضمین SLA ۹۹.۹۹٪ برای بیش از ۸۵ سامانه ملی', desc: 'پوشش تراکنش‌های روزانه چندمیلیونی در حوزه‌های بانکی، لجستیک و تلکام بدون حتی یک دقیقه قطعی.' },
  ],
  team: [
    {
      name: 'مهندس آرش رادمنش',
      role: 'معمار ارشد سیستم و هم‌بنیان‌گذار',
      bio: 'بیش از ۱۵ سال سابقه طراحی معماری نرم‌افزارهای تجاری با ترافیک میلیون تراکنش روزانه و متخصص سیستم‌های توزیع‌شده.',
      image: '/uploads/home/contact-programming.jpg',
      tags: ['Distributed Systems', 'Golang Core', 'Kubernetes'],
    },
    {
      name: 'مهندس نیما سهرابی',
      role: 'سرپرست ارشد زیرساخت ابری و DevOps',
      bio: 'متخصص کلاسترهای چندناحیه‌ای کوبرنتیز، امنیت Zero-Trust و اتوماسیون CI/CD با تجارب استقرار بانکی.',
      image: '/uploads/home/contact-datacenter.jpg',
      tags: ['Cloud Architecture', 'Zero-Trust', 'Terraform'],
    },
    {
      name: 'دکتر سارا یزدانی',
      role: 'سرپرست تیم هوش مصنوعی و داده',
      bio: 'پژوهشگر یادگیری عمیق، مدل‌های زبانی بزرگ (LLM) و پردازش بلادرنگ داده‌های صوتی و متنی در لبه شبکه.',
      image: '/uploads/home/hero-corporate.jpg',
      tags: ['Edge AI', 'PyTorch C++', 'RAG Systems'],
    },
    {
      name: 'مهندس مهرداد کیا',
      role: 'مدیر ارشد طراحی محصول و تجربه کاربری',
      bio: 'طراح استراتژیک سیستم‌های دیزاین سازمانی، رابط‌های کاربری تعاملی مدرن و متخصص ارگونومی بصری.',
      image: '/Modern 3D Tech Dashboard Illustration(1).png',
      tags: ['Design Systems', 'Micro-interactions', 'Design Ops'],
    },
  ],
}

// Default Articles Section & Full Page Data
export const DEFAULT_ARTICLES = {
  badge: 'پایگاه دانش و مقالات فنی',
  title: 'تحلیل‌های تخصصی و مقالات مهندسی',
  desc: 'دیدگاه‌ها، درس‌آموخته‌ها و مقالات فنی تیم مهندسی کهکشان هوشمند در حوزه‌های معماری ابری، امنیت، طراحی محصول و هوش مصنوعی.',
  categories: ['همه', 'رایانش ابری', 'معماری میکروسرویس', 'هوش مصنوعی', 'امنیت ابری', 'دیزاین سیستم'],
  items: [
    {
      id: 1,
      title: 'چرا پردازش در لبه شبکه (Edge Computing) آینده پلتفرم‌های پرسرعت است؟',
      excerpt: 'تحلیل دقیق معماری توزیع درخواست‌ها در نزدیک‌ترین فاصله جغرافیایی به کاربر و کاهش ۹۰ درصدی تاخیر بارگذاری.',
      content: `### لزوم حرکت به سمت پردازش در لبه
در دنیای مدرن وب، میلی‌ثانیه‌ها ارزش تجاری تعیین‌کننده‌ای دارند. تاخیر شبکه (Network Latency) نه فقط ناشی از توان سرور، بلکه حاصل فاصله فیزیکی تا دیتاسنتر و مراحل عبور بسته‌ها از گره‌های متعدد مسیریابی است.

#### مزایای اساسی معماری Edge:
۱. **کاهش لتنسی تا زیر ۱۵ میلی‌ثانیه**: انتقال کدهای محاسباتی به گره‌های Anycast در نزدیکی کاربر نهایی.
۲. **کاهش بار سرورهای هسته**: مدیریت ترافیک‌های بازرسی و کش هوشمند لایه‌ای.
۳. **امنیت در لبه**: جلوگیری از حملات DDoS پیش از رسیدن به هسته سامانه.

با بهره‌گیری از پلتفرم لبه کهکشان هوشمند، تمامی فرآیندهای SSR و اعتبارسنجی توکن‌ها در لبه شبکه انجام می‌پذیرد.`,
      category: 'رایانش ابری',
      readTime: '۵ دقیقه مطالعه',
      topic: 'معماری سیستم',
      image: '/uploads/articles/edge-computing.jpg',
      date: '۱۵ شهریور ۱۴۰۵',
      author: {
        name: 'نیما سهرابی',
        role: 'سرپرست زیرساخت ابری',
        avatar: '/uploads/home/contact-datacenter.jpg',
      },
      tags: ['Edge Network', 'Anycast', 'Latency Optimization'],
    },
    {
      id: 2,
      title: 'الگوهای ضدپایداری در مهاجرت به میکروسرویس‌ها و روش‌های پیشگیری از آن',
      excerpt: 'بررسی چالش‌های رایج ارتباطات بین سرویسی، شکست متوالی (Cascading Failures) و پیاده‌سازی Circuit Breaker در عمل.',
      content: `### دام‌های پنهان معماری میکروسرویس
میکروسرویس‌ها مقیاس‌پذیری تیم‌ها را آزاد می‌کنند، اما بدون نظم مهندسی می‌توانند شبکه را به یک کلاف سردرگم از درخواست‌های شکست‌خورده تبدیل نمایند.

#### کلیدی‌ترین الگوهای ضدپایداری:
- **شکست‌های زنجیره‌ای (Cascading Failures)**: زمانی که کندی یک سرویس وابسته، کل صف ارتباطی سرویس‌های بالادست را قفل می‌کند.
- **ارتباطات همزمان بیش‌ازحد (Chatty HTTP Calls)**: جایگزین کردن آن‌ها با رویدادمحوری (Event-Driven) مبتنی بر Kafka.
- **کمبود تایم‌اوت‌های دفاعی**: پیاده‌سازی الگوی Circuit Breaker با کتابخانه‌های مقاوم و مش سرویس mTLS.`,
      category: 'معماری میکروسرویس',
      readTime: '۸ دقیقه مطالعه',
      topic: 'الگوهای توزیع‌شده',
      image: '/uploads/articles/microservices.jpg',
      date: '۲۸ مرداد ۱۴۰۵',
      author: {
        name: 'آرش رادمنش',
        role: 'معمار ارشد سیستم',
        avatar: '/uploads/home/contact-programming.jpg',
      },
      tags: ['Microservices', 'Resilience', 'Circuit Breaker', 'Kafka'],
    },
    {
      id: 3,
      title: 'یکپارچه‌سازی ایمن مدل‌های زبانی بزرگ (LLM) با پایگاه‌داده‌های سازمانی',
      excerpt: 'راهنمای عملی پیاده‌سازی الگوهای RAG با حفظ محرمانگی داده‌ها و جلوگیری از درز اطلاعات حساس کاربران.',
      content: `### RAG سازمانی بدون خطر درز داده
چگونه می‌توان از قدرت هوش مصنوعی مولد بر روی اسناد محرمانه سازمان استفاده کرد بدون اینکه داده‌ها به سرویس‌های ابری عمومی ارسال شوند؟

#### چارچوب معماری RAG ایمن:
۱. **ایزولاسیون کامل دیتابیس برداری**: استقرار Qdrant یا Milvus در شبکه خصوصی VPC.
۲. **مدل‌های بازمتن فشرده**: به‌کارگیری مدل‌های خانواده Llama و Mistral با کوانتیزاسیون ۴ بیتی روی سرورهای محلی GPU.
۳. **کنترل دسترسی مبتنی بر نقش (RBAC)**: فیلتر کردن وکتورهای بازیابی‌شده متناسب با سطح دسترسی کارمند پیش از ارسال به پرامپت نهایی.`,
      category: 'هوش مصنوعی',
      readTime: '۶ دقیقه مطالعه',
      topic: 'RAG & داده سازمانی',
      image: '/uploads/articles/llm-rag.jpg',
      date: '۱۰ مرداد ۱۴۰۵',
      author: {
        name: 'دکتر سارا یزدانی',
        role: 'سرپرست هوش مصنوعی',
        avatar: '/uploads/home/hero-corporate.jpg',
      },
      tags: ['LLM', 'RAG', 'Vector DB', 'Security'],
    },
    {
      id: 4,
      title: 'معماری امنیت Zero-Trust: عبور از فایروال‌های سنتی به احراز هویت پیوسته',
      excerpt: 'چرا مفهوم مرز شبکه (Perimeter) دیگر کارایی ندارد و چگونه هر درخواست را به عنوان یک تهدید بالقوه ایزوله و اعتبارسنجی کنیم.',
      content: `### اصول سه‌گانه تفکر Zero-Trust
در محیط‌های ابری مدرن، شعار اصلی «هرگز اعتماد نکن، همیشه راستی‌آزمایی کن» است.

#### اجزای اساسی معماری:
- **احراز هویت پیوسته هویت و دستگاه**: استفاده از کلیدهای سخت‌افزاری FIDO2 و گواهی‌های کوتاه مدت X.509.
- **میکروسگمنتیشن شبکه**: ایزولاسیون کامل جریان ترافیک بین پادهای کوبرنتیز با استانداردهای Calico یا Cilium.
- **رمزنگاری در حال انتقال و سکون**: استفاده اجباری از mTLS 1.3 با پروتکل‌های سازمانی.`,
      category: 'امنیت ابری',
      readTime: '۷ دقیقه مطالعه',
      topic: 'امنیت سازمانی',
      image: '/uploads/home/contact-datacenter.jpg',
      date: '۲۲ تیر ۱۴۰۵',
      author: {
        name: 'نیما سهرابی',
        role: 'سرپرست زیرساخت ابری',
        avatar: '/uploads/home/contact-datacenter.jpg',
      },
      tags: ['Zero-Trust', 'mTLS', 'Kubernetes Security'],
    },
    {
      id: 5,
      title: 'طراحی سیستم دیزاین سازمانی: پلی میان تیم محصول و تیم فرانت‌اند',
      excerpt: 'بررسی راهکارهای توسعه کامپوننت‌های دسترسی‌پذیر، توکن‌های دیزاین مقیاس‌پذیر و اتوماسیون تست‌های بصری در Figma و Vue.',
      content: `### خلق زبان مشترک میان طراحان و مهندسان
سیستم دیزاین فراتر از یک کیت رابط کاربری است؛ این یک دارایی نرم‌افزاری زنده و قابل نسخه‌بندی برای سازمان است.

#### رویکرد کهکشان هوشمند در سیستم‌های دیزاین:
- **دیزاین توکن‌های ساخت‌یافته**: تعریف متغیرهای معنایی (Semantic Tokens) برای رنگ، فاصله‌گذاری و تایپوگرافی.
- **دسترسی‌پذیری طبق WCAG 2.1 AA**: رعایت کنتراست رنگ و پشتیبانی کامل از صفحه‌خوان‌ها و ناوبری کیبورد.
- **مستندسازی خودکار Storybook**: همگام‌سازی کامپوننت‌های کد با کتابخانه‌های Figma.`,
      category: 'دیزاین سیستم',
      readTime: '۵ دقیقه مطالعه',
      topic: 'طراحی محصول',
      image: '/uploads/general/Modern 3D Tech Dashboard Illustration(1).png',
      date: '۵ تیر ۱۴۰۵',
      author: {
        name: 'مهرداد کیا',
        role: 'مدیر ارشد دیزاین',
        avatar: '/uploads/general/Modern 3D Tech Dashboard Illustration(1).png',
      },
      tags: ['Design System', 'Design Tokens', 'Accessibility'],
    },
    {
      id: 6,
      title: 'مدیریت ترافیک‌های شدید میلیونی با کلاسترهای بهینه‌سازی‌شده Redis',
      excerpt: 'تکنیک‌های عملی شاردینگ، خط لوله درخواست‌ها (Pipelining) و جلوگیری از سناریوی وحشتناک Thundering Herd.',
      content: `### پایداری حافظه در مواجهه با بار ناگهانی
هنگام برگزاری کمپین‌های بزرگ ملی، هزاران درخواست همزمان برای داده‌های یکسان ایجاد می‌شود.

#### استراتژی‌های جلوگیری از قفل شدن دیتابیس:
۱. **Distributed Mutex**: استفاده از قفل‌های توزیع‌شده Redlock برای جلوگیری از استعلام همزمان صدها درخواست به سمت بانک داده اصلی.
۲. **Probabilistic Early Expiration**: بازتولید داده‌های کش پیش از انقضای قطعی کلید به صورت تصادفی.
۳. **Read Replicas Cluster**: پخش درخواست‌های خواندن در چند نود مجزا با لتنسی زیر ۱ میلی‌ثانیه.`,
      category: 'معماری میکروسرویس',
      readTime: '۹ دقیقه مطالعه',
      topic: 'کارایی دیتابیس',
      image: '/uploads/home/hero-corporate.jpg',
      date: '۱۸ خرداد ۱۴۰۵',
      author: {
        name: 'آرش رادمنش',
        role: 'معمار ارشد سیستم',
        avatar: '/uploads/home/contact-programming.jpg',
      },
      tags: ['Redis', 'Caching', 'High Availability', 'Performance'],
    },
  ],
}

// Default Contact Section & Full Page Data
export const DEFAULT_CONTACT = {
  badge: 'ارتباط مستقیم و مشاوره تخصصی',
  title: 'بیایید پروژه نرم‌افزاری و زیرساخت ابری شما را آغاز کنیم',
  description: 'کارشناسان و معماران ارشد کهکشان هوشمند آماده ارائه مشاوره در زمینه معماری نرم‌افزار، زیرساخت ابری و تخمین زمان و هزینه پروژه‌های شما هستند.',
  email: 'contact@smartgalaxy.land',
  phone: '۰۲۱ - ۸۸۹۰ ۱۲۳۴',
  address: 'تهران، نلسون ماندلا (جردن)، بالاتر از میرداماد، برج کهکشان، طبقه ۱۲',
  workingHours: 'شنبه تا چهارشنبه: ۸:۰۰ الی ۱۸:۰۰ | پنجشنبه: ۸:۰۰ الی ۱۳:۰۰',
  emergencySupport: 'پایش و پشتیبانی زیرساخت‌های ابری: ۲۴ ساعته / ۷ روز هفته',
  slaResponse: 'میانگین زمان پاسخ‌دهی به درخواست‌های جدید کمتر از ۲ ساعت است.',
  formTitle: 'درخواست جلسه مشاوره و بررسی پروژه',
  formSubtitle: 'مشخصات اولیه سازمان و نیازمندی‌های فنی خود را ثبت کنید تا در سریع‌ترین زمان با شما تماس بگیریم.',
  faqs: [
    {
      q: 'فرآیند شروع همکاری و بررسی نیازمندی‌ها چگونه است؟',
      a: 'پس از تکمیل فرم، ظرف کمتر از ۲ ساعت کاری معمار ارشد سیستم با شما تماس گرفته و جلسه آنلاین یا حضوری جهت دریافت نیازمندی‌ها و تنظیم توافق‌نامه محرمانگی (NDA) هماهنگ می‌شود.',
    },
    {
      q: 'آیا امکان ارائه قرارداد سطح خدمات (SLA) رسمی وجود دارد؟',
      a: 'بله، تمامی پروژه‌های سازمانی و استقرار زیرساخت‌های ابری ما دارای تضمین رسمی آپ‌تایم ۹۹.۹۹٪ با جبران خسارت مکتوب در قرارداد حقوقی هستند.',
    },
    {
      q: 'تخمین هزینه و زمان‌بندی پروژه چقدر زمان می‌برد؟',
      a: 'معمولاً پس از جلسه اولیه شناخت و دریافت RFC یا مستندات، سند تفصیلی معماری (Architecture Blueprint) به همراه هزینه شفاف ظرف حداکثر ۳ تا ۵ روز کاری تقدیم می‌شود.',
    },
    {
      q: 'آیا سورس‌کد و مالکیت فکری پروژه به کارفرما واگذار می‌شود؟',
      a: 'صد در صد. تمامی کدهای توسعه‌یافته، خطوط استقرار CI/CD و اسناد معماری به صورت کامل و اختصاصی به سازمان شما واگذار خواهد شد.',
    },
  ],
}

// Helper to load stored data safely
function loadStoredData () {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (raw) return JSON.parse(raw)
  } catch (e) {
    console.warn('Could not read master content storage:', e)
  }
  return null
}

const savedData = loadStoredData() || {}

// Reactive singletons
const servicesState = ref(savedData.services || DEFAULT_SERVICES)
const projectsState = ref(savedData.projects || DEFAULT_PROJECTS)
const aboutState = ref(savedData.about || DEFAULT_ABOUT)
const articlesState = ref(savedData.articles || DEFAULT_ARTICLES)
const contactState = ref(savedData.contact || DEFAULT_CONTACT)

// Ensure nested properties are merged if loaded data was from an older schema
if (!aboutState.value.values || !aboutState.value.values.length) {
  aboutState.value = { ...DEFAULT_ABOUT, ...aboutState.value }
}
if (!contactState.value.faqs || !contactState.value.faqs.length) {
  contactState.value = { ...DEFAULT_CONTACT, ...contactState.value }
}
if (!articlesState.value.items || articlesState.value.items.length < 4) {
  articlesState.value = { ...DEFAULT_ARTICLES, ...articlesState.value }
}
(articlesState.value.items || []).forEach((art) => {
  if (!art.author || typeof art.author !== 'object') {
    art.author = { name: 'معمار ارشد سیستم', role: 'کهکشان هوشمند', avatar: '/Modern 3D Tech Dashboard Illustration(1).png' }
  }
})

// Master Editor UI state
const isMasterEditorOpen = ref(false)
const activeTab = ref('hero')
const isSaving = ref(false)

export function useMasterEditor () {
  const $q = useQuasar()
  const { settings: homeSettings, loadHome } = useHomeContent()
  const { settings: siteSettings } = useSiteContent()

  // If localStorage has saved site & footer customizations, merge them into siteSettings
  if (savedData.site && typeof savedData.site === 'object') {
    Object.assign(siteSettings.value, savedData.site)
  }

  function openMasterEditor (tab = 'hero') {
    activeTab.value = tab
    isMasterEditorOpen.value = true
  }

  function closeMasterEditor () {
    isMasterEditorOpen.value = false
  }

  async function saveAllContent (formData) {
    isSaving.value = true
    try {
      // 1. Update our master reactive state
      if (formData.services) servicesState.value = JSON.parse(JSON.stringify(formData.services))
      if (formData.projects) projectsState.value = JSON.parse(JSON.stringify(formData.projects))
      if (formData.about) aboutState.value = JSON.parse(JSON.stringify(formData.about))
      if (formData.articles) articlesState.value = JSON.parse(JSON.stringify(formData.articles))
      if (formData.contact) contactState.value = JSON.parse(JSON.stringify(formData.contact))

      // 2. Persist in local storage
      const storePayload = {
        services: servicesState.value,
        projects: projectsState.value,
        about: aboutState.value,
        articles: articlesState.value,
        contact: contactState.value,
        site: {
          site_name: formData.site_name,
          footer_description: formData.footer_description,
          footer_copyright: formData.footer_copyright,
          footer_credit: formData.footer_credit,
          social_github: formData.social_github,
          social_linkedin: formData.social_linkedin,
          social_telegram: formData.social_telegram,
          social_twitter: formData.social_twitter,
          quick_phone: formData.quick_phone,
          quick_phone_label: formData.quick_phone_label,
          quick_telegram: formData.quick_telegram,
          quick_telegram_label: formData.quick_telegram_label,
          quick_whatsapp: formData.quick_whatsapp,
          quick_whatsapp_label: formData.quick_whatsapp_label,
          quick_cta_link: formData.quick_cta_link,
          quick_cta_label: formData.quick_cta_label,
          quick_is_enabled: formData.quick_is_enabled,
        },
      }
      localStorage.setItem(STORAGE_KEY, JSON.stringify(storePayload))

      // 3. Prepare backend settings payload for Home
      const backendHomePayload = {
        hero_badge: formData.hero_badge || homeSettings.value.hero_badge,
        hero_title: formData.hero_title || homeSettings.value.hero_title,
        hero_title_color: formData.hero_title_color || homeSettings.value.hero_title_color || '#0a0a0a',
        hero_description: formData.hero_description || homeSettings.value.hero_description,
        hero_image_url: formData.hero_image_url || homeSettings.value.hero_image_url,
        hero_scroll_label: formData.hero_scroll_label || homeSettings.value.hero_scroll_label,
        why_badge: formData.why_badge || homeSettings.value.why_badge,
        why_title: formData.why_title || homeSettings.value.why_title,
        why_description: formData.why_description || homeSettings.value.why_description,
        works_eyebrow: formData.works_eyebrow || homeSettings.value.works_eyebrow,
        works_title: formData.works_title || homeSettings.value.works_title,
        works_description: formData.works_description || homeSettings.value.works_description,
        articles_badge: formData.articles?.badge || formData.articles_badge || homeSettings.value.articles_badge,
        articles_title: formData.articles?.title || formData.articles_title || homeSettings.value.articles_title,
        articles_description: formData.articles?.desc || formData.articles_description || homeSettings.value.articles_description,
        cta_title: formData.cta_title || homeSettings.value.cta_title,
        cta_description: formData.cta_description || homeSettings.value.cta_description,
        services: formData.services || servicesState.value,
        projects: formData.projects || projectsState.value,
      }

      if (Array.isArray(formData.buttons)) {
        backendHomePayload.buttons = formData.buttons
      }

      // Sync backend home settings
      try {
        await api.put('/api/home/admin/settings', backendHomePayload)
      } catch (err) {
        console.warn('Backend home settings sync warning:', err)
      }

      // Sync catalog page settings (projects page header)
      if (formData.works_eyebrow || formData.works_title || formData.works_description) {
        try {
          await api.put('/api/catalog-page/admin/settings', {
            page_badge: formData.works_eyebrow || homeSettings.value.works_eyebrow,
            page_title: formData.works_title || homeSettings.value.works_title,
            page_description: formData.works_description || homeSettings.value.works_description,
          })
        } catch (err) {
          console.warn('Backend catalog page settings sync warning:', err)
        }
      }

      // Sync solutions page settings (articles/solutions header)
      if (formData.articles?.badge || formData.articles?.title || formData.articles?.desc) {
        try {
          await api.put('/api/solutions-page/admin/settings', {
            page_badge: formData.articles.badge,
            page_title: formData.articles.title,
            page_description: formData.articles.desc,
          })
        } catch (err) {
          console.warn('Backend solutions page settings sync warning:', err)
        }
      }

      // Sync backend site settings
      const sitePayload = {
        site_name: formData.site_name || siteSettings.value.site_name,
        footer_description: formData.footer_description !== undefined ? formData.footer_description : siteSettings.value.footer_description,
        footer_copyright: formData.footer_copyright || siteSettings.value.footer_copyright,
        footer_contact_phone: formData.contact?.phone || siteSettings.value.footer_contact_phone,
        footer_contact_email: formData.contact?.email || siteSettings.value.footer_contact_email,
        quick_phone: formData.quick_phone !== undefined ? formData.quick_phone : siteSettings.value.quick_phone,
        quick_phone_label: formData.quick_phone_label !== undefined ? formData.quick_phone_label : siteSettings.value.quick_phone_label,
        quick_telegram: formData.quick_telegram !== undefined ? formData.quick_telegram : siteSettings.value.quick_telegram,
        quick_telegram_label: formData.quick_telegram_label !== undefined ? formData.quick_telegram_label : siteSettings.value.quick_telegram_label,
        quick_whatsapp: formData.quick_whatsapp !== undefined ? formData.quick_whatsapp : siteSettings.value.quick_whatsapp,
        quick_whatsapp_label: formData.quick_whatsapp_label !== undefined ? formData.quick_whatsapp_label : siteSettings.value.quick_whatsapp_label,
        quick_cta_link: formData.quick_cta_link !== undefined ? formData.quick_cta_link : siteSettings.value.quick_cta_link,
        quick_cta_label: formData.quick_cta_label !== undefined ? formData.quick_cta_label : siteSettings.value.quick_cta_label,
        quick_is_enabled: formData.quick_is_enabled !== undefined ? formData.quick_is_enabled : siteSettings.value.quick_is_enabled,
      }

      // Also support custom footer social fields & credit in client siteSettings and localStorage
      const extendedSiteData = {
        ...sitePayload,
        footer_credit: formData.footer_credit !== undefined ? formData.footer_credit : siteSettings.value.footer_credit,
        social_github: formData.social_github !== undefined ? formData.social_github : siteSettings.value.social_github,
        social_linkedin: formData.social_linkedin !== undefined ? formData.social_linkedin : siteSettings.value.social_linkedin,
        social_telegram: formData.social_telegram !== undefined ? formData.social_telegram : siteSettings.value.social_telegram,
        social_twitter: formData.social_twitter !== undefined ? formData.social_twitter : siteSettings.value.social_twitter,
      }

      // Update local reactive siteSettings immediately
      Object.assign(siteSettings.value, extendedSiteData)

      try {
        await api.put('/api/site/admin/settings', sitePayload)
      } catch (err) {
        console.warn('Backend site settings sync warning:', err)
      }

      // Sync backend about settings
      if (formData.about) {
        try {
          await api.put('/api/about/admin/settings', {
            hero_badge: formData.about.badge || '',
            hero_title: formData.about.title || '',
            hero_description: formData.about.desc || '',
            statement_title: formData.about.statementTitle || '',
            statement_p1: formData.about.statementP1 || '',
            statement_p2: formData.about.statementP2 || '',
            cta_primary_label: formData.about.button_text || '',
            cta_primary_link: formData.about.button_link || '',
            metrics: formData.about.metrics || [],
            values: formData.about.values || [],
            milestones: formData.about.milestones || [],
          })
        } catch (err) {
          console.warn('Backend about settings sync warning:', err)
        }
      }

      // Sync backend contact settings
      if (formData.contact) {
        try {
          await api.put('/api/contact/admin/settings', {
            hero_badge: formData.contact.badge || '',
            hero_title: formData.contact.title || '',
            hero_description: formData.contact.description || '',
            form_title: formData.contact.formTitle || '',
            form_subtitle: formData.contact.formSubtitle || '',
            phone: formData.contact.phone || '',
            email: formData.contact.email || '',
            address: formData.contact.address || '',
            working_hours: formData.contact.workingHours || '',
            emergency_support: formData.contact.emergencySupport || '',
            sla_response: formData.contact.slaResponse || '',
            faqs: formData.contact.faqs || [],
          })
        } catch (err) {
          console.warn('Backend contact settings sync warning:', err)
        }
      }

      // Sync backend articles
      if (formData.articles && Array.isArray(formData.articles.items)) {
        try {
          await api.put('/api/articles/admin/sync', { items: formData.articles.items })
        } catch (err) {
          console.warn('Backend articles sync warning:', err)
        }
      }

      // Optimistic home settings update
      Object.assign(homeSettings.value, backendHomePayload)

      $q.notify({
        type: 'positive',
        message: 'تمامی تغییرات با موفقیت ذخیره و در سایت اعمال شد.',
        position: 'top',
        timeout: 2500,
      })

      isMasterEditorOpen.value = false
    } catch (e) {
      console.error('Save error:', e)
      $q.notify({
        type: 'negative',
        message: 'خطا در ثبت تغییرات. لطفاً مجدداً تلاش کنید.',
      })
    } finally {
      isSaving.value = false
    }
  }

  function resetToDefaults () {
    servicesState.value = JSON.parse(JSON.stringify(DEFAULT_SERVICES))
    projectsState.value = JSON.parse(JSON.stringify(DEFAULT_PROJECTS))
    aboutState.value = JSON.parse(JSON.stringify(DEFAULT_ABOUT))
    articlesState.value = JSON.parse(JSON.stringify(DEFAULT_ARTICLES))
    contactState.value = JSON.parse(JSON.stringify(DEFAULT_CONTACT))
    localStorage.removeItem(STORAGE_KEY)
    $q.notify({
      type: 'info',
      message: 'محتوا به مقادیر پیش‌فرض ریست شد.',
    })
  }

  function addArticle (article) {
    if (!articlesState.value.items) articlesState.value.items = []
    const newArt = {
      id: Date.now(),
      title: article.title || 'مقاله مهندسی جدید',
      excerpt: article.excerpt || '',
      content: article.content || '',
      category: article.category || 'رایانش ابری',
      readTime: article.readTime || '۵ دقیقه مطالعه',
      topic: article.topic || 'معماری سیستم',
      image: article.image || '/assets/articles/edge-computing.jpg',
      date: article.date || 'امروز',
      author: article.author || { name: 'تیم مهندسی', role: 'کهکشان هوشمند', avatar: '/Modern 3D Tech Dashboard Illustration(1).png' },
      tags: article.tags || ['مهندسی'],
    }
    articlesState.value.items.unshift(newArt)
    saveCurrentStateToStorage()
    // Background sync to backend
    api.put('/api/articles/admin/sync', { items: articlesState.value.items }).catch(() => {})
    return newArt
  }

  function removeArticle (index) {
    if (articlesState.value.items && articlesState.value.items[index]) {
      articlesState.value.items.splice(index, 1)
      saveCurrentStateToStorage()
      api.put('/api/articles/admin/sync', { items: articlesState.value.items }).catch(() => {})
    }
  }

  function saveCurrentStateToStorage () {
    const storePayload = {
      services: servicesState.value,
      projects: projectsState.value,
      about: aboutState.value,
      articles: articlesState.value,
      contact: contactState.value,
    }
    localStorage.setItem(STORAGE_KEY, JSON.stringify(storePayload))
  }

  return {
    isMasterEditorOpen,
    activeTab,
    isSaving,
    servicesState,
    projectsState,
    aboutState,
    articlesState,
    contactState,
    openMasterEditor,
    closeMasterEditor,
    loadMasterContent,
    saveAllContent,
    resetToDefaults,
    addArticle,
    removeArticle,
  }
}

let masterLoadingPromise = null

export async function loadMasterContent () {
  if (masterLoadingPromise) return masterLoadingPromise
  masterLoadingPromise = (async () => {
    try {
      // 1. Home
      const homeRes = await api.get('/api/home').catch(() => null)
      if (homeRes?.data?.data) {
        const hData = homeRes.data.data
        if (Array.isArray(hData.services) && hData.services.length) {
          servicesState.value = hData.services
        } else if (Array.isArray(hData.features) && hData.features.length) {
          servicesState.value = hData.features
        }
        if (Array.isArray(hData.projects) && hData.projects.length) {
          projectsState.value = hData.projects
        } else if (Array.isArray(hData.works) && hData.works.length) {
          projectsState.value = hData.works
        }
      }

      // 2. About
      const aboutRes = await api.get('/api/about').catch(() => null)
      if (aboutRes?.data?.data) {
        const aData = aboutRes.data.data
        aboutState.value = {
          ...aboutState.value,
          badge: aData.settings?.hero_badge || aboutState.value.badge,
          title: aData.settings?.hero_title || aboutState.value.title,
          desc: aData.settings?.hero_description || aboutState.value.desc,
          statementTitle: aData.statementTitle || aboutState.value.statementTitle,
          statementP1: aData.statementP1 || aboutState.value.statementP1,
          statementP2: aData.statementP2 || aboutState.value.statementP2,
          metrics: aData.metrics?.length ? aData.metrics : aboutState.value.metrics,
          values: aData.values?.length ? aData.values : aboutState.value.values,
          milestones: aData.milestones?.length ? aData.milestones : aboutState.value.milestones,
          team: aData.team?.length ? aData.team : aboutState.value.team,
        }
      }

      // 3. Contact
      const contactRes = await api.get('/api/contact').catch(() => null)
      if (contactRes?.data?.data) {
        const cData = contactRes.data.data
        contactState.value = {
          ...contactState.value,
          badge: cData.settings?.hero_badge || contactState.value.badge,
          title: cData.settings?.hero_title || contactState.value.title,
          description: cData.settings?.hero_description || contactState.value.description,
          formTitle: cData.settings?.form_title || contactState.value.formTitle,
          formSubtitle: cData.settings?.form_subtitle || contactState.value.formSubtitle,
          phone: cData.phone || contactState.value.phone,
          email: cData.email || contactState.value.email,
          address: cData.address || contactState.value.address,
          workingHours: cData.workingHours || contactState.value.workingHours,
          emergencySupport: cData.emergencySupport || contactState.value.emergencySupport,
          slaResponse: cData.slaResponse || contactState.value.slaResponse,
          faqs: cData.faqs?.length ? cData.faqs : contactState.value.faqs,
        }
      }

      // 4. Articles
      const articlesRes = await api.get('/api/articles').catch(() => null)
      if (articlesRes?.data?.data && Array.isArray(articlesRes.data.data) && articlesRes.data.data.length) {
        articlesState.value = {
          ...articlesState.value,
          items: articlesRes.data.data,
        }
      }
    } catch (e) {
      console.warn('loadMasterContent error:', e)
    } finally {
      masterLoadingPromise = null
    }
  })()
  return masterLoadingPromise
}

// Initial background prefetch
loadMasterContent().catch(() => {})
