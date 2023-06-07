### Script to collect SQL query from config file

Json file example:
```json
{
    "Clients": {
        "schema": "clients",
        "alias": "C",
        "pk": "ClientId",
        "fk": {},
        "columns": [
            "ClientId",
            "FirstName",
            "MiddleName",
            "LastName",
            "Email",
            "CreatedAt"
        ],
        "filter": []
    },
    "BillingContracts": {
        "schema": "billing",
        "alias": "B",
        "pk": "ContractId",
        "fk": {
            "Clients": "ClientId"
        },
        "columns": [
            "ContractId",
            "PayDay",
            "OfferId",
            "Discount",
            "BalanceAmount",
            "CreatedAt"
        ],
        "filter": {
            "column": "CreatedAt",
            "type": "BETWEEN"
        }
    }
}
```


The result:
```sql
SELECT
    C."ClientId",
    C."FirstName",
    C."MiddleName",
    C."LastName",
    C."Email",
    C."CreatedAt",
    B."ContractId",
    B."PayDay",
    B."OfferId",
    B."Discount",
    B."BalanceAmount",
    B."CreatedAt"
FROM clients."Clients" AS C
INNER JOIN billing."BillingContracts" AS B ON B.ContractId = C.ClientId
WHERE B."CreatedAt" BETWEEN '{start}' AND '{end}'
```