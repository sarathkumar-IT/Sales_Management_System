USE sales_management_system;

DROP TRIGGER IF EXISTS after_payment_insert;
DROP TRIGGER IF EXISTS after_payment_update;
DROP TRIGGER IF EXISTS after_payment_delete;

DELIMITER //

CREATE TRIGGER after_payment_insert
AFTER INSERT ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ),
        status = IF(gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ) <= 0, 'close', 'open')
    WHERE sale_id = NEW.sale_id;
END //

CREATE TRIGGER after_payment_update
AFTER UPDATE ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ),
        status = IF(gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = NEW.sale_id
        ) <= 0, 'close', 'open')
    WHERE sale_id = NEW.sale_id;

    IF OLD.sale_id <> NEW.sale_id THEN
        UPDATE customer_sales
        SET received_amount = (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits WHERE sale_id = OLD.sale_id
            ),
            pending_amount = gross_sales - (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits WHERE sale_id = OLD.sale_id
            ),
            status = IF(gross_sales - (
                SELECT COALESCE(SUM(amount_paid), 0)
                FROM payment_splits WHERE sale_id = OLD.sale_id
            ) <= 0, 'close', 'open')
        WHERE sale_id = OLD.sale_id;
    END IF;
END //

CREATE TRIGGER after_payment_delete
AFTER DELETE ON payment_splits
FOR EACH ROW
BEGIN
    UPDATE customer_sales
    SET received_amount = (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = OLD.sale_id
        ),
        pending_amount = gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = OLD.sale_id
        ),
        status = IF(gross_sales - (
            SELECT COALESCE(SUM(amount_paid), 0)
            FROM payment_splits WHERE sale_id = OLD.sale_id
        ) <= 0, 'close', 'open')
    WHERE sale_id = OLD.sale_id;
END //

DELIMITER ;

SHOW TRIGGERS;