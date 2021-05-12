SELECT * FROM aus_sold_houses.australian_capital_territory
WHERE time > '2020-01-28 00:00:00'
ORDER BY id DESC;

SELECT YEAR(sold_date) as year, COUNT(*) AS total_sold, AVG(sold_price) as avg_price
FROM aus_sold_houses.australian_capital_territory
WHERE sold_date is not null and sold_price is not null AND YEAR(sold_date) > 2007
AND sold_price < 100000000 and sold_price > 10000 AND
(LOWER(house_type) LIKE 'house' OR LOWER(house_type) LIKE 'townhouse' OR LOWER(house_type) LIKE 'unit')
GROUP BY YEAR(sold_date) ORDER BY YEAR(sold_date);

SELECT COUNT(*) FROM aus_sold_houses.australian_capital_territory
WHERE REA_id is not null
ORDER BY id DESC;

SELECT COUNT(*) FROM aus_sold_houses.australian_capital_territory
WHERE land_size is not Null or floor_area is not Null or year_built is not Null
ORDER BY id DESC;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM aus_sold_houses.australian_capital_territory
WHERE id > 29000;
SET SQL_SAFE_UPDATES = 1;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM aus_sold_houses.australian_capital_territory
WHERE postcode >= 3000 OR postcode < 2600
OR (postcode >= 2700 AND postcode < 2900);
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE aus_sold_houses.australian_capital_territory ADD COLUMN land_size INTEGER NULL DEFAULT NULL AFTER parking;
ALTER TABLE aus_sold_houses.australian_capital_territory ADD COLUMN floor_area INTEGER NULL DEFAULT NULL AFTER land_size;
ALTER TABLE aus_sold_houses.australian_capital_territory ADD COLUMN year_built INTEGER NULL DEFAULT NULL AFTER floor_area;

ALTER TABLE aus_sold_houses.australian_capital_territory ADD COLUMN REA_id INTEGER NULL DEFAULT NULL AFTER house_id;
ALTER TABLE aus_sold_houses.australian_capital_territory ADD UNIQUE (REA_id);