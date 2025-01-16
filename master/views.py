from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import connection, connections  # Untuk menjalankan query langsung
from django.utils.timezone import now
# from django.http import JsonResponse

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator

class PagePagination(PageNumberPagination):
    page_size = 10  # Jumlah item per halaman
    page_size_query_param = 'page_size'  # Query parameter untuk mengatur jumlah item per halaman
    max_page_size = 100  # Batas maksimal item per halaman

class JenisBahanViewSet(ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login
    pagination_class = PagePagination  # Menetapkan pagination
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def list(self, request):
        """ Mendapatkan semua data tb_jenisbahan yang belum dihapus """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted FROM tb_jenisbahan WHERE is_deleted = 0")
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "nama_jenis": row[1],
                "created_by": row[2],
                "created_date": row[3],
                "updated_by": row[4],
                "updated_date": row[5],
                "is_deleted": row[6],
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'Authorization', openapi.IN_HEADER, 
                description="Token JWT, silakan tambahkan 'Bearer ' sebelum token Anda", 
                type=openapi.TYPE_STRING,
                default="Bearer "
            ),
            openapi.Parameter(
                'page', openapi.IN_QUERY, 
                description="Nomor halaman", 
                type=openapi.TYPE_INTEGER
            ),
            openapi.Parameter(
                'page_size', openapi.IN_QUERY, 
                description="Jumlah item per halaman", 
                type=openapi.TYPE_INTEGER
            )
        ],
        responses={200: "Success"}
    )
    def list_pagination(self, request):
        """ Mendapatkan semua data tb_jenisbahan yang belum dihapus dengan pagination """
        page = request.GET.get('page', 1)  # Default halaman pertama
        page_size = request.GET.get('page_size', 10)  # Default 10 item per halaman

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                """
                SELECT id, nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted 
                FROM tb_jenisbahan WHERE is_deleted = 0
                """
            )
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "nama_jenis": row[1],
                "created_by": row[2],
                "created_date": row[3],
                "updated_by": row[4],
                "updated_date": row[5],
                "is_deleted": row[6],
            }
            for row in rows
        ]

        # Menggunakan Paginator untuk pagination manual
        paginator = Paginator(data, page_size)
        paginated_data = paginator.get_page(page)

        response_data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": paginated_data.number,
            "next": paginated_data.next_page_number() if paginated_data.has_next() else None,
            "previous": paginated_data.previous_page_number() if paginated_data.has_previous() else None,
            "results": paginated_data.object_list,
        }

        return Response(response_data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['nama_jenis'],
            properties={
                'nama_jenis': openapi.Schema(type=openapi.TYPE_STRING, description="Nama jenis bahan"),
            }
        ),
        responses={201: "Created"},
    )
    def create(self, request):
        """ Menambahkan data baru ke tb_jenisbahan """
        nama_jenis = request.data.get("nama_jenis")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        if not nama_jenis:
            return Response({"error": "NamaJenis is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tb_jenisbahan (nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted) 
                VALUES (%s, %s, %s, %s, %s, 0)
                """,
                [nama_jenis, username, created_date, username, created_date]
            )
            new_id = cursor.lastrowid

        return Response({"id": new_id, "nama_jenis": nama_jenis}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID Jenis Bahan", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    def retrieve(self, request, pk=None):
        """ Mendapatkan detail data berdasarkan ID """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted FROM tb_jenisbahan WHERE id = %s", [pk])
            row = cursor.fetchone()

        if row:
            return Response(
                {
                    "id": row[0],
                    "nama_jenis": row[1],
                    "created_by": row[2],
                    "created_date": row[3],
                    "updated_by": row[4],
                    "updated_date": row[5],
                    "is_deleted": row[6],
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
            required=['nama_jenis'],
            properties={
                'nama_jenis': openapi.Schema(type=openapi.TYPE_STRING, description="Nama jenis bahan"),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        nama_jenis = request.data.get("nama_jenis")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not nama_jenis:
            return Response({"error": "NamaJenis is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                "UPDATE tb_jenisbahan SET nama_jenis=%s, updated_by=%s, updated_date=%s WHERE id=%s",
                [nama_jenis, username, updated_date, pk]
            )

        return Response({"id": pk, "nama_jenis": nama_jenis, "updated_by": username, "updated_date": updated_date}, status=status.HTTP_200_OK)

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
                "UPDATE tb_jenisbahan SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


class BahanViewSet(ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login
    pagination_class = PagePagination  # Menetapkan pagination
    
    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    def list(self, request):
        """ Mendapatkan semua data tb_bahan yang belum dihapus """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, item_code, item_name, id_jenis, ukuran, keterangan," + 
                           "created_by, created_date, updated_by, updated_date, is_deleted FROM tb_bahan WHERE is_deleted = 0")
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "item_code": row[1],
                "item_name": row[2],
                "id_jenis": row[3],
                "ukuran": row[4],
                "keterangan": row[5],
                "created_by": row[6],
                "created_date": row[7],
                "updated_by": row[8],
                "updated_date": row[9],
                "is_deleted": row[10],
            }
            for row in rows
        ]
        return Response(data, status=status.HTTP_200_OK)


    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer "),
            openapi.Parameter('page', openapi.IN_QUERY, description="Nomor Halaman", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Jumlah Item per halaman", type=openapi.TYPE_INTEGER),
        ],
        responses={200: "Success"}
    )
    def list_pagination(self, request):
        """ Mendapatkan semua data tb_bahan yang belum dihapus dengan pagination """
        page = request.GET.get('page', 1)  # Default halaman pertama
        page_size = request.GET.get('page_size', 10)  # Default 10 item per halaman

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                SELECT id, item_code, item_name, id_jenis, ukuran, keterangan, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_bahan
                WHERE is_deleted = 0
            """
            )
            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "item_code": row[1],
                "item_name": row[2],
                "id_jenis": row[3],
                "ukuran": row[4],
                "keterangan": row[5],
                "created_by": row[6],
                "created_date": row[7],
                "updated_by": row[8],
                "updated_date": row[9],
                "is_deleted": row[10],
            }
            for row in rows
        ]

        # Menggunakan Paginator untuk pagination manual
        paginator = Paginator(data, page_size)
        paginated_data = paginator.get_page(page)

        response_data = {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": paginated_data.number,
            "next": paginated_data.next_page_number() if paginated_data.has_next() else None,
            "previous": paginated_data.previous_page_number() if paginated_data.has_previous() else None,
            "results": paginated_data.object_list,
        }

        return Response(response_data, status=status.HTTP_200_OK)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['item_code','id_jenis'],
            properties={
                'item_code': openapi.Schema(type=openapi.TYPE_STRING),
                'item_name': openapi.Schema(type=openapi.TYPE_STRING),
                'id_jenis': openapi.Schema(type=openapi.TYPE_INTEGER),
                'ukuran': openapi.Schema(type=openapi.TYPE_INTEGER),
                'keterangan': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            }
        ),
        responses={201: "Created"},
    )
    def create(self, request):
        """ Menambahkan data baru ke tb_bahan """
        item_code = request.data.get("item_code")
        item_name = request.data.get("item_name")
        id_jenis = request.data.get("id_jenis")
        ukuran = request.data.get("ukuran")
        keterangan = request.data.get("keterangan")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        if not item_code:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_jenis:
            return Response({"error": "ID Jenis Bahan is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tb_bahan (item_code, item_name, id_jenis, ukuran, keterangan, created_by, created_date, updated_by, updated_date, is_deleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """,
                [item_code, item_name, id_jenis, ukuran, keterangan, username, created_date, username, created_date]
            )
            new_id = cursor.lastrowid

        return Response({"id": new_id, "item_code": item_code, "item_name": item_name, 
                         "id_jenis": id_jenis, "ukuran": ukuran, "keterangan": keterangan}, status=status.HTTP_201_CREATED)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('id', openapi.IN_PATH, description="ID Bahan", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"},
    )
    def retrieve(self, request, pk=None):
        """ Mendapatkan detail data berdasarkan ID """
        with connections['mysql'].cursor() as cursor:
            cursor.execute("SELECT id, item_code, item_name, id_jenis, ukuran, keterangan, " + 
                           "created_by, created_date, updated_by, updated_date, is_deleted FROM tb_bahan WHERE id = %s", [pk])
            row = cursor.fetchone()

        if row:
            return Response(
                {
                    "id": row[0],
                    "item_code": row[1],
                    "item_name": row[2],
                    "id_jenis": row[3],
                    "ukuran": row[4],
                    "keterangan": row[5],
                    "created_by": row[6],
                    "created_date": row[7],
                    "updated_by": row[8],
                    "updated_date": row[9],
                    "is_deleted": row[10],
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
            required=['item_code', 'id_jenis'],
            properties={
                'item_code': openapi.Schema(type=openapi.TYPE_STRING),
                'item_name': openapi.Schema(type=openapi.TYPE_STRING),
                'id_jenis': openapi.Schema(type=openapi.TYPE_INTEGER),
                'ukuran': openapi.Schema(type=openapi.TYPE_INTEGER),
                'keterangan': openapi.Schema(type=openapi.TYPE_STRING, nullable=True),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        item_code = request.data.get("item_code")
        item_name = request.data.get("item_nama")
        id_jenis = request.data.get("id_jenis")
        ukuran = request.data.get("ukuran")
        keterangan = request.data.get("keterangan")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not item_code:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_jenis:
            return Response({"error": "ID Jenis Bahan is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                    UPDATE tb_bahan SET item_code=%s, item_name=%s, id_jenis=%s, ukuran=%s, keterangan=%s, updated_by=%s, updated_date=%s
                    WHERE id=%s
                """,
                [item_code, item_name, id_jenis, ukuran, keterangan, username, updated_date, pk]
            )

        return Response({"id": pk, "item_code": item_code, "item_name": item_name, 
                         "id_jenis": id_jenis, "ukuran": ukuran, "keterangan": keterangan, 
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
                "UPDATE tb_bahan SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
