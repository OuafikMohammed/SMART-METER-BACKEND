# ✅ SPRINT 3 - Verification Checklist

Complete this checklist to ensure everything is working correctly.

---

## 🔧 Backend Setup

- [ ] `.env` file created with `HUGGINGFACE_API_KEY`
- [ ] `.env` file created with `EMAIL_HOST_USER` and `EMAIL_HOST_PASSWORD`
- [ ] Database migrations applied: `python manage.py migrate`
- [ ] Backend server running: `python manage.py runserver 0.0.0.0:8000`
- [ ] No migration errors in console

---

## 🚀 Frontend Setup

- [ ] `framer-motion` installed: `npm install framer-motion`
- [ ] `lucide-react` installed: `npm install lucide-react`
- [ ] `sonner` installed: `npm install sonner`
- [ ] Frontend server running: `npm run dev`
- [ ] No build errors in console

---

## 📂 File Structure

### Backend Files Created

- [ ] `energy/services/__init__.py` exists
- [ ] `energy/services/anomaly_service.py` exists (400+ lines)
- [ ] `energy/management/__init__.py` exists
- [ ] `energy/management/commands/__init__.py` exists
- [ ] `energy/management/commands/process_anomalies.py` exists

### Frontend Files Created

- [ ] `hooks/useAnomalies.ts` exists (~150 lines)
- [ ] `components/anomalies/AnomalyBadge.tsx` exists (~60 lines)
- [ ] `components/anomalies/ScoreBar.tsx` exists (~70 lines)
- [ ] `app/dashboard/anomalies/page.tsx` exists (~400 lines)

### Documentation Files

- [ ] `SPRINT3_IMPLEMENTATION_GUIDE.md` created
- [ ] `SPRINT3_QUICK_COMMANDS.md` created
- [ ] `SPRINT3_COMPLETION_SUMMARY.md` created
- [ ] `SPRINT3_UI_DESIGN.md` created
- [ ] `.env.example` updated with new variables

---

## 🧪 API Tests

### Test Hugging Face Integration

```bash
# Test command:
python manage.py shell
>>> from energy.services.anomaly_service import obtenir_score_huggingface
>>> score = obtenir_score_huggingface(95.5)
>>> print(f"Score: {score:.2%}")

- [ ] Command runs without error
- [ ] Score is between 0.0 and 1.0
- [ ] If no API key: returns 0.5 (expected behavior)
```

### Test Classifier

```bash
python manage.py shell
>>> from energy.services.anomaly_service import classifier_severite
>>> print(classifier_severite(0.95))  # Should: HAUTE
>>> print(classifier_severite(0.65))  # Should: HAUTE
>>> print(classifier_severite(0.45))  # Should: MOYENNE

- [ ] Returns 'HAUTE' for score > 0.6
- [ ] Returns 'MOYENNE' for score < 0.6
```

### Test Management Command

```bash
python manage.py process_anomalies

- [ ] Command runs without error
- [ ] Output shows: "✓ Traitement terminé!"
- [ ] Shows count of created anomalies
- [ ] Shows error count (should be 0 if all OK)
```

### Test API Endpoint

```bash
# Get token first (you need to authenticate)
# Then test:

curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/

- [ ] Returns JSON with anomalies list
- [ ] Response has: id, score_confiance, severite, statut
- [ ] HTTP 200 status
```

### Test Filter Endpoint

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/energy/anomalies/?severite=HAUTE"

- [ ] Returns only HAUTE severity anomalies
- [ ] HTTP 200 status

curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/energy/anomalies/?statut=NOUVELLE"

- [ ] Returns only NOUVELLE status anomalies
- [ ] HTTP 200 status
```

### Test Acknowledge Endpoint

```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_acquittee/

- [ ] Returns JSON with updated anomalie
- [ ] Status changed to: ACQUITTEE
- [ ] Field acquittee_at is populated
- [ ] HTTP 200 status
```

---

## 🎨 Frontend Tests

### Test Hook - useAnomalies

```typescript
// In your component or test:
import { useAnomalies } from '@/hooks/useAnomalies';

function TestComponent() {
  const { anomalies, loading, error, stats } = useAnomalies();
  
  useEffect(() => {
    console.log('Anomalies:', anomalies.length);
    console.log('Stats:', stats);
  }, [anomalies]);
}

- [ ] Hook fetches anomalies without error
- [ ] Stats object is populated
- [ ] Numbers are correct (can verify in DB)
```

### Test Components

```typescript
import AnomalyBadge from '@/components/anomalies/AnomalyBadge';
import ScoreBar from '@/components/anomalies/ScoreBar';

// Test badges
<AnomalyBadge severite="CRITIQUE" />
<AnomalyBadge severite="HAUTE" />
<AnomalyBadge severite="BASSE" />

- [ ] Badges render without error
- [ ] Colors are correct (red, orange, amber)
- [ ] CRITIQUE has pulsing dot animation

// Test score bars
<ScoreBar score={0.95} />
<ScoreBar score={0.65} />
<ScoreBar score={0.35} />

- [ ] Bars render without error
- [ ] Fill width matches score
- [ ] Colors change based on score
- [ ] Percentages display correctly
```

### Test Dashboard Page

Open in browser: `http://localhost:3000/dashboard/anomalies`

- [ ] Page loads without errors
- [ ] Stats cards display
- [ ] Filter buttons present
- [ ] Table loads with anomalies
- [ ] Rows animate in on load
- [ ] Hover effects work
- [ ] Acquire button is clickable

### Test Filter Functionality

On dashboard:

- [ ] Click filter "NOUVELLE" → table updates
- [ ] Click filter "CRITIQUE" → table updates
- [ ] Click multiple filters → works correctly
- [ ] Click "Tous" → shows all anomalies

### Test Acknowledge Button

On dashboard:

- [ ] Click "Acquitter" button
- [ ] Confirmation toast appears
- [ ] Row status changes to "Acquittée"
- [ ] Button becomes disabled
- [ ] Can still see row (not deleted)

### Test Empty State

In dashboard:

- [ ] Filter with no results
- [ ] Shows "✨ Aucune anomalie" message
- [ ] No errors in console

### Test Error Handling

- [ ] Disconnect network
- [ ] Try to acquire an anomalie
- [ ] Error toast appears
- [ ] Row reverts to original state
- [ ] No crashed UI

---

## 📧 Email Configuration Test

### Gmail Setup

- [ ] Gmail account has 2FA enabled
- [ ] App Password generated at: https://myaccount.google.com/apppasswords
- [ ] App Password copied to `.env` (16 chars with spaces)
- [ ] Not using regular Gmail password

### Test Email Sending

```python
from django.core.mail import send_mail

result = send_mail(
    subject="Test Email",
    message="This is a test",
    from_email="your.email@gmail.com",
    recipient_list=["target@example.com"],
    fail_silently=False,
)

- [ ] No exception thrown
- [ ] Result is 1 (success)
- [ ] Email received in inbox
```

### Test Alert Email

1. Run: `python manage.py process_anomalies`
2. Check Gmail inbox
3. Should see email with:

- [ ] Subject: "⚠️ [HAUTE] Anomalie Foyer F001 — SmartMeter"
- [ ] Body contains: Foyer number, timestamp, kWh, score %
- [ ] Recipient is admin email
- [ ] Formatting is correct

---

## 📊 Database Verification

### Check Anomalie Records Created

```bash
python manage.py shell
>>> from energy.models import Anomalie
>>> Anomalie.objects.count()
# Should show number of anomalies

>>> anomalie = Anomalie.objects.first()
>>> print(f"Score: {anomalie.score_confiance}")
>>> print(f"Severite: {anomalie.severite}")
>>> print(f"Statut: {anomalie.statut}")

- [ ] Anomalie records exist in DB
- [ ] score_confiance is between 0.0 and 1.0
- [ ] severite is one of: BASSE, MOYENNE, HAUTE, CRITIQUE
- [ ] statut is one of: NOUVELLE, CONSULTEE, ACQUITTEE
```

### Check Alerte Records Created

```bash
>>> from energy.models import Alerte
>>> Alerte.objects.count()
# Should show number of alerts

>>> alerte = Alerte.objects.first()
>>> print(f"Statut: {alerte.statut}")
>>> print(f"Acquittee: {alerte.acquittee}")

- [ ] Alerte records exist
- [ ] statut matches anomalie
- [ ] acquittee is boolean
```

### Verify Relationships

```bash
>>> anomalie = Anomalie.objects.first()
>>> print(anomalie.consommation)  # Should show consommation
>>> print(anomalie.alerte)        # Should show alerte

- [ ] OneToOne relationships working
- [ ] Can access related objects
```

---

## 🔒 Security Checks

- [ ] `.env` file is in `.gitignore` (keys not exposed)
- [ ] `DEBUG=False` in production
- [ ] JWT tokens required for API access
- [ ] CORS configured correctly
- [ ] Email credentials not logged
- [ ] HF API key not logged

---

## 📈 Performance Checks

### Load Test

```bash
# Create 50 anomalies
python manage.py shell
>>> from energy.models import Consommation, Anomalie
>>> for i in range(50):
...     # Create test data
...     pass

# Then test dashboard
# - [ ] Page loads in < 2 seconds
# - [ ] No JavaScript errors
# - [ ] Animations smooth (60fps)
```

### API Response Time

```bash
curl -w "\nTime: %{time_total}s\n" \
  -H "Authorization: Bearer TOKEN" \
  http://localhost:8000/api/energy/anomalies/

- [ ] Response time < 500ms (local)
- [ ] Response time < 1s (production)
```

---

## 🧹 Cleanup

- [ ] Remove test data from database
- [ ] Clean up log files if needed
- [ ] Remove temporary files

---

## ✅ Final Sign-Off

- [ ] All backend components working
- [ ] All frontend components working
- [ ] API endpoints responsive
- [ ] Database operations working
- [ ] Email notifications working
- [ ] Dashboard fully functional
- [ ] Animations smooth
- [ ] No console errors
- [ ] No unhandled exceptions
- [ ] Documentation complete

---

## 🚀 Ready for Production?

Before deploying to production:

- [ ] All checklist items above ✅
- [ ] Environment variables configured on server
- [ ] HTTPS enabled
- [ ] Database backed up
- [ ] Error logging configured
- [ ] Monitoring/alerting in place
- [ ] Load testing completed
- [ ] Security audit done
- [ ] Team trained on new features

---

**Last Checked:** [Date]
**Checked By:** [Name]
**Status:** ✅ Ready for Production
