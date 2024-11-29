-- --------------------------------------------------------
-- Хост:                         127.0.0.1
-- Версия сервера:               8.0.39 - MySQL Community Server - GPL
-- Операционная система:         Win64
-- HeidiSQL Версия:              12.8.0.6908
-- --------------------------------------------------------

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET NAMES utf8 */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;


-- Дамп структуры базы данных sugar_accepting
CREATE DATABASE IF NOT EXISTS `sugar_accepting` /*!40100 DEFAULT CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci */ /*!80016 DEFAULT ENCRYPTION='N' */;
USE `sugar_accepting`;

-- Дамп структуры для таблица sugar_accepting.accepting_act
CREATE TABLE IF NOT EXISTS `accepting_act` (
  `rep_id` int NOT NULL AUTO_INCREMENT,
  `creating_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `accept_info` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT 'Замечаний к принятому ТС нет',
  `id_te` int NOT NULL,
  `weighting_result` float NOT NULL DEFAULT '0',
  PRIMARY KEY (`rep_id`),
  KEY `accepting_act_ibfk_1` (`id_te`),
  CONSTRAINT `accepting_act_ibfk_1` FOREIGN KEY (`id_te`) REFERENCES `te` (`id_te`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=43 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.distr_report
CREATE TABLE IF NOT EXISTS `distr_report` (
  `rep_id` int NOT NULL AUTO_INCREMENT,
  `creating_date` timestamp NOT NULL DEFAULT (now()),
  `destination` enum('Анализ показателей, вызвавших сомнение, в сырьевой лаборатории','Взвешивание','Взвешивание и последующий лабораторный контроль') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `id_te` int NOT NULL,
  `note` varchar(50) DEFAULT NULL,
  PRIMARY KEY (`rep_id`),
  KEY `distr_report_ibfk_1` (`id_te`),
  CONSTRAINT `distr_report_ibfk_1` FOREIGN KEY (`id_te`) REFERENCES `te` (`id_te`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=54 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.laborant
CREATE TABLE IF NOT EXISTS `laborant` (
  `staff_lid` int NOT NULL AUTO_INCREMENT,
  `primary_checking_info` mediumtext CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci,
  `secondary_checking_info` mediumtext,
  `user` int DEFAULT NULL,
  `user_final` int DEFAULT NULL,
  PRIMARY KEY (`staff_lid`),
  KEY `laborant_ibfk_1` (`user`),
  KEY `FK_laborant_usertbl` (`user_final`),
  CONSTRAINT `FK_laborant_usertbl` FOREIGN KEY (`user_final`) REFERENCES `usertbl` (`user`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `laborant_ibfk_1` FOREIGN KEY (`user`) REFERENCES `usertbl` (`user`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=27 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.operator
CREATE TABLE IF NOT EXISTS `operator` (
  `staff_id` int NOT NULL AUTO_INCREMENT,
  `accepting_data` mediumtext NOT NULL,
  `user` int NOT NULL,
  PRIMARY KEY (`staff_id`),
  KEY `operator_ibfk_1` (`user`),
  CONSTRAINT `operator_ibfk_1` FOREIGN KEY (`user`) REFERENCES `usertbl` (`user`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=73 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.operator_te
CREATE TABLE IF NOT EXISTS `operator_te` (
  `staff_id` int NOT NULL,
  `id_te` int NOT NULL,
  PRIMARY KEY (`staff_id`,`id_te`),
  KEY `operator_te_ibfk_1` (`id_te`),
  CONSTRAINT `operator_te_ibfk_1` FOREIGN KEY (`id_te`) REFERENCES `te` (`id_te`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `operator_te_ibfk_2` FOREIGN KEY (`staff_id`) REFERENCES `operator` (`staff_id`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.scale_operator
CREATE TABLE IF NOT EXISTS `scale_operator` (
  `staff_soid` int NOT NULL AUTO_INCREMENT,
  `info_primary_weighted` float NOT NULL DEFAULT '0',
  `info_secondary_weighted` float NOT NULL DEFAULT '0',
  `user` int NOT NULL,
  `user_final` int DEFAULT NULL,
  PRIMARY KEY (`staff_soid`),
  KEY `scale_operator_ibfk_1` (`user`),
  CONSTRAINT `scale_operator_ibfk_1` FOREIGN KEY (`user`) REFERENCES `usertbl` (`user`) ON DELETE RESTRICT ON UPDATE RESTRICT,
  CONSTRAINT `scale` CHECK ((`info_primary_weighted` > `info_secondary_weighted`))
) ENGINE=InnoDB AUTO_INCREMENT=35 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci COMMENT='Триггер, срабатывающий после разгрузки';

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.te
CREATE TABLE IF NOT EXISTS `te` (
  `id_te` int NOT NULL AUTO_INCREMENT,
  `staff_lid` int DEFAULT NULL,
  `staff_uoid` int DEFAULT NULL,
  `staff_soid` int DEFAULT NULL,
  `vendor_item` varchar(50) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `sugar_beet_charact` enum('Соответствует характеристикам','Не соответствует характеристикам') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL,
  `transport_reg_num` varchar(11) NOT NULL,
  `note` mediumtext,
  `distr_stat` enum('1','0') NOT NULL DEFAULT '0',
  `primary_check_stat` enum('1','0') NOT NULL DEFAULT '0',
  `secondary_check_stat` enum('1','0') CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci NOT NULL DEFAULT '0',
  `primary_weighted_stat` enum('1','0') NOT NULL DEFAULT '0',
  `unload_stat` enum('1','0') NOT NULL DEFAULT '0',
  `accept_stat` enum('1','0') NOT NULL DEFAULT '0',
  `reject_stat` enum('1','0') NOT NULL DEFAULT '0',
  `time` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY (`id_te`),
  KEY `te_ibfk_1` (`staff_lid`),
  KEY `te_ibfk_2` (`staff_uoid`),
  KEY `te_ibfk_4` (`staff_soid`),
  CONSTRAINT `te_ibfk_1` FOREIGN KEY (`staff_lid`) REFERENCES `laborant` (`staff_lid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `te_ibfk_2` FOREIGN KEY (`staff_uoid`) REFERENCES `unloading_operator` (`staff_uoid`) ON DELETE CASCADE ON UPDATE CASCADE,
  CONSTRAINT `te_ibfk_4` FOREIGN KEY (`staff_soid`) REFERENCES `scale_operator` (`staff_soid`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=111 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.unloading_operator
CREATE TABLE IF NOT EXISTS `unloading_operator` (
  `staff_uoid` int NOT NULL AUTO_INCREMENT,
  `unload_place` varchar(50) NOT NULL,
  `info_unloaded` varchar(50) NOT NULL,
  `user` int NOT NULL,
  PRIMARY KEY (`staff_uoid`),
  KEY `FK_unloading_operator_usertbl` (`user`),
  CONSTRAINT `FK_unloading_operator_usertbl` FOREIGN KEY (`user`) REFERENCES `usertbl` (`user`) ON DELETE RESTRICT ON UPDATE RESTRICT
) ENGINE=InnoDB AUTO_INCREMENT=58 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.unloading_report
CREATE TABLE IF NOT EXISTS `unloading_report` (
  `id_te` int NOT NULL,
  `creating_date` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `unload_info` varchar(50) NOT NULL,
  `rep_id` int NOT NULL AUTO_INCREMENT,
  PRIMARY KEY (`rep_id`),
  KEY `unloading_report_ibfk_1` (`id_te`),
  CONSTRAINT `unloading_report_ibfk_1` FOREIGN KEY (`id_te`) REFERENCES `te` (`id_te`) ON DELETE CASCADE ON UPDATE CASCADE
) ENGINE=InnoDB AUTO_INCREMENT=18 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для таблица sugar_accepting.usertbl
CREATE TABLE IF NOT EXISTS `usertbl` (
  `user` int NOT NULL AUTO_INCREMENT,
  `fio` longtext NOT NULL,
  `login` varchar(50) NOT NULL,
  `password` varchar(50) NOT NULL,
  `stat` enum('Активен','Заблокирован') DEFAULT 'Активен',
  `token` varchar(40) CHARACTER SET utf8mb4 COLLATE utf8mb4_0900_ai_ci DEFAULT NULL,
  PRIMARY KEY (`user`),
  UNIQUE KEY `usertbl` (`user`),
  UNIQUE KEY `u_id` (`user`),
  UNIQUE KEY `ulogin` (`login`)
) ENGINE=InnoDB AUTO_INCREMENT=16 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;

-- Экспортируемые данные не выделены.

-- Дамп структуры для представление sugar_accepting.unloading_operations_list
-- Создание временной таблицы для обработки ошибок зависимостей представлений
CREATE TABLE `unloading_operations_list` (
	`Гос.рег.знак` VARCHAR(1) NOT NULL COLLATE 'utf8mb4_0900_ai_ci',
	`Оператор разгрузки` LONGTEXT NOT NULL COLLATE 'utf8mb4_0900_ai_ci'
) ENGINE=MyISAM;

-- Дамп структуры для процедура sugar_accepting.add_primary_weight
DELIMITER //
CREATE PROCEDURE `add_primary_weight`(pw int, id_te int, login varchar(50))
BEGIN
	IF (@pw > 0) THEN
	INSERT INTO scale_operator(info_primary_weighted) VALUES (pw, (SELECT user FROM usertbl WHERE login = @login));
    SELECT staff_soid INTO @temp FROM scale_operator ORDER BY staff_soid DESC LIMIT 1;
    UPDATE te SET staff_soid = @temp WHERE id_te = @id_te;
    ELSE
		SELECT "Вес не может быть равен или меньше 0!" as Message;
    END IF;
END//
DELIMITER ;

-- Дамп структуры для процедура sugar_accepting.add_te
DELIMITER //
CREATE PROCEDURE `add_te`(vi varchar(50),  sbc mediumtext, trn varchar(11), o int, ad mediumtext, login varchar(50))
BEGIN
	INSERT INTO te(vendor_item, sugar_beet_charact, transport_reg_num) 
    VALUES (@vi, @sbc, @trn);
    INSERT INTO operator(accepting_data) VALUES (@a);
    INSERT INTO operator_te(staff_id, id_te) VALUES ((SELECT id_te FROM te ORDER BY id_te DESC LIMIT 1), (SELECT staff_id FROM operator ORDER BY staff_id DESC LIMIT 1)); 
END//
DELIMITER ;

-- Дамп структуры для процедура sugar_accepting.create_user
DELIMITER //
CREATE PROCEDURE `create_user`(fio varchar(50), login varchar(50))
BEGIN
	INSERT INTO users(fio,login) VALUES (@fio, @login);
END//
DELIMITER ;

-- Дамп структуры для процедура sugar_accepting.send_te_reject_all
DELIMITER //
CREATE PROCEDURE `send_te_reject_all`()
BEGIN
    UPDATE te SET reject_stat = '1' WHERE accept_stat = '0';
END//
DELIMITER ;

-- Дамп структуры для процедура sugar_accepting.send_te_scale_all
DELIMITER //
CREATE PROCEDURE `send_te_scale_all`()
BEGIN
    DECLARE done INT DEFAULT FALSE;
    DECLARE id_te INT;
    DECLARE te_cursor CURSOR FOR SELECT id_te FROM te WHERE distr_stat = '0' AND id_te IS NOT NULL;
    DECLARE CONTINUE HANDLER FOR NOT FOUND SET done = TRUE;

    OPEN te_cursor;

    read_loop: LOOP
        FETCH te_cursor INTO id_te;
        
        IF done THEN
            LEAVE read_loop;
        END IF;
        
        INSERT INTO distr_report(destination, id_te) VALUES ('Взвешивание', @id_te);
    END LOOP;

    CLOSE te_cursor;
END//
DELIMITER ;

-- Дамп структуры для функция sugar_accepting.get_active_users
DELIMITER //
CREATE FUNCTION `get_active_users`() RETURNS int
    READS SQL DATA
BEGIN
	SELECT COUNT(*) INTO @a FROM operator INNER JOIN usertbl ON operator.user = usertbl.user;
RETURN @a;
END//
DELIMITER ;

-- Дамп структуры для функция sugar_accepting.get_count_accept_dates
DELIMITER //
CREATE FUNCTION `get_count_accept_dates`(
	`starter` timestamp,
	`stoper` timestamp
) RETURNS int
    READS SQL DATA
BEGIN
	SELECT COUNT(*) as 'count' INTO @a FROM accepting_act WHERE creating_date;
RETURN @a;
END//
DELIMITER ;

-- Дамп структуры для функция sugar_accepting.get_final_weight1
DELIMITER //
CREATE FUNCTION `get_final_weight1`(id_te int) RETURNS int
    READS SQL DATA
BEGIN
	SELECT staff_soid INTO @te FROM te WHERE id_te = @id_te;
	SELECT IF (info_primary_weighted - info_secondary_weighted > 0, info_primary_weighted - info_secondary_weighted, -1) INTO @a FROM scale_operator WHERE staff_soid = @te;
RETURN  @te;
END//
DELIMITER ;

-- Дамп структуры для функция sugar_accepting.get_reject_te
DELIMITER //
CREATE FUNCTION `get_reject_te`() RETURNS int
    READS SQL DATA
BEGIN
	SELECT COUNT(*) AS 'count' INTO @a FROM te WHERE reject_stat = '1';
RETURN @a;
END//
DELIMITER ;

-- Дамп структуры для триггер sugar_accepting.scale_operator_AFTER_UPDATE_1
SET @OLDTMP_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
DELIMITER //
CREATE TRIGGER `scale_operator_AFTER_UPDATE_1` AFTER UPDATE ON `scale_operator` FOR EACH ROW BEGIN
	/*IF (NEW.info_secondary_weighted > 0) THEN BEGIN
		SELECT id_te INTO @temp FROM te WHERE te.staff_soid = NEW.staff_soid;
		UPDATE te SET accept_stat = 1 WHERE te.id_te = @temp;
        END;
	END IF;*/
END//
DELIMITER ;
SET SQL_MODE=@OLDTMP_SQL_MODE;

-- Удаление временной таблицы и создание окончательной структуры представления
DROP TABLE IF EXISTS `unloading_operations_list`;
CREATE ALGORITHM=UNDEFINED SQL SECURITY DEFINER VIEW `unloading_operations_list` AS select `te`.`transport_reg_num` AS `Гос.рег.знак`,`usertbl`.`fio` AS `Оператор разгрузки` from ((`te` join `unloading_operator` on((`te`.`staff_uoid` = `unloading_operator`.`staff_uoid`))) join `usertbl` on((`unloading_operator`.`user` = `usertbl`.`user`)));

/*!40103 SET TIME_ZONE=IFNULL(@OLD_TIME_ZONE, 'system') */;
/*!40101 SET SQL_MODE=IFNULL(@OLD_SQL_MODE, '') */;
/*!40014 SET FOREIGN_KEY_CHECKS=IFNULL(@OLD_FOREIGN_KEY_CHECKS, 1) */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40111 SET SQL_NOTES=IFNULL(@OLD_SQL_NOTES, 1) */;
