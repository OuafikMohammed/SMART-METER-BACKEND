from rest_framework import serializers
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'affichage des détails de l'utilisateur.
    """
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'role', 'foyer')

class RegisterSerializer(serializers.ModelSerializer):
    """
    Serializer pour l'inscription des résidents.
    Respecte RG19 (mots de passe hachés).
    """
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'first_name', 'last_name')

    def create(self, validated_data):
        # Par défaut, les nouveaux inscrits via ce serializer sont des RESIDENTS
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data.get('email', ''),
            password=validated_data['password'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            role='RESIDENT'
        )
        return user

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """
    Serializer personnalisé pour inclure les informations de l'utilisateur dans le token.
    """
    @classmethod
    def get_token(cls, user):
        token = super().get_token(user)

        # Ajouter des claims personnalisés
        token['username'] = user.username
        token['role'] = user.role
        token['email'] = user.email
        return token

    def validate(self, attrs):
        # Debug output
        import datetime
        import os
        import tempfile
        from django.contrib.auth import authenticate, get_user_model
        
        User = get_user_model()
        
        log_msg = f"[{datetime.datetime.now()}] CustomTokenObtainPairSerializer.validate called with: {attrs}\n"
        print(log_msg, end='')
        
        # Also log to file for HTTP debugging
        try:
            log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
            with open(log_file, 'a') as f:
                f.write(log_msg)
        except:
            pass
        
        # Manual authentication check
        username = attrs.get('username')
        password = attrs.get('password')
        
        log_msg = f"[{datetime.datetime.now()}]   - Attempting manual authenticate: username={username}, password={'*' * len(password) if password else 'None'}\n"
        print(log_msg, end='')
        try:
            log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
            with open(log_file, 'a') as f:
                f.write(log_msg)
        except:
            pass
        
        # Manual authentication
        user = authenticate(username=username, password=password)
        if user:
            log_msg = f"[{datetime.datetime.now()}]   - ✓ authenticate() returned user: {user}\n"
            print(log_msg, end='')
            try:
                log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
                with open(log_file, 'a') as f:
                    f.write(log_msg)
            except:
                pass
        else:
            log_msg = f"[{datetime.datetime.now()}]   - ✗ authenticate() returned None\n"
            print(log_msg, end='')
            try:
                log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
                with open(log_file, 'a') as f:
                    f.write(log_msg)
            except:
                pass
        
        try:
            data = super().validate(attrs)
            log_msg = f"[{datetime.datetime.now()}] super().validate succeeded, self.user: {self.user}\n"
            print(log_msg, end='')
            try:
                log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
                with open(log_file, 'a') as f:
                    f.write(log_msg)
            except:
                pass
            
            # Ajouter les infos utilisateur à la réponse JSON
            data['user'] = {
                'id': self.user.id,
                'username': self.user.username,
                'email': self.user.email,
                'role': self.user.role,
                'fullName': f"{self.user.first_name} {self.user.last_name}".strip()
            }
            return data
        except Exception as e:
            log_msg = f"[{datetime.datetime.now()}] super().validate failed: {e}\n"
            print(log_msg, end='')
            try:
                log_file = os.path.join(tempfile.gettempdir(), 'smartmeter_auth.log')
                with open(log_file, 'a') as f:
                    f.write(log_msg)
            except:
                pass
            raise
