# 📋 دليل التحقق من Sprint 3 (RG7-RG12)

## ✅ ملخص سريع

| RG | المتطلب | الحالة | الاختبار |
|----|--------|--------|---------|
| **RG7** | Anomalies مرتبطة بـ Consommation | ✅ PASSED | Python shell |
| **RG8** | Score HF + 4 مستويات Severite | ✅ PASSED | API endpoint |
| **RG9** | الحالات: NOUVELLE → CONSULTEE → ACQUITTEE | ✅ PASSED | POST actions |
| **RG10** | التنبيهات (visible في App فقط) | ✅ PASSED | Frontend pages |
| **RG11** | الإداري يدير التنبيهات | ✅ PASSED | Django Admin |
| **RG12** | الأرشفة (Never Delete) | ✅ PASSED | Database check |

---

## 🔍 كيفية التحقق من كل متطلب؟

### 1️⃣ RG7: Anomalies مرتبطة بـ Consommation

**ما هو المتطلب؟**
- كل شذوذ يجب أن يكون مرتبط بـ Consommation واحد فقط (1:1 relationship)
- الشذوذ يظهر فقط عندما يكون `anomaly_label=1` (أو 'pic' في النموذج)

**كيفية الاختبار؟**

```bash
# من Django Shell
cd SMART-METER-BACKEND/backend
python manage.py shell

# اكتب:
from energy.models import Anomalie
anomalie = Anomalie.objects.first()
print(f"Anomalie ID: {anomalie.id}")
print(f"Consommation ID: {anomalie.consommation.id}")
print(f"Consommation kWh: {anomalie.consommation.kwh}")
print(f"Anomaly Label: {anomalie.consommation.anomaly_label}") # يجب أن يكون 'pic'
```

**النتيجة المتوقعة:**
```
✓ Anomalie مرتبطة بـ Consommation واحدة فقط
✓ Consommation به anomaly_label='pic'
✓ One-to-One relationship يعمل
```

---

### 2️⃣ RG8: Score Hugging Face + 4 مستويات Severite

**ما هو المتطلب؟**
- كل شذوذ له `score_confiance` من 0.0 إلى 1.0
- 4 مستويات للخطورة: BASSE, MOYENNE, HAUTE, CRITIQUE

**كيفية الاختبار؟**

```bash
# من API
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/

# يجب أن ترى:
{
  "id": 1,
  "score_confiance": 0.95,    ← RG8: من 0 إلى 1
  "severite": "HAUTE",         ← RG8: 4 مستويات
  "statut": "NOUVELLE",
  ...
}
```

**أو من Django Shell:**
```python
from energy.models import Anomalie
for a in Anomalie.objects.all():
    print(f"ID: {a.id}, Score: {a.score_confiance:.2f}, Severite: {a.get_severite_display()}")

# النتيجة:
# ID: 1, Score: 0.95, Severite: Haute ✓
# ID: 2, Score: 0.72, Severite: Moyenne ✓
```

---

### 3️⃣ RG9: الحالات (NOUVELLE → CONSULTEE → ACQUITTEE)

**ما هو المتطلب؟**
- كل شذوذ يمر عبر 3 حالات بالترتيب
- الانتقال يجب أن يسجل الوقت

**كيفية الاختبار؟**

#### الطريقة 1: من API

```bash
# الحصول على شذوذ
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/

# يجب أن ترى:
{
  "id": 1,
  "statut": "NOUVELLE",        ← الحالة الأولى
  "consultee_at": null,
  "acquittee_at": null
}

# تحويل إلى CONSULTEE
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_consultee/

# النتيجة:
{
  "id": 1,
  "statut": "CONSULTEE",       ← تم التحويل
  "consultee_at": "2026-04-28T22:04:25Z",  ← تم تسجيل الوقت
  "acquittee_at": null
}

# تحويل إلى ACQUITTEE
curl -X POST -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_acquittee/

# النتيجة:
{
  "id": 1,
  "statut": "ACQUITTEE",       ← الحالة النهائية
  "consultee_at": "2026-04-28T22:04:25Z",
  "acquittee_at": "2026-04-28T22:04:26Z"  ← الوقت النهائي
}
```

#### الطريقة 2: من Django Shell

```python
from energy.models import Anomalie

anomalie = Anomalie.objects.get(id=1)
print(f"1. الحالة الأولى: {anomalie.statut}")

# الانتقال إلى CONSULTEE
anomalie.marquer_consultee()
print(f"2. بعد marquer_consultee: {anomalie.statut}")
print(f"   consultee_at: {anomalie.consultee_at}")

# الانتقال إلى ACQUITTEE
anomalie.marquer_acquittee()
print(f"3. بعد marquer_acquittee: {anomalie.statut}")
print(f"   acquittee_at: {anomalie.acquittee_at}")

# النتيجة:
# 1. الحالة الأولى: NOUVELLE
# 2. بعد marquer_consultee: CONSULTEE
#    consultee_at: 2026-04-28 22:04:25.251101+00:00
# 3. بعد marquer_acquittee: ACQUITTEE
#    acquittee_at: 2026-04-28 22:04:25.262651+00:00
```

---

### 4️⃣ RG10: التنبيهات (visible في App فقط)

**ما هو المتطلب؟**
- التنبيهات تظهر فقط في التطبيق (الواجهة الرسومية)
- بدون بريد إلكتروني أو SMS (في المستقبل)
- مرتبطة بـ Anomalie

**كيفية الاختبار؟**

#### من الواجهة الرسومية

```bash
1. اذهب إلى: http://localhost:3000/admin/alertes
2. يجب أن ترى جدول مع التنبيهات
3. أزرار: "استشر" و "وافق"
4. ✓ التنبيهات ظاهرة في التطبيق
```

#### من API

```bash
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/alertes/

# النتيجة:
[
  {
    "id": 1,
    "anomalie": 1,              ← مرتبطة بـ Anomalie
    "anomalie_severite": "Haute",
    "anomalie_score": 0.95,
    "statut": "NOUVELLE",
    "acquittee": false,          ← RG12: لم تُحذف
    ...
  }
]
```

#### من قاعدة البيانات

```python
from energy.models import Alerte

# عدد التنبيهات
print(f"عدد التنبيهات: {Alerte.objects.count()}")
# النتيجة: 2

# التنبيهات الجديدة
nouvelles = Alerte.objects.filter(statut='NOUVELLE')
print(f"التنبيهات الجديدة: {nouvelles.count()}")

# ✓ ظاهرة في التطبيق فقط (لا بريد، لا SMS)
```

---

### 5️⃣ RG11: الإداري يدير التنبيهات

**ما هو المتطلب؟**
- الإداري (Admin) يستطيع:
  - عرض جميع التنبيهات
  - تعليم كمقروء (CONSULTEE)
  - الموافقة والأرشفة (ACQUITTEE)
- الساكنين (Residents) يرون فقط تنبيهاتهم

**كيفية الاختبار؟**

#### 1. من Django Admin

```bash
1. اذهب إلى: http://localhost:8000/admin
2. ادخل ببيانات admin
3. اضغط: Energy → Alertes
4. يجب أن ترى:
   ✓ قائمة بجميع التنبيهات
   ✓ فلاتر: statut, acquittee
   ✓ إجراءات batch
```

#### 2. من الواجهة الرسومية Admin

```bash
1. اذهب إلى: http://localhost:3000/admin/alertes
2. يجب أن ترى:
   ✓ جدول التنبيهات
   ✓ فلاتر (statut, acquittee)
   ✓ أزرار "استشر" و "وافق"
3. جرّب الأزرار
```

#### 3. من API

```bash
# الإداري يرى جميع التنبيهات
curl -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/energy/alertes/

# الإداري يمكنه تعليم كمقروء
curl -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/energy/alertes/1/marquer_consultee/

# النتيجة: status 200 ✓

# الإداري يمكنه الموافقة
curl -X POST -H "Authorization: Bearer ADMIN_TOKEN" \
  http://localhost:8000/api/energy/alertes/1/acquitter/

# النتيجة: status 200 ✓
```

---

### 6️⃣ RG12: الأرشفة (Never Delete)

**ما هو المتطلب؟**
- التنبيهات لا تُحذف أبداً
- تُأرشف بـ وضع `acquittee=True`
- تُسجل `acquittee_at` لتتبع الوقت
- تظل في قاعدة البيانات للتدقيق

**كيفية الاختبار؟**

#### الطريقة 1: من Django Shell

```python
from energy.models import Alerte

# إنشاء تنبيه
alerte = Alerte.objects.create(...)

# التحقق من أنه موجود
print(f"✓ Alerte قبل الأرشفة: {Alerte.objects.count()}")

# الأرشفة
alerte.acquittee = True
alerte.acquittee_at = timezone.now()
alerte.save()

# ✗ لم نحذف
print(f"✓ Alerte بعد الأرشفة: {Alerte.objects.count()}")  # نفس الرقم!

# ✓ التنبيه لا يزال موجود
print(f"✓ التنبيه المؤرشف: {Alerte.objects.filter(acquittee=True).first()}")
```

#### الطريقة 2: من قاعدة البيانات

```bash
# فتح SQLite shell
cd SMART-METER-BACKEND
sqlite3 backend/db.sqlite3

# الأمر:
SELECT COUNT(*) FROM energy_alerte;

# قبل الأرشفة: 2 تنبيهات
# بعد الأرشفة: 2 تنبيهات (لم تُحذف!)
# SELECT COUNT(*) FROM energy_alerte WHERE acquittee=1;
# النتيجة: 1 (مؤرشفة)
```

#### الطريقة 3: من API

```bash
# عرض المؤرشفة
curl -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/alertes/?acquittee=true

# النتيجة:
[
  {
    "id": 1,
    "acquittee": true,           ← تم الأرشفة
    "acquittee_at": "2026-04-28T22:04:25Z",
    "statut": "ACQUITTEE"
  }
]

# ✓ ظاهرة في النتائج (لم تُحذف)
```

---

## 🚀 اختبار سريع (5 دقائق)

```bash
# 1. تطبيق الترقيعات
cd SMART-METER-BACKEND/backend
python manage.py migrate

# 2. إنشاء البيانات
python test_data_sprint3.py

# 3. اختبار API
python test_api_sprint3.py

# 4. فتح Django Admin
python manage.py runserver

# 5. زر الواجهة الرسومية
cd SMART-METER-FRONTEND
npm run dev
```

**النتائج المتوقعة:**
- ✅ جميع الترقيعات مطبقة
- ✅ 2 شذوذ + 2 تنبيه مُنشأ
- ✅ جميع الحالات تعمل
- ✅ الأرشفة تعمل
- ✅ الصفحات تظهر البيانات

---

## 📊 قائمة التحقق النهائية

```
☐ RG7: هل الشذوذ مرتبط بـ Consommation مع anomaly_label='pic'?
   ✓ نعم - من Django Shell

☐ RG8: هل يوجد score_confiance و 4 مستويات severite؟
   ✓ نعم - Score: 0.0-1.0, Severite: BASSE/MOYENNE/HAUTE/CRITIQUE

☐ RG9: هل الحالات تنتقل بشكل صحيح؟
   ✓ نعم - NOUVELLE → CONSULTEE → ACQUITTEE مع timestamps

☐ RG10: هل التنبيهات ظاهرة في التطبيق فقط؟
   ✓ نعم - في /admin/alertes والـ API فقط

☐ RG11: هل الإداري يدير التنبيهات؟
   ✓ نعم - من Django Admin والواجهة الرسومية

☐ RG12: هل الأرشفة تعمل (لا حذف)؟
   ✓ نعم - acquittee=true + acquittee_at + تظل في DB

✅ جميع المتطلبات مُحققة!
```

---

## 🐛 استكشاف الأخطاء

| المشكلة | الحل |
|--------|-----|
| "Migration not applied" | اشغل: `python manage.py migrate` |
| "No anomalies found" | اشغل: `python test_data_sprint3.py` |
| "401 Unauthorized" | تأكد من الـ token صحيح |
| "Page 404" | تأكد أن السيرفرات تعمل على 8000 و 3000 |
| بيانات فارغة في الجدول | أعد تحميل الصفحة أو امسح cache |

---

## 📝 الملفات المهمة

| الملف | الغرض |
|------|------|
| `energy/models.py` | نماذج Anomalie و Alerte |
| `energy/views.py` | API endpoints |
| `energy/serializers.py` | JSON serializers |
| `energy/admin.py` | Django admin interfaces |
| `src/app/admin/anomalies/page.tsx` | صفحة الشذوذ |
| `src/app/admin/alertes/page.tsx` | صفحة التنبيهات |

---

## ✅ النتيجة

```
SPRINT 3 IMPLEMENTATION: COMPLETE ✓

✅ RG7: Anomalies detection working
✅ RG8: Hugging Face scores integrated
✅ RG9: Status transitions implemented
✅ RG10: Alerts visible in app
✅ RG11: Admin management enabled
✅ RG12: Archival system (never delete)

Ready for production!
```
