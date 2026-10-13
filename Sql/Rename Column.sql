USE sales_management_system;

ALTER TABLE users RENAME COLUMN user_name TO username;
ALTER TABLE users RENAME COLUMN pass_word TO password;

ALTER TABLE customer_sales RENAME COLUMN sale_date TO date;
ALTER TABLE customer_sales RENAME COLUMN customer_name TO name;
ALTER TABLE customer_sales RENAME COLUMN course_name TO product_name;
ALTER TABLE customer_sales RENAME COLUMN gross_sale TO gross_sales;



select * from users;
