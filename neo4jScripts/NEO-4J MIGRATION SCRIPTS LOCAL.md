# NEO-4J MIGRATION SCRIPTS 
## _Migrating exported CSV files from northwind MySQL Database_

[![N|Solid](https://cldup.com/dTxpPi9lDf.thumb.png)](https://nodesource.com/products/nsolid)

[![Build Status](https://travis-ci.org/joemccann/dillinger.svg?branch=master)](https://travis-ci.org/joemccann/dillinger)


## SCRIPT-1 MIGRATING PRODUCT TABLE: 
```sh
CALL apoc.load.json("file:///products.json") YIELD value AS row
CREATE (p:Product)
SET p = row,
    p.ProductID = toInteger(row.ProductID),
    p.ProductName = row.ProductName,
    p.SupplierID = toInteger(row.SupplierID),
    p.CategoryID = toInteger(row.CategoryID),
    p.QuantityPerUnit = row.QuantityPerUnit,
    p.UnitPrice = toFloat(row.UnitPrice),
    p.UnitsInStock = toInteger(row.UnitsInStock),
    p.UnitsOnOrder = toInteger(row.UnitsOnOrder),
    p.ReorderLevel = toInteger(row.ReorderLevel),
    p.Discontinued = (row.Discontinued <> "0"),
    p.ProductImageUrl = row.ProductImageUrl,
    p.ProductDescription = row.ProductDescription,
    p.ProductMetaInfo = row.ProductMetaInfo;
```

## SCRIPT-2 MIGRATING CATEGORIES TABLE:
```sh
CALL apoc.load.json("file:///categories.json") YIELD value AS row
CREATE (c:Category)
SET c.CategoryID = row.CategoryID,
    c.CategoryName = row.CategoryName,
    c.Description = row.Description
```

## SCRIPT-3 CREATING INDEXES ON PRODUCT/CATEGORIES:
```sh
CREATE INDEX FOR (p:Product) ON (p.productID);
```
```sh
CREATE INDEX FOR (c:Category) ON (c.categoryID);
```

## SCRIPT-4 CREATING RELATIONSHIPS ON PRODUCT/CATEGORIES:
```sh
MATCH (p:Product),(c:Category)
WHERE p.CategoryID = c.CategoryID
CREATE (p)-[:PART_OF]-> ( c );
```

## SCRIPT-5 UPLOADING EMBEDDINGS

### Embedding for Local
```sh
LOAD CSV WITH HEADERS FROM 'https://drive.usercontent.google.com/download?id=1rce1699bmAAEUK_4DtSnqvhB_eWVGl_4&export=download' AS row
MATCH (p:Product {ProductName: row.ProductName})
CALL db.create.setNodeVectorProperty(p, 'mxbai-embeddings', apoc.convert.fromJsonList(row.`mxbai-embeddings`))
RETURN count(*)
```

### Embedding with OPEN AI
```sh
CALL apoc.load.json("https://drive.usercontent.google.com/download?id=1n6uX-W-lKS1e_Dd7kEmW65wOSUXSs8XE&export=download") YIELD value AS row
MATCH (p:Product {ProductName: row.ProductName})
CALL db.create.setNodeVectorProperty(p, 'text-embedding-3-small', row.`text-embedding-3-small`)
RETURN count(*)
```

## SCRIPT-6 CREATING INDEX
```sh
CREATE VECTOR INDEX productsMetaIndex IF NOT EXISTS
FOR (p:Product)
ON p.`mxbai-embeddings`
OPTIONS {indexConfig: {
 `vector.dimensions`: 1024,
 `vector.similarity_function`: 'cosine'
}}
```
```sh
CREATE VECTOR INDEX productsMetaIndex2 IF NOT EXISTS
FOR (p:Product)
ON p.`text-embedding-3-small`
OPTIONS {indexConfig: {
 `vector.dimensions`: 1536,
 `vector.similarity_function`: 'cosine'
}}
```

## SCRIPT-7 EXAMPLE SYNTAX TO QUERY NEWLY CREATED INDEX
```sh
MATCH (p:Product {ProductName: 'Chai'})
CALL db.index.vector.queryNodes('productsMetaIndex', 2, p.`mxbai-embeddings`)
YIELD node, score
RETURN node.ProductName AS ProductName, node.ProductID AS ProductID, score
```


## SCRIPT-8 UPLOADING IMAGE EMBEDDINGS

```sh
LOAD CSV WITH HEADERS FROM 'https://drive.usercontent.google.com/download?id=16UT77RrEyKEPd72dKhId9o4YM7p50gdI&export=download' AS row
MATCH (p:Product {ProductName: row.ProductName})
CALL db.create.setNodeVectorProperty(p, 'st-image-openai-embeddings', apoc.convert.fromJsonList(row.`ImageOpenaiClipEmbeddings`))
RETURN count(*)
```sh

## SCRIPT-9 CREATING IMAGE INDEX
```sh
CREATE VECTOR INDEX productsSTImageIndex IF NOT EXISTS
FOR (p:Product)
ON p.`st-image-openai-embeddings`
OPTIONS {indexConfig: {
 `vector.dimensions`: 512,
 `vector.similarity_function`: 'cosine'
}}
```

## SCRIPT-10 CHECK TO VERIFY INDEX HAS CREATED SUCESSFULLY
```sh
SHOW INDEXES  YIELD id, name, type, state, populationPercent WHERE type = "VECTOR"
```