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

from rest_framework.decorators import action
# from django.db.models import Q  # Untuk query pencarian

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
        Search data tb_jenisbahan berdasarkan beberapa field dengan pagination
        """
        search_query = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        with connections["mysql"].cursor() as cursor:
            # Hitung total hasil
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tb_jenisbahan 
                WHERE is_deleted = 0 AND (
                    nama_jenis LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%"])
            total_items = cursor.fetchone()[0]

            # Query dengan pagination
            cursor.execute("""
                SELECT id, nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted
                FROM tb_jenisbahan
                WHERE is_deleted = 0 AND (
                    nama_jenis LIKE %s OR 
                    created_by LIKE %s OR 
                    updated_by LIKE %s
                )
                LIMIT %s OFFSET %s
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", page_size, (page - 1) * page_size])

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

        return Response({
            "count": total_items,
            "total_pages": (total_items // page_size) + (1 if total_items % page_size else 0),
            "current_page": page,
            "results": data
        }, status=status.HTTP_200_OK)
    
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
                           "created_by, created_date, updated_by, updated_date, is_deleted," +
                           "harga_beli, harga_jual FROM tb_bahan WHERE is_deleted = 0")
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
                "harga_beli": row[11],
                "harga_jual": row[12]
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
                SELECT id, item_code, item_name, id_jenis, ukuran, keterangan, created_by, created_date, 
                       updated_by, updated_date, is_deleted,
                       harga_beli, harga_jual    
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
                "harga_beli": row[11],
                "harga_jual": row[12]
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
                'harga_beli': openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
                'harga_jual': openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
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
        harga_beli = request.data.get("harga_beli")
        harga_jual = request.data.get("harga_jual")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        if not item_code:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_jenis:
            return Response({"error": "ID Jenis Bahan is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tb_bahan (item_code, item_name, id_jenis, ukuran, keterangan, created_by, created_date, 
                    harga_beli, harga_jual, updated_by, updated_date, is_deleted)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 0)
                """,
                [item_code, item_name, id_jenis, ukuran, keterangan, username, created_date, harga_beli, harga_jual, username, created_date]
            )
            new_id = cursor.lastrowid

        return Response({"id": new_id, "item_code": item_code, "item_name": item_name, 
                         "id_jenis": id_jenis, "ukuran": ukuran, "keterangan": keterangan,
                         "harga_beli": harga_beli, "harga_jual": harga_jual}, status=status.HTTP_201_CREATED)

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
                           "created_by, created_date, updated_by, updated_date, is_deleted, " +
                           "harga_beli, harga_jual FROM tb_bahan WHERE id = %s", [pk])
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
                    "harga_beli": row[11],
                    "harga_jual": row[12],
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
                'harga_beli': openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
                'harga_jual': openapi.Schema(type=openapi.TYPE_NUMBER, format="float"),
            }
        ),
        responses={200: "Updated"},
    )
    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        item_code = request.data.get("item_code")
        item_name = request.data.get("item_name")
        id_jenis = request.data.get("id_jenis")
        ukuran = request.data.get("ukuran")
        keterangan = request.data.get("keterangan")
        harga_beli = request.data.get("harga_beli")
        harga_jual = request.data.get("harga_jual")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not item_code:
            return Response({"error": "Item Code is required"}, status=status.HTTP_400_BAD_REQUEST)

        if not id_jenis:
            return Response({"error": "ID Jenis Bahan is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connections['mysql'].cursor() as cursor:
            cursor.execute("""
                    UPDATE tb_bahan SET item_code=%s, item_name=%s, id_jenis=%s, ukuran=%s, keterangan=%s, updated_by=%s, updated_date=%s, harga_beli=%s, harga_jual=%s
                    WHERE id=%s
                """,
                [item_code, item_name, id_jenis, ukuran, keterangan, username, updated_date, harga_beli, harga_jual, pk]
            )

        return Response({"id": pk, "item_code": item_code, "item_name": item_name, 
                         "id_jenis": id_jenis, "ukuran": ukuran, "keterangan": keterangan, 
                         "harga_beli": harga_beli, "harga_jual": harga_jual,
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('search', openapi.IN_QUERY, description="Search by item_code or item_name", type=openapi.TYPE_STRING),
            openapi.Parameter('page', openapi.IN_QUERY, description="Page number", type=openapi.TYPE_INTEGER),
            openapi.Parameter('page_size', openapi.IN_QUERY, description="Page size", type=openapi.TYPE_INTEGER),
            openapi.Parameter('Authorization', openapi.IN_HEADER, description="Token JWT", type=openapi.TYPE_STRING, default="Bearer ")
        ],
        responses={200: "Success"}
    )
    @action(detail=False, methods=["get"], url_path="search")
    def search(self, request):
        """ Search data bahan with pagination """
        search_query = request.GET.get("search", "")
        page = int(request.GET.get("page", 1))
        page_size = int(request.GET.get("page_size", 10))

        with connections["mysql"].cursor() as cursor:
            # Hitung total data
            cursor.execute("""
                SELECT COUNT(*) 
                FROM tb_bahan 
                WHERE is_deleted = 0 AND (
                    item_code LIKE %s OR 
                    item_name LIKE %s
                )
            """, [f"%{search_query}%", f"%{search_query}%"])
            total_items = cursor.fetchone()[0]

            # Ambil data sesuai pagination
            cursor.execute("""
                SELECT b.id, b.item_code, b.item_name, b.id_jenis, j.nama_jenis, b.ukuran, b.keterangan, b.created_by, 
                       b.created_date, b.updated_by, b.updated_date, b.is_deleted, b.harga_beli, b.harga_jual
                FROM tb_bahan b
                LEFT JOIN tb_jenisbahan j ON b.id_jenis = j.id
                WHERE b.is_deleted = 0 AND (
                    b.item_code LIKE %s OR 
                    b.item_name LIKE %s OR
                    b.ukuran LIKE %s OR
                    b.keterangan LIKE %s OR
                    b.harga_beli LIKE %s OR
                    b.harga_jual LIKE %s              
                )
                LIMIT %s OFFSET %s
            """, [f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", f"%{search_query}%", page_size, (page - 1) * page_size])

            rows = cursor.fetchall()

        data = [
            {
                "id": row[0],
                "item_code": row[1],
                "item_name": row[2],
                "id_jenis": row[3],
                "nama_jenis": row[4],
                "ukuran": row[5],
                "keterangan": row[6],
                "created_by": row[7],
                "created_date": row[8],
                "updated_by": row[9],
                "updated_date": row[10],
                "is_deleted": row[11],
                "harga_beli": row[12],
                "harga_jual": row[13],
            }
            for row in rows
        ]

        return Response({
            "count": total_items,
            "total_pages": (total_items // page_size) + (1 if total_items % page_size else 0),
            "current_page": page,
            "results": data
        }, status=status.HTTP_200_OK)