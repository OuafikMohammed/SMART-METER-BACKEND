from users.models import User
from energy.models import Foyer

# Create a resident user
resident = User.objects.create_user(
    username='resident1',
    email='resident1@smartmeter.fr',
    password='resident123',
    role='RESIDENT',
    first_name='Jean',
    last_name='Dupont'
)

# Create a foyer for this resident
foyer = Foyer.objects.create(
    user=resident,
    adresse='123 Rue de Paris, 75000 Paris',
    nombre_personnes=4,
    surface_m2=100
)

print(f"User '{resident.username}' created successfully!")
print(f"Foyer created: {foyer.adresse}")
