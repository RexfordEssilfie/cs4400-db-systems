-- MySQL Script generated by MySQL Workbench
-- Thu Dec  1 16:32:17 2022
-- Model: New Model    Version: 1.0
-- MySQL Workbench Forward Engineering

SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';

-- -----------------------------------------------------
-- Schema airline_db
-- -----------------------------------------------------

-- -----------------------------------------------------
-- Schema airline_db
-- -----------------------------------------------------
CREATE SCHEMA IF NOT EXISTS `airline_db` DEFAULT CHARACTER SET utf8 ;
USE `airline_db` ;

-- -----------------------------------------------------
-- Table `airline_db`.`Aircraft`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Aircraft` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Aircraft` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Airline_Id` INT NOT NULL,
  `Name` VARCHAR(45) NULL,
  `Model` VARCHAR(45) NULL,
  `Capacity` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Aircraft_Airline1`
    FOREIGN KEY (`Airline_Id`)
    REFERENCES `airline_db`.`Airline` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `Aircraftid_UNIQUE` ON `airline_db`.`Aircraft` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Aircraft_Airline1_idx` ON `airline_db`.`Aircraft` (`Airline_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Airline`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Airline` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Airline` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NOT NULL,
  `City` VARCHAR(45) NULL,
  `State` VARCHAR(45) NULL,
  `Longitude` VARCHAR(45) NULL,
  `Latitude` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idAirline_UNIQUE` ON `airline_db`.`Airline` (`Id` ASC) VISIBLE;

CREATE UNIQUE INDEX `Name_UNIQUE` ON `airline_db`.`Airline` (`Name` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Airport`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Airport` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Airport` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `City` VARCHAR(45) NULL,
  `State` VARCHAR(45) NULL,
  `Abbreviation` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `AirlineId_UNIQUE` ON `airline_db`.`Airport` (`Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`BillingDetail`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`BillingDetail` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`BillingDetail` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Airline_Id` INT NOT NULL,
  `User_id` INT NOT NULL,
  `CardNumberLastFourDigit` VARCHAR(45) NULL,
  `CardToken` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Customer_Airline1`
    FOREIGN KEY (`Airline_Id`)
    REFERENCES `airline_db`.`Airline` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_BillingDetail_User1`
    FOREIGN KEY (`User_id`)
    REFERENCES `airline_db`.`User` (`id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idCustomer_UNIQUE` ON `airline_db`.`BillingDetail` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Customer_Airline1_idx` ON `airline_db`.`BillingDetail` (`Airline_Id` ASC) VISIBLE;

CREATE INDEX `fk_BillingDetail_User1_idx` ON `airline_db`.`BillingDetail` (`User_id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Class`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Class` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Class` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Name` VARCHAR(45) NULL,
  `Tier` INT NULL DEFAULT NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idClass_UNIQUE` ON `airline_db`.`Class` (`Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Confirmation`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Confirmation` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Confirmation` (
  `Confirmation_Name` INT NOT NULL,
  `Status` VARCHAR(45) NULL,
  `ConfirmationDate` DATETIME NULL,
  `Ticket_Id` INT NOT NULL,
  `Passenger_Id` INT NOT NULL,
  PRIMARY KEY (`Confirmation_Name`),
  CONSTRAINT `fk_Confirmation_Ticket1`
    FOREIGN KEY (`Ticket_Id`)
    REFERENCES `airline_db`.`Ticket` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Confirmation_Passenger1`
    FOREIGN KEY (`Passenger_Id`)
    REFERENCES `airline_db`.`Passenger` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `Confirmation_Id_UNIQUE` ON `airline_db`.`Confirmation` (`Confirmation_Name` ASC) VISIBLE;

CREATE INDEX `fk_Confirmation_Ticket1_idx` ON `airline_db`.`Confirmation` (`Ticket_Id` ASC) VISIBLE;

CREATE INDEX `fk_Confirmation_Passenger1_idx` ON `airline_db`.`Confirmation` (`Passenger_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Flight`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Flight` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Flight` (
  `Id` INT NOT NULL AUTO_INCREMENT, 
  `DepartureGate_Id` INT NOT NULL,
  `ArrivalGate_Id` INT NOT NULL,
  `Departure_date` DATETIME NULL,
  `Arrival_date` DATETIME NULL,
  `Airline_Id` INT NOT NULL,
  `Name` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Flight_Gate1`
    FOREIGN KEY (`DepartureGate_Id`)
    REFERENCES `airline_db`.`Gate` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Flight_Gate2`
    FOREIGN KEY (`ArrivalGate_Id`)
    REFERENCES `airline_db`.`Gate` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Flight_Airline1`
    FOREIGN KEY (`Airline_Id`)
    REFERENCES `airline_db`.`Airline` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `FlightId_UNIQUE` ON `airline_db`.`Flight` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Flight_Gate1_idx` ON `airline_db`.`Flight` (`DepartureGate_Id` ASC) VISIBLE;

CREATE INDEX `fk_Flight_Gate2_idx` ON `airline_db`.`Flight` (`ArrivalGate_Id` ASC) VISIBLE;

CREATE INDEX `fk_Flight_Airline1_idx` ON `airline_db`.`Flight` (`Airline_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Gate`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Gate` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Gate` (
  `Id` INT NOT NULL AUTO_INCREMENT,
  `Terminal_Id` INT NOT NULL,
  `Name` VARCHAR(45) NULL,
  `Longitude` VARCHAR(45) NULL,
  `Latitude` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Gate_Terminal1`
    FOREIGN KEY (`Terminal_Id`)
    REFERENCES `airline_db`.`Terminal` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Gate_Terminal1_idx` ON `airline_db`.`Gate` (`Terminal_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Passenger`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Passenger` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Passenger` (
  `Id` INT NOT NULL,
  `Payment_Id` INT NOT NULL,
  `Passport_No` VARCHAR(45) NULL,
  `FirstName` VARCHAR(45) NULL,
  `LastName` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Passenger_Payment1`
    FOREIGN KEY (`Payment_Id`)
    REFERENCES `airline_db`.`Payment` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idPassengers_UNIQUE` ON `airline_db`.`Passenger` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Passenger_Payment1_idx` ON `airline_db`.`Passenger` (`Payment_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Payment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Payment` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Payment` (
  `Id` INT NOT NULL,
  `Amount` INT NULL,
  `DateCreated` DATETIME NULL,
  PRIMARY KEY (`Id`))
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idPayment_UNIQUE` ON `airline_db`.`Payment` (`Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Refund`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Refund` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Refund` (
  `Id` INT NOT NULL,
  `Payment_Id` INT NOT NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Refund_Payment1`
    FOREIGN KEY (`Payment_Id`)
    REFERENCES `airline_db`.`Payment` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idRefund_UNIQUE` ON `airline_db`.`Refund` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Refund_Payment1_idx` ON `airline_db`.`Refund` (`Payment_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Seat`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Seat` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Seat` (
  `Id` INT NOT NULL,
  `Aircraft_Id` INT NOT NULL,
  `Class_Id` INT NOT NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_AircraftSeat_Aircraft1`
    FOREIGN KEY (`Aircraft_Id`)
    REFERENCES `airline_db`.`Aircraft` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Seat_Class1`
    FOREIGN KEY (`Class_Id`)
    REFERENCES `airline_db`.`Class` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_AircraftSeat_Aircraft1_idx` ON `airline_db`.`Seat` (`Aircraft_Id` ASC) VISIBLE;

CREATE INDEX `fk_Seat_Class1_idx` ON `airline_db`.`Seat` (`Class_Id` ASC) VISIBLE;

CREATE UNIQUE INDEX `Id_UNIQUE` ON `airline_db`.`Seat` (`Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Terminal`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Terminal` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Terminal` (
  `Id` INT NOT NULL,
  `Airport_Id` INT NOT NULL,
  `Name` VARCHAR(45) NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Terminal_Airline1`
    FOREIGN KEY (`Airport_Id`)
    REFERENCES `airline_db`.`Airport` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `TerminalId_UNIQUE` ON `airline_db`.`Terminal` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Terminal_Airline1_idx` ON `airline_db`.`Terminal` (`Airport_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`TicektAssignment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`TicektAssignment` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`TicektAssignment` (
  `Id` INT NOT NULL,
  `Ticket_Id` INT NOT NULL,
  `Passenger_Id` INT NOT NULL,
  PRIMARY KEY (`Ticket_Id`, `Id`),
  CONSTRAINT `fk_TicektAssignment_Ticket1`
    FOREIGN KEY (`Ticket_Id`)
    REFERENCES `airline_db`.`Ticket` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_TicektAssignment_Passenger1`
    FOREIGN KEY (`Passenger_Id`)
    REFERENCES `airline_db`.`Passenger` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_TicektAssignment_Ticket1_idx` ON `airline_db`.`TicektAssignment` (`Ticket_Id` ASC) VISIBLE;

CREATE INDEX `fk_TicektAssignment_Passenger1_idx` ON `airline_db`.`TicektAssignment` (`Passenger_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Ticket`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Ticket` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Ticket` (
  `Id` INT NOT NULL,
  `Flight_Id` INT NOT NULL,
  `Seat_Id` INT NOT NULL,
  `Price` INT NULL,
  PRIMARY KEY (`Id`),
  CONSTRAINT `fk_Ticket_Flight1`
    FOREIGN KEY (`Flight_Id`)
    REFERENCES `airline_db`.`Flight` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ticket_Seat1`
    FOREIGN KEY (`Seat_Id`)
    REFERENCES `airline_db`.`Seat` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `idTicket_UNIQUE` ON `airline_db`.`Ticket` (`Id` ASC) VISIBLE;

CREATE INDEX `fk_Ticket_Flight1_idx` ON `airline_db`.`Ticket` (`Flight_Id` ASC) VISIBLE;

CREATE INDEX `fk_Ticket_Seat1_idx` ON `airline_db`.`Ticket` (`Seat_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Ticket_Payment`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Ticket_Payment` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Ticket_Payment` (
  `Ticket_Id` INT NOT NULL,
  `Payment_Id` INT NOT NULL,
  PRIMARY KEY (`Ticket_Id`, `Payment_Id`),
  CONSTRAINT `fk_Ticket_has_Payment_Ticket1`
    FOREIGN KEY (`Ticket_Id`)
    REFERENCES `airline_db`.`Ticket` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Ticket_has_Payment_Payment1`
    FOREIGN KEY (`Payment_Id`)
    REFERENCES `airline_db`.`Payment` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Ticket_has_Payment_Payment1_idx` ON `airline_db`.`Ticket_Payment` (`Payment_Id` ASC) VISIBLE;

CREATE INDEX `fk_Ticket_has_Payment_Ticket1_idx` ON `airline_db`.`Ticket_Payment` (`Ticket_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`Trip`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`Trip` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`Trip` (
  `Flight_Id` INT NOT NULL,
  `Confirmation_Confirmation_Id` INT NOT NULL,
  `Id` VARCHAR(45) NOT NULL,
  PRIMARY KEY (`Flight_Id`, `Confirmation_Confirmation_Id`, `Id`),
  CONSTRAINT `fk_Flight_has_Confirmation_Flight1`
    FOREIGN KEY (`Flight_Id`)
    REFERENCES `airline_db`.`Flight` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION,
  CONSTRAINT `fk_Flight_has_Confirmation_Confirmation1`
    FOREIGN KEY (`Confirmation_Confirmation_Id`)
    REFERENCES `airline_db`.`Confirmation` (`Confirmation_Name`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE INDEX `fk_Flight_has_Confirmation_Confirmation1_idx` ON `airline_db`.`Trip` (`Confirmation_Confirmation_Id` ASC) VISIBLE;

CREATE INDEX `fk_Flight_has_Confirmation_Flight1_idx` ON `airline_db`.`Trip` (`Flight_Id` ASC) VISIBLE;


-- -----------------------------------------------------
-- Table `airline_db`.`User`
-- -----------------------------------------------------
DROP TABLE IF EXISTS `airline_db`.`User` ;

CREATE TABLE IF NOT EXISTS `airline_db`.`User` (
  `id` INT NOT NULL,
  `FirstName` VARCHAR(45) NULL,
  `Airline_Id` INT NOT NULL,
  `LastName` VARCHAR(45) NULL,
  `Password` VARCHAR(45) NULL,
  `Email` VARCHAR(45) NULL,
  PRIMARY KEY (`id`),
  CONSTRAINT `fk_User_Airline1`
    FOREIGN KEY (`Airline_Id`)
    REFERENCES `airline_db`.`Airline` (`Id`)
    ON DELETE NO ACTION
    ON UPDATE NO ACTION)
ENGINE = InnoDB;

CREATE UNIQUE INDEX `id_UNIQUE` ON `airline_db`.`User` (`id` ASC) VISIBLE;

CREATE INDEX `fk_User_Airline1_idx` ON `airline_db`.`User` (`Airline_Id` ASC) VISIBLE;



-- -----------------------------------------------------
-- STORED PROCEDURE `airline_db`.create_airline
-- -----------------------------------------------------

DELIMITER $$
CREATE PROCEDURE `create_airline`(name varchar(45), city varchar(45), state varchar(45))
BEGIN
	INSERT INTO `airline_db`.`Airline`
	(`Name`,
	`City`,
	`State`)
	VALUES
	(
	name,
	city,
	state);
END$$
DELIMITER ;



-- -----------------------------------------------------
-- STORED PROCEDURE `airline_db`.create_airline
-- -----------------------------------------------------

DELIMITER $$
CREATE PROCEDURE `find_available_tickets`(in flight_id int)
BEGIN
  SELECT * from Ticket left join Confirmation on Ticket.Id = Confirmation.Ticket_id 
  WHERE Confirmation.Status != "Active";
END$$
DELIMITER ;



-- -----------------------------------------------------
-- STORED PROCEDURE `airline_db`.create_class
-- -----------------------------------------------------

DELIMITER $$
CREATE PROCEDURE `create_class` (in name varchar(45), in tier int)
BEGIN
	INSERT INTO `airline_db`.`Class`
	(`Name`,
	`Tier`)
	VALUES
	(name,
    tier
	);
END$$
DELIMITER ;


SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;
