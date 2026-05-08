#!/usr/bin/env python
"""Script لإنشاء بيانات اختبار Sprint 3 (RG7-RG12)"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings')
django.setup()

from energy.models import Foyer, Consommation, Anomalie, Alerte, User
from django.utils import timezone
from datetime import timedelta

print("=" * 70)
print("🔬 إنشاء بيانات اختبار Sprint 3 (RG7-RG12)")
print("=" * 70)

# 1️⃣ إنشاء مستخدم ADMIN
admin_user, _ = User.objects.get_or_create(
    username='admin',
    defaults={
        'email': 'admin@smartmeter.local',
        'password': 'admin123',
        'role': 'ADMIN',
        'is_active': True,
    }
)
print(f"\n✓ Admin User: {admin_user.username} (ID={admin_user.id})")

# 2️⃣ إنشاء 3 منازل للاختبار
foyerA, _ = Foyer.objects.get_or_create(
    numero_foyer='FOY_TEST_A',
    defaults={
        'adresse': '123 شارع النيل',
        'code_postal': '75001',
        'ville': 'باريس',
        'puissance_souscrite': 6.0,
    }
)
print(f"✓ Foyer A: {foyerA.numero_foyer}")

foyerB, _ = Foyer.objects.get_or_create(
    numero_foyer='FOY_TEST_B',
    defaults={
        'adresse': '456 بوليفار سان جيرمان',
        'code_postal': '75006',
        'ville': 'باريس',
        'puissance_souscrite': 9.0,
    }
)
print(f"✓ Foyer B: {foyerB.numero_foyer}")

foyerC, _ = Foyer.objects.get_or_create(
    numero_foyer='FOY_TEST_C',
    defaults={
        'adresse': '789 شارع الشانزليزيه',
        'code_postal': '75008',
        'ville': 'باريس',
        'puissance_souscrite': 3.0,
    }
)
print(f"✓ Foyer C: {foyerC.numero_foyer}")

# 3️⃣ إنشاء استهلاك مع شذوذ
print("\n" + "="*70)
print("📊 RG7: إنشاء استهلاك مع شذوذ")
print("="*70)

# ✓ RG7: استهلاك عالي جداً (شذوذ)
conso1 = Consommation.objects.create(
    foyer=foyerA,
    timestamp=timezone.now() - timedelta(hours=2),
    kwh=85.0,  # عالي جداً!
    anomaly_label='pic',  # ✓ RG7
    temperature=20.0
)
print(f"\n✓ Consommation: {conso1.kwh} kWh (Anomalous - pic)")

# 4️⃣ إنشاء شذوذ مع درجة Hugging Face
print("\n" + "="*70)
print("🤖 RG8: إضافة Score Hugging Face + Severite")
print("="*70)

anomalie1 = Anomalie.objects.create(
    consommation=conso1,
    score_confiance=0.95,  # ✓ RG8: درجة HF من 0 إلى 1
    severite='HAUTE',      # ✓ RG8: 4 مستويات (BASSE, MOYENNE, HAUTE, CRITIQUE)
    statut='NOUVELLE'      # ✓ RG9: الحالة الأولى
)
print(f"\n✓ Anomalie 1:")
print(f"  - Score HF: {anomalie1.score_confiance:.2f} (95%)")
print(f"  - Severite: {anomalie1.get_severite_display()}")
print(f"  - Statut: {anomalie1.get_statut_display()} ✓ RG9 (1/3)")

# 5️⃣ إنشاء شذوذ آخر
anomalie2 = Anomalie.objects.create(
    consommation=Consommation.objects.create(
        foyer=foyerB,
        timestamp=timezone.now() - timedelta(hours=1),
        kwh=15.0,
        anomaly_label='pic',
        temperature=22.0
    ),
    score_confiance=0.72,
    severite='MOYENNE',
    statut='NOUVELLE'
)
print(f"\n✓ Anomalie 2:")
print(f"  - Score HF: {anomalie2.score_confiance:.2f} (72%)")
print(f"  - Severite: {anomalie2.get_severite_display()}")
print(f"  - Statut: {anomalie2.get_statut_display()}")

# 6️⃣ إنشاء شذوذ (CONSULTEE)
print("\n" + "="*70)
print("📖 RG9: تحويل الحالة NOUVELLE → CONSULTEE")
print("="*70)

anomalie1.marquer_consultee()
print(f"\n✓ Anomalie 1 → CONSULTEE")
print(f"  - Statut: {anomalie1.get_statut_display()} ✓ RG9 (2/3)")
print(f"  - consultee_at: {anomalie1.consultee_at}")

# 7️⃣ إنشاء شذوذ (ACQUITTEE)
print("\n" + "="*70)
print("✅ RG9: تحويل الحالة CONSULTEE → ACQUITTEE")
print("="*70)

anomalie1.marquer_acquittee()
print(f"\n✓ Anomalie 1 → ACQUITTEE")
print(f"  - Statut: {anomalie1.get_statut_display()} ✓ RG9 (3/3)")
print(f"  - acquittee_at: {anomalie1.acquittee_at}")

# 8️⃣ إنشاء تنبيهات
print("\n" + "="*70)
print("🔔 RG10: التنبيهات (visible dans l'app فقط)")
print("="*70)

alerte1 = Alerte.objects.create(
    anomalie=anomalie1,
    statut='NOUVELLE'  # ✓ RG10: التنبيهات في التطبيق فقط
)
print(f"\n✓ Alerte 1 للـ Anomalie ACQUITTEE")
print(f"  - Statut: {alerte1.get_statut_display()}")
print(f"  - Acquittee: {alerte1.acquittee} (RG12: لم يتم الحذف)")

alerte2 = Alerte.objects.create(
    anomalie=anomalie2,
    statut='NOUVELLE'
)
print(f"\n✓ Alerte 2 للـ Anomalie 2")
print(f"  - Statut: {alerte2.get_statut_display()}")

# 9️⃣ إدارة التنبيهات (RG11)
print("\n" + "="*70)
print("👨‍💼 RG11: إدارة التنبيهات من طرف Admin")
print("="*70)

alerte2.statut = 'CONSULTEE'
alerte2.consultee_at = timezone.now()
alerte2.save()
print(f"\n✓ Alerte 2 → CONSULTEE")
print(f"  - الإداري شاهد التنبيه")
print(f"  - consultee_at: {alerte2.consultee_at}")

# 🔟 أرشفة (RG12)
print("\n" + "="*70)
print("📦 RG12: الأرشفة (Never Delete)")
print("="*70)

alerte2.statut = 'ACQUITTEE'
alerte2.acquittee = True
alerte2.acquittee_at = timezone.now()
alerte2.save()
print(f"\n✓ Alerte 2 → ACQUITTEE + Acquittee=True")
print(f"  - ✗ لا نحذف أبداً")
print(f"  - ✓ نضع علامة: acquittee = {alerte2.acquittee}")
print(f"  - ✓ نسجل الوقت: acquittee_at = {alerte2.acquittee_at}")
print(f"  - تظل البيانات في الـ Database للتدقيق!")

# 📊 ملخص
print("\n" + "="*70)
print("📊 ملخص البيانات المُنشأة")
print("="*70)

print(f"\n✓ عدد الشذوذ: {Anomalie.objects.count()}")
print(f"  - NOUVELLE: {Anomalie.objects.filter(statut='NOUVELLE').count()}")
print(f"  - CONSULTEE: {Anomalie.objects.filter(statut='CONSULTEE').count()}")
print(f"  - ACQUITTEE: {Anomalie.objects.filter(statut='ACQUITTEE').count()}")

print(f"\n✓ عدد التنبيهات: {Alerte.objects.count()}")
print(f"  - NOUVELLE: {Alerte.objects.filter(statut='NOUVELLE').count()}")
print(f"  - CONSULTEE: {Alerte.objects.filter(statut='CONSULTEE').count()}")
print(f"  - ACQUITTEE: {Alerte.objects.filter(statut='ACQUITTEE').count()}")
print(f"  - Acquittee (مؤرشفة): {Alerte.objects.filter(acquittee=True).count()}")

print("\n" + "="*70)
print("✅ تم إنشاء جميع البيانات بنجاح!")
print("="*70)
