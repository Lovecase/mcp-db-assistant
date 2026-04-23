PRAGMA foreign_keys = ON;

BEGIN TRANSACTION;

DROP TABLE IF EXISTS orders;
DROP TABLE IF EXISTS customers;
DROP TABLE IF EXISTS products;
DROP TABLE IF EXISTS regions;

CREATE TABLE regions (
    id   INTEGER PRIMARY KEY,
    name TEXT    NOT NULL
);

CREATE TABLE customers (
    id          INTEGER PRIMARY KEY,
    name        TEXT    NOT NULL,
    email       TEXT    NOT NULL UNIQUE,
    region_id   INTEGER NOT NULL REFERENCES regions(id),
    signup_date TEXT    NOT NULL
);

CREATE TABLE products (
    id       INTEGER PRIMARY KEY,
    name     TEXT    NOT NULL,
    category TEXT    NOT NULL,
    price    REAL    NOT NULL
);

CREATE TABLE orders (
    id          INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers(id),
    product_id  INTEGER NOT NULL REFERENCES products(id),
    quantity    INTEGER NOT NULL,
    amount      REAL    NOT NULL,
    order_date  TEXT    NOT NULL,
    status      TEXT    NOT NULL
);

-- ─── Regions ──────────────────────────────────────────────────────────────────

INSERT INTO regions (id, name) VALUES
(1, 'North'),
(2, 'South'),
(3, 'East'),
(4, 'West'),
(5, 'Central');

-- ─── Products ─────────────────────────────────────────────────────────────────

INSERT INTO products (id, name, category, price) VALUES
(1,  'Laptop Pro 15',           'Electronics', 1299.99),
(2,  'Smartphone X12',          'Electronics',  799.99),
(3,  'Wireless Headphones',     'Electronics',  149.99),
(4,  'Smart Watch Series 5',    'Electronics',  349.99),
(5,  'Bluetooth Speaker',       'Electronics',   89.99),
(6,  '4K Monitor 27in',         'Electronics',  499.99),
(7,  'Digital Camera',          'Electronics',  599.99),
(8,  'Tablet Air',              'Electronics',  449.99),
(9,  'Classic Denim Jeans',     'Clothing',      59.99),
(10, 'Cotton T-Shirt',          'Clothing',      24.99),
(11, 'Winter Jacket',           'Clothing',     129.99),
(12, 'Summer Dress',            'Clothing',      49.99),
(13, 'Running Sneakers',        'Clothing',      89.99),
(14, 'Leather Boots',           'Clothing',     149.99),
(15, 'Wool Sweater',            'Clothing',      69.99),
(16, 'Athletic Shorts',         'Clothing',      29.99),
(17, 'Premium Coffee Beans',    'Food',          24.99),
(18, 'Extra Virgin Olive Oil',  'Food',          19.99),
(19, 'Artisan Pasta Set',       'Food',          14.99),
(20, 'World Spice Kit',         'Food',          34.99),
(21, 'Dark Chocolate Box',      'Food',          22.99),
(22, 'Premium Tea Collection',  'Food',          18.99),
(23, 'Raw Honey Jar',           'Food',          16.99),
(24, 'Python Programming Guide','Books',         39.99),
(25, 'Data Science Handbook',   'Books',         44.99),
(26, 'Machine Learning Mastery','Books',         49.99),
(27, 'SQL for Beginners',       'Books',         34.99),
(28, 'Business Analytics Pro',  'Books',         42.99),
(29, 'Clean Code Principles',   'Books',         37.99),
(30, 'System Design Interview', 'Books',         46.99);

-- ─── Customers (200 rows, ~40 per region) ─────────────────────────────────────

INSERT INTO customers (id, name, email, region_id, signup_date) VALUES
-- North (1–40)
(1,   'James Smith',        'james.smith@gmail.com',          1, '2023-01-15'),
(2,   'Emma Johnson',       'emma.johnson@yahoo.com',          1, '2022-03-22'),
(3,   'Liam Williams',      'liam.williams@hotmail.com',       1, '2023-07-10'),
(4,   'Olivia Brown',       'olivia.brown@outlook.com',        1, '2022-11-05'),
(5,   'Noah Jones',         'noah.jones@icloud.com',           1, '2024-02-18'),
(6,   'Ava Garcia',         'ava.garcia@gmail.com',            1, '2022-08-30'),
(7,   'William Miller',     'william.miller@yahoo.com',        1, '2023-04-14'),
(8,   'Sophia Davis',       'sophia.davis@hotmail.com',        1, '2024-06-25'),
(9,   'Benjamin Wilson',    'benjamin.wilson@outlook.com',     1, '2022-12-03'),
(10,  'Isabella Moore',     'isabella.moore@icloud.com',       1, '2023-09-17'),
(11,  'Lucas Taylor',       'lucas.taylor@gmail.com',          1, '2024-01-08'),
(12,  'Mia Anderson',       'mia.anderson@yahoo.com',          1, '2022-05-20'),
(13,  'Henry Thomas',       'henry.thomas@hotmail.com',        1, '2023-11-29'),
(14,  'Charlotte Jackson',  'charlotte.jackson@outlook.com',   1, '2024-04-07'),
(15,  'Alexander White',    'alexander.white@icloud.com',      1, '2022-02-14'),
(16,  'Amelia Harris',      'amelia.harris@gmail.com',         1, '2023-06-11'),
(17,  'Mason Martin',       'mason.martin@yahoo.com',          1, '2024-08-22'),
(18,  'Harper Thompson',    'harper.thompson@hotmail.com',     1, '2022-10-31'),
(19,  'Ethan Robinson',     'ethan.robinson@outlook.com',      1, '2023-03-05'),
(20,  'Evelyn Lewis',       'evelyn.lewis@icloud.com',         1, '2024-05-16'),
(21,  'Daniel Walker',      'daniel.walker@gmail.com',         1, '2022-07-09'),
(22,  'Abigail Hall',       'abigail.hall@yahoo.com',          1, '2023-01-28'),
(23,  'Michael Allen',      'michael.allen@hotmail.com',       1, '2024-03-19'),
(24,  'Emily Young',        'emily.young@outlook.com',         1, '2022-09-24'),
(25,  'Matthew King',       'matthew.king@icloud.com',         1, '2023-12-07'),
(26,  'Elizabeth Scott',    'elizabeth.scott@gmail.com',       1, '2024-07-13'),
(27,  'Jackson Green',      'jackson.green@yahoo.com',         1, '2022-04-02'),
(28,  'Sofia Baker',        'sofia.baker@hotmail.com',         1, '2023-08-18'),
(29,  'Sebastian Adams',    'sebastian.adams@outlook.com',     1, '2024-10-30'),
(30,  'Avery Nelson',       'avery.nelson@icloud.com',         1, '2022-06-15'),
(31,  'Jack Carter',        'jack.carter@gmail.com',           1, '2023-02-27'),
(32,  'Ella Mitchell',      'ella.mitchell@yahoo.com',         1, '2024-09-04'),
(33,  'Owen Perez',         'owen.perez@hotmail.com',          1, '2022-01-20'),
(34,  'Scarlett Roberts',   'scarlett.roberts@outlook.com',    1, '2023-05-11'),
(35,  'Samuel Turner',      'samuel.turner@icloud.com',        1, '2024-11-23'),
(36,  'Grace Phillips',     'grace.phillips@gmail.com',        1, '2022-03-08'),
(37,  'David Campbell',     'david.campbell@yahoo.com',        1, '2023-10-16'),
(38,  'Chloe Parker',       'chloe.parker@hotmail.com',        1, '2024-02-01'),
(39,  'Joseph Evans',       'joseph.evans@outlook.com',        1, '2022-08-17'),
(40,  'Victoria Edwards',   'victoria.edwards@icloud.com',     1, '2023-07-04'),
-- South (41–80)
(41,  'James Taylor',       'james.taylor@gmail.com',          2, '2023-02-14'),
(42,  'Emma Anderson',      'emma.anderson@yahoo.com',         2, '2022-06-25'),
(43,  'Liam Thomas',        'liam.thomas@hotmail.com',         2, '2023-10-08'),
(44,  'Olivia Jackson',     'olivia.jackson@outlook.com',      2, '2024-01-17'),
(45,  'Noah White',         'noah.white@icloud.com',           2, '2022-09-03'),
(46,  'Ava Harris',         'ava.harris@gmail.com',            2, '2023-05-19'),
(47,  'William Martin',     'william.martin@yahoo.com',        2, '2024-07-28'),
(48,  'Sophia Thompson',    'sophia.thompson@hotmail.com',     2, '2022-11-14'),
(49,  'Benjamin Robinson',  'benjamin.robinson@outlook.com',   2, '2023-04-01'),
(50,  'Isabella Lewis',     'isabella.lewis@icloud.com',       2, '2024-08-09'),
(51,  'Lucas Walker',       'lucas.walker@gmail.com',          2, '2022-02-22'),
(52,  'Mia Hall',           'mia.hall@yahoo.com',              2, '2023-09-30'),
(53,  'Henry Allen',        'henry.allen@hotmail.com',         2, '2024-04-15'),
(54,  'Charlotte Young',    'charlotte.young@outlook.com',     2, '2022-07-06'),
(55,  'Alexander King',     'alexander.king@icloud.com',       2, '2023-12-21'),
(56,  'Amelia Scott',       'amelia.scott@gmail.com',          2, '2024-06-03'),
(57,  'Mason Green',        'mason.green@yahoo.com',           2, '2022-04-28'),
(58,  'Harper Baker',       'harper.baker@hotmail.com',        2, '2023-08-12'),
(59,  'Ethan Adams',        'ethan.adams@outlook.com',         2, '2024-02-25'),
(60,  'Evelyn Nelson',      'evelyn.nelson@icloud.com',        2, '2022-10-10'),
(61,  'Daniel Carter',      'daniel.carter@gmail.com',         2, '2023-03-07'),
(62,  'Abigail Mitchell',   'abigail.mitchell@yahoo.com',      2, '2024-09-18'),
(63,  'Michael Perez',      'michael.perez@hotmail.com',       2, '2022-01-31'),
(64,  'Emily Roberts',      'emily.roberts@outlook.com',       2, '2023-07-22'),
(65,  'Matthew Turner',     'matthew.turner@icloud.com',       2, '2024-05-05'),
(66,  'Elizabeth Phillips', 'elizabeth.phillips@gmail.com',    2, '2022-03-16'),
(67,  'Jackson Campbell',   'jackson.campbell@yahoo.com',      2, '2023-11-27'),
(68,  'Sofia Parker',       'sofia.parker@hotmail.com',        2, '2024-01-02'),
(69,  'Sebastian Evans',    'sebastian.evans@outlook.com',     2, '2022-06-19'),
(70,  'Avery Edwards',      'avery.edwards@icloud.com',        2, '2023-09-08'),
(71,  'Jack Smith',         'jack.smith@gmail.com',            2, '2024-03-25'),
(72,  'Ella Johnson',       'ella.johnson@yahoo.com',          2, '2022-05-14'),
(73,  'Owen Williams',      'owen.williams@hotmail.com',       2, '2023-01-16'),
(74,  'Scarlett Brown',     'scarlett.brown@outlook.com',      2, '2024-10-07'),
(75,  'Samuel Jones',       'samuel.jones@icloud.com',         2, '2022-08-23'),
(76,  'Grace Garcia',       'grace.garcia@gmail.com',          2, '2023-06-04'),
(77,  'David Miller',       'david.miller@yahoo.com',          2, '2024-11-16'),
(78,  'Chloe Davis',        'chloe.davis@hotmail.com',         2, '2022-12-29'),
(79,  'Joseph Wilson',      'joseph.wilson@outlook.com',       2, '2023-04-19'),
(80,  'Victoria Moore',     'victoria.moore@icloud.com',       2, '2024-08-31'),
-- East (81–120)
(81,  'James Walker',       'james.walker@gmail.com',          3, '2023-01-09'),
(82,  'Emma Hall',          'emma.hall@yahoo.com',             3, '2022-04-21'),
(83,  'Liam Allen',         'liam.allen@hotmail.com',          3, '2023-08-14'),
(84,  'Olivia Young',       'olivia.young@outlook.com',        3, '2024-01-27'),
(85,  'Noah King',          'noah.king@icloud.com',            3, '2022-07-16'),
(86,  'Ava Scott',          'ava.scott@gmail.com',             3, '2023-05-03'),
(87,  'William Green',      'william.green@yahoo.com',         3, '2024-09-12'),
(88,  'Sophia Baker',       'sophia.baker@hotmail.com',        3, '2022-02-08'),
(89,  'Benjamin Adams',     'benjamin.adams@outlook.com',      3, '2023-11-25'),
(90,  'Isabella Nelson',    'isabella.nelson@icloud.com',      3, '2024-04-04'),
(91,  'Lucas Carter',       'lucas.carter@gmail.com',          3, '2022-06-29'),
(92,  'Mia Mitchell',       'mia.mitchell@yahoo.com',          3, '2023-03-17'),
(93,  'Henry Perez',        'henry.perez@hotmail.com',         3, '2024-07-06'),
(94,  'Charlotte Roberts',  'charlotte.roberts@outlook.com',   3, '2022-09-20'),
(95,  'Alexander Turner',   'alexander.turner@icloud.com',     3, '2023-02-11'),
(96,  'Amelia Phillips',    'amelia.phillips@gmail.com',        3, '2024-05-24'),
(97,  'Mason Campbell',     'mason.campbell@yahoo.com',        3, '2022-01-07'),
(98,  'Harper Parker',      'harper.parker@hotmail.com',       3, '2023-10-30'),
(99,  'Ethan Evans',        'ethan.evans@outlook.com',         3, '2024-03-13'),
(100, 'Evelyn Edwards',     'evelyn.edwards@icloud.com',       3, '2022-08-04'),
(101, 'Daniel Smith',       'daniel.smith@gmail.com',          3, '2023-06-28'),
(102, 'Abigail Johnson',    'abigail.johnson@yahoo.com',       3, '2024-12-09'),
(103, 'Michael Williams',   'michael.williams@hotmail.com',    3, '2022-03-25'),
(104, 'Emily Brown',        'emily.brown@outlook.com',         3, '2023-09-11'),
(105, 'Matthew Jones',      'matthew.jones@icloud.com',        3, '2024-02-16'),
(106, 'Elizabeth Garcia',   'elizabeth.garcia@gmail.com',      3, '2022-05-31'),
(107, 'Jackson Miller',     'jackson.miller@yahoo.com',        3, '2023-01-04'),
(108, 'Sofia Davis',        'sofia.davis@hotmail.com',         3, '2024-08-17'),
(109, 'Sebastian Wilson',   'sebastian.wilson@outlook.com',    3, '2022-11-22'),
(110, 'Avery Moore',        'avery.moore@icloud.com',          3, '2023-07-15'),
(111, 'Jack Taylor',        'jack.taylor@gmail.com',           3, '2024-04-28'),
(112, 'Ella Anderson',      'ella.anderson@yahoo.com',         3, '2022-02-13'),
(113, 'Owen Thomas',        'owen.thomas@hotmail.com',         3, '2023-12-01'),
(114, 'Scarlett Jackson',   'scarlett.jackson@outlook.com',    3, '2024-06-19'),
(115, 'Samuel White',       'samuel.white@icloud.com',         3, '2022-04-07'),
(116, 'Grace Harris',       'grace.harris@gmail.com',          3, '2023-04-24'),
(117, 'David Martin',       'david.martin@yahoo.com',          3, '2024-10-05'),
(118, 'Chloe Thompson',     'chloe.thompson@hotmail.com',      3, '2022-07-18'),
(119, 'Joseph Robinson',    'joseph.robinson@outlook.com',     3, '2023-02-06'),
(120, 'Victoria Lewis',     'victoria.lewis@icloud.com',       3, '2024-09-29'),
-- West (121–160)
(121, 'James Carter',       'james.carter@gmail.com',          4, '2023-03-20'),
(122, 'Emma Mitchell',      'emma.mitchell@yahoo.com',         4, '2022-07-31'),
(123, 'Liam Perez',         'liam.perez@hotmail.com',          4, '2023-11-13'),
(124, 'Olivia Roberts',     'olivia.roberts@outlook.com',      4, '2024-04-26'),
(125, 'Noah Turner',        'noah.turner@icloud.com',          4, '2022-01-09'),
(126, 'Ava Phillips',       'ava.phillips@gmail.com',          4, '2023-08-22'),
(127, 'William Campbell',   'william.campbell@yahoo.com',      4, '2024-06-07'),
(128, 'Sophia Parker',      'sophia.parker@hotmail.com',       4, '2022-10-14'),
(129, 'Benjamin Evans',     'benjamin.evans@outlook.com',      4, '2023-05-29'),
(130, 'Isabella Edwards',   'isabella.edwards@icloud.com',     4, '2024-01-12'),
(131, 'Lucas Smith',        'lucas.smith@gmail.com',           4, '2022-03-03'),
(132, 'Mia Johnson',        'mia.johnson@yahoo.com',           4, '2023-09-16'),
(133, 'Henry Williams',     'henry.williams@hotmail.com',      4, '2024-07-25'),
(134, 'Charlotte Brown',    'charlotte.brown@outlook.com',     4, '2022-05-08'),
(135, 'Alexander Jones',    'alexander.jones@icloud.com',      4, '2023-02-17'),
(136, 'Amelia Garcia',      'amelia.garcia@gmail.com',         4, '2024-10-01'),
(137, 'Mason Miller',       'mason.miller@yahoo.com',          4, '2022-08-12'),
(138, 'Harper Davis',       'harper.davis@hotmail.com',        4, '2023-04-07'),
(139, 'Ethan Wilson',       'ethan.wilson@outlook.com',        4, '2024-11-18'),
(140, 'Evelyn Moore',       'evelyn.moore@icloud.com',         4, '2022-11-27'),
(141, 'Daniel Taylor',      'daniel.taylor@gmail.com',         4, '2023-07-10'),
(142, 'Abigail Anderson',   'abigail.anderson@yahoo.com',      4, '2024-03-23'),
(143, 'Michael Thomas',     'michael.thomas@hotmail.com',      4, '2022-04-16'),
(144, 'Emily Jackson',      'emily.jackson@outlook.com',       4, '2023-12-29'),
(145, 'Matthew White',      'matthew.white@icloud.com',        4, '2024-08-11'),
(146, 'Elizabeth Harris',   'elizabeth.harris@gmail.com',      4, '2022-06-24'),
(147, 'Jackson Martin',     'jackson.martin@yahoo.com',        4, '2023-01-03'),
(148, 'Sofia Thompson',     'sofia.thompson@hotmail.com',      4, '2024-05-14'),
(149, 'Sebastian Robinson', 'sebastian.robinson@outlook.com',  4, '2022-09-07'),
(150, 'Avery Lewis',        'avery.lewis@icloud.com',          4, '2023-10-20'),
(151, 'Jack Walker',        'jack.walker@gmail.com',           4, '2024-02-08'),
(152, 'Ella Hall',          'ella.hall@yahoo.com',             4, '2022-12-15'),
(153, 'Owen Allen',         'owen.allen@hotmail.com',          4, '2023-06-01'),
(154, 'Scarlett Young',     'scarlett.young@outlook.com',      4, '2024-09-24'),
(155, 'Samuel King',        'samuel.king@icloud.com',          4, '2022-02-28'),
(156, 'Grace Scott',        'grace.scott@gmail.com',           4, '2023-08-13'),
(157, 'David Green',        'david.green@yahoo.com',           4, '2024-04-06'),
(158, 'Chloe Baker',        'chloe.baker@hotmail.com',         4, '2022-06-19'),
(159, 'Joseph Adams',       'joseph.adams@outlook.com',        4, '2023-03-24'),
(160, 'Victoria Nelson',    'victoria.nelson@icloud.com',      4, '2024-12-05'),
-- Central (161–200)
(161, 'James Garcia',       'james.garcia@gmail.com',          5, '2023-04-18'),
(162, 'Emma Miller',        'emma.miller@yahoo.com',           5, '2022-08-29'),
(163, 'Liam Davis',         'liam.davis@hotmail.com',          5, '2023-12-11'),
(164, 'Olivia Wilson',      'olivia.wilson@outlook.com',       5, '2024-05-24'),
(165, 'Noah Moore',         'noah.moore@icloud.com',           5, '2022-01-17'),
(166, 'Ava Taylor',         'ava.taylor@gmail.com',            5, '2023-07-03'),
(167, 'William Anderson',   'william.anderson@yahoo.com',      5, '2024-09-16'),
(168, 'Sophia Thomas',      'sophia.thomas@hotmail.com',       5, '2022-03-30'),
(169, 'Benjamin Jackson',   'benjamin.jackson@outlook.com',    5, '2023-02-12'),
(170, 'Isabella White',     'isabella.white@icloud.com',       5, '2024-07-01'),
(171, 'Lucas Harris',       'lucas.harris@gmail.com',          5, '2022-05-16'),
(172, 'Mia Martin',         'mia.martin@yahoo.com',            5, '2023-10-27'),
(173, 'Henry Thompson',     'henry.thompson@hotmail.com',      5, '2024-04-08'),
(174, 'Charlotte Robinson', 'charlotte.robinson@outlook.com',  5, '2022-08-03'),
(175, 'Alexander Lewis',    'alexander.lewis@icloud.com',      5, '2023-06-19'),
(176, 'Amelia Walker',      'amelia.walker@gmail.com',         5, '2024-01-30'),
(177, 'Mason Hall',         'mason.hall@yahoo.com',            5, '2022-10-25'),
(178, 'Harper Allen',       'harper.allen@hotmail.com',        5, '2023-09-07'),
(179, 'Ethan Young',        'ethan.young@outlook.com',         5, '2024-03-20'),
(180, 'Evelyn King',        'evelyn.king@icloud.com',          5, '2022-12-08'),
(181, 'Daniel Scott',       'daniel.scott@gmail.com',          5, '2023-05-14'),
(182, 'Abigail Green',      'abigail.green@yahoo.com',         5, '2024-08-27'),
(183, 'Michael Baker',      'michael.baker@hotmail.com',       5, '2022-02-21'),
(184, 'Emily Adams',        'emily.adams@outlook.com',         5, '2023-11-04'),
(185, 'Matthew Nelson',     'matthew.nelson@icloud.com',       5, '2024-06-17'),
(186, 'Elizabeth Carter',   'elizabeth.carter@gmail.com',      5, '2022-04-11'),
(187, 'Jackson Mitchell',   'jackson.mitchell@yahoo.com',      5, '2023-01-26'),
(188, 'Sofia Perez',        'sofia.perez@hotmail.com',         5, '2024-10-09'),
(189, 'Sebastian Roberts',  'sebastian.roberts@outlook.com',   5, '2022-07-14'),
(190, 'Avery Turner',       'avery.turner@icloud.com',         5, '2023-08-28'),
(191, 'Jack Phillips',      'jack.phillips@gmail.com',         5, '2024-02-14'),
(192, 'Ella Campbell',      'ella.campbell@yahoo.com',         5, '2022-11-02'),
(193, 'Owen Parker',        'owen.parker@hotmail.com',         5, '2023-04-10'),
(194, 'Scarlett Evans',     'scarlett.evans@outlook.com',      5, '2024-07-23'),
(195, 'Samuel Edwards',     'samuel.edwards@icloud.com',       5, '2022-09-18'),
(196, 'Grace Smith',        'grace.smith@gmail.com',           5, '2023-03-01'),
(197, 'David Johnson',      'david.johnson@yahoo.com',         5, '2024-11-14'),
(198, 'Chloe Williams',     'chloe.williams@hotmail.com',      5, '2022-06-07'),
(199, 'Joseph Brown',       'joseph.brown@outlook.com',        5, '2023-07-20'),
(200, 'Victoria Jones',     'victoria.jones@icloud.com',       5, '2024-01-05');

-- ─── Orders (1500 rows via recursive CTE) ─────────────────────────────────────
-- Dates span 2024-04-23 → 2026-04-22 (730-day window).
-- Amount = product price × quantity × ±10% variation.
-- Status: ~70% completed, ~20% pending, ~10% refunded.

WITH RECURSIVE gen(i) AS (
    SELECT 1
    UNION ALL
    SELECT i + 1 FROM gen WHERE i < 1500
)
INSERT INTO orders (id, customer_id, product_id, quantity, amount, order_date, status)
SELECT
    g.i,
    ((g.i * 37 + 17) % 200) + 1,
    ((g.i * 13 + 7)  % 30)  + 1,
    ((g.i * 3  + 2)  % 5)   + 1,
    ROUND(
        p.price
        * (((g.i * 3 + 2) % 5) + 1)
        * (1.0 + (((g.i * 11 + 3) % 21) - 10) * 0.01),
        2
    ),
    date('2024-04-23', '+' || ((g.i * 17 + 11) % 730) || ' days'),
    CASE ((g.i * 7 + 3) % 10)
        WHEN 0 THEN 'refunded'
        WHEN 1 THEN 'pending'
        WHEN 2 THEN 'pending'
        ELSE 'completed'
    END
FROM gen g
JOIN products p ON p.id = ((g.i * 13 + 7) % 30) + 1;

COMMIT;
