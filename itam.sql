-- phpMyAdmin SQL Dump
-- version 5.2.0
-- https://www.phpmyadmin.net/
--
-- Host: localhost
-- Generation Time: Nov 23, 2022 at 07:54 AM
-- Server version: 10.4.21-MariaDB
-- PHP Version: 7.4.29

SET SQL_MODE = "NO_AUTO_VALUE_ON_ZERO";
START TRANSACTION;
SET time_zone = "+00:00";

create database itam;

use itam;

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;

--
-- Database: `itam`
--

-- --------------------------------------------------------

--
-- Table structure for table `Asset`
--

CREATE TABLE `Asset` (
  `asset_id` int(20) NOT NULL,
  `serial_no` varchar(50) NOT NULL,
  `asset_state_id` int(20) NOT NULL,
  `asset_tag` varchar(50) NOT NULL,
  `asset_state` varchar(30) NOT NULL,
  `asset_location` varchar(100) NOT NULL,
  `asset_room_no` varchar(15) NOT NULL,
  `stockroom_id` int(10) NOT NULL,
  `asset_condition` varchar(20) NOT NULL,
  `asset_condition_id` int(10) NOT NULL,
  `asset_model` varchar(30) NOT NULL,
  `assigned_to` varchar(50) DEFAULT NULL,
  `employee_id` int(10) DEFAULT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `update_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `asset_condition`
--

CREATE TABLE `asset_condition` (
  `condition_id` int(5) NOT NULL,
  `condition_state` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Dumping data for table `asset_condition`
--

INSERT INTO `asset_condition` (`condition_id`, `condition_state`) VALUES
(1, 'new'),
(2, 'good'),
(3, 'fair'),
(4, 'unusable'),
(5, 'parts');


-- --------------------------------------------------------

--
-- Table structure for table `asset_request`
--

CREATE TABLE `asset_request` (
  `ticket_no` int(20) NOT NULL,
  `employee_name` varchar(30) NOT NULL,
  `employee_id` int(20) NOT NULL,
  `priority_id` int(20) NOT NULL,
  `request_priority` varchar(15) NOT NULL,
  `asset_id` int(10) NOT NULL,
  `asset_model` varchar(30) NOT NULL,
  `asset_tag` varchar(30) NOT NULL,
  `asset_serial_no` varchar(30) NOT NULL,
  `number_of_units` int(5) NOT NULL,
  `additional_comments` text DEFAULT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `update_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `asset_retirement`
--

CREATE TABLE `asset_retirement` (
  `asset_id` int(20) NOT NULL,
  `serial_no` varchar(50) NOT NULL,
  `asset_tag` varchar(50) NOT NULL,
  `asset_model` varchar(30) NOT NULL,
  `is_warehouse_disposal` tinyint(1) NOT NULL,
  `stockroom_id` int(10) NOT NULL,
  `disposal_date` datetime NOT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `update_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- --------------------------------------------------------

--
-- Table structure for table `asset_state`
--

CREATE TABLE `asset_state` (
  `state_id` int(10) NOT NULL,
  `asset_state` varchar(20) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `asset_state`
--

INSERT INTO `asset_state` (`state_id`, `asset_state`) VALUES
(1, 'inuse'),
(2, 'unorder'),
(3, 'lost'),
(4, 'stolen'),
(5, 'instock');


-- --------------------------------------------------------

--
-- Table structure for table `priority`
--

CREATE TABLE `priority` (
  `id` int(10) NOT NULL,
  `priority_type` varchar(15) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `priority`
--

INSERT INTO `priority` (`id`, `priority_type`) VALUES
(1, 'high'),
(2, 'medium'),
(3, 'low');



-- --------------------------------------------------------

--
-- Table structure for table `request_fulfillment`
--

CREATE TABLE `request_fulfillment` (
  `fulfillment_id` int(11) NOT NULL,
  `ticket_no` int(10) NOT NULL,
  `employee_id` int(10) NOT NULL,
  `employee_name` varchar(30) NOT NULL,
  `request_priority` varchar(15) NOT NULL,
  `asset_id` int(20) NOT NULL,
  `asset_model` varchar(50) DEFAULT NULL,
  `asset_tag` varchar(50) DEFAULT NULL,
  `asset_serial_no` varchar(50) DEFAULT NULL,
  `no_of_units` int(5) DEFAULT NULL,
  `service_request_type` varchar(20) NOT NULL,
  `support_service` varchar(20) DEFAULT NULL,
  `additional_comments` text DEFAULT NULL,
  `status` varchar(15) NOT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `update_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `stockroom_management`
--

CREATE TABLE `stockroom_management` (
  `stockroom_id` int(11) NOT NULL,
  `building` varchar(50) DEFAULT NULL,
  `room_number` varchar(15) DEFAULT NULL,
  `address` varchar(250) DEFAULT NULL,
  `security_control` varchar(100) DEFAULT NULL,
  `stockroom_manager` varchar(100) DEFAULT NULL,
  `security_control_id` int(11) DEFAULT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `stockroom_security_type`
--

CREATE TABLE `stockroom_security_type` (
  `stockroom_security_type_id` int(11) NOT NULL,
  `security_control_type` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

--
-- Dumping data for table `stockroom_security_type`
--

INSERT INTO `stockroom_security_type` (`stockroom_security_type_id`, `security_control_type`) VALUES
(1, 'physical lock'),
(2, 'knob lock'),
(3, 'camera lock'),
(4, 'deadbolt lock'),
(5, 'keypad lock'),
(6, 'smart lock'),
(7, 'mortise lock');


-- --------------------------------------------------------

--
-- Table structure for table `support`
--

CREATE TABLE `support` (
  `support_ticket_no` int(20) NOT NULL,
  `employee_id` int(20) NOT NULL,
  `employee_name` varchar(50) NOT NULL,
  `request_priority` varchar(10) NOT NULL,
  `request_id` int(10) NOT NULL,
  `asset_id` int(10) NOT NULL,
  `asset_model` varchar(30) NOT NULL,
  `asset_tag` varchar(30) NOT NULL,
  `asset_serial_no` varchar(30) NOT NULL,
  `support_type` varchar(20) NOT NULL,
  `additional_comments` text NOT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `update_date` datetime NOT NULL DEFAULT current_timestamp()
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


-- --------------------------------------------------------

--
-- Table structure for table `user`
--

CREATE TABLE `user` (
  `employee_id` int(11) NOT NULL,
  `first_name` varchar(50) NOT NULL,
  `middle_name` varchar(50) NOT NULL,
  `last_name` varchar(50) NOT NULL,
  `email_address` varchar(100) NOT NULL,
  `contact_no` varchar(15) NOT NULL,
  `birthdate` datetime NOT NULL DEFAULT current_timestamp(),
  `password` varchar(50) NOT NULL,
  `creation_date` datetime NOT NULL DEFAULT current_timestamp(),
  `updated_date` datetime NOT NULL DEFAULT current_timestamp(),
  `role` varchar(15) NOT NULL,
  `status` varchar(15) NOT NULL,
  `qr_code` blob DEFAULT NULL,
  `otp_encoder` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;


--
-- Indexes for dumped tables
--

--
-- Indexes for table `Asset`
--
ALTER TABLE `Asset`
  ADD PRIMARY KEY (`asset_id`),
  ADD KEY `asset_stockroom` (`stockroom_id`),
  ADD KEY `asset_condition_type` (`asset_condition_id`),
  ADD KEY `asset_state_condition` (`asset_state_id`),
  ADD KEY `asset_employee` (`employee_id`);

--
-- Indexes for table `asset_condition`
--
ALTER TABLE `asset_condition`
  ADD PRIMARY KEY (`condition_id`);

--
-- Indexes for table `asset_request`
--
ALTER TABLE `asset_request`
  ADD PRIMARY KEY (`ticket_no`),
  ADD KEY `employee_relation` (`employee_id`),
  ADD KEY `asset_relation` (`asset_id`),
  ADD KEY `priority_type` (`priority_id`);

--
-- Indexes for table `asset_retirement`
--
ALTER TABLE `asset_retirement`
  ADD PRIMARY KEY (`asset_id`);

--
-- Indexes for table `asset_state`
--
ALTER TABLE `asset_state`
  ADD PRIMARY KEY (`state_id`);

--
-- Indexes for table `priority`
--
ALTER TABLE `priority`
  ADD PRIMARY KEY (`id`);

--
-- Indexes for table `request_fulfillment`
--
ALTER TABLE `request_fulfillment`
  ADD PRIMARY KEY (`fulfillment_id`),
  ADD KEY `employee` (`employee_id`),
  ADD KEY `request` (`ticket_no`),
  ADD KEY `request_fulfillment` (`asset_id`);

--
-- Indexes for table `stockroom_management`
--
ALTER TABLE `stockroom_management`
  ADD PRIMARY KEY (`stockroom_id`),
  ADD KEY `security_control_type` (`security_control_id`);

--
-- Indexes for table `stockroom_security_type`
--
ALTER TABLE `stockroom_security_type`
  ADD PRIMARY KEY (`stockroom_security_type_id`);

--
-- Indexes for table `support`
--
ALTER TABLE `support`
  ADD PRIMARY KEY (`support_ticket_no`),
  ADD KEY `employee` (`employee_id`),
  ADD KEY `priority` (`request_id`);

--
-- Indexes for table `user`
--
ALTER TABLE `user`
  ADD PRIMARY KEY (`employee_id`),
  ADD UNIQUE KEY `email_address` (`email_address`);

--
-- AUTO_INCREMENT for dumped tables
--

--
-- AUTO_INCREMENT for table `Asset`
--
ALTER TABLE `Asset`
  MODIFY `asset_id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=7;

--
-- AUTO_INCREMENT for table `asset_condition`
--
ALTER TABLE `asset_condition`
  MODIFY `condition_id` int(5) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `asset_retirement`
--
ALTER TABLE `asset_retirement`
  MODIFY `asset_id` int(20) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=2;

--
-- AUTO_INCREMENT for table `asset_state`
--
ALTER TABLE `asset_state`
  MODIFY `state_id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=6;

--
-- AUTO_INCREMENT for table `priority`
--
ALTER TABLE `priority`
  MODIFY `id` int(10) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=4;

--
-- AUTO_INCREMENT for table `request_fulfillment`
--
ALTER TABLE `request_fulfillment`
  MODIFY `fulfillment_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=9;

--
-- AUTO_INCREMENT for table `stockroom_management`
--
ALTER TABLE `stockroom_management`
  MODIFY `stockroom_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=13;

--
-- AUTO_INCREMENT for table `stockroom_security_type`
--
ALTER TABLE `stockroom_security_type`
  MODIFY `stockroom_security_type_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=8;

--
-- AUTO_INCREMENT for table `user`
--
ALTER TABLE `user`
  MODIFY `employee_id` int(11) NOT NULL AUTO_INCREMENT, AUTO_INCREMENT=1013;

--
-- Constraints for dumped tables
--

--
-- Constraints for table `Asset`
--
ALTER TABLE `Asset`
  ADD CONSTRAINT `asset_employee` FOREIGN KEY (`employee_id`) REFERENCES `user` (`employee_id`);

--
-- Constraints for table `asset_request`
--
ALTER TABLE `asset_request`
  ADD CONSTRAINT `priority_type` FOREIGN KEY (`priority_id`) REFERENCES `priority` (`id`);

--
-- Constraints for table `request_fulfillment`
--
ALTER TABLE `request_fulfillment`
  ADD CONSTRAINT `request_fulfillment` FOREIGN KEY (`asset_id`) REFERENCES `Asset` (`asset_id`);

--
-- Constraints for table `stockroom_management`
--
ALTER TABLE `stockroom_management`
  ADD CONSTRAINT `security_control_type` FOREIGN KEY (`security_control_id`) REFERENCES `stockroom_security_type` (`stockroom_security_type_id`);

--
-- Constraints for table `support`
--
ALTER TABLE `support`
  ADD CONSTRAINT `priority` FOREIGN KEY (`request_id`) REFERENCES `priority` (`id`);
COMMIT;

/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
