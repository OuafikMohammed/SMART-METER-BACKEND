# ⚡ SPRINT 3 - Guide Complet d'Implémentation

## 📋 Vue d'ensemble

Le Sprint 3 implémente la détection, classification et gestion des anomalies de consommation électrique avec intégration Hugging Face et notifications email.

### Règles de gestion
- **RG7**: Détection des anomalies depuis dataset (anomaly_label=1)
- **RG8**: Score de confiance Hugging Face (0.0 → 1.0)
- **RG9**: Statuts anomalies (NOUVELLE → CONSULTÉE → ACQUITTÉE)
- **RG10**: Gestion des alertes dans l'app
- **RG11**: Notifications email aux admins (<5 min)
- **RG12**: Archivage des alertes (jamais supprimées)

---

## 🔧 Backend Setup

### 1. Configuration des variables d'environnement

Créez ou mettez à jour votre fichier `.env`:

```bash
# Hugging Face API
HUGGINGFACE_API_KEY=hf_your_token_here

# Email (Gmail example)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your.email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password  # NOT your regular password!
DEFAULT_FROM_EMAIL=your.email@gmail.com
```

**Important**: Pour Gmail, vous devez générer un **App Password**:
1. Allez à https://myaccount.google.com/apppasswords
2. Sélectionnez "Mail" et "Windows Computer"
3. Copiez le mot de passe généré

### 2. Installer les dépendances

```bash
pip install -r requirements.txt
```

Vérifiez que `requests` est installé (pour les appels API Hugging Face).

### 3. Appliquer les migrations

```bash
python manage.py migrate
```

### 4. Traiter les anomalies

Exécutez le management command pour détecter et traiter les anomalies:

```bash
# Traiter toutes les anomalies non traitées
python manage.py process_anomalies

# Résultat attendu:
# ✓ Traitement terminé!
#   - Anomalies créées: 5
#   - Erreurs: 0
```

---

## 🔌 Endpoints API

### Liste des anomalies

```http
GET /api/energy/anomalies/
Authorization: Bearer <your_token>

# Filtres:
# - statut: NOUVELLE|CONSULTEE|ACQUITTEE
# - severite: BASSE|MOYENNE|HAUTE|CRITIQUE
# - consommation__foyer: <foyer_id>

# Exemples:
GET /api/energy/anomalies/?statut=NOUVELLE
GET /api/energy/anomalies/?severite=HAUTE
GET /api/energy/anomalies/?statut=NOUVELLE&severite=CRITIQUE
```

**Réponse exemple**:
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "consommation": {
        "foyer_numero": "F001",
        "foyer_id": 1,
        "timestamp_consommation": "2024-05-04T14:30:00Z",
        "kwh": 95.5,
        "temperature": 22.5
      },
      "score_confiance": 0.95,
      "severite": "HAUTE",
      "statut": "NOUVELLE",
      "created_at": "2024-05-04T14:35:00Z"
    }
  ]
}
```

### Acquitter une anomalie

```http
POST /api/energy/anomalies/{id}/marquer_acquittee/
Authorization: Bearer <your_token>
Content-Type: application/json
```

**Réponse**:
```json
{
  "id": 1,
  "statut": "ACQUITTEE",
  "acquittee_at": "2024-05-04T14:40:00Z",
  ...
}
```

---

## 🎨 Frontend Implementation

### Installation des dépendances

Assurez-vous que vous avez:
- `framer-motion` (animations)
- `lucide-react` (icônes)
- `sonner` (toasts)

```bash
npm install framer-motion lucide-react sonner
```

### Utilisation du hook `useAnomalies`

```typescript
import { useAnomalies } from '@/hooks/useAnomalies';

function MyComponent() {
  // Récupérer toutes les anomalies
  const { anomalies, loading, error, acquitter, refetch, stats } = useAnomalies();

  // Avec filtres
  const { anomalies: critical } = useAnomalies({
    severite: 'HAUTE'
  });

  // Acquitter une anomalie
  const handleAcquitter = async (id: number) => {
    try {
      await acquitter(id);
      toast.success('Acquittée');
    } catch (err) {
      toast.error('Erreur');
    }
  };

  return (
    <div>
      <p>Nouvelles: {stats.nouvelles}</p>
      <p>Critiques: {stats.critical}</p>
      ...
    </div>
  );
}
```

### Composants réutilisables

#### AnomalyBadge
```typescript
import AnomalyBadge from '@/components/anomalies/AnomalyBadge';

<AnomalyBadge severite="HAUTE" />  // Orange avec point animé
<AnomalyBadge severite="CRITIQUE" />  // Rouge avec pulse
<AnomalyBadge severite="BASSE" />  // Amber (warning)
```

#### ScoreBar
```typescript
import ScoreBar from '@/components/anomalies/ScoreBar';

<ScoreBar score={0.95} showPercent={true} />  // 95% - Rouge
<ScoreBar score={0.65} />  // 65% - Orange
<ScoreBar score={0.45} />  // 45% - Cyan
```

### Page Dashboard complète

La page `/dashboard/anomalies` inclut:

✅ **Cartes de statistiques** (Nouvelles, Critiques, Consultées, Acquittées)
✅ **Filtres** (Statut + Sévérité)
✅ **Table animée** avec AnimatePresence
✅ **Boutons d'action** (Acquitter)
✅ **Toasts** (Succès/Erreur)
✅ **Design sombre** (#0f1117) avec accents cyan/orange/rouge

---

## 🤖 Modèle Hugging Face

### Modèle utilisé

```
distilbert-base-uncased-finetuned-sst-2-english
```

**URL API**:
```
https://api-inference.huggingface.co/models/distilbert-base-uncased-finetuned-sst-2-english
```

### Prompt template

```python
prompt = f"Electricity consumption spike detected: {kwh_value} kWh unusually high"
```

**Résponse attendue**:
```json
[
  {"label": "POSITIVE", "score": 0.95},
  {"label": "NEGATIVE", "score": 0.05}
]
```

### Classification de sévérité

```python
def classifier_severite(score: float) -> str:
    if score > 0.8:      # POSITIVE > 80%
        return 'HAUTE'   # Critical
    elif score >= 0.6:   # POSITIVE >= 60%
        return 'HAUTE'   # High
    else:                # POSITIVE < 60%
        return 'MOYENNE' # Warning
```

---

## 📧 Configuration Email

### Gmail setup

1. **Activer l'authentification 2FA**:
   - Allez à https://myaccount.google.com/security
   - Activez "2-Step Verification"

2. **Générer App Password**:
   - Allez à https://myaccount.google.com/apppasswords
   - Sélectionnez "Mail" et "Windows Computer"
   - Copiez le mot de passe généré

3. **.env**:
   ```
   EMAIL_HOST_USER=your.email@gmail.com
   EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx  # App password avec espaces
   ```

### Format d'email reçu

```
De: noreply@smartmeter.local
Sujet: ⚠️ [HAUTE] Anomalie Foyer F001 — SmartMeter

Corps:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
DÉTAILS DE L'ANOMALIE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Foyer : F001
Adresse : 123 Rue Example, 75001 Paris

Timestamp : 2024-05-04 14:30:00
Consommation : 95.5 kWh
Score Hugging Face : 95.0%
Sévérité : Haute
Statut : NOUVELLE

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

---

## 🧪 Tests et Vérification

### Test l'API Hugging Face

```python
from energy.services.anomaly_service import obtenir_score_huggingface

score = obtenir_score_huggingface(95.5)  # Essayer avec 95.5 kWh
print(f"Score: {score:.2%}")  # Score: 95.00%
```

### Test l'email

```python
from django.core.mail import send_mail

send_mail(
    subject="Test SmartMeter",
    message="Email de test",
    from_email="your.email@gmail.com",
    recipient_list=["admin@example.com"],
)
```

### Test le management command

```bash
python manage.py process_anomalies --verbosity=2
```

### Test l'endpoint API

```bash
# Récupérer les anomalies critiques
curl -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/?severite=HAUTE

# Acquitter une anomalie
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
  http://localhost:8000/api/energy/anomalies/1/marquer_acquittee/
```

---

## 📊 Architecture complète

```
┌─────────────────────────────────────────────────────────────┐
│                      Frontend (Next.js)                      │
│                                                               │
│  /dashboard/anomalies                                        │
│  ├── useAnomalies hook                                       │
│  │   ├── GET /api/energy/anomalies/ (filtres)              │
│  │   └── POST /api/energy/anomalies/{id}/marquer_acquittee/│
│  ├── AnomalyBadge (severite display)                        │
│  ├── ScoreBar (HF score visualization)                      │
│  └── Stats Cards, Filters, Animated Table                   │
│                                                               │
└─────────────────┬───────────────────────────────────────────┘
                  │ HTTP/JSON
┌─────────────────▼───────────────────────────────────────────┐
│                    Backend (Django)                          │
│                                                               │
│  /api/energy/anomalies/   (ViewSet)                         │
│  ├── GET list (filtres: statut, severite)                   │
│  ├── POST marquer_consultee/                                │
│  └── POST marquer_acquittee/ (log_action)                   │
│                                                               │
│  Modèles:                                                    │
│  ├── Anomalie (score_confiance, severite, statut)          │
│  └── Alerte (anomalie, acquittee)                           │
│                                                               │
│  Services:                                                   │
│  ├── anomaly_service.py                                     │
│  │   ├── obtenir_score_huggingface(kwh) → [0.0, 1.0]      │
│  │   ├── classifier_severite(score) → str                  │
│  │   ├── traiter_nouvelles_anomalies() → dict              │
│  │   └── envoyer_email_alerte(anomalie) → bool             │
│  │                                                           │
│  └── Management command:                                    │
│      └── process_anomalies.py                              │
│                                                               │
└─────────────────┬───────────────────────────────────────────┘
                  │
        ┌─────────┼─────────┐
        │         │         │
   ┌────▼──┐ ┌───▼────┐ ┌──▼────────┐
   │ MySQL │ │Hugging │ │   Gmail   │
   │       │ │ Face   │ │   SMTP    │
   │ DB    │ │ API    │ │   Email   │
   └───────┘ └────────┘ └───────────┘
```

---

## 🚀 Déploiement

### Production Checklist

- [ ] Configurer `HUGGINGFACE_API_KEY` en production
- [ ] Configurer Email SMTP (Gmail ou autre)
- [ ] Activer HTTPS et cookies sécurisés
- [ ] Augmenter les timeouts de request (Hugging Face peut être lent)
- [ ] Mettre en place Celery/Redis pour les tâches async (optionnel)
- [ ] Ajouter monitoring/alertes pour les erreurs API
- [ ] Tester la capacité à traiter ~1000 anomalies/jour

### Logs

```bash
# Voir les logs du traitement
tail -f logs/smartmeter.log | grep anomaly

# Vérifier les emails envoyés
tail -f logs/smartmeter.log | grep email_alerte
```

---

## ❓ FAQ

**Q: Pourquoi 0.5 est retourné en cas d'erreur?**
R: C'est une valeur neutre (50% de confiance) qui ne déclenche pas d'alerte mais enregistre l'erreur.

**Q: Peux-je utiliser un autre modèle Hugging Face?**
R: Oui! Changez le modèle dans `obtenir_score_huggingface()` et adaptez le parsing de la réponse.

**Q: Comment archiver les anciennes anomalies?**
R: Les anomalies acquittées restent en BD (RG12). Vous pouvez les filtrer avec `statut=ACQUITTEE`.

**Q: Combien de fois peut-on appeler l'API HF?**
R: Dépend de votre plan. Utilisateurs gratuits: ~30,000 requêtes/mois. Mettez en place une mise en cache si nécessaire.

---

## 📚 Références

- [Hugging Face Inference API](https://huggingface.co/docs/api-inference)
- [Django Email Documentation](https://docs.djangoproject.com/en/5.0/topics/email/)
- [Next.js Data Fetching](https://nextjs.org/docs/app/building-application-features/data-fetching)
- [Framer Motion](https://www.framer.com/motion/)
