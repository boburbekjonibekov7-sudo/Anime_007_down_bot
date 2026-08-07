# DEPLOY — Webhook bilan Telegram botni serverga ulash

Bu loyiha **polling** rejimidan **webhook** rejimiga o'tkazildi. Endi bot Telegram
update'larini o'zi so'rab olmaydi — Telegram ularni sizning serveringizga
`POST /webhook` orqali o'zi yuboradi. Buning uchun serverda **HTTPS** (domen +
sertifikat) bo'lishi shart, aks holda Telegram so'rov yubormaydi.

## Tayyorlangan fayllar

| Fayl | Vazifasi |
|---|---|
| `main.py` | Webhook endpoint (`/webhook`) + avtomatik `setWebhook` |
| `config.py` | Env o'zgaruvchilar: `WEBHOOK_URL`, `WEBHOOK_PATH`, `WEBHOOK_SECRET`, `PORT`, `DB_PATH` |
| `Dockerfile` | Python **3.11.9** (slim) image |
| `docker-compose.yml` | Bitta buyruq bilan ishga tushirish + DB volume |
| `.env` | Token va sozlamalar (git'ga commit qilinmaydi) |
| `Caddyfile.example` | Avtomatik HTTPS reverse-proxy (tavsiya etiladi) |

> **Muhim:** `WEBHOOK_URL` bo'sh bo'lsa, bot eski **polling** rejimida ishlaydi —
> hech narsa buzilmaydi. `WEBHOOK_URL` to'ldirilsa — webhook rejimida ishlaydi.

---

## VPS'da o'rnatish (Docker + Caddy)

### 1-qadam. Domenni serverga ulang

Domeningizning **A record**'ini VPS IP-manziliga yo'naltiring
(masalan `anime-bot.example.com` → `1.2.3.4`). DNS tarqalishi 5–30 daqiqa davom etadi.

### 2-qadam. Loyihani serverga ko'chiring

```bash
git clone https://github.com/boburbekjonibekov7-sudo/Anime_007_down_bot.git
cd Anime_007_down_bot
```

### 3-qadam. `.env` faylini to'ldiring

```bash
cp .env.example .env
nano .env
```

Eng muhimi — `WEBHOOK_URL`:

```ini
BOT_TOKEN=8811290434:AAFsPEdSWLnpmpME5-LOMr3AyoZ-eYGED-Q
WEBHOOK_URL=https://anime-bot.example.com
WEBHOOK_PATH=/webhook
# Ixtiyoriy, lekin tavsiya etiladi - tasodifiy uzun satr yozing, masalan:
WEBHOOK_SECRET=uzun_tasodifiy_satr_12345
```

### 4-qadam. Botni ishga tushiring

```bash
docker compose up -d --build
docker compose logs -f bot    # loglarni kuzatish
```

Loglarda quyidagini ko'rsangiz — hammasi joyida:

```
✅ Webhook o'rnatildi: https://anime-bot.example.com/webhook
🚀 Bot muvaffaqiyatli ishga tushdi!
```

### 5-qadam. HTTPS (Caddy)

Caddy avtomatik Let's Encrypt sertifikat oladi, hech qanday sozlash shart emas:

```bash
sudo apt install -y caddy
sudo nano /etc/caddy/Caddyfile
```

`Caddyfile.example` dagi qatorni domeningiz bilan yozing:

```
anime-bot.example.com {
    reverse_proxy 127.0.0.1:10000
}
```

So'ng:

```bash
sudo systemctl restart caddy
```

Tekshirish: brauzerda `https://anime-bot.example.com` oching — *"Ani Yuki bot is running!"*
degan yozuv chiqishi kerak.

### 6-qadam. Webhook holatini tekshirish

```bash
curl "https://api.telegram.org/bot8811290434:AAFsPEdSWLnpmpME5-LOMr3AyoZ-eYGED-Q/getWebhookInfo"
```

Natijada:

```json
{"ok":true,"result":{"url":"https://anime-bot.example.com/webhook","pending_update_count":0,"last_error_date":0}}
```

---

## Muqobil: qo'lda webhook o'rnatish

Bot `WEBHOOK_URL` bilan ishga tushganda webhook'ni o'zi o'rnatadi. Agar qo'lda
o'rnatmoqchi bo'lsangiz (masalan bot o'chgan paytda):

```bash
curl -F "url=https://anime-bot.example.com/webhook" \
     -F "secret_token=uzun_tasodifiy_satr_12345" \
     -F "allowed_updates=[]" \
     "https://api.telegram.org/bot<TOKEN>/setWebhook"
```

Webhook'ni o'chirish (polling rejimiga qaytish):

```bash
curl "https://api.telegram.org/bot<TOKEN>/deleteWebhook"
```

---

## Muqobil: Render (PaaS — domen/sertifikat shart emas)

Agar alohida VPS bo'lmasa, Render.com bepul HTTPS beradi:

1. GitHub reponi Render'ga ulang, **Web Service** yarating.
2. Env o'zgaruvchilar:
   - `BOT_TOKEN=8811290434:AAFsPEdSWLnpmpME5-LOMr3AyoZ-eYGED-Q`
   - `PYTHON_VERSION=3.11.9` (yoki `runtime.txt` dagi `python-3.11.9` yetarli)
   - `WEBHOOK_URL=https://<app-nomi>.onrender.com`
   - `PORT` — Render uni avtomatik beradi (kod `PORT` env'ni o'qiydi)
3. Build Command: `pip install -r requirements.txt`
4. Start Command: `python main.py`
5. Render'da disk **ephemeral** — DB ma'lumotlari restartda yo'qoladi. Doimiy
   saqlash uchun Render **Disk** qo'shing va `DB_PATH=/data/anime_bot.db` qiling.

---

## Xavfsizlik eslatmasi

⚠️ Bot tokeni shu suhbatda ochiq matnda yozildi. Token boshqa birovga ma'lum
bo'lib qolgan bo'lishi mumkin. Ishga tushirgandan so'ng **tokenni almashtirishni**
tavsiya qilaman:

1. Telegram'da `@BotFather` → `/token` → botni tanlang → **Revoke current token**
2. Yangi token oling va `.env` dagi `BOT_TOKEN` ni yangilang → `docker compose up -d`

---

## Muammolar (Troubleshooting)

| Muammo | Yechim |
|---|---|
| `404 Not Found` webhook'da | `WEBHOOK_PATH` botdagi endpoint bilan mosligini tekshiring (default `/webhook`). |
| `502 Bad Gateway` | Caddy `reverse_proxy` porti (`10000`) Docker'da ochilganiga ishonch hosil qiling. |
| `getWebhookInfo` da `last_error_message: 404/502` | Domen/server ishlamayapti — `https://domen` ni brauzerda ochib ko'ring. |
| `Unauthorized` xatolari | `WEBHOOK_SECRET` `.env` da yozilgan bo'lsa, Telegram'ga ham xuddi shu secret o'tganini tekshiring. |
| Bot javob bermayapti | `docker compose logs bot` ni qarang; `drop_pending_updates=True` eski xabarlarni o'chiradi. |
| Port band | `.env` da `PORT` ni boshqa qiymatga o'zgartiring va compose'da ham moslang. |
