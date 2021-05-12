SELECT * FROM aus_sold_houses.queensland
ORDER BY id DESC;

SELECT COUNT(*) FROM aus_sold_houses.queensland
WHERE REA_id is not null
ORDER BY id DESC;

SELECT * FROM aus_sold_houses.queensland
WHERE house_id = 201408194;

SELECT COUNT(*) FROM aus_sold_houses.queensland;

SET SQL_SAFE_UPDATES = 0;
DELETE FROM aus_sold_houses.queensland
WHERE postcode >= 5000 OR postcode < 4000;
SET SQL_SAFE_UPDATES = 1;

ALTER TABLE aus_sold_houses.queensland ADD COLUMN REA_id INTEGER NULL DEFAULT NULL AFTER house_id;
ALTER TABLE aus_sold_houses.queensland ADD UNIQUE (REA_id);