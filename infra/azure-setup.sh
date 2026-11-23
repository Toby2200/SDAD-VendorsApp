#!/usr/bin/env bash

# ---------- 0. Variables (change LOCATION to a region from YOUR allowed list) ----------
PREFIX=abefeler-ieu2024
RG=rg-$PREFIX
LOCATION=germanywestcentral              # one region from MY allowed list (step 1), used for everything
STORAGE=abefelerieu2024ui                # storage account for the UI (letters and digits only)
SQL_SERVER=$PREFIX-sql
SQL_ADMIN_USER=vendorsadmin
ENV_NAME=$PREFIX-env
CATALOG_APP=$PREFIX-catalog
SALES_APP=$PREFIX-sales
CATALOG_DB=$PREFIX-catalog-db
SALES_DB=$PREFIX-sales-db
IDENTITY=$PREFIX-github
GH_REPO=Toby2200/SDAD-VendorsApp

gh auth login

# ---------- 1. Subscription and allowed regions ----------
az account set --subscription "Azure for Students"
az policy assignment list --query "[].{name:displayName, regions:parameters.listOfAllowedLocations.value}" --output json

# ---------- 2. Providers and resource group ----------
for p in Microsoft.App Microsoft.OperationalInsights Microsoft.Sql Microsoft.Storage Microsoft.ManagedIdentity; do
  az provider register --namespace "$p"
done
az group create --name "$RG" --location "$LOCATION"

# ---------- 3. The UI: Storage static website ----------
az storage account create --name "$STORAGE" --resource-group "$RG" --location "$LOCATION" \
  --sku Standard_LRS --kind StorageV2
az storage account update --name "$STORAGE" --resource-group "$RG" --min-tls-version TLS1_2
az storage blob service-properties update --account-name "$STORAGE" \
  --static-website --index-document index.html
UI_ORIGIN=$(az storage account show --name "$STORAGE" --resource-group "$RG" --query primaryEndpoints.web -o tsv)
UI_ORIGIN=${UI_ORIGIN%/}                  # the services' CORS origin: no trailing slash
echo "UI public URL: $UI_ORIGIN"

# ---------- 4. SQL server, two serverless databases (free offer), one contained user each ----------
SQL_ADMIN_PASSWORD="Adm-$(openssl rand -hex 16)"
CATALOG_DB_PASSWORD="Cat-$(openssl rand -hex 16)"
SALES_DB_PASSWORD="Sal-$(openssl rand -hex 16)"

az sql server create --name "$SQL_SERVER" --resource-group "$RG" --location "$LOCATION" \
  --admin-user "$SQL_ADMIN_USER" --admin-password "$SQL_ADMIN_PASSWORD" --minimal-tls-version 1.2
az sql server firewall-rule create --resource-group "$RG" --server "$SQL_SERVER" \
  --name AllowAzureServices --start-ip-address 0.0.0.0 --end-ip-address 0.0.0.0

for DB in "$CATALOG_DB" "$SALES_DB"; do
  az sql db create --resource-group "$RG" --server "$SQL_SERVER" --name "$DB" \
    --edition GeneralPurpose --compute-model Serverless --family Gen5 \
    --capacity 1 --min-capacity 0.5 --backup-storage-redundancy Local \
    --use-free-limit true --free-limit-exhaustion-behavior AutoPause
done

# Cloud Shell does not include sqlcmd: install Microsoft's go-sqlcmd in ~/bin
mkdir -p ~/bin && (cd ~/bin && gh release download --repo microsoft/go-sqlcmd \
  --pattern 'sqlcmd-linux-amd64.tar.bz2' --clobber && tar -xjf sqlcmd-linux-amd64.tar.bz2)
export PATH="$HOME/bin:$PATH"

# Open the firewall to this Cloud Shell only while creating the users, then close it
MY_IP=$(curl -s https://api.ipify.org)
az sql server firewall-rule create --resource-group "$RG" --server "$SQL_SERVER" \
  --name TempSetup --start-ip-address "$MY_IP" --end-ip-address "$MY_IP"

# Contained users: they exist only inside their own database (not db_owner)
create_user() {  # database, user, password
  SQLCMDPASSWORD="$SQL_ADMIN_PASSWORD" sqlcmd -S "$SQL_SERVER.database.windows.net" \
    -d "$1" -U "$SQL_ADMIN_USER" -b -Q "
    IF NOT EXISTS (SELECT 1 FROM sys.database_principals WHERE name = '$2')
      CREATE USER [$2] WITH PASSWORD = '$3';
    ALTER ROLE db_ddladmin ADD MEMBER [$2];
    ALTER ROLE db_datareader ADD MEMBER [$2];
    ALTER ROLE db_datawriter ADD MEMBER [$2];"
}
create_user "$CATALOG_DB" catalog_user "$CATALOG_DB_PASSWORD"
create_user "$SALES_DB" sales_user "$SALES_DB_PASSWORD"

# Isolation check: catalog_user must NOT be able to open the sales database (Login failed 18456)
SQLCMDPASSWORD="$CATALOG_DB_PASSWORD" sqlcmd -S "$SQL_SERVER.database.windows.net" -d "$SALES_DB" \
  -U catalog_user -Q "SELECT DB_NAME()" || echo "OK: catalog_user cannot open $SALES_DB"

az sql server firewall-rule delete --resource-group "$RG" --server "$SQL_SERVER" --name TempSetup

# Keep the database passwords only as GitHub secrets
gh secret set CATALOG_DB_PASSWORD --body "$CATALOG_DB_PASSWORD" --repo "$GH_REPO"
gh secret set SALES_DB_PASSWORD --body "$SALES_DB_PASSWORD" --repo "$GH_REPO"

# ---------- 5. Container Apps environment and one Container App per service ----------
TOKEN_SECRET=$(openssl rand -hex 32)
gh secret set TOKEN_SECRET --body "$TOKEN_SECRET" --repo "$GH_REPO"

az containerapp env create --name "$ENV_NAME" --resource-group "$RG" --location "$LOCATION"

az containerapp create --name "$CATALOG_APP" --resource-group "$RG" --environment "$ENV_NAME" \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --ingress external --target-port 8000 --min-replicas 0 --max-replicas 1 --cpu 0.25 --memory 0.5Gi \
  --secrets "database-url=mssql://catalog_user:$CATALOG_DB_PASSWORD@$SQL_SERVER.database.windows.net:1433/$CATALOG_DB" \
            "token-secret=$TOKEN_SECRET" \
  --env-vars DATABASE_URL=secretref:database-url TOKEN_SECRET=secretref:token-secret \
             ALLOWED_ORIGIN="$UI_ORIGIN" PORT=8000 DB_CONNECT_RETRIES=10 DB_RETRY_DELAY_S=3

CATALOG_URL="https://$(az containerapp show --name "$CATALOG_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv)"

az containerapp create --name "$SALES_APP" --resource-group "$RG" --environment "$ENV_NAME" \
  --image mcr.microsoft.com/k8se/quickstart:latest \
  --ingress external --target-port 8000 --min-replicas 0 --max-replicas 1 --cpu 0.25 --memory 0.5Gi \
  --secrets "database-url=mssql://sales_user:$SALES_DB_PASSWORD@$SQL_SERVER.database.windows.net:1433/$SALES_DB" \
            "token-secret=$TOKEN_SECRET" \
  --env-vars DATABASE_URL=secretref:database-url TOKEN_SECRET=secretref:token-secret \
             ALLOWED_ORIGIN="$UI_ORIGIN" PORT=8000 CATALOG_URL="$CATALOG_URL" CATALOG_TIMEOUT_S=10 \
             DB_CONNECT_RETRIES=10 DB_RETRY_DELAY_S=3

SALES_URL="https://$(az containerapp show --name "$SALES_APP" --resource-group "$RG" --query properties.configuration.ingress.fqdn -o tsv)"
echo "catalog: $CATALOG_URL"
echo "sales:   $SALES_URL"

# ---------- 6. The pipeline's identity (managed identity + OIDC, no stored credentials) ----------
az identity create --name "$IDENTITY" --resource-group "$RG" --location "$LOCATION"
CLIENT_ID=$(az identity show --name "$IDENTITY" --resource-group "$RG" --query clientId -o tsv)
PRINCIPAL_ID=$(az identity show --name "$IDENTITY" --resource-group "$RG" --query principalId -o tsv)
RG_ID=$(az group show --name "$RG" --query id -o tsv)
STORAGE_ID=$(az storage account show --name "$STORAGE" --resource-group "$RG" --query id -o tsv)

# Least privilege: Contributor only on this resource group, plus upload rights on the UI storage
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal \
  --role Contributor --scope "$RG_ID"
az role assignment create --assignee-object-id "$PRINCIPAL_ID" --assignee-principal-type ServicePrincipal \
  --role "Storage Blob Data Contributor" --scope "$STORAGE_ID"

# GitHub may send the subject with names or with numeric IDs: register both
OWNER_ID=$(gh api "repos/$GH_REPO" --jq .owner.id)
REPO_ID=$(gh api "repos/$GH_REPO" --jq .id)
az identity federated-credential create --name github-main --identity-name "$IDENTITY" --resource-group "$RG" \
  --issuer https://token.actions.githubusercontent.com --audiences api://AzureADTokenExchange \
  --subject "repo:${GH_REPO}:ref:refs/heads/main"
az identity federated-credential create --name github-main-ids --identity-name "$IDENTITY" --resource-group "$RG" \
  --issuer https://token.actions.githubusercontent.com --audiences api://AzureADTokenExchange \
  --subject "repo:Toby2200@${OWNER_ID}/SDAD-VendorsApp@${REPO_ID}:ref:refs/heads/main"

# ---------- 7. GitHub secrets and variables ----------
gh secret set AZURE_CLIENT_ID --body "$CLIENT_ID" --repo "$GH_REPO"
gh secret set AZURE_TENANT_ID --body "$(az account show --query tenantId -o tsv)" --repo "$GH_REPO"
gh secret set AZURE_SUBSCRIPTION_ID --body "$(az account show --query id -o tsv)" --repo "$GH_REPO"
gh variable set PREFIX --body "$PREFIX" --repo "$GH_REPO"
gh variable set RESOURCE_GROUP --body "$RG" --repo "$GH_REPO"
gh variable set UI_STORAGE --body "$STORAGE" --repo "$GH_REPO"
gh variable set CATALOG_URL --body "$CATALOG_URL" --repo "$GH_REPO"
gh variable set SALES_URL --body "$SALES_URL" --repo "$GH_REPO"

# ---------- 9. Read access for the professors ----------
for PROF in amartini@faculty.ie.edu bserra@faculty.ie.edu; do
  az role assignment create --assignee "$PROF" --role Reader --scope "$RG_ID"
done

# ---------- Check ----------
az resource list --resource-group "$RG" --output table
gh secret list --repo "$GH_REPO"
gh variable list --repo "$GH_REPO"

# Finally, sign GitHub out of Cloud Shell
gh auth logout