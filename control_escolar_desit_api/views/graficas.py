from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from control_escolar_desit_api.models import Administradores, Maestros, Alumnos


class TotalesUsuariosView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        total_admins = Administradores.objects.count()
        total_maestros = Maestros.objects.count()
        total_alumnos = Alumnos.objects.count()

        data = {
            "administradores": total_admins,
            "maestros": total_maestros,
            "alumnos": total_alumnos,
            "total": total_admins + total_maestros + total_alumnos
        }
        return Response(data)
