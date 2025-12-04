from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from control_escolar_desit_api.models import Materias, Maestros
from control_escolar_desit_api.serializers import MateriaSerializer
from datetime import time


class MateriasAll(generics.CreateAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        materias = Materias.objects.select_related('profesor__user').order_by("nrc")
        data = MateriaSerializer(materias, many=True).data
        return Response(data, status=status.HTTP_200_OK)


class MateriasView(generics.CreateAPIView):
    def get_permissions(self):
        if self.request.method in ['GET', 'PUT', 'DELETE']:
            return [permissions.IsAuthenticated()]
        return []

    # Obtener una materia por ID
    def get(self, request, *args, **kwargs):
        materia_id = request.GET.get("id")
        materia = get_object_or_404(Materias.objects.select_related('profesor__user'), id=materia_id)
        data = MateriaSerializer(materia, many=False).data
        return Response(data, status=status.HTTP_200_OK)

    # Registrar materia
    @transaction.atomic
    def post(self, request, *args, **kwargs):
        # Validaciones
        nrc = request.data.get("nrc")
        if Materias.objects.filter(nrc=nrc).exists():
            return Response({"message": f"El NRC {nrc} ya existe."}, status=status.HTTP_400_BAD_REQUEST)

        # Profesor (id de maestro)
        profesor_id = request.data.get("profesor")
        profesor = get_object_or_404(Maestros, id=profesor_id)

        # Horas 
        hora_inicio_str = request.data.get("hora_inicio")
        hora_fin_str = request.data.get("hora_fin")

        try:
            h_ini = time.fromisoformat(hora_inicio_str)
            h_fin = time.fromisoformat(hora_fin_str)
        except Exception:
            return Response({"message": "Formato de hora inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if h_ini >= h_fin:
            return Response({"message": "La hora de inicio debe ser menor a la hora final."},
                            status=status.HTTP_400_BAD_REQUEST)

        materia = Materias.objects.create(
            nrc=nrc,
            nombre_materia=request.data.get("nombre_materia"),
            seccion=request.data.get("seccion"),
            dias=request.data.get("dias"),
            hora_inicio=h_ini,
            hora_fin=h_fin,
            salon=request.data.get("salon"),
            programa_educativo=request.data.get("programa_educativo"),
            profesor=profesor,
            creditos=request.data.get("creditos"),
        )
        return Response({"materia_created_id": materia.id}, status=status.HTTP_201_CREATED)

    # Actualizar materia
    @transaction.atomic
    def put(self, request, *args, **kwargs):
        materia = get_object_or_404(Materias, id=request.data.get("id"))

        nuevo_nrc = request.data.get("nrc")
        if Materias.objects.filter(nrc=nuevo_nrc).exclude(id=materia.id).exists():
            return Response({"message": f"El NRC {nuevo_nrc} ya está en uso."}, status=status.HTTP_400_BAD_REQUEST)

        profesor_id = request.data.get("profesor")
        profesor = get_object_or_404(Maestros, id=profesor_id)

        hora_inicio_str = request.data.get("hora_inicio")
        hora_fin_str = request.data.get("hora_fin")
        try:
            h_ini = time.fromisoformat(hora_inicio_str)
            h_fin = time.fromisoformat(hora_fin_str)
        except Exception:
            return Response({"message": "Formato de hora inválido."}, status=status.HTTP_400_BAD_REQUEST)

        if h_ini >= h_fin:
            return Response({"message": "La hora de inicio debe ser menor a la hora final."},
                            status=status.HTTP_400_BAD_REQUEST)

        materia.nrc = nuevo_nrc
        materia.nombre_materia = request.data.get("nombre_materia")
        materia.seccion = request.data.get("seccion")
        materia.dias = request.data.get("dias")
        materia.hora_inicio = h_ini
        materia.hora_fin = h_fin
        materia.salon = request.data.get("salon")
        materia.programa_educativo = request.data.get("programa_educativo")
        materia.profesor = profesor
        materia.creditos = request.data.get("creditos")
        materia.save()

        return Response({"message": "Materia actualizada correctamente"}, status=status.HTTP_200_OK)

    # Eliminar materia
    @transaction.atomic
    def delete(self, request, *args, **kwargs):
        materia_id = kwargs.get("id_materia", None)
        if not materia_id:
            return Response({"message": "Se necesita el ID de la materia."}, status=status.HTTP_400_BAD_REQUEST)

        materia = get_object_or_404(Materias, id=materia_id)
        materia.delete()
        return Response({"message": f"Materia con ID {materia_id} eliminada correctamente."},
                        status=status.HTTP_200_OK)
