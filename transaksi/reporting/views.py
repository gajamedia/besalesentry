from django.db import connections
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now
from rest_framework.decorators import action

class PenawaranViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_project_header', openapi.IN_QUERY, description="ID Project Header", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def penawaran_summary(self, request):
        """ API untuk menampilkan data penawaran berdasarkan ID Project """
        id_project_header = request.GET.get("id_project_header")

        # if not id_project_header:
        #     return Response({"error": "id_project_heaader is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        with connections["mysql"].cursor() as cursor:
            # Ambil data project header
            if id_project_header:
                cursor.execute("""
                    SELECT id, no_project, tgl_project, ket_project, nama_customer, status_project, addr_customer
                    FROM tb_project_header
                    WHERE id = %s
                """, [id_project_header])
            else:
                cursor.execute("""
                    SELECT id, no_project, tgl_project, ket_project, nama_customer, status_project, addr_customer
                    FROM tb_project_header
                    WHERE status_project='0'
                """)
            projects = cursor.fetchall()

            if not projects:
                return Response({"error": "Tidak ada proyek yang ditemukan"}, status=status.HTTP_404_NOT_FOUND)

            response_data = []
            
            for project in projects:
                project_data = {
                    "id": project[0],
                    "no_project": project[1],
                    "tgl_project": project[2],
                    "ket_project": project[3],
                    "nama_customer": project[4],
                    "status_project": project[5],
                    "addr_customer": project[6],
                }

                # Ambil data project detil
                cursor.execute("""
                    SELECT id, lebar_bahan, lantai, ruangan, bed, tipe, 
                        uk_room_l, uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase, nilai_pembagi, tinggi_lipatan
                    FROM tb_project_detil
                    WHERE id_project_header = %s
                """, [project_data["id"]])
                project_details = cursor.fetchall()

                details_data = []
                qty_map = {}

                for detail in project_details:
                    id_detail = detail[0]
                    lantai = detail[2]
                    ruangan = detail[3]
                    tinggi_lipatan = detail[13]

                    key = f"{lantai}_{ruangan}"
                    qty_map[key] = qty_map.get(key, 0) + 1

                    tinggi_gorden = detail[8] - detail[10]
                    lebar_gorden = detail[6] + detail[7]
                    tinggi_kain = tinggi_gorden - detail[11]
                    panel = lebar_gorden / detail[12]

                    print ("id_detail: ", id_detail)
                    # Ambil item terkait
                        # JOIN tb_bahan bi ON pdi.item_id = bi.id
                        # JOIN tb_jenisbahan jb ON bi.id_jenis = jb.id
                        #, jb.nama_jenis
                    cursor.execute("""
                        SELECT pdi.item_code, pdi.ukuran, pdi.harga_beli, pdi.harga_jual, pdi.item_name
                        FROM tb_project_detil_item pdi
                        WHERE pdi.id_project_detil = %s
                    """, [id_detail])
                    items = cursor.fetchall()

                    item_data = []
                    for item in items:
                        print ("isi items[]: ", item[0])
                        volume = ((tinggi_gorden + tinggi_lipatan) * panel) / 100
                        item_data.append({
                            "item_code": item[0],
                            "ukuran": item[1],
                            "harga_beli": item[2],
                            "harga_jual": item[3],
                            "item_name": item[4],
                            "volume": volume
                        })

                    details_data.append({
                        "lantai": lantai,
                        "ruangan": ruangan,
                        "bed": detail[4],
                        "tipe": detail[5],
                        "tinggi_gorden": tinggi_gorden,
                        "lebar_gorden": lebar_gorden,
                        "tinggi_kain": tinggi_kain,
                        "panel": panel,
                        "items": item_data
                    })

                # Menambahkan Qty berdasarkan lantai dan ruangan yang sama
                for detail in details_data:
                    key = f"{detail['lantai']}_{detail['ruangan']}"
                    detail["qty"] = qty_map[key]
                    for item in detail["items"]:
                        item["volume"] *= detail["qty"]  # Sesuaikan volume berdasarkan Qty

                response_data.append({
                    "customer": {
                        "nama_customer": project_data["nama_customer"],
                        "addr_customer": project_data["addr_customer"]
                    },
                    "project": {
                        "no_project": project_data["no_project"],
                        "tgl_project": project_data["tgl_project"],
                        "ket_project": project_data["ket_project"]
                    },
                    "details": details_data
                })

        return Response(response_data, status=status.HTTP_200_OK)    
    #@action(detail=False, methods=["get"], url_path="penawaran_summary")
    # def penawaran_summary(self, request):
    #     """
    #     Mengambil data dari tb_project_detil yang dijumlahkan berdasarkan ruangan dan id_project_header
    #     """
    #     id_project_header = request.GET.get("id_project_header")

    #     if not id_project_header:
    #         return Response({"error": "id_project_header is required"}, status=status.HTTP_400_BAD_REQUEST)

    #     with connections["mysql"].cursor() as cursor:
    #         cursor.execute("""
    #             SELECT ruangan, COUNT(*) as qty
    #             FROM tb_project_detil
    #             WHERE is_deleted = 0 AND id_project_header = %s
    #             GROUP BY ruangan
    #         """, [id_project_header])
            
    #         results = cursor.fetchall()

    #     data = [{"ruangan": row[0], "qty": row[1]} for row in results]

    #     return Response({"results": data}, status=status.HTTP_200_OK)    