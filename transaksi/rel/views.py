from django.db import connections
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
# from django.utils.timezone import now
# from rest_framework.decorators import action
import math

class RelViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('item_code', openapi.IN_QUERY, description="Kode Item", type=openapi.TYPE_STRING)
        ],
        responses={200: "Success"}
    )
    def kebutuhan_rel(self, request):
        """ Menghitung total kebutuhan rel untuk semua detil project """
        id_project_detil = request.GET.get("id_project_detil")
        item_code = request.GET.get("item_code")

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

            kebutuhan_qty_rel = 0

            for detil in detils:
                uk_room_l = detil[4]
                uk_room_p = detil[5]

                # kebutuhan_qty_rel += kebutuhan_qty_rel
                kebutuhan_qty_rel += (uk_room_l + uk_room_p) / 100

        # Ambil harga jual dari tb_bahan
        harga_satuan = 0
        if item_code:
            with connections["mysql"].cursor() as cursor:
                cursor.execute("""
                    SELECT harga_jual 
                    FROM tb_bahan
                    WHERE item_code = %s
                    LIMIT 1
                """, [item_code])
                row = cursor.fetchone()
                if row:
                    harga_satuan = row[0]

        # Hitung harga total rel
        harga_total_rel = kebutuhan_qty_rel * harga_satuan

        return Response({
            "total_qty_rel": round(kebutuhan_qty_rel, 2),
            "harga_rel": round(harga_total_rel, 2)
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('item_code', openapi.IN_QUERY, description="Kode Item", type=openapi.TYPE_STRING)
        ],
        responses={200: "Success"}
    )
    def kebutuhan_roda(self, request):
        """ Menghitung total kebutuhan roda untuk semua detil project """
        id_project_detil = request.GET.get("id_project_detil")
        item_code = request.GET.get("item_code")

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

            kebutuhan_qty_roda = 0

            for detil in detils:
                uk_room_l = detil[4]
                uk_room_p = detil[5]
                nilai_pembagi = detil[9]

                lebar_total = uk_room_l + uk_room_p
                panel = math.ceil(lebar_total / nilai_pembagi)


                # kebutuhan_qty_rel += kebutuhan_qty_rel
                kebutuhan_qty_roda += panel * 6

        # Ambil harga jual dari tb_bahan
        harga_satuan = 0
        if item_code:
            with connections["mysql"].cursor() as cursor:
                cursor.execute("""
                    SELECT harga_jual 
                    FROM tb_bahan
                    WHERE item_code = %s
                    LIMIT 1
                """, [item_code])
                row = cursor.fetchone()
                if row:
                    harga_satuan = row[0]

        # Hitung harga total rel
        harga_total_roda = kebutuhan_qty_roda * harga_satuan

        return Response({
            "total_qty_roda": round(kebutuhan_qty_roda, 2),
            "harga_roda": round(harga_total_roda, 2)
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('item_code', openapi.IN_QUERY, description="Kode Item", type=openapi.TYPE_STRING),
            openapi.Parameter('qty_curved45', openapi.IN_QUERY, description="Qty Curved45", type=openapi.TYPE_INTEGER)
        ],
        responses={200: "Success"}
    )
    def kebutuhan_bracketl(self, request):
        """ Menghitung total kebutuhan Bracket L untuk semua detil project """
        id_project_detil = request.GET.get("id_project_detil")
        item_code = request.GET.get("item_code")
        qty_curved45 = request.GET.get("qty_curved45")

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

            kebutuhan_qty_bracketl = 0

            for detil in detils:
                # uk_room_l = detil[4]
                # uk_room_p = detil[5]
                # nilai_pembagi = detil[9]

                # lebar_total = uk_room_l + uk_room_p
                # panel = math.ceil(lebar_total / nilai_pembagi)


                # kebutuhan_qty_rel += kebutuhan_qty_rel
                kebutuhan_qty_bracketl += qty_curved45 * 2

        # Ambil harga jual dari tb_bahan
        harga_satuan = 0
        if item_code:
            with connections["mysql"].cursor() as cursor:
                cursor.execute("""
                    SELECT harga_jual 
                    FROM tb_bahan
                    WHERE item_code = %s
                    LIMIT 1
                """, [item_code])
                row = cursor.fetchone()
                if row:
                    harga_satuan = row[0]

        # Hitung harga total rel
        harga_total_bracketl = kebutuhan_qty_bracketl * harga_satuan

        return Response({
            "total_qty_bracketl": round(kebutuhan_qty_bracketl, 2),
            "harga_bracketl": round(harga_total_bracketl, 2)
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail (Opsional)", type=openapi.TYPE_INTEGER),
            openapi.Parameter('item_code', openapi.IN_QUERY, description="Kode Item", type=openapi.TYPE_STRING),
            openapi.Parameter('l', openapi.IN_QUERY, description="L", type=openapi.TYPE_INTEGER),
            openapi.Parameter('p', openapi.IN_QUERY, description="P", type=openapi.TYPE_INTEGER)
        ],
        responses={200: "Success"}
    )
    def kebutuhan_brackets(self, request):
        """ Menghitung total kebutuhan Bracket L untuk semua detil project """
        id_project_detil = request.GET.get("id_project_detil")
        item_code = request.GET.get("item_code")
        l = request.GET.get("l")
        p = request.GET.get("p")

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

            kebutuhan_qty_brackets = 0

            for detil in detils:
                # uk_room_l = detil[4]
                # uk_room_p = detil[5]
                # nilai_pembagi = detil[9]

                # lebar_total = uk_room_l + uk_room_p
                # panel = math.ceil(lebar_total / nilai_pembagi)


                # kebutuhan_qty_rel += kebutuhan_qty_rel
                kebutuhan_qty_brackets += (l+p)

        # Ambil harga jual dari tb_bahan
        harga_satuan = 0
        if item_code:
            with connections["mysql"].cursor() as cursor:
                cursor.execute("""
                    SELECT harga_jual 
                    FROM tb_bahan
                    WHERE item_code = %s
                    LIMIT 1
                """, [item_code])
                row = cursor.fetchone()
                if row:
                    harga_satuan = row[0]

        # Hitung harga total rel
        harga_total_brackets = kebutuhan_qty_brackets * harga_satuan

        return Response({
            "total_qty_brackets": round(kebutuhan_qty_brackets, 2),
            "harga_brackets": round(harga_total_brackets, 2)
        }, status=status.HTTP_200_OK)

