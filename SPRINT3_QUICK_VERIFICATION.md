# ✅ التحقق السريع من Sprint 3

## 🚀 البدء السريع (2 دقائق)

### Step 1: تطبيق الترقيعات
```bash
cd SMART-METER-BACKEND/backend
python manage.py migrate
```
**النتيجة المتوقعة:**
```
Applying energy.0004_sprint3_anomalies_alertes... OK
```

### Step 2: إنشاء البيانات الاختبارية
```bash
python test_data_sprint3.py
```
**النتيجة المتوقعة:**
```
✓ Anomalie 1: Score HF 0.95 (95%) - Severite: Haute - Statut: NOUVELLE → CONSULTEE → ACQUITTEE
✓ Alerte 1: Statut NOUVELLE → CONSULTEE → ACQUITTEE + Acquittee=True
✓ Alerte 2: Acquittee (مؤرشفة)
✓ عدد الشذوذ: 2 (1 جديد, 1 مؤرشف)
✓ عدد التنبيهات: 2 (1 جديد, 1 مؤرشف)
```

### Step 3: تشغيل السيرفرات

```bash
# Terminal 1: Backend
cd SMART-METER-BACKEND/backend
python manage.py runserver 0.0.0.0:8000

# Terminal 2: Frontend
cd SMART-METER-FRONTEND
npm run dev
```

**النتيجة:**
```
Backend: Starting development server at http://127.0.0.1:8000/
Frontend: Ready in XXXms on http://localhost:3000
```

---

## 📊 التحقق من المتطلبات

### ✅ RG7: Anomalies مرتبطة بـ Consommation

**فحص سريع:**
```bash
python manage.py shell
>>> from energy.models import Anomalie
>>> a = Anomalie.objects.first()
>>> print(f"Score: {a.score_confiance}, Severite: {a.severite}")
Score: 0.95, Severite: HAUTE ✓
```

### ✅ RG8: Score Hugging Face

**API Test:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/ | grep -E "score_confiance|severite"
```

**النتيجة:**
```
"score_confiance": 0.95,
"severite": "HAUTE"
```

### ✅ RG9: الحالات

**Web UI Test:**
1. اذهب إلى: http://localhost:3000/admin/anomalies
2. ستشاهد جدول مع أزرار "استشر" و "وافق"
3. اضغط الزر وشاهد الحالة تتغير ✓

**أو من API:**
```bash
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_consultee/
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_acquittee/
```

### ✅ RG10: التنبيهات في التطبيق

**فتح الصفحة:**
```
http://localhost:3000/admin/alertes
```

**ستشاهد:**
- ✓ جدول التنبيهات
- ✓ فلاتر (statut, acquittee)
- ✓ أزرار الإجراءات
- ✓ التنبيهات ظاهرة في التطبيق فقط

### ✅ RG11: إدارة Admin

**Django Admin:**
```
http://localhost:8000/admin/energy/alerte
```

**الواجهة الرسومية:**
```
http://localhost:3000/admin/alertes
```

**يجب أن ترى:**
- ✓ جميع التنبيهات
- ✓ إمكانية تغيير الحالة
- ✓ أزرار الأرشفة

### ✅ RG12: الأرشفة (Never Delete)

**فحص قاعدة البيانات:**
```bash
python manage.py shell
>>> from energy.models import Alerte
>>> archived = Alerte.objects.filter(acquittee=True).first()
>>> print(f"Acquittee: {archived.acquittee}, Time: {archived.acquittee_at}")
Acquittee: True, Time: 2026-04-28 22:04:25.304879+00:00 ✓
>>> print(f"عدد التنبيهات المؤرشفة: {Alerte.objects.filter(acquittee=True).count()}")
عدد التنبيهات المؤرشفة: 1 ✓
```

**النقطة المهمة:**
- ✗ لم نحذف التنبيه
- ✓ وضعنا علامة: acquittee=True
- ✓ سجلنا الوقت: acquittee_at
- ✓ تظل البيانات في Database

---

## 🎯 المسارات والـ Endpoints

| المسار | الغرض |
|--------|-------|
| `GET /api/energy/anomalies/` | قائمة الشذوذ |
| `POST /api/energy/anomalies/{id}/marquer_consultee/` | تعليم كمقروء |
| `POST /api/energy/anomalies/{id}/marquer_acquittee/` | الموافقة |
| `GET /api/energy/alertes/` | قائمة التنبيهات |
| `POST /api/energy/alertes/{id}/marquer_consultee/` | تعليم تنبيه |
| `POST /api/energy/alertes/{id}/acquitter/` | أرشفة تنبيه |
| `http://localhost:3000/admin/anomalies` | صفحة الشذوذ |
| `http://localhost:3000/admin/alertes` | صفحة التنبيهات |
| `http://localhost:8000/admin/energy/anomalie` | Django Admin Anomalies |
| `http://localhost:8000/admin/energy/alerte` | Django Admin Alertes |

---

## 📋 قائمة التحقق النهائية

```
☐ تم تطبيق الترقيعات (migration)
  ✓ python manage.py migrate

☐ تم إنشاء البيانات الاختبارية
  ✓ python test_data_sprint3.py

☐ الشذوذ ظاهر في الـ API
  ✓ GET /api/energy/anomalies/

☐ الدرجات الهيفينج فيس ظاهرة
  ✓ score_confiance: 0.0-1.0

☐ 4 مستويات الخطورة موجودة
  ✓ BASSE, MOYENNE, HAUTE, CRITIQUE

☐ الحالات تنتقل بنجاح
  ✓ NOUVELLE → CONSULTEE → ACQUITTEE

☐ التنبيهات ظاهرة في التطبيق
  ✓ http://localhost:3000/admin/alertes

☐ الإداري يستطيع الإدارة
  ✓ Admin صفحات وـ Django Admin

☐ الأرشفة تعمل (لا حذف)
  ✓ acquittee=True + timestamps

✅ جميع المتطلبات اكتملت!
```

---

## 🐛 حل المشاكل الشائعة

| المشكلة | الحل |
|--------|-----|
| "No module named django" | تأكد من البيئة الافتراضية: `source .venv/Scripts/activate` |
| "Database is locked" | أغلق أي connections أخرى وأعد محاولة |
| "No such table" | اشغل: `python manage.py migrate` |
| أزرار لا تعمل | تأكد من الـ token في localStorage وأن السيرفر يعمل |
| بيانات فارغة | أعد تحميل الصفحة (F5) أو امسح cache |

---

## 📌 ملاحظات مهمة

1. **الترقيعات يجب أن تُطبق مرة واحدة فقط:**
   ```bash
   python manage.py migrate
   # بعدها، لا تحتاج لتطبيقها مرة أخرى
   ```

2. **البيانات الاختبارية:**
   - تُنشأ من `test_data_sprint3.py`
   - تشمل: 3 منازل، 2 شذوذ، 2 تنبيه

3. **الأرشفة آمنة:**
   - لا نحذف البيانات أبداً
   - نضع `acquittee=True` فقط
   - تظل البيانات للتدقيق

4. **الصلاحيات:**
   - ADMIN: يرى الكل ويدير الكل
   - RESIDENT: يرى فقط منزله

---

## ✅ الخلاصة

```
Sprint 3 Implementation Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ RG7: Anomalies Detection
✅ RG8: Hugging Face Scoring
✅ RG9: Status Transitions
✅ RG10: App-Only Alerts
✅ RG11: Admin Management
✅ RG12: Safe Archival

Status: READY FOR PRODUCTION ✓
```

---

## 📞 للمساعدة

جرّب اتباع هذه الخطوات بالترتيب:
1. تطبيق الترقيعات
2. إنشاء البيانات
3. تشغيل السيرفرات
4. فتح الصفحات
5. اختبار الأزرار
6. التحقق من قاعدة البيانات

**النتيجة: جميع المتطلبات تعمل! ✅**
