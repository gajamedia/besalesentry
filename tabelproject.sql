/*
SQLyog Community v12.4.3 (32 bit)
MySQL - 8.0.37 : Database - dbsales
*********************************************************************
*/

/*!40101 SET NAMES utf8 */;

/*!40101 SET SQL_MODE=''*/;

/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;
CREATE DATABASE /*!32312 IF NOT EXISTS*/`dbsales` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;

USE `dbsales`;

/*Table structure for table `tb_project_detil` */

DROP TABLE IF EXISTS `tb_project_detil`;

CREATE TABLE `tb_project_detil` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_project_header` int DEFAULT NULL,
  `lebar_bahan` int DEFAULT '0',
  `lantai` varchar(3) DEFAULT NULL,
  `ruangan` varchar(5) DEFAULT NULL,
  `bed` varchar(10) DEFAULT NULL,
  `tipe` char(1) DEFAULT '0' COMMENT '0: - | 1: L',
  `uk_room_l` int DEFAULT '0',
  `uk_room_p` int DEFAULT '0',
  `uk_room_t` int DEFAULT '0',
  `stik` int DEFAULT '0',
  `elevasi` int DEFAULT '0',
  `tinggi_vitrase` int DEFAULT '0',
  `tinggi_lipatan` int DEFAULT '0' COMMENT '+tinggi',
  `nilai_pembagi` int DEFAULT '0',
  `created_by` varchar(100) DEFAULT NULL,
  `created_date` timestamp NULL DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `updated_date` timestamp NULL DEFAULT NULL,
  `is_deleted` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tb_project_detil` */

/*Table structure for table `tb_project_header` */

DROP TABLE IF EXISTS `tb_project_header`;

CREATE TABLE `tb_project_header` (
  `id` int NOT NULL AUTO_INCREMENT,
  `no_project` varchar(30) DEFAULT NULL,
  `tgl_project` timestamp NULL DEFAULT NULL,
  `ket_project` varchar(255) DEFAULT NULL,
  `nama_customer` varchar(100) DEFAULT NULL,
  `addr_customer` varchar(150) DEFAULT NULL,
  `contact_customer` varchar(30) DEFAULT NULL,
  `status_project` char(1) DEFAULT '0' COMMENT '0:Fu;1:kontrak;2:pengerjaan;3:pemasangan;4:pengecekan;5:penagihan;6:lunas',
  `created_by` varchar(100) DEFAULT NULL,
  `created_date` timestamp NULL DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `updated_date` timestamp NULL DEFAULT NULL,
  `is_deleted` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tb_project_header` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
