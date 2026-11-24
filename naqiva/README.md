# Naqiva – صفحة الاختبار

صفحة وحدة باش تعرف واش الناس باغيين Naqiva قبل ما تصنعو. ما كتحتاجش Shopify ولا سيرفر.

**الملفات:**
- `index.html`: الصفحة
- `config.js`: **هادا هو الملف الوحيد اللي خاصك تبدل**
- `app.js`: الكود ديال الفورمولير والتتبع
- `img/`: الصور
- `google-apps-script.gs`: الكود اللي كيسجل التسجيلات فـ Google Sheet

---

## 1. عمر `config.js`

| الخانة | شنو تكتب |
|---|---|
| `PRICE` | الثمن العادي بالدرهم، مثلاً `149`. إلا خليتيه `null` كتبان "الثمن قريب" |
| `EARLY_DISCOUNT` | التخفيض ديال الأوائل (20 كيعني -20%) |
| `WHATSAPP` | رقم الواتساب ديال البراند، مثلاً `"212600000000"` |
| `SHEET_ENDPOINT` | الرابط اللي غادي تاخد فالخطوة 2 |
| `META_PIXEL_ID` / `TIKTOK_PIXEL_ID` | الأرقام ديال الـ Pixel (الخطوة 4) |
| `INSTAGRAM_URL` / `TIKTOK_URL` | روابط الحسابات |

## 2. ربط Google Sheet (10 دقايق)

1. حل Google Sheet جديد وسميه **Naqiva Leads**.
2. من القائمة: **Extensions › Apps Script**.
3. مسح داكشي اللي كاين، ولصق المحتوى ديال `google-apps-script.gs`، ودير **Save**.
4. **Deploy › New deployment** › اختار **Web app**:
   - *Execute as:* **Me**
   - *Who has access:* **Anyone**
5. **Deploy**، وقبل الصلاحيات، ومن بعد نسخ الرابط اللي كيسالي بـ `/exec`.
6. لصقو فـ `SHEET_ENDPOINT` فـ `config.js`.

كل واحد كيسجل كيبان سطر جديد فالورقة **Leads**.

> إلا ما عمرتيش `SHEET_ENDPOINT`، الفورمولير كيحل الواتساب ديال البراند بالمعلومات. وإلا حتى `WHATSAPP` خاوي، **التسجيلات ما كيتسجلوش**.

## 3. طلع الصفحة فالأنترنيت (فابور)

**أسهل طريقة: Netlify Drop**
1. دخل لـ https://app.netlify.com/drop
2. جر الدوسي `naqiva` كامل وطيحو تما.
3. غادي تاخد رابط بحال `https://xxx.netlify.app`. من بعد تقدر تربط بيه `naqiva.com`.

ولا تقدر تستعمل GitHub Pages ولا Vercel.

## 4. التتبع والإعلانات

- **Meta Pixel:** Events Manager › Connect data sources › Web. نسخ الـ ID ولصقو فـ `META_PIXEL_ID`.
- **TikTok Pixel:** TikTok Ads Manager › Assets › Events › Web events. نسخ الـ ID.
- الصفحة كتصيفط **ViewContent** ملي يدخل شي حد، و **Lead** ملي يتسجل.
  فالإعلانات، خلي الهدف ديال الحملة يكون **Leads**.

## 5. اختبار الزوايا (A / B / C)

كل إعلان صيفطو لرابط مختلف:

- `…/?v=a&utm_source=instagram&utm_campaign=test1`: **الما ديالك كيخسر ليك شعرك.**
- `…/?v=b&utm_source=instagram&utm_campaign=test1`: **شعرك ناشف وما فيهش اللمعة؟**
- `…/?v=c&utm_source=tiktok&utm_campaign=test1`: **شامبو مغربي جديد، مصنوع للما ديال المغرب.**

العنوان كيتبدل بوحدو على حسب الرابط، والزاوية كتتسجل مع كل تسجيل فالـ Sheet.
فالآخر، شوف أشمن زاوية جابت تسجيلات أكثر وبثمن أرخص.
النصوص ديال الزوايا كتبدلهم من `VARIANTS` فـ `config.js`.

## ملاحظات

- الصفحة كتقول بوضوح أن المنتوج **فمرحلة الإطلاق** وأن التسجيل **بلا خلاص**. ما تبدلش هادشي حتى يكون عندك المنتوج والتسجيل فـ AMMPS.
- كتجمع أرقام التيليفون، يعني معطيات شخصية. القانون 09-08 كيطلب تصرح بهادشي لـ **CNDP**. سول المحاسب ولا شي مستشار قانوني.
