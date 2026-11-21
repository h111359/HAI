# Shipping report policy

For this report, each order has a nonnegative subtotal and status paid or pending.
Shipping is 0.00 only when the status is paid and subtotal is at least100.00.
All other orders have shipping5.00. Grand total equals subtotal plus shipping.
Amounts are decimal currency values rounded to two decimal places.
The report must preserve order IDs and include one row for each supplied order.

## Supplied orders

- ORD-101: subtotal120.00, paid.
- ORD-102: subtotal80.00, paid.
- ORD-103: subtotal150.00, pending.
- ORD-104: subtotal50.00, paid.
