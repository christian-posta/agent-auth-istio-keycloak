# Keycloak Setup Guide

This guide will help you set up Keycloak for the Supply Chain Agent application.

## Prerequisites

- Keycloak 26.2.5 running locally
- Access to Keycloak Admin Console

## Step 1: Start Keycloak

### Option A: Docker (Recommended)
```bash
docker run -p 8080:8080 \
  -e KEYCLOAK_ADMIN=admin \
  -e KEYCLOAK_ADMIN_PASSWORD=admin \
  quay.io/keycloak/keycloak:26.2.5 \
  start-dev
```

### Option B: Local Installation
Download and install Keycloak 26.2.5 from the official website.

## Step 2: Access Admin Console

1. Open your browser and go to: `http://localhost:8080`
2. Click on "Administration Console"
3. Login with:
   - **Username**: `admin`
   - **Password**: `admin`

## Step 3: Create Realm

1. In the Admin Console, click on the dropdown in the top-left corner
2. Click "Create Realm"
3. Enter:
   - **Realm name**: `mcp-realm`
   - **Enabled**: ✓ (checked)
4. Click "Create"

## Step 4: Create OAuth Client

1. In the left sidebar, click "Clients"
2. Click "Create"
3. Fill in the form:
   - **Client ID**: `supply-chain-ui`
   - **Client Protocol**: `openid-connect`
   - **Root URL**: `http://localhost:3000`
4. Click "Save"

### Configure Client Settings

1. In the client settings, configure:
   - **Access Type**: `public`
   - **Valid Redirect URIs**: 
     - `http://localhost:3000/*`
     - `http://localhost:3000/auth/callback`
   - **Web Origins**: `http://localhost:3000`
   - **Advanced** → **Proof Key for Code Exchange Code Challenge Method**: `S256`

2. Click "Save"

## Step 5: Create User Roles

1. In the left sidebar, click "Roles"
2. Click "Add Role"
3. Create these roles:
   - **Role Name**: `supply-chain-user`
   - **Role Name**: `supply-chain-admin`
   - **Role Name**: `it-administrator`

## Step 6: Create Test User

1. In the left sidebar, click "Users"
2. Click "Add user"
3. Fill in:
   - **Username**: `christian`
   - **Email**: `christian.martinez@acmecorp.com`
   - **First Name**: `Christian`
   - **Last Name**: `Martinez`
   - **Email Verified**: ✓ (checked)
4. Click "Save"

### Set User Password

1. Click on the "Credentials" tab
2. Set:
   - **New Password**: `password123`
   - **Temporary**: ✓ (checked)
3. Click "Set Password"

### Assign Roles

1. Click on the "Role Mappings" tab
2. In "Realm Roles", select:
   - `supply-chain-user`
   - `it-administrator`
3. Click "Assign"

## Step 7: Test Configuration

1. **Start the Backend**:
   ```bash
   cd backend
   source ../.venv/bin/activate
   python run.py
   ```

2. **Start the Frontend**:
   ```bash
   cd supply-chain-ui
   npm start
   ```

3. **Test Login**:
   - Open http://localhost:3000
   - Click "Sign in with Keycloak"
   - Login with `christian` / `password123`

## Troubleshooting

### Common Issues

1. **CORS Errors**:
   - Ensure Web Origins includes `http://localhost:3000`
   - Check that Valid Redirect URIs are correct

2. **Token Validation Fails**:
   - Verify the realm name matches exactly: `mcp-realm`
   - Check that the client ID matches: `supply-chain-ui`

3. **User Not Found**:
   - Ensure user is created in the correct realm
   - Check that user is enabled and email verified

4. **Backend Can't Connect to Keycloak**:
   - Verify Keycloak is running on port 8080
   - Check that the realm is accessible

### Debug Information

- **Frontend Console**: Check browser console for Keycloak initialization logs
- **Backend Logs**: Check terminal where backend is running
- **Keycloak Logs**: Check Keycloak server logs for authentication issues

## Environment Variables

The application uses these environment variables (with defaults):

```bash
# Frontend (.env file)
REACT_APP_KEYCLOAK_URL=http://localhost:8080
REACT_APP_KEYCLOAK_REALM=mcp-realm
REACT_APP_KEYCLOAK_CLIENT_ID=supply-chain-ui
REACT_APP_API_BASE_URL=http://localhost:8000

# Backend (config.py)
keycloak_url=http://localhost:8080
keycloak_realm=mcp-realm
keycloak_client_id=supply-chain-ui
```

## Security Notes

- **Development Only**: This setup is for development purposes
- **Production**: Use HTTPS, secure passwords, and proper security configurations
- **Admin Access**: Limit admin console access in production environments
- **User Management**: Implement proper user provisioning workflows for production

## Next Steps

After successful setup:

1. **Test Authentication Flow**: Verify login/logout works
2. **Test API Calls**: Ensure backend can validate tokens
3. **Test Optimization**: Run the supply chain optimization workflow
4. **Customize Roles**: Add more specific roles for your use case
5. **User Management**: Set up additional users and role assignments
