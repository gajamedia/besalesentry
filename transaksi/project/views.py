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
                FROM tb_jenisbahan
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
