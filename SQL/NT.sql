SELECT * FROM aus_sold_houses.northern_territory
WHERE LOWER(house_type) LIKE 'apartment' and year(sold_date)>2019
ORDER BY sold_price DESC;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM aus_sold_houses.northern_territory
WHERE postcode >= 900 OR postcode < 800;
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE aus_sold_houses.northern_territory ADD COLUMN REA_id INTEGER NULL DEFAULT NULL AFTER house_id;
ALTER TABLE aus_sold_houses.northern_territory ADD UNIQUE (REA_id);
