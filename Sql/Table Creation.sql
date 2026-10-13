create database Sales_Management_System;

create table branches(
branch_id int primary key auto_increment, 
branch_name varchar(100), 
branch_admin_name varchar(100));

create table users(
user_id int primary key auto_increment,
user_name varchar(100),
pass_word varchar(100),
email varchar(100),
role enum('Super Admin', 'Admin'),
branch_id int,
foreign key(branch_id) references branches(branch_id));

create table customer_sales(
sale_id int primary key auto_increment,
sale_date date,
customer_name varchar(100),
mobile_number varchar(100),
course_name varchar(100),
gross_sale decimal(12,2),
received_amount decimal(12,2),
pending_amount decimal(12,2),
status enum('open', 'close'),
branch_id int,
foreign key(branch_id) references branches(branch_id));

create table payment_splits(
payment_id int primary key auto_increment,
payment_date date,
amount_paid decimal(12,2),
payment_method varchar(50),
sale_id int,
foreign key(sale_id) references customer_sales(sale_id));

