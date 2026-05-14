from django.contrib.auth import get_user_model
from energy.models import ConsumptionReading

User = get_user_model()

# Show all users
print("="*60)
print("ALL USERS")
print("="*60)
for user in User.objects.all():
    managed = user.managed_by.email if user.managed_by else "None"
    print(f"{user.email:40} | Role: {user.role:8} | Managed by: {managed}")

# Show readings by resident
print("\n" + "="*60)
print("CONSUMPTION READINGS")
print("="*60)
for resident in User.objects.filter(role='RESIDENT'):
    readings_count = resident.consumption_readings.count()
    total_kwh = sum([float(r.consumption_kwh) for r in resident.consumption_readings.all()])
    print(f"{resident.email:40} | Readings: {readings_count} | Total kWh: {total_kwh:.1f}")

# Show data aggregation for Admin 1
print("\n" + "="*60)
print("ADMIN 1 DATA (houdamouttalib@gmail.com)")
print("="*60)
admin1 = User.objects.get(email='houdamouttalib@gmail.com')
for resident in admin1.residents.all():
    readings_count = resident.consumption_readings.count()
    total_kwh = sum([float(r.consumption_kwh) for r in resident.consumption_readings.all()])
    total_cost = sum([float(r.cost_estimate) for r in resident.consumption_readings.all()])
    print(f"  - {resident.email:35} | kWh: {total_kwh:7.1f} | Cost: {total_cost:6.2f}")

# Show data aggregation for Admin 2
print("\n" + "="*60)
print("ADMIN 2 DATA (youneseljonhy@gmail.com)")
print("="*60)
admin2 = User.objects.get(email='youneseljonhy@gmail.com')
for resident in admin2.residents.all():
    readings_count = resident.consumption_readings.count()
    total_kwh = sum([float(r.consumption_kwh) for r in resident.consumption_readings.all()])
    total_cost = sum([float(r.cost_estimate) for r in resident.consumption_readings.all()])
    print(f"  - {resident.email:35} | kWh: {total_kwh:7.1f} | Cost: {total_cost:6.2f}")

print("\n" + "="*60)
print("SUMMARY")
print("="*60)
print(f"Total Users: {User.objects.count()}")
print(f"Total Admins: {User.objects.filter(role='ADMIN').count()}")
print(f"Total Residents: {User.objects.filter(role='RESIDENT').count()}")
print(f"Total Readings: {ConsumptionReading.objects.count()}")
