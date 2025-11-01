CREATE DATABASE  IF NOT EXISTS `iesa_db` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `iesa_db`;
-- MySQL dump 10.13  Distrib 8.0.38, for Win64 (x86_64)
--
-- Host: localhost    Database: iesa_db
-- ------------------------------------------------------
-- Server version	8.0.38

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `annual_electricity_data`
--

DROP TABLE IF EXISTS `annual_electricity_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `annual_electricity_data` (
  `Year` varchar(1024) DEFAULT NULL,
  `Installed Capacity (MW)` double DEFAULT NULL,
  `Generation (GWh)` double DEFAULT NULL,
  `Imports (GWh)` double DEFAULT NULL,
  `Consumption (GWh)` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `annual_electricity_data`
--

LOCK TABLES `annual_electricity_data` WRITE;
/*!40000 ALTER TABLE `annual_electricity_data` DISABLE KEYS */;
INSERT INTO `annual_electricity_data` VALUES ('2002-03',17787,75682,NULL,51655),('2003-04',18252,80827,73,57491),('2004-05',19379,85629,109,61328),('2005-06',19450,93774,146,67603),('2006-07',19420,98384,171,72712),('2007-08',19420,95860,199,73400),('2008-09',19786,91843,227,70371),('2009-10',20922,95608,249,74348),('2010-11',22477,94285,269,77099),('2011-12',22797,95091,274,76761),('2012-13',22812,96122,375,76789),('2013-14',23531,103670,419,83409),('2014-15',23579,106966,443,85818),('2015-16',25889,111300,463,90431),('2016-17',29944,123118,496,95530),('2017-18',33554,131275,556,106227),('2018-19',35114,128532,487,109461);
/*!40000 ALTER TABLE `annual_electricity_data` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `electricity_consumption_by_sector_gwh`
--

DROP TABLE IF EXISTS `electricity_consumption_by_sector_gwh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `electricity_consumption_by_sector_gwh` (
  `Year` varchar(1024) DEFAULT NULL,
  `Domestic` double DEFAULT NULL,
  `Commercial` double DEFAULT NULL,
  `Industrial` double DEFAULT NULL,
  `Agriculture` double DEFAULT NULL,
  `Street Light` double DEFAULT NULL,
  `Traction` double DEFAULT NULL,
  `Bulk Supply` double DEFAULT NULL,
  `other Govt` double DEFAULT NULL,
  `Total` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `electricity_consumption_by_sector_gwh`
--

LOCK TABLES `electricity_consumption_by_sector_gwh` WRITE;
/*!40000 ALTER TABLE `electricity_consumption_by_sector_gwh` DISABLE KEYS */;
INSERT INTO `electricity_consumption_by_sector_gwh` VALUES ('2002-03',23624,3218,16181,6016,244,10,3318,45,52656),('2003-04',25846,3689,17366,6669,262,9,3603,46,57490),('2004-05',27601,4080,18591,6988,305,12,3700,50,61327),('2005-06',30720,4730,19803,7949,353,13,3985,51,67604),('2006-07',33335,5363,21066,8176,387,12,4246,127,72712),('2007-08',33704,5572,20729,8472,415,8,4342,158,73400),('2008-09',32282,5252,19330,8795,430,5,4177,101,70372),('2009-10',34272,5605,19823,9689,458,2,4417,81,74347),('2010-11',35885,5782,21207,8971,456,1,4715,82,77099),('2011-12',35589,5754,21801,8548,478,1,4502,88,76761),('2012-13',36116,6007,22313,7697,457,0,4137,61,76788),('2013-14',39549,6375,24356,8290,458,0,4313,68,83409),('2014-15',41450,6512,24979,8033,441,0,4334,69,85818),('2015-16',44486,7181,25035,8526,459,0,4666,76,90429),('2016-17',48698,7856,24010,9221,484,0,5018,242,95529),('2017-18',54028,8606,27468,10128,475,0,5515,708,106928),('2018-19',53685,8513,28760,9809,451,0,5622,2618,109458);
/*!40000 ALTER TABLE `electricity_consumption_by_sector_gwh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `energy_supply_and_consumption_analysis`
--

DROP TABLE IF EXISTS `energy_supply_and_consumption_analysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `energy_supply_and_consumption_analysis` (
  `YEAR` double DEFAULT NULL,
  `Total Primary Energy Supply (MTOE)` double DEFAULT NULL,
  `Total Final Consumption of Energy (MTOE)` double DEFAULT NULL,
  `       Supply & Consumption Gap (MTOE)` double DEFAULT NULL,
  `Transformation losses (TTOE)` double DEFAULT NULL,
  `Transformation Losses MTOE` double DEFAULT NULL,
  `T&D losses (TTOE)` double DEFAULT NULL,
  `T&D losses MTOE` double DEFAULT NULL,
  `Total Losses` double DEFAULT NULL,
  `Energy used  in Transformation` double DEFAULT NULL,
  `Energy sector own use` double DEFAULT NULL,
  `Annual Compound Growth Rate` double DEFAULT NULL,
  `Savings` double DEFAULT NULL,
  `% Savings` double DEFAULT NULL,
  `Class` varchar(1024) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `energy_supply_and_consumption_analysis`
--

LOCK TABLES `energy_supply_and_consumption_analysis` WRITE;
/*!40000 ALTER TABLE `energy_supply_and_consumption_analysis` DISABLE KEYS */;
INSERT INTO `energy_supply_and_consumption_analysis` VALUES (2005,58.058983,33.94,24.118983,16427,16.427,2067,2.067,18.494,19200,707,NULL,5.624983,9.688393956194513,'Unsustainable'),(2006,60.62,36,24.619999999999997,16960,16.96,2214,2.214,19.174,19873,699,0.0207727249527891,5.445999999999998,8.983833718244801,'Unsustainable'),(2007,62.91,39.41,23.5,NULL,NULL,NULL,NULL,0,NULL,NULL,NULL,23.5,37.35495151804165,'Futuristic'),(2008,62.56,37.34,25.22,16539,16.539,2267,2.267,18.806,19602,795,0.07319148936170206,6.4140000000000015,10.252557544757034,'Unsustainable'),(2009,63.08,38.76,24.32,18397,18.397,1772,1.772,20.168999999999997,20820,652,-0.0356859635210151,4.151000000000003,6.58053265694357,'Unsustainable'),(2010,64.52,38.84,25.679999999999993,17114,17.114,2468,2.468,19.582,20188,606,0.05592105263157854,6.097999999999992,9.451332920024786,'Unsustainable'),(2011,64.65,40.02,24.630000000000003,18322,18.322,2838,2.838,21.16,21717,557,-0.04088785046728938,3.469999999999999,5.367362722351119,'Unsustainable'),(2012,64.58,40.18,24.4,18495,18.495,1999,1.999,20.494,21050,557,-0.009338205440519887,3.905999999999999,6.048312170950758,'Unsustainable'),(2013,66.84,39.81,27.03,18138,18.138,2365,2.365,20.503,21179,677,0.10778688524590185,6.527000000000001,9.765110712148415,'Unsustainable'),(2014,70.26,41.98,28.28000000000001,19613,19.613,3294,3.294,22.907,23589,682,0.046244913059563686,5.373000000000005,7.647309991460296,'Unsustainable'),(2015,73.96,45.38,28.57999999999999,20374,20.374,3519,3.519,23.893,245454,651,0.01060820367750992,4.686999999999998,6.337209302325578,'Unsustainable'),(2016,79.58,50.12,29.46,22036,22.036,1838,1.838,23.874000000000002,24580,706,0.03079076277116899,5.5859999999999985,7.01935159587836,'Unsustainable'),(2018,86.3,54.99,31.309999999999995,27819,27.819,1433,1.433,26.386,27202,816,NULL,4.923999999999992,5.705677867902656,'Unsustainable'),(2019,83.81,54.99,28.82,18529,18.529,5128,5.128,23.657,24628,972,NULL,5.162999999999997,6.160362725211785,'Unsustainable');
/*!40000 ALTER TABLE `energy_supply_and_consumption_analysis` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `final_energy_consumption_by_source_toe`
--

DROP TABLE IF EXISTS `final_energy_consumption_by_source_toe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `final_energy_consumption_by_source_toe` (
  `Year` varchar(1024) DEFAULT NULL,
  `Oil` double DEFAULT NULL,
  `Gas` double DEFAULT NULL,
  `LPG` double DEFAULT NULL,
  `Coal` double DEFAULT NULL,
  `Electricity` double DEFAULT NULL,
  `Total` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `final_energy_consumption_by_source_toe`
--

LOCK TABLES `final_energy_consumption_by_source_toe` WRITE;
/*!40000 ALTER TABLE `final_energy_consumption_by_source_toe` DISABLE KEYS */;
INSERT INTO `final_energy_consumption_by_source_toe` VALUES ('2002-03',10865717,9109870,352766,1691274,4288227,26307854),('2003-04',11145365,10067245,380370,2703906,4682063,28978949),('2004-05',11710920,11637566,450379,3310512,4994560,32103937),('2005-06',10877601,13325251,625792,3611490,5505555,33945689),('2006-07',10575330,14701024,658225,4149041,5921635,36005255),('2007-08',11528722,15881990,619944,5404715,5977697,39413068),('2008-09',10842614,16307898,569995,3893001,5731032,37344540),('2009-10',10829455,17024933,576631,4282061,6054921,38768001),('2010-11',11252938,16781247,503272,4025380,6278947,38841784),('2011-12',11617788,17618199,481064,4057678,6251421,40026150),('2012-13',12219941,17521615,528417,3661193,6253675,40184841),('2013-14',12718011,16277023,585560,3446131,6792794,39819519),('2014-15',13851467,15755616,756414,4631627,6989011,41984135),('2015-16',16290075,15544358,1210419,4975472,7364702,45385026),('2016-17',17904977,17031100,1308471,6097816,7779939,50122303),('2017-18',19264954,16693880,1385427,8940477,8708151,54992889),('2018-19',17364897,17275180,1148380,10292739,8914489,54995685);
/*!40000 ALTER TABLE `final_energy_consumption_by_source_toe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `natural_gas_production_and_consumption`
--

DROP TABLE IF EXISTS `natural_gas_production_and_consumption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `natural_gas_production_and_consumption` (
  `Year` varchar(1024) DEFAULT NULL,
  `Natural Gas Production` double DEFAULT NULL,
  `Natural Gas Consumption` double DEFAULT NULL,
  `Production in billion` double DEFAULT NULL,
  `consumption in billion` double DEFAULT NULL,
  `GAP` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `natural_gas_production_and_consumption`
--

LOCK TABLES `natural_gas_production_and_consumption` WRITE;
/*!40000 ALTER TABLE `natural_gas_production_and_consumption` DISABLE KEYS */;
INSERT INTO `natural_gas_production_and_consumption` VALUES ('1999-2000',818342,712100,818.342,712.1,-106.24199999999996),('2000-01',875433,768068,875.433,768.068,-107.36500000000001),('2001-02',923758,824604,923.758,824.604,-99.154),('2002-03',992589,872265,992.589,872.265,-120.32400000000007),('2003-04',1202750,1051418,1202.75,1051.418,-151.3320000000001),('2004-05',1344964,1157628,1344.964,1157.628,-187.336),('2005-06',1400026,1221762,1400.026,1221.762,-178.26400000000012),('2006-07',1413581,1220929,1413.581,1220.929,-192.65199999999982),('2007-08',1454194,1275212,1454.194,1275.212,-178.98199999999997),('2008-09',1460679,1269433,1460.679,1269.433,-191.2460000000001),('2009-10',1482847,1277821,1482.847,1277.821,-205.02600000000007),('2010-11',1471591,1240671,1471.591,1240.671,-230.91999999999985),('2011-12',1558959,1288198,1558.959,1288.198,-270.76099999999997),('2012-13',1505841,1267980,1505.841,1267.98,-237.86099999999988),('2013-14',1493508,1220493,1493.508,1220.493,-273.0150000000001),('2014-15',1465760,1224893,1465.76,1224.893,-240.86699999999996),('2015-16',1481551,1304919,1481.551,1304.919,-176.63199999999983),('2016-17',1471855,1377307,1471.855,1377.307,-94.548),('2017-18',1458936,1454697,1458.936,1454.697,-4.239000000000033),('2018-19',1436546,1453517,1436.546,1453.517,16.971000000000004);
/*!40000 ALTER TABLE `natural_gas_production_and_consumption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `primary_energy_supplies_by_source_toe`
--

DROP TABLE IF EXISTS `primary_energy_supplies_by_source_toe`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `primary_energy_supplies_by_source_toe` (
  `Year` varchar(1024) DEFAULT NULL,
  `Oil` double DEFAULT NULL,
  `Gas` double DEFAULT NULL,
  `LNG Imports` double DEFAULT NULL,
  `LPG` double DEFAULT NULL,
  `Coal` double DEFAULT NULL,
  `Hydro Electricity` double DEFAULT NULL,
  `Nuclear electricity` double DEFAULT NULL,
  `Imported electricity` double DEFAULT NULL,
  `Renewable Electricity` double DEFAULT NULL,
  `Total` double DEFAULT NULL,
  `Imports` double DEFAULT NULL,
  `Percent` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `primary_energy_supplies_by_source_toe`
--

LOCK TABLES `primary_energy_supplies_by_source_toe` WRITE;
/*!40000 ALTER TABLE `primary_energy_supplies_by_source_toe` DISABLE KEYS */;
INSERT INTO `primary_energy_supplies_by_source_toe` VALUES ('2002-03',18016214,20590425,0,181661,2519881,5335041,415242,85,NULL,47058549,85,0.00018062605372724092),('2003-04',15221024,25254481,0,205526,3300491,6431312,420135,17418,NULL,50850387,17418,0.03425342662583866),('2004-05',16329979,27953380,0,251789,4227842,6127429,667234,26050,NULL,55583703,26050,0.04686625502442685),('2005-06',16411834,29202362,0,400430,4049654,7366452,592887,34775,NULL,58058394,34775,0.05989659307489628),('2006-07',18188280,29322338,0,470998,4426678,7626755,546159,40781,NULL,60621989,40781,0.06727096994458562),('2007-08',19206441,29872105,0,418952,5783844,6851955,734537,47550,NULL,62915384,47550,0.07557769972444259),('2008-09',20103060,30255885,0,401705,4732823,6631841,386165,54266,NULL,62565745,54266,0.08673436238951522),('2009-10',19806314,30808523,0,395583,4621639,6705533,690821,59537,NULL,63087950,59537,0.09437142909224344),('2010-11',20674840,30683357,0,339633,4350868,7593074,816370,64093,NULL,64522235,64093,0.09933474871104511),('2011-12',19958483,32033074,0,321214,4285400,6806704,1256791,65515,NULL,64727181,65515,0.10121713782035402),('2012-13',20968730,31144006,0,309524,3863081,7126623,1086846,89542,NULL,64588352,89542,0.13863490432454445),('2013-14',23006510,30964868,0,363710,3590386,7607804,1215042,99907,NULL,66848227,99907,0.14945347765169598),('2014-15',24970360,29977755,472503,457197,4952556,7751133,1385283,105632,191407,70263826,578135,0.822806033932738),('2015-16',25280073,30460521,2404128,908705,5066935,8266670,1099261,110525,369731,73966549,2514653,3.3997165394318993),('2016-17',27366526,30163334,4455734,1008637,6482401,7681699,1670560,118480,636825,79584196,4574214,5.747641152270986),('2017-18',26903431,29849030,7492597,1054006,10925200,6665328,2358200,132659,920580,86301031,7625256,8.835648788483187),('2018-19',21568315,29318489,8913006,953834,12933087,6525607,2365268,116196,1117482,83811284,9029202,10.77325339628492);
/*!40000 ALTER TABLE `primary_energy_supplies_by_source_toe` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `province_wise_electricity_consumption_gwh`
--

DROP TABLE IF EXISTS `province_wise_electricity_consumption_gwh`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `province_wise_electricity_consumption_gwh` (
  `Year` varchar(1024) DEFAULT NULL,
  `Panjab` double DEFAULT NULL,
  `Sindh` double DEFAULT NULL,
  `KPK` double DEFAULT NULL,
  `Balochistan` double DEFAULT NULL,
  `AJK` double DEFAULT NULL,
  `T&D  Losses` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `province_wise_electricity_consumption_gwh`
--

LOCK TABLES `province_wise_electricity_consumption_gwh` WRITE;
/*!40000 ALTER TABLE `province_wise_electricity_consumption_gwh` DISABLE KEYS */;
INSERT INTO `province_wise_electricity_consumption_gwh` VALUES ('2002-03',32328,10704,6758,2864,0,20043),('2003-04',35374,11624,7230,3263,0,20371),('2004-05',37696,12496,7644,3492,0,21037),('2005-06',42018,13500,8255,3829,0,22506),('2006-07',45294,14201,8459,3965,792,21912),('2007-08',45040,14726,8223,4089,1322,18742),('2008-09',43465,14518,7560,4110,719,19396),('2009-10',45906,15293,8259,4099,790,18957),('2010-11',47638,15876,8712,4048,825,15315),('2011-12',46981,16325,8528,4086,841,16054),('2012-13',46467,17193,8455,3812,862,16372),('2013-14',52008,17839,8837,3744,901,16932),('2014-15',53249,18997,8700,3994,878,17627),('2015-16',57245,19213,8812,4220,941,17209),('2016-17',60940,19479,9660,4452,999,23582),('2017-18',69718,20850,10278,4915,1166,21110),('2018-19',71735,21016,10677,4778,1255,16765);
/*!40000 ALTER TABLE `province_wise_electricity_consumption_gwh` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `province_wise_energy_consumption`
--

DROP TABLE IF EXISTS `province_wise_energy_consumption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `province_wise_energy_consumption` (
  `Province` varchar(1024) DEFAULT NULL,
  `Consumption` double DEFAULT NULL,
  `Convert to Billion C feet` double DEFAULT NULL,
  `Percentage` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `province_wise_energy_consumption`
--

LOCK TABLES `province_wise_energy_consumption` WRITE;
/*!40000 ALTER TABLE `province_wise_energy_consumption` DISABLE KEYS */;
INSERT INTO `province_wise_energy_consumption` VALUES ('Panjab',720386,720.386,49.56158063510781),('KPK',78777,78.777,5.419750852587208),('Sindh',518647,518.647,35.68221080317603),('Balochistan',135707,135.707,9.336457709128961),('total',1453517,1453.5169999999998,100.00000000000001);
/*!40000 ALTER TABLE `province_wise_energy_consumption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `provincial_energy_distribution_and_transmission_losses`
--

DROP TABLE IF EXISTS `provincial_energy_distribution_and_transmission_losses`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `provincial_energy_distribution_and_transmission_losses` (
  `Year` varchar(1024) DEFAULT NULL,
  `T&D  Losses` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `provincial_energy_distribution_and_transmission_losses`
--

LOCK TABLES `provincial_energy_distribution_and_transmission_losses` WRITE;
/*!40000 ALTER TABLE `provincial_energy_distribution_and_transmission_losses` DISABLE KEYS */;
INSERT INTO `provincial_energy_distribution_and_transmission_losses` VALUES ('2002-03',20043),('2003-04',20371),('2004-05',21037),('2005-06',22506),('2006-07',21912),('2007-08',18742),('2008-09',19396),('2009-10',18957),('2010-11',15315),('2011-12',16054),('2012-13',16372),('2013-14',16932),('2014-15',17627),('2015-16',17209),('2016-17',23582),('2017-18',21110),('2018-19',16765);
/*!40000 ALTER TABLE `provincial_energy_distribution_and_transmission_losses` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `scenario_definitions`
--

DROP TABLE IF EXISTS `scenario_definitions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `scenario_definitions` (
  `id` int NOT NULL AUTO_INCREMENT,
  `category` varchar(50) NOT NULL,
  `scenario` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `category` (`category`,`scenario`)
) ENGINE=InnoDB AUTO_INCREMENT=10 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `scenario_definitions`
--

LOCK TABLES `scenario_definitions` WRITE;
/*!40000 ALTER TABLE `scenario_definitions` DISABLE KEYS */;
INSERT INTO `scenario_definitions` VALUES (1,'Electricity','Future Electricity Demand Growth'),(4,'Electricity','Impact of Industrial Expansion on Electricity Demand'),(3,'Electricity','Power Shortage Risk'),(2,'Electricity','Renewable Energy Contribution'),(5,'Gas','Future Gas Demand Forecast'),(6,'Gas','Gas Production vs. Consumption Balance'),(7,'Gas','Supply Chain Disruptions in Gas Imports'),(9,'Overall Energy','Sector-Wise Energy Consumption Changes'),(8,'Overall Energy','Total Energy Demand vs. Supply Balance');
/*!40000 ALTER TABLE `scenario_definitions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `sector_wise_energy_consumption`
--

DROP TABLE IF EXISTS `sector_wise_energy_consumption`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `sector_wise_energy_consumption` (
  `Year` varchar(1024) DEFAULT NULL,
  `Domestic` double DEFAULT NULL,
  `Commercial` double DEFAULT NULL,
  `Gen. Industries` double DEFAULT NULL,
  `Power` double DEFAULT NULL,
  `Fertalizer as feed stock` double DEFAULT NULL,
  `Transport` double DEFAULT NULL,
  `fertalizer in fuel use` double DEFAULT NULL,
  `Cement` double DEFAULT NULL,
  `SSGC` double DEFAULT NULL,
  `Total` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `sector_wise_energy_consumption`
--

LOCK TABLES `sector_wise_energy_consumption` WRITE;
/*!40000 ALTER TABLE `sector_wise_energy_consumption` DISABLE KEYS */;
INSERT INTO `sector_wise_energy_consumption` VALUES ('2013-14',269135,38117,250490,349535,164378,87634,52139,522,0,1211950),('2014-15',278069,35187,239591,371562,166903,66517,58609,831,0,1217269),('2015-16',271302,33633,230436,440593,182076,64455,80847,497,0,1303839),('2016-17',290868,32858,261267,446941,182241,67245,94564,583,0,1376567),('2017-18',284428,32096,273339,544654,181662,70455,66442,886,0,1453962),('2018-19',311887,31205,245958,511140,196576,65099,37258,387,53261,1452771);
/*!40000 ALTER TABLE `sector_wise_energy_consumption` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `total_imports_lng`
--

DROP TABLE IF EXISTS `total_imports_lng`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `total_imports_lng` (
  `Year` varchar(1024) DEFAULT NULL,
  `Imports` double DEFAULT NULL,
  `Imports value (Million US $)` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `total_imports_lng`
--

LOCK TABLES `total_imports_lng` WRITE;
/*!40000 ALTER TABLE `total_imports_lng` DISABLE KEYS */;
INSERT INTO `total_imports_lng` VALUES ('2014-15',1975505,151),('2015-16',100720923,642),('2016-17',186672977,1278),('2017-18',313902345,2452),('2018-19',3734100403,3392);
/*!40000 ALTER TABLE `total_imports_lng` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `total_proved_reserves`
--

DROP TABLE IF EXISTS `total_proved_reserves`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `total_proved_reserves` (
  `Year` double DEFAULT NULL,
  `Proved Reserves (TCM)` double DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `total_proved_reserves`
--

LOCK TABLES `total_proved_reserves` WRITE;
/*!40000 ALTER TABLE `total_proved_reserves` DISABLE KEYS */;
INSERT INTO `total_proved_reserves` VALUES (1998,0.4),(2008,0.6),(2017,0.4),(2018,0.4);
/*!40000 ALTER TABLE `total_proved_reserves` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_data`
--

DROP TABLE IF EXISTS `user_data`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `user_data` (
  `id` bigint unsigned NOT NULL AUTO_INCREMENT,
  `username` varchar(50) NOT NULL,
  `password` varchar(255) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_data`
--

LOCK TABLES `user_data` WRITE;
/*!40000 ALTER TABLE `user_data` DISABLE KEYS */;
INSERT INTO `user_data` VALUES (1,'inputentryoperator@iesa','00000149bf8c'),(2,'energyplanner@iesa','0000927c464a'),(3,'mspakistan59','000090e0f074'),(4,'yasirkhan2024','000055e4531e'),(5,'farzambaig2024','0000f97324cc');
/*!40000 ALTER TABLE `user_data` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2025-03-22 23:19:26
