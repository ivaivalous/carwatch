-- MySQL dump 10.13  Distrib 5.1.73, for redhat-linux-gnu (x86_64)
--
-- Host: localhost    Database: carwatch
-- ------------------------------------------------------
-- Server version	5.1.73-log

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `cars`
--

DROP TABLE IF EXISTS `cars`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cars` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `siteid` varchar(45) NOT NULL,
  `carid` varchar(45) NOT NULL COMMENT 'Car ID as defined by the site',
  `url` varchar(255) NOT NULL COMMENT 'URL car was retrieved from',
  `make` varchar(255) DEFAULT 'N/A' COMMENT '''Car brand''',
  `name` varchar(255) DEFAULT 'N/A' COMMENT '''Car name as given by the site''',
  `price` int(11) DEFAULT '-1' COMMENT 'Car price in BGN',
  `currency` tinyint(4) DEFAULT '1' COMMENT '1 for BGN, 0 for EUR',
  `production_year` int(11) DEFAULT '-1' COMMENT 'Year of production',
  `production_month` int(11) DEFAULT '-1' COMMENT 'Month car was produced',
  `power` int(11) DEFAULT '-1' COMMENT 'Power in HP',
  `mileage` int(20) DEFAULT NULL COMMENT 'Mileage in km',
  `cubature` int(20) DEFAULT NULL COMMENT 'Engine cubature',
  `fuel` varchar(255) DEFAULT 'N/A' COMMENT '''Fuel type, like LPG''',
  `doors` varchar(255) DEFAULT 'N/A' COMMENT '''Number of doors''',
  `color` varchar(255) DEFAULT 'N/A' COMMENT 'Car color',
  `transmission_automatic` tinyint(4) DEFAULT '-1' COMMENT '1 if automatic, 0 if manual, -1 unknown',
  `description` text COMMENT 'Description as provided by the seller',
  `date_collected` timestamp NULL DEFAULT NULL COMMENT 'Date the car was first crawed',
  `date_added` timestamp NULL DEFAULT CURRENT_TIMESTAMP,
  `active` tinyint(4) NOT NULL DEFAULT '1' COMMENT 'Whether the ad is still active, deactivated when not found in subsequent crawling',
  `date_updated` timestamp NULL DEFAULT NULL,
  `date_deactivated` timestamp NULL DEFAULT NULL COMMENT 'Set when a car has been deactivated',
  PRIMARY KEY (`id`),
  UNIQUE KEY `carid_UNIQUE` (`carid`),
  UNIQUE KEY `url_UNIQUE` (`url`)
) ENGINE=MyISAM AUTO_INCREMENT=1032685 DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `sites`
--

DROP TABLE IF EXISTS `sites`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `sites` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `sitename` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `sitename_UNIQUE` (`sitename`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2016-12-26 19:20:09
