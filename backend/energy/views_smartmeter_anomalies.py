
class AdminAnomaliesListView(APIView):
    """
    GET /api/admin/anomalies/
    
    Liste toutes les anomalies des résidents gérés par l'admin connecté.
    Accessible uniquement aux ADMIN.
    
    Réponse:
    {
        "count": 12,
        "results": [
            {
                "id": 1,
                "consommation_id": 5,
                "foyer_numero": "F001",
                "foyer_id": 1,
                "timestamp_consommation": "2026-05-01T00:00:00Z",
                "consommation_kwh": 10.5,
                "temperature": 20.0,
                "score_confiance": 0.85,
                "severite": "HAUTE",
                "statut": "NOUVELLE",
                "consultee_at": null,
                "acquittee_at": null,
                "description": "Anomalie détectée le jour 3",
                "created_at": "2026-05-01T00:00:00Z",
                "updated_at": "2026-05-01T00:00:00Z"
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated, IsAdminRole]
    
    def get(self, request):
        # Récupérer les résidents gérés par cet admin
        residents = User.objects.filter(
            role='RESIDENT',
            managed_by=request.user
        )
        
        # Récupérer les foyers de ces résidents
        managed_foyers = Foyer.objects.filter(
            user__in=residents
        ).distinct()
        
        # Récupérer les anomalies
        anomalies = Anomalie.objects.filter(
            consommation__foyer__in=managed_foyers
        ).select_related('consommation__foyer').order_by('-created_at')
        
        # Sérialiser
        anomalies_data = []
        for anomalie in anomalies:
            anomalies_data.append({
                'id': anomalie.id,
                'consommation_id': anomalie.consommation.id,
                'foyer_numero': anomalie.consommation.foyer.numero_foyer,
                'foyer_id': anomalie.consommation.foyer.id,
                'timestamp_consommation': anomalie.consommation.timestamp,
                'consommation_kwh': float(anomalie.consommation.kwh),
                'temperature': float(anomalie.consommation.temperature) if anomalie.consommation.temperature else None,
                'score_confiance': float(anomalie.score_confiance),
                'severite': anomalie.severite,
                'statut': anomalie.statut,
                'consultee_at': anomalie.consultee_at,
                'acquittee_at': anomalie.acquittee_at,
                'description': anomalie.description,
                'created_at': anomalie.created_at,
                'updated_at': anomalie.updated_at,
            })
        
        return Response({
            'count': len(anomalies_data),
            'results': anomalies_data,
        }, status=status.HTTP_200_OK)
