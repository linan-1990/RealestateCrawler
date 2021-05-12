SELECT * FROM aus_sold_houses.tasmania
where sold_date is null
ORDER BY id DESC;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM aus_sold_houses.tasmania
WHERE postcode >= 8000 OR postcode < 7000;
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE aus_sold_houses.tasmania ADD COLUMN REA_id INTEGER NULL DEFAULT NULL AFTER house_id;
ALTER TABLE aus_sold_houses.tasmania ADD UNIQUE (REA_id);