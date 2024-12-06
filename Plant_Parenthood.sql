
BEGIN TRANSACTION;
CREATE TABLE CUSTOMERS(
    cid INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email TEXT);
INSERT INTO CUSTOMERS VALUES(1,'dylan','dylana');
INSERT INTO CUSTOMERS VALUES(2,'cora','cora@gmail.com');
INSERT INTO CUSTOMERS VALUES(3,'comfort','comfort@gmail.com');
CREATE TABLE PLANTS(
    pid INTEGER PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    quantity INTEGER
    );
INSERT INTO PLANTS VALUES(1,'pothos',5);
INSERT INTO PLANTS VALUES(2,'monstera',4);
CREATE TABLE Orders (
    oid INTEGER PRIMARY KEY,
    cid INTEGER NOT NULL,
    OrderDate TEXT NOT NULL,
    shippingAddress TEXT NOT NULL,
    FOREIGN KEY (cid) REFERENCES CUSTOMERS (cid)
);
INSERT INTO Orders VALUES(1,2,'2024-08-09','100 Chapel Hill Dr, Chapel Hill, NC');
INSERT INTO Orders VALUES(2,1,'2024-08-09','100 Chapel Hill Dr, Chapel Hill, NC');
INSERT INTO Orders VALUES(3,2,'2024-09-09','500 Chapel Hill Dr, Chapel Hill, NC');
INSERT INTO Orders VALUES(4,3,'2024-10-09','700 Chapel Hill Dr, Chapel Hill, NC');
CREATE TABLE STATUS (
    cid INTEGER,
    oid INTEGER,
    status TEXT CHECK (status IN ('success', 'pending')),
    PRIMARY KEY (cid, oid),
    FOREIGN KEY (cid) REFERENCES CUSTOMERS (cid) ON DELETE CASCADE,
    FOREIGN KEY (oid) REFERENCES Orders (oid) ON DELETE CASCADE
);
INSERT INTO STATUS VALUES(1,2,'pending');
INSERT INTO STATUS VALUES(2,3,'pending');
INSERT INTO STATUS VALUES(3,4,'pending');
CREATE TRIGGER UpdateStatusOnInsert
AFTER INSERT ON STATUS
FOR EACH ROW
BEGIN
    -- If plant quantity is sufficient, set status to 'success'
    UPDATE STATUS
    SET status = 'success'
    WHERE cid = NEW.cid
    AND oid = NEW.oid
    AND (SELECT quantity FROM PLANTS WHERE PLANTS.pid = NEW.oid AND PLANTS.quantity > 0) IS NOT NULL;

    -- If plant quantity is insufficient, set status to 'pending'
    UPDATE STATUS
    SET status = 'pending'
    WHERE cid = NEW.cid
    AND oid = NEW.oid
    AND (SELECT quantity FROM PLANTS WHERE PLANTS.pid = NEW.oid AND PLANTS.quantity <= 0) IS NOT NULL;
END
;
CREATE TRIGGER AddToStatusAfterOrderInsert
AFTER INSERT ON Orders
FOR EACH ROW
BEGIN
    INSERT INTO STATUS (cid, oid, status)
    VALUES (NEW.cid, NEW.oid, 'pending');
END;
COMMIT;
