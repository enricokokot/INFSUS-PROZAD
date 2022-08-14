# Information Systems - Project Assignment

## Project description

The application has 2 interfaces: checkout and management.

Anyone who "logs into" the register has access to all items in the warehouse and basic insight into the most recently issued invoices.
Items can be added to the basket and, if there is a sale, they are removed from the stock and information about the purchase and the invoice issued, which imitates the real invoice, is sent to the database.

The manager interface has access to all CRUD operations on items in the following forms: adding new items to inventory, insight into all articles, changes to the details of existing articles (change of name, price, quantity in stock, article category) and ejecting the present items. Also, the manager can review the sales statistics so far and can view and download the invoices in the issued format.

## Functionalities

- CRUD
- sales at the cash register
- statistics in the form of graphs that monitor (1) total turnover per day and (2) comparison of the number of items sold for that day
- simulation of a real invoice

## Quick instructions

Inside the project directory, create an image based on the existing Dockerfile.

```
# docker build --tag pis-projekt:1.0 .
```

Start a Docker container based on the created image.

```
# docker run -p 8080:8080 pis-projekt:1.0
```

Visit the following address in the browser.

```
localhost:8080
```
