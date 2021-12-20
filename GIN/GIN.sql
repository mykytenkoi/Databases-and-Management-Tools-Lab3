
\timing on

DROP TABLE IF EXISTS "test_gin";
CREATE TABLE "test_gin"(
	"id" bigserial PRIMARY KEY,
	"test_text" tsvector
);

INSERT INTO "test_gin"("test_text")
SELECT
	substr(characters, (random() * length(characters) + 1)::integer, 10)::tsvector
FROM
	(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters), generate_series(1, 1000000) as q;

SELECT COUNT(*) FROM "test_gin" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_gin" WHERE "id" % 2 = 0 OR "test_text"::text LIKE 'b%';
SELECT COUNT(*), SUM("id") FROM "test_gin" WHERE "test_text"::text LIKE 'b%' GROUP BY "id" % 2;

DROP INDEX IF EXISTS "test_gin_test_text_index";
CREATE INDEX "test_gin_test_text_index" ON "test_gin" USING gin ("test_text");

SELECT COUNT(*) FROM "test_gin" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_gin" WHERE "id" % 2 = 0 OR "test_text"::text LIKE 'b%';
SELECT COUNT(*), SUM("id") FROM "test_gin" WHERE "test_text"::text LIKE 'b%' GROUP BY "id" % 2;

--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "test_hash";
CREATE TABLE "test_hash"(
	"id" bigserial PRIMARY KEY,
	"test_time" timestamp
);

INSERT INTO "test_hash"("test_time")
SELECT
	(timestamp '2021-01-01' + random() * (timestamp '2020-01-01' - timestamp '2022-01-01'))
FROM
	(VALUES('qwertyuiopasdfghjklzxcvbnmQWERTYUIOPASDFGHJKLZXCVBNM')) as symbols(characters), generate_series(1, 1000000) as q;


SELECT COUNT(*) FROM "test_hash" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_hash" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505';
SELECT COUNT(*), SUM("id") FROM "test_hash" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505' GROUP BY "id" % 2;

DROP INDEX IF EXISTS "test_hash_test_time_index";
CREATE INDEX "test_hash_test_time_index" ON "test_hash" USING hash ("test_time");

SELECT COUNT(*) FROM "test_hash" WHERE "id" % 2 = 0;
SELECT COUNT(*) FROM "test_hash" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505';
SELECT COUNT(*), SUM("id") FROM "test_hash" WHERE "test_time" >= '20200505' AND "test_time" <= '20210505' GROUP BY "id" % 2;

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "reader";
CREATE TABLE "reader"(
	"readerID" bigserial PRIMARY KEY,
	"readerName" varchar(255)
);


DROP TABLE IF EXISTS "readerLog";
CREATE TABLE "readerLog"(
	"id" bigserial PRIMARY KEY,
	"readerLogID" bigint,
	"readerLogName" varchar(255)
);

--------------------------------------------------------------------------------------------------------------------------------

-- https://stackoverflow.com/questions/56544430/trigger-before-delete-doesnt-delete-data-in-table

CREATE OR REPLACE FUNCTION update_insert_func() RETURNS TRIGGER as $$

DECLARE
	CURSOR_LOG CURSOR FOR SELECT * FROM "readerLog";
	row_Log "readerLog"%ROWTYPE;

begin
	IF NEW."readerID" % 2 = 0 THEN
		INSERT INTO "readerLog"("readerLogID", "readerLogName") VALUES (new."readerID", new."readerName");
		UPDATE "readerLog" SET "readerLogName" = trim(BOTH 'x' FROM "readerLogName");
		RETURN NEW;
	ELSE 
		RAISE NOTICE 'readerID is odd';
		FOR row_log IN cursor_log LOOP
			UPDATE "readerLog" SET "readerLogName" = 'y' || row_Log."readerLogName" || 'y' WHERE "id" = row_log."id";
		END LOOP;
		RETURN NEW;
	END IF; 
END;

$$ LANGUAGE plpgsql;

CREATE TRIGGER "test_trigger"
AFTER UPDATE OR INSERT ON "reader"
FOR EACH ROW
EXECUTE procedure update_insert_func();

--------------------------------------------------------------------------------------------------------------------------------

INSERT INTO "reader"("readerName")
VALUES ('reader1'), ('reader2'), ('reader3'), ('reader4'), ('reader5');

SELECT * FROM "reader";
SELECT * FROM "readerLog";

UPDATE "reader" SET "readerName" = "readerName" || 'Lx' WHERE "readerID" = 5;
UPDATE "reader" SET "readerName" = "readerName" || 'Lx' WHERE "readerID" = 4;
# DELETE FROM "reader" WHERE "readerID" = 3;

--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------
--------------------------------------------------------------------------------------------------------------------------------

DROP TABLE IF EXISTS "task4";
CREATE TABLE "task4"(
	"id" bigserial PRIMARY KEY,
	"num" bigint,
	"char" varchar(255)
);

INSERT INTO "task4"("num", "char") VALUES (100, 'ABC'), (200, 'BCA'), (300, 'CAB');

SELECT * FROM "task4";

--------------------------------------------------------------------------------------------------------------------------------
-- -- READ UNCOMMITTED UNSUPPORTED
-- -- T1
-- START TRANSACTION;
-- SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED READ WRITE;
	
-- UPDATE "task4" SET "num" = "num" + 1;

-- COMMIT;
-- ROLLBACK;
-- -- /T1

-- -- T2
-- START TRANSACTION;
-- SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED READ WRITE;

-- SELECT * FROM "task4";

-- COMMIT;
-- -- /T2

--------------------------------------------------------------------------------------------------------------------------------
-- READ COMMITTED
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL READ COMMITTED READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2

--------------------------------------------------------------------------------------------------------------------------------
-- REPEATABLE READ
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL REPEATABLE READ READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2

--------------------------------------------------------------------------------------------------------------------------------
-- SERIALIZABLE
-- T1
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ WRITE;
	
UPDATE "task4" SET "num" = "num" + 1;

COMMIT;
-- /T1

-- T2
START TRANSACTION;
SET TRANSACTION ISOLATION LEVEL SERIALIZABLE READ WRITE;

SELECT * FROM "task4";

UPDATE "task4" SET "num" = "num" + 4;

COMMIT;
-- /T2


