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

/*Table structure for table `tb_project_detil_item` */

DROP TABLE IF EXISTS `tb_project_detil_item`;

CREATE TABLE `tb_project_detil_item` (
  `id` int NOT NULL AUTO_INCREMENT,
  `id_project_detil` int DEFAULT NULL,
  `item_id` int DEFAULT NULL,
  `item_code` varchar(15) DEFAULT NULL,
  `item_name` varchar(255) DEFAULT NULL,
  `ukuran` int DEFAULT '0',
  `harga_beli` double DEFAULT '0',
  `harga_jual` double DEFAULT '0',
  `created_by` varchar(100) DEFAULT NULL,
  `created_date` timestamp NULL DEFAULT NULL,
  `updated_by` varchar(100) DEFAULT NULL,
  `updated_date` timestamp NULL DEFAULT NULL,
  `is_Deleted` int DEFAULT '0',
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

/*Data for the table `tb_project_detil_item` */

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;
