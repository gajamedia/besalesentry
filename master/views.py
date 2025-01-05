from rest_framework.viewsets import ViewSet
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated
from django.db import connection  # Untuk menjalankan query langsung
from django.utils.timezone import now
# from django.http import JsonResponse

class JenisBahanViewSet(ViewSet):
    permission_classes = [IsAuthenticated]  # API hanya bisa diakses oleh user yang login

    def list(self, request):
        """ Mendapatkan semua data tb_jenisbahan yang belum dihapus """
        with connection.cursor() as cursor:
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

    def create(self, request):
        """ Menambahkan data baru ke tb_jenisbahan """
        nama_jenis = request.data.get("nama_jenis")
        username = request.user.username  # Username pengguna yang login
        created_date = now()

        if not nama_jenis:
            return Response({"error": "NamaJenis is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO tb_jenisbahan (nama_jenis, created_by, created_date, updated_by, updated_date, is_deleted) 
                VALUES (%s, %s, %s, %s, %s, 0) RETURNING id
                """,
                [nama_jenis, username, created_date, username, created_date]
            )
            new_id = cursor.fetchone()[0]

        return Response({"id": new_id, "nama_jenis": nama_jenis}, status=status.HTTP_201_CREATED)

    def retrieve(self, request, pk=None):
        """ Mendapatkan detail data berdasarkan ID """
        with connection.cursor() as cursor:
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

    def update(self, request, pk=None):
        """ Mengupdate data berdasarkan ID """
        nama_jenis = request.data.get("nama_jenis")
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        if not nama_jenis:
            return Response({"error": "NamaJenis is required"}, status=status.HTTP_400_BAD_REQUEST)

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tb_jenisbahan SET nama_jenis=%s, updated_by=%s, updated_date=%s WHERE id=%s",
                [nama_jenis, username, updated_date, pk]
            )

        return Response({"id": pk, "nama_jenis": nama_jenis, "updated_by": username, "updated_date": updated_date}, status=status.HTTP_200_OK)

    def destroy(self, request, pk=None):
        """ Soft Delete: Menandai data sebagai is_deleted = 1 """
        username = request.user.username  # Username pengguna yang login
        updated_date = now()

        with connection.cursor() as cursor:
            cursor.execute(
                "UPDATE tb_jenisbahan SET is_deleted=1, updated_by=%s, updated_date=%s WHERE id=%s",
                [username, updated_date, pk]
            )

        return Response({"message": "Soft deleted successfully"}, status=status.HTTP_204_NO_CONTENT)
