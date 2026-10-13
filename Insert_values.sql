INSERT INTO branches
(branch_name, branch_admin_name)
VALUES
('Pondicherry', 'Arun Kumar'),
('Cuddalore', 'Ravi Kumar'),
('Chennai', 'Suresh Babu'),
('Bangalore', 'Karthik Raj');

INSERT INTO customer_sales
(sale_date, customer_name, mobile_number, course_name, gross_sale,
 received_amount, pending_amount, status, branch_id)
VALUES
('2026-10-01', 'Ramesh', '9876543210', 'Laptop', 50000.00, 0, 50000.00, 'open', 1),
('2026-10-01', 'Suresh', '9876543211', 'Mobile', 30000.00, 0, 30000.00, 'open', 1),
('2026-10-02', 'Priya', '9876543212', 'Tablet', 40000.00, 0, 40000.00, 'open', 2),
('2026-10-02', 'Arun', '9876543213', 'Laptop', 60000.00, 0, 60000.00, 'open', 2),
('2026-10-03', 'Kumar', '9876543214', 'Monitor', 25000.00, 0, 25000.00, 'open', 3),
('2026-10-03', 'Divya', '9876543215', 'Printer', 20000.00, 0, 20000.00, 'open', 3),
('2026-10-04', 'Vijay', '9876543216', 'Desktop', 55000.00, 0, 55000.00, 'open', 4),
('2026-10-04', 'Anitha', '9876543217', 'Keyboard', 10000.00, 0, 10000.00, 'open', 4),
('2026-10-05', 'Manoj', '9876543218', 'Laptop', 70000.00, 0, 70000.00, 'open', 1),
('2026-10-05', 'Deepa', '9876543219', 'Mobile', 35000.00, 0, 35000.00, 'open', 2);

INSERT INTO users
(user_name, pass_word, email, role, branch_id)
VALUES
('ArunAdmin', 'Arun@123', 'arun@gmail.com', 'Super Admin', 1),
('RaviAdmin', 'Ravi@123', 'ravi@gmail.com', 'Admin', 2),
('SureshAdmin', 'Suresh@123', 'suresh@gmail.com', 'Admin', 3),
('KarthikAdmin', 'Karthik@123', 'karthik@gmail.com', 'Admin', 4),
('PondyUser', 'Pondy@123', 'pondy@gmail.com', 'Admin', 1);

INSERT INTO payment_splits
(payment_date, amount_paid, payment_method, sale_id)
VALUES
('2026-10-01', 10000.00, 'Cash', 1),
('2026-10-02', 15000.00, 'UPI', 1),

('2026-10-02', 20000.00, 'Bank Transfer', 2),
('2026-10-03', 5000.00, 'Cash', 2),

('2026-10-03', 12000.00, 'UPI', 3),
('2026-10-04', 8000.00, 'Card', 3),

('2026-10-04', 25000.00, 'Bank Transfer', 4),
('2026-10-05', 10000.00, 'Cash', 4),

('2026-10-05', 10000.00, 'UPI', 5),
('2026-10-06', 5000.00, 'Card', 5),

('2026-10-06', 5000.00, 'Cash', 6),
('2026-10-06', 5000.00, 'UPI', 6),

('2026-10-06', 30000.00, 'Bank Transfer', 7),
('2026-10-06', 10000.00, 'Cash', 7),

('2026-10-06', 4000.00, 'UPI', 8),
('2026-10-06', 3000.00, 'Card', 8),

('2026-10-06', 30000.00, 'Bank Transfer', 9),
('2026-10-06', 10000.00, 'UPI', 9),

('2026-10-06', 15000.00, 'Cash', 10),
('2026-10-06', 5000.00, 'Card', 10);

SELECT * FROM branches;
select * from users;
select * from customer_sales;
SELECT * FROM payment_splits;




SET SQL_SAFE_UPDATES = 0;

UPDATE customer_sales
SET course_name = CASE sale_id
    WHEN 1  THEN 'Python'
    WHEN 2  THEN 'Java'
    WHEN 3  THEN 'SQL'
    WHEN 4  THEN 'Power BI'
    WHEN 5  THEN 'Data Science'
    WHEN 6  THEN 'Python'
    WHEN 7  THEN 'Java'
    WHEN 8  THEN 'SQL'
    WHEN 9  THEN 'Power BI'
    WHEN 10 THEN 'Data Science'
END
WHERE sale_id BETWEEN 1 AND 10;

SET SQL_SAFE_UPDATES = 1;