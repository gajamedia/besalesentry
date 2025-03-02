from django.db import connections
from rest_framework.response import Response
from rest_framework import status, viewsets
from rest_framework.permissions import IsAuthenticated
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.utils.timezone import now

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator
from rest_framework.decorators import action


class PagePagination(PageNumberPagination):
    page_size = 10  # Jumlah item per halaman
    page_size_query_param = 'page_size'  # Query parameter untuk mengatur jumlah item per halaman
    max_page_size = 100  # Batas maksimal item per halaman

class ProjectHeaderViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def list(self, request):
        """ Mendapatkan semua data tb_project_header yang belum dihapus """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, no_project, tgl_project, ket_project, nama_customer, " + 
                           "addr_customer, contact_customer, status_project, created_by, created_date, updated_by, updated_date, is_deleted " + 
                           "FROM tb_project_header WHERE is_deleted = 0")
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "no_project": row[1],
                "tgl_project": row[2],
                "ket_project": row[3],
                "nama_customer": row[4],
                "addr_customer": row[5],
                "contact_customer": row[6],
                "status_project": row[7],
                "created_by": row[8],
                "created_date": row[9],
                "updated_by": row[10],
                "updated_date": row[11],
                "is_deleted": row[12],
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'no_project': openapi.Schema(type=openapi.TYPE_STRING, description='Nomor Project'),
                'tgl_project': openapi.Schema(type=openapi.TYPE_STRING, format="date-time", description='Tanggal Project (YYYY-MM-DD HH:MM:SS)'),
                'ket_project': openapi.Schema(type=openapi.TYPE_STRING, description='Keterangan Project'),
                'nama_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Nama Customer'),
                'addr_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Alamat Customer'),
                'contact_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Kontak Customer'),
                'status_project': openapi.Schema(type=openapi.TYPE_STRING, maxLength=1, description='Status Project (1 karakter)'),
            },
            required=['no_project', 'tgl_project', 'nama_customer', 'status_project']
        ),
        responses={201: "Created"}
    )
    def create(self, request):
        """ Create new project header """
        # Ambil data dari body request
        no_project = request.data.get("no_project")
        tgl_project = request.data.get("tgl_project")
        ket_project = request.data.get("ket_project", "")
        nama_customer = request.data.get("nama_customer")
        addr_customer = request.data.get("addr_customer", "")
        contact_customer = request.data.get("contact_customer", "")
        status_project = request.data.get("status_project")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        # Validasi input
        if not (no_project and tgl_project and nama_customer and status_project):
            return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connections["mysql"].cursor() as cursor:
                # Masukkan data ke tabel
                cursor.execute("""
                    INSERT INTO tb_project_header 
                    (no_project, tgl_project, ket_project, nama_customer, addr_customer, contact_customer, status_project, 
                    created_by, created_date, updated_by, updated_date, is_deleted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, [
                    no_project, tgl_project, ket_project, nama_customer, addr_customer, contact_customer,
                    status_project, username, created_date, username, created_date
                ])

            return Response({"message": "Project created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID Project Header", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    def retrieve(self, request, pk=None):
        """ Mendapatkan detail data berdasarkan ID """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, no_project, tgl_project, ket_project, nama_customer, " + 
                           "addr_customer, contact_customer, status_project, created_by, created_date, updated_by, updated_date, is_deleted " + 
                           "FROM tb_project_header WHERE id = %s", [pk])
            row = cursor.fetchone()

        if row:
            return Response(
                {
                    "id": row[0],
                    "no_project": row[1],
                    "tgl_project": row[2],
                    "ket_project": row[3],
                    "nama_customer": row[4],
                    "addr_customer": row[5],
                    "contact_customer": row[6],
                    "status_project": row[7],
                    "created_by": row[8],
                    "created_date": row[9],
                    "updated_by": row[10],
                    "updated_date": row[11],
                    "is_deleted": row[12],
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('status_project', openapi.IN_QUERY, description="Status Project", type=openapi.TYPE_STRING),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    @action(detail=False, methods=["get"], url_path="retrieveby")
    def retrieve_by(self, request):
        """ Mendapatkan data berdasarkan status_project """
        status_project = request.GET.get("status_project")

        if not status_project:
            return Response({"error": "status_project is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                SELECT id, no_project, tgl_project, ket_project, nama_customer, 
                       addr_customer, contact_customer, status_project, 
                       created_by, created_date, updated_by, updated_date, is_deleted 
                FROM tb_project_header 
                WHERE status_project = %s
            """, [status_project])

            rows = cursor.fetchall()

        if not rows:
            return Response({"error": "No data found"}, status=status.HTTP_404_NOT_FOUND)

        data = [
            {
                "id": row[0],
                "no_project": row[1],
                "tgl_project": row[2],
                "ket_project": row[3],
                "nama_customer": row[4],
                "addr_customer": row[5],
                "contact_customer": row[6],
                "status_project": row[7],
                "created_by": row[8],
                "created_date": row[9],
                "updated_by": row[10],
                "updated_date": row[11],
                "is_deleted": row[12],
            }
            for row in rows
        ]

        return Response({"results": data}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['no_project', 'tgl_project', 'nama_customer', 'status_project'],
            properties={
                'no_project': openapi.Schema(type=openapi.TYPE_STRING, description='Nomor Project'),
                'tgl_project': openapi.Schema(type=openapi.TYPE_STRING, format="date-time", description='Tanggal Project (YYYY-MM-DD HH:MM:SS)'),
                'ket_project': openapi.Schema(type=openapi.TYPE_STRING, description='Keterangan Project'),
                'nama_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Nama Customer'),
                'addr_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Alamat Customer'),
                'contact_customer': openapi.Schema(type=openapi.TYPE_STRING, description='Kontak Customer'),
                'status_project': openapi.Schema(type=openapi.TYPE_STRING, maxLength=1, description='Status Project (1 karakter)'),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        no_project = request.data.get("no_project")
        tgl_project = request.data.get("tgl_project")
        ket_project = request.data.get("ket_project", "")
        nama_customer = request.data.get("nama_customer")
        addr_customer = request.data.get("addr_customer", "")
        contact_customer = request.data.get("contact_customer", "")
        status_project = request.data.get("status_project")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        # Validasi input
        if not (no_project and tgl_project and nama_customer and status_project):
            return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                    UPDATE tb_project_header SET no_project=%s, tgl_project=%s, ket_project=%s, nama_customer=%s, 
                        addr_customer=%s, contact_customer=%s, status_project=%s, updated_by=%s, updated_date=%s
                    WHERE id=%s
                """,
                [no_project, tgl_project, ket_project, nama_customer, addr_customer, contact_customer,
                    status_project, username, updated_date, pk]
            )

        return Response({"id": pk, "no_project": no_project, "tgl_project": tgl_project, 
                         "ket_project": ket_project, "nama_customer": nama_customer, "addr_customer": addr_customer,  
                         "contact_customer": contact_customer, "status_project": status_project,
                         "updated_by": username, "updated_date": updated_date}, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={204: "Deleted"},
    )
    def destroy(self, request, pk=None):
        """ Soft Delete: Menandai data sebagai is_deleted = 1 """
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                "UPDATE tb_project_header SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """
        Search data tb_project_header berdasarkan beberapa field dengan pagination
        """
        search_query = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        with connections["mysql"].cursor() as cursor:
            # Hitung total hasil
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tb_project_header
                WHERE is_deleted = 0 AND (
                    no_project LIKE %s OR 
                    tgl_project LIKE %s OR 
                    ket_project LIKE %s OR 
                    nama_customer LIKE %s OR 
                    addr_customer LIKE %s OR 
                    contact_customer LIKE %s OR 
                    status_project LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%"])
            total_items = cursor.fetchone()[0]

            # Query dengan pagination
            cursor.execute("""
                SELECT id, no_project, tgl_project, ket_project, nama_customer, 
                    addr_customer, contact_customer, status_project, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_project_header
                WHERE is_deleted = 0 AND (
                    no_project LIKE %s OR 
                    tgl_project LIKE %s OR 
                    ket_project LIKE %s OR 
                    nama_customer LIKE %s OR 
                    addr_customer LIKE %s OR 
                    contact_customer LIKE %s OR 
                    status_project LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
                LIMIT %s OFFSET %s
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", 
                  page_size, (page - 1) * page_size])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "no_project": row[1], 
                "tgl_project": row[2], 
                "ket_project": row[3], 
                "nama_customer": row[4], 
                "addr_customer": row[5], 
                "contact_customer": row[6], 
                "status_project": row[7], 
                "created_by": row[8],
                "created_date": row[9],
                "updated_by": row[10],
                "updated_date": row[11],
                "is_deleted": row[12],
            }
            for row in rows
        ]

        return Response({
            "count": total_items,
            "total_pages": (total_items // page_size) + (1 if total_items % page_size else 0),
            "current_page": page,
            "results": data
        }, status=status.HTTP_200_OK)

##################################################################################################################################################################
# Detail Project 
class ProjectDetilViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def list(self, request):
        """ Mendapatkan semua data tb_project_detail yang belum dihapus """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, id_project_header, lebar_bahan, lantai, ruangan, bed, tipe, " + 
                           "uk_room_l, uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase, tinggi_lipatan, nilai_pembagi, " +
                           "created_by, crated_date, updated_by, updated_date, is_deleted " + 
                           "FROM tb_project_detil WHERE is_deleted = 0")
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "id_project_header": row[1],
                "lebar_bahan": row[2],
                "lantai": row[3],
                "ruangan": row[4],
                "bed": row[5],
                "tipe": row[6],
                "uk_room_l": row[7],
                "uk_room_p": row[8],
                "uk_room_t": row[9],
                "stik": row[10],
                "elevasi": row[11],
                "tinggi_vitrase": row[12],
                "tinggi_lipatan": row[11],
                "nilai_pembagi": row[12],
                "created_by": row[13],
                "created_date": row[14],
                "updated_by": row[15],
                "updated_date": row[16],
                "is_deleted": row[17],
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_project_header': openapi.Schema(type=openapi.TYPE_INTEGER, description='id Project header'),
                'lebar_bahan': openapi.Schema(type=openapi.TYPE_INTEGER, description='Lebar Bahan'),
                'lantai': openapi.Schema(type=openapi.TYPE_STRING, description='Lantai'),
                'ruangan': openapi.Schema(type=openapi.TYPE_STRING, description='Ruangan'),
                'bed': openapi.Schema(type=openapi.TYPE_STRING, description='No.Bed'),
                'tipe': openapi.Schema(type=openapi.TYPE_STRING, description='Tipe'),
                'uk_room_l': openapi.Schema(type=openapi.TYPE_INTEGER, description='Lebar Ruangan'),
                'uk_room_p': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panjang Ruangan'),
                'uk_room_t': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Ruangan'),
                'stik': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stik'),
                'elevasi': openapi.Schema(type=openapi.TYPE_INTEGER, description='Elevasi'),
                'tinggi_vitrase': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Vitrase'),
                'tinggi_lipatan': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Lipatan'),
                'nilai_pembagi': openapi.Schema(type=openapi.TYPE_INTEGER, description='Nilai Pembagi'),
            },
            required=['id_project_header']
        ),
        responses={201: "Created"}
    )
    def create(self, request):
        """ Create new project detil """
        # Ambil data dari body request
        id_project_header = request.data.get("id_project_header")
        lebar_bahan = request.data.get("lebar_bahan")
        lantai = request.data.get("lantai", "")
        ruangan = request.data.get("ruangan")
        bed = request.data.get("bed", "")
        tipe = request.data.get("tipe", "")
        uk_room_l = request.data.get("uk_room_l")
        uk_room_p = request.data.get("uk_room_p")
        uk_room_t = request.data.get("uk_room_t")
        stik = request.data.get("stik", "")
        elevasi = request.data.get("elevasi")
        tinggi_vitrase = request.data.get("tinggi_vitrase", "")
        tinggi_lipatan = request.data.get("tinggi_lipatan", "")
        nilai_pembagi = request.data.get("nilai_pembagi")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        # Validasi input
        if not (id_project_header):
            return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connections["mysql"].cursor() as cursor:
                # Masukkan data ke tabel
                cursor.execute("""
                    INSERT INTO tb_project_detil 
                    (id_project_header, lebar_bahan, lantai, ruangan, bed, tipe, uk_room_l,
                    uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase, tinggi_lipatan, nilai_pembagi,            
                    created_by, created_date, updated_by, updated_date, is_deleted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, [
                    id_project_header, lebar_bahan, lantai, ruangan, bed, tipe,
                    uk_room_l, uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase,
                    tinggi_lipatan, nilai_pembagi, username, created_date, username, created_date
                ])

            return Response({"message": "Project Detil created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID Project Detil", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    def retrieve(self, request, pk=None):
        """ Mendapatkan detail data berdasarkan ID """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, id_project_header, lebar_bahan, lantai, ruangan, bed, tipe, " + 
                           "uk_room_l, uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase, tinggi_lipatan, nilai_pembagi, " + 
                           "created_by, created_date, updated_by, updated_date, is_deleted " + 
                           "FROM tb_project_detil WHERE id = %s", [pk])
            row = cursor.fetchone()

        if row:
            return Response(
                {
                    "id": row[0],
                    "id_project_header": row[1],
                    "lebar_bahan": row[2],
                    "lantai": row[3],
                    "ruangan": row[4],
                    "bed": row[5],
                    "tipe": row[6],
                    "uk_room_l": row[7],
                    "uk_room_p": row[8],
                    "uk_room_t": row[9],
                    "stik": row[10],
                    "elevasi": row[11],
                    "tinggi_vitrase": row[12],
                    "tinggi_lipatan": row[11],
                    "nilai_pembagi": row[12],
                    "created_by": row[13],
                    "created_date": row[14],
                    "updated_by": row[15],
                    "updated_date": row[16],
                    "is_deleted": row[17],
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_project_header'],
            properties={
                'id_project_header': openapi.Schema(type=openapi.TYPE_INTEGER, description='id Project header'),
                'lebar_bahan': openapi.Schema(type=openapi.TYPE_INTEGER, description='Lebar Bahan'),
                'lantai': openapi.Schema(type=openapi.TYPE_STRING, description='Lantai'),
                'ruangan': openapi.Schema(type=openapi.TYPE_STRING, description='Ruangan'),
                'bed': openapi.Schema(type=openapi.TYPE_STRING, description='No.Bed'),
                'tipe': openapi.Schema(type=openapi.TYPE_STRING, description='Tipe'),
                'uk_room_l': openapi.Schema(type=openapi.TYPE_INTEGER, description='Lebar Ruangan'),
                'uk_room_p': openapi.Schema(type=openapi.TYPE_INTEGER, description='Panjang Ruangan'),
                'uk_room_t': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Ruangan'),
                'stik': openapi.Schema(type=openapi.TYPE_INTEGER, description='Stik'),
                'elevasi': openapi.Schema(type=openapi.TYPE_INTEGER, description='Elevasi'),
                'tinggi_vitrase': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Vitrase'),
                'tinggi_lipatan': openapi.Schema(type=openapi.TYPE_INTEGER, description='Tinggi Lipatan'),
                'nilai_pembagi': openapi.Schema(type=openapi.TYPE_INTEGER, description='Nilai Pembagi'),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        id_project_header = request.data.get("id_project_header")
        lebar_bahan = request.data.get("lebar_bahan")
        lantai = request.data.get("lantai", "")
        ruangan = request.data.get("ruangan")
        bed = request.data.get("bed", "")
        tipe = request.data.get("tipe", "")
        uk_room_l = request.data.get("uk_room_l")
        uk_room_p = request.data.get("uk_room_p")
        uk_room_t = request.data.get("uk_room_t")
        stik = request.data.get("stik", "")
        elevasi = request.data.get("elevasi")
        tinggi_vitrase = request.data.get("tinggi_vitrase", "")
        tinggi_lipatan = request.data.get("tinggi_lipatan", "")
        nilai_pembagi = request.data.get("nilai_pembagi")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not id_project_header:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                    UPDATE tb_project_detil SET id_project_header=%s, lebar_bahan=%s, lantai=%s, ruangan=%s, bed=%s, tipe=%s, 
                        uk_room_l=%s, uk_room_p=%s, uk_room_t=%s, stik=%s, elevasi=%s, tinggi_vitrase=%s, tinggi_lipatan=%s, 
                        nilai_pembagi=%s, updated_by=%s, updated_date=%s
                    WHERE id=%s
                """,
                [id_project_header, lebar_bahan, lantai, ruangan, bed, tipe, uk_room_l, uk_room_p, uk_room_t, 
                 stik, elevasi, tinggi_vitrase, tinggi_lipatan, nilai_pembagi, username, updated_date, pk]
            )

        return Response({"id": pk, "id_project_header": id_project_header, "lebar_bahan": lebar_bahan, 
                         "lantai": lantai, "ruangan": ruangan, "bed": bed, "tipe": tipe, 
                         "stik": stik, "elevasi": elevasi, "tinggi_vitrase": tinggi_vitrase, "tinggi_lipatan": tinggi_lipatan,
                         "nilai_pembagi": nilai_pembagi, "updated_by": username, "updated_date": updated_date}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={204: "Deleted"},
    )
    def destroy(self, request, pk=None):
        """ Soft Delete: Menandai data sebagai is_deleted = 1 """
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                "UPDATE tb_project_detil SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """
        Search data tb_project_detil berdasarkan beberapa field dengan pagination
        """
        search_query = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        with connections["mysql"].cursor() as cursor:
            # Hitung total hasil
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tb_project_detil
                WHERE is_deleted = 0 AND (
                    id_project_header LIKE %s OR 
                    lebar_bahan LIKE %s OR 
                    lantai LIKE %s OR 
                    ruangan LIKE %s OR 
                    bed LIKE %s OR 
                    tipe LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
            total_items = cursor.fetchone()[0]

            # Query dengan pagination
            cursor.execute("""
                SELECT id, id_project_header, lebar_bahan, lantai, ruangan, bed, tipe, uk_room_l, uk_room_p, uk_room_t, 
                    stik, elevasi, tinggi_vitrase, tinggi_lipatan, nilai_pembagi, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_project_detil
                WHERE is_deleted = 0 AND (
                    id_project_header LIKE %s OR 
                    lebar_bahan LIKE %s OR  
                    lantai LIKE %s OR 
                    ruangan LIKE %s OR 
                    bed LIKE %s OR 
                    tipe LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
                LIMIT %s OFFSET %s
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", 
                  page_size, (page - 1) * page_size])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "id_project_header": row[1], 
                "lebar_bahan": row[2], 
                "lantai": row[3], 
                "ruangan": row[4], 
                "bed": row[5], 
                "tipe": row[6], 
                "uk_room_l": row[7],
                "uk_room_p": row[8],
                "uk_room_t": row[9],
                "stik": row[10],
                "elevasi": row[11],
                "tinggi_vitrase": row[12],
                "tinggi_lipatan": row[11],
                "nilai_pembagi": row[12],
                "created_by": row[13],
                "created_date": row[14],
                "updated_by": row[15],
                "updated_date": row[16],
                "is_deleted": row[17],
            }
            for row in rows
        ]

        return Response({
            "count": total_items,
            "total_pages": (total_items // page_size) + (1 if total_items % page_size else 0),
            "current_page": page,
            "results": data
        }, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_project_header', openapi.IN_QUERY, description="ID Project Header", type=openapi.TYPE_STRING),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def searchbyiph(self, request):
        """
        Search data tb_project_detil berdasarkan id_project_header
        """
        id_project_header = request.GET.get("id_project_header", "")
        
        if not id_project_header:
            return Response({"error": "Parameter id_project_header is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections["mysql"].cursor() as cursor:
            # Query data berdasarkan id_project_header
            cursor.execute("""
                SELECT id, id_project_header, lebar_bahan, lantai, ruangan, bed, tipe,  
                    uk_room_l, uk_room_p, uk_room_t, stik, elevasi, tinggi_vitrase, nilai_pembagi,
                    created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_project_detil
                WHERE is_deleted = 0 AND id_project_header = %s
            """, [id_project_header])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "id_project_header": row[1],
                "lebar_bahan": row[2],
                "lantai": row[3],
                "ruangan": row[4],
                "bed": row[5],
                "tipe": row[6],
                "uk_room_l": row[7],
                "uk_room_p": row[8],
                "uk_room_t": row[9],
                "stik": row[10],
                "elevasi": row[11],
                "tinggi_vitrase": row[12],
                "nilai_pembagi": row[13],
                "created_by": row[14],
                "created_date": row[15],
                "updated_by": row[16],
                "updated_date": row[17],
                "is_deleted": row[18],
            }
            for row in rows
        ]

        return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)





##################################################################################################################################################################
# Detail Item Project 
class DetilItemViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'id_project_detil': openapi.Schema(type=openapi.TYPE_INTEGER, description='id Project detil'),
                'item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID Bahan'),
                'item_code': openapi.Schema(type=openapi.TYPE_STRING, description='Kode Bahan'),
                'item_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nama Bahan'),
                'ukuran': openapi.Schema(type=openapi.TYPE_INTEGER, description='Ukuran Bahan'),
                'harga_beli': openapi.Schema(type=openapi.TYPE_NUMBER, format="float", description='Harga Beli'),
                'harga_jual': openapi.Schema(type=openapi.TYPE_NUMBER, format="float", description='Harga Jual'),
            },
            required=['id_project_detil']
        ),
        responses={201: "Created"}
    )
    def create(self, request):
        """ Create new project detil item """
        # Ambil data dari body request
        id_project_detil = request.data.get("id_project_detil")
        item_id = request.data.get("item_id")
        item_code = request.data.get("item_code")
        item_name = request.data.get("item_name")
        ukuran = request.data.get("ukuran")
        harga_beli = request.data.get("harga_beli")
        harga_jual = request.data.get("harga_jual")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        # Validasi input
        if not (id_project_detil):
            return Response({"error": "Required fields are missing"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            with connections["mysql"].cursor() as cursor:
                # Masukkan data ke tabel
                cursor.execute("""
                    INSERT INTO tb_project_detil_item 
                    (id_project_detil, item_id, item_code, item_name, ukuran, 
                    harga_beli, harga_jual, created_by, created_date, updated_by, updated_date, is_deleted)
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """, [
                    id_project_detil, item_id, item_code, item_name, 
                    ukuran, harga_beli, harga_jual, username, created_date, username, created_date
                ])

            return Response({"message": "Detil Item created successfully"}, status=status.HTTP_201_CREATED)

        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID Detil Item", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    def retrieve(self, request, pk=None):
        """ Mendapatkan detail Item data berdasarkan ID """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, id_project_detil, item_id, item_code, item_name, " + 
                           "ukuran, harga_beli, harga_jual, " + 
                           "created_by, created_date, updated_by, updated_date, is_deleted " + 
                           "FROM tb_project_detil_item WHERE id = %s", [pk])
            row = cursor.fetchone()

        if row:
            return Response(
                {
                    "id": row[0],
                    "id_project_detil": row[1],
                    "item_id": row[2],
                    "item_code": row[3],
                    "item_name": row[4],
                    "ukuran": row[5],
                    "harga_beli": row[6],
                    "harga_jual": row[7],
                    "created_by": row[8],
                    "created_date": row[9],
                    "updated_by": row[10],
                    "updated_date": row[11],
                    "is_deleted": row[12],
                },
                status=status.HTTP_200_OK
            )
        else:
            return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['id_project_detil'],
            properties={
                'id_project_detil': openapi.Schema(type=openapi.TYPE_INTEGER, description='id Project detil'),
                'item_id': openapi.Schema(type=openapi.TYPE_INTEGER, description='ID Bahan'),
                'item_code': openapi.Schema(type=openapi.TYPE_STRING, description='Kode Bahan'),
                'item_name': openapi.Schema(type=openapi.TYPE_STRING, description='Nama Bahan'),
                'ukuran': openapi.Schema(type=openapi.TYPE_INTEGER, description='Ukuran Bahan'),
                'harga_beli': openapi.Schema(type=openapi.TYPE_NUMBER, format="float", description='Harga Beli'),
                'harga_jual': openapi.Schema(type=openapi.TYPE_NUMBER, format="float", description='Harga Jual'),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        id_project_detil = request.data.get("id_project_detil")
        item_id = request.data.get("item_id")
        item_code = request.data.get("item_code")
        item_name = request.data.get("item_name")
        ukuran = request.data.get("ukuran")
        harga_beli = request.data.get("harga_beli")
        harga_jual = request.data.get("harga_jual")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not id_project_detil:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                    UPDATE tb_project_detil_item SET id_project_detil=%s, item_id=%s, item_code=%s, item_name=%s, 
                        ukuran=%s, harga_beli=%s, harga_jual=%s, updated_by=%s, updated_date=%s
                    WHERE id=%s
                """,
                [id_project_detil, item_id, item_code, item_name, ukuran,  
                 harga_beli, harga_jual, username, updated_date, pk]
            )

        return Response({"id": pk, "id_project_detil": id_project_detil, "item_id": item_id, 
                         "item_code": item_code, "item_name": item_name, "harga_beli": harga_beli,
                         "harga_jual": harga_jual, "updated_by": username, "updated_date": updated_date}, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={204: "Deleted"},
    )
    def destroy(self, request, pk=None):
        """ Soft Delete: Menandai data sebagai is_deleted = 1 """
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                "UPDATE tb_project_detil_item SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search query", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """
        Search data tb_project_detil berdasarkan beberapa field dengan pagination
        """
        search_query = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        with connections["mysql"].cursor() as cursor:
            # Hitung total hasil
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tb_project_detil_item
                WHERE is_deleted = 0 AND (
                    id_project_detil LIKE %s OR 
                    item_id LIKE %s OR 
                    item_code LIKE %s OR 
                    item_name LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%"])
            total_items = cursor.fetchone()[0]

            # Query dengan pagination
            cursor.execute("""
                SELECT id, id_project_detil, item_id, item_code, item_name,  
                    ukuran, harga_beli, harga_jual, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_project_detil_item
                WHERE is_deleted = 0 AND (
                    id_project_detil LIKE %s OR 
                    item_id LIKE %s OR  
                    item_code LIKE %s OR 
                    item_name LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
                LIMIT %s OFFSET %s
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  f"%{search_query}%", f"%{search_query}%", f"%{search_query}%",
                  page_size, (page - 1) * page_size])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "id_project_detil": row[1], 
                "item_id": row[2], 
                "item_code": row[3], 
                "item_name": row[4], 
                "ukuran": row[5], 
                "harga_beli": row[6], 
                "harga_jual": row[7],
                "created_by": row[8],
                "created_date": row[9],
                "updated_by": row[10],
                "updated_date": row[11],
                "is_deleted": row[12],
            }
            for row in rows
        ]

        return Response({
            "count": total_items,
            "total_pages": (total_items // page_size) + (1 if total_items % page_size else 0),
            "current_page": page,
            "results": data
        }, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id_project_detil', openapi.IN_QUERY, description="ID Project Detail", type=openapi.TYPE_STRING),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def searchbyipd(self, request):
        """
        Search data tb_project_detil_item berdasarkan id_project_detil
        """
        id_project_detil = request.GET.get("id_project_detil", "")
        
        if not id_project_detil:
            return Response({"error": "Parameter id_project_detil is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections["mysql"].cursor() as cursor:
            # Query data berdasarkan id_project_detil
            cursor.execute("""
                SELECT id, id_project_detil, item_id, item_code, item_name,  
                    ukuran, harga_beli, harga_jual, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_project_detil_item
                WHERE is_deleted = 0 AND id_project_detil = %s
            """, [id_project_detil])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "id_project_detil": row[1],
                "item_id": row[2],
                "item_code": row[3],
                "item_name": row[4],
                "ukuran": row[5],
                "harga_beli": row[6],
                "harga_jual": row[7],
                "created_by": row[8],
                "created_date": row[9],
                "updated_by": row[10],
                "updated_date": row[11],
                "is_deleted": row[12],
            }
            for row in rows
        ]

        return Response({"count": len(data), "results": data}, status=status.HTTP_200_OK)
