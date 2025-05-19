from django.db import connections
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now
from rest_framework.decorators import action
import math

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

            kebutuhan_total_kain_split = 0
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
                lebar_total = uk_room_l + uk_room_p
                panel = math.ceil(lebar_total / nilai_pembagi)

                # Volume Kain
                volume_kain = ((tinggi_gorden + tinggi_lipatan) * panel)/100

                tinggi_kain = (tinggi_gorden - tinggi_vitrase)

                if tinggi_lipatan==25:
                    kain = (tinggi_gorden - tinggi_vitrase) + tinggi_lipatan
                else:
                    kain = (tinggi_gorden - tinggi_vitrase) + (tinggi_lipatan/2)

                kebutuhan_kain_split = (kain * panel) / 100
                # kebutuhan_kain_vitrase = (tinggi_vitrase * panel) / 100
                # kebutuhan = tinggi_kain * panel

                kebutuhan_total_kain_split += kebutuhan_kain_split
                # kebutuhan_total_kain_vitrase += kebutuhan_kain_vitrase

                detail_list.append({
                    # "lantai": lantai,
                    # "ruangan": ruangan,
                    "tinggi_kain": tinggi_kain,
                    "lebar_total": lebar_total,
                    "panel": panel,
                    "volume_kain": volume_kain,
                    "elevasi": elevasi,
                    "tinggivitrase": tinggi_vitrase,
                    "tinggiruangan": uk_room_t,
                    "tinggilipatan": tinggi_lipatan,
                    "kebutuhan_kain_split": kebutuhan_kain_split
                })

        return Response({
            "total_kebutuhan_kain_split": round(kebutuhan_total_kain_split, 2),
            "details": detail_list
        }, status=status.HTTP_200_OK)
    

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def kebutuhan_vitrase(self, request):
        """ Menghitung total kebutuhan vitrase untuk semua detil project """
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
            kebutuhan = 0
            detail_list = []

            for detil in detils:
                uk_room_l = detil[4]
                uk_room_p = detil[5]
                tinggi_vitrase = detil[8]
                nilai_pembagi = detil[9]
                tinggi_lipatan = detil[10]

                lebar_total = uk_room_l + uk_room_p
                panel = math.ceil(lebar_total / nilai_pembagi)

                if tinggi_lipatan==30:
                    tinggi_lipatan = tinggi_lipatan/2
                    kebutuhan = ((tinggi_vitrase + tinggi_lipatan) * panel) / 100

                kebutuhan_total += kebutuhan

                detail_list.append({
                    "tinggi_vitrase": tinggi_vitrase,
                    "tinggi_lipatan": tinggi_lipatan,
                    "lebar_total": lebar_total,
                    "panel": panel,
                    "kebutuhan_kain_vitrase": kebutuhan
                })

        return Response({
            "total_kebutuhan_kain_vitrase": round(kebutuhan_total, 2),
            "details": detail_list
        }, status=status.HTTP_200_OK)
