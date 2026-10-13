select * from payment_splits;
USE sales_management_system;

SET SQL_SAFE_UPDATES = 0;

DELETE FROM payment_splits;
DELETE FROM customer_sales;

ALTER TABLE payment_splits AUTO_INCREMENT = 1;
ALTER TABLE customer_sales AUTO_INCREMENT = 1;

SET SQL_SAFE_UPDATES = 1;

SET SQL_SAFE_UPDATES = 0;
UPDATE customer_sales
SET received_amount = 0, pending_amount = gross_sales, status = 'open';
SET SQL_SAFE_UPDATES = 1;


SELECT 'branches' AS table_name, COUNT(*) AS total FROM branches
UNION ALL SELECT 'users', COUNT(*) FROM users
UNION ALL SELECT 'customer_sales', COUNT(*) FROM customer_sales
UNION ALL SELECT 'payment_splits', COUNT(*) FROM payment_splits;

SELECT SUM(gross_sales) AS gross, SUM(received_amount) AS received, SUM(pending_amount) AS pending
FROM customer_sales;

SELECT user_id, username, role, branch_id FROM users ORDER BY user_id;

INSERT INTO users (user_id, username, password, email, role, branch_id)
VALUES (1, 'superadmin', 'super123', 'superadmin@company.com', 'Super Admin', NULL);
select * from users;


DESCRIBE customer_sales;
select * from payment_splits;
select * from customer_sales;

delete from customer_sales where sale_id between 1001 and 1005;
SELECT 
    cs.sale_id,
    b.branch_name,
    cs.date,
    cs.name,
    cs.mobile_number,
    cs.product_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    cs.status
FROM customer_sales cs
LEFT JOIN branches b ON cs.branch_id = b.branch_id
WHERE cs.name = 'sarath';

SELECT * FROM customer_sales WHERE name = 'sarath';

	select p.payment_id,
    p.payment_date,
    p.amount_paid,
    p.payment_method,
    cs.sale_id,
    cs.name AS student_name,
    cs.gross_sales,
    cs.received_amount,
    cs.pending_amount,
    cs.status
FROM payments p
JOIN customer_sales cs ON p.sale_id = cs.sale_id
ORDER BY p.payment_id DESC
LIMIT 10;

select * from users;
UPDATE users SET role = 'Branch Admin' WHERE user_id > 1;
                    
                    
