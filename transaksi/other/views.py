from django.db import connections
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now
from rest_framework.decorators import action

class OtherViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def kebutuhan_kain(self, request):
        """ Menghitung total kebutuhan kain untuk semua detil project """
        id_project_detil = request.GET.get("id_project_detil")

        with connections["mysql"].cursor() as cursor:
            if id_project_detil:
                cursor.execute("""
                    SELECT id, lebar_bahan, lantai, ruangan, 
                        uk_room_l, uk_room_p, uk_room_t, elevasi, tinggi_vitrase, nilai_pembagi, tinggi_lipatan
                    FROM tb_project_detil
                    WHERE id = %s
                """, [id_project_detil])
            else:
                cursor.execute("""
                    SELECT id, lebar_bahan, lantai, ruangan, 
                        uk_room_l, uk_room_p, uk_room_t, elevasi, tinggi_vitrase, nilai_pembagi, tinggi_lipatan
                    FROM tb_project_detil
                """)

            detils = cursor.fetchall()

            if not detils:
                return Response({"error": "Data detil tidak ditemukan"}, status=status.HTTP_404_NOT_FOUND)

            kebutuhan_total = 0
            detail_list = []

            for detil in detils:
                # id = detil[0]
                # lantai = detil[2]
                # ruangan = detil[3]
                uk_room_l = detil[4]
                uk_room_p = detil[5]
                uk_room_t = detil[6]
                elevasi = detil[7]
                tinggi_vitrase = detil[8]
                nilai_pembagi = detil[9]
                tinggi_lipatan = detil[10]

                # Hitung kebutuhan kain
                tinggi_gorden = uk_room_t - elevasi
                tinggi_kain = (tinggi_gorden - tinggi_vitrase) + tinggi_lipatan
                lebar_total = uk_room_l + uk_room_p
                panel = lebar_total / nilai_pembagi

                kebutuhan = (tinggi_kain * panel) / 100

                kebutuhan_total += kebutuhan

                detail_list.append({
                    # "lantai": lantai,
                    # "ruangan": ruangan,
                    "tinggi_kain": tinggi_kain,
                    "lebar_total": lebar_total,
                    "panel": panel,
                    "kebutuhan_kain": kebutuhan
                })

        return Response({
            "total_kebutuhan_kain": round(kebutuhan_total, 2),
            "details": detail_list
        }, status=status.HTTP_200_OK)