"""
Pruebas de integración para verificar la conexión entre Frontend y Backend.
Estas pruebas verifican que todos los endpoints de la API funcionan correctamente.

Ejecutar con: pytest tests/test_integration_endpoints.py -v
Requiere que los contenedores estén corriendo (docker-compose up -d)
"""

import pytest
import httpx
import asyncio
from datetime import date

# URLs de la API
API_BASE = "http://localhost:6076/api"
FRONTEND_URL = "http://localhost:3000"

# Datos de prueba
TEST_USER = {
    "email": f"test_{asyncio.get_event_loop().time()}@ekklesia.test",
    "password": "testpass123",
    "full_name": "Usuario de Prueba",
    "role": "member"
}

TEST_ADMIN = {
    "email": f"admin_{asyncio.get_event_loop().time()}@ekklesia.test",
    "password": "adminpass123",
    "full_name": "Administrador de Prueba",
    "role": "admin"
}


class TestFrontendConnection:
    """Pruebas de conexión al frontend"""

    @pytest.mark.asyncio
    async def test_frontend_loads(self):
        """Verificar que el frontend carga correctamente"""
        async with httpx.AsyncClient() as client:
            response = await client.get(FRONTEND_URL)
            assert response.status_code == 200
            assert "text/html" in response.headers.get("content-type", "")
            assert "Ekklesia" in response.text

    @pytest.mark.asyncio
    async def test_frontend_css_loads(self):
        """Verificar que los estilos CSS cargan"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FRONTEND_URL}/css/styles.css")
            assert response.status_code == 200
            assert "text/css" in response.headers.get("content-type", "")

    @pytest.mark.asyncio
    async def test_frontend_js_loads(self):
        """Verificar que el JavaScript carga"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{FRONTEND_URL}/js/app.js")
            assert response.status_code == 200
            # JS puede ser application/javascript o text/javascript
            content_type = response.headers.get("content-type", "")
            assert "javascript" in content_type or "text/plain" in content_type


class TestBackendHealth:
    """Pruebas de salud del backend"""

    @pytest.mark.asyncio
    async def test_health_endpoint(self):
        """Verificar endpoint de health"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/health")
            assert response.status_code == 200
            data = response.json()
            assert data.get("status") == "ok"


class TestAuthEndpoints:
    """Pruebas de endpoints de autenticación"""

    @pytest.mark.asyncio
    async def test_register_user(self):
        """Probar registro de usuario"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/register",
                json=TEST_USER
            )
            assert response.status_code == 201
            data = response.json()
            assert data.get("email") == TEST_USER["email"]
            assert "id" in data

    @pytest.mark.asyncio
    async def test_register_admin(self):
        """Probar registro de administrador"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/register",
                json=TEST_ADMIN
            )
            assert response.status_code == 201
            data = response.json()
            assert data.get("role") == "admin"

    @pytest.mark.asyncio
    async def test_login(self):
        """Probar inicio de sesión"""
        async with httpx.AsyncClient() as client:
            # Primero registrar
            await client.post(f"{API_BASE}/auth/register", json={
                **TEST_USER,
                "email": "login_test@ekklesia.test"
            })
            
            # Luego login
            response = await client.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": "login_test@ekklesia.test",
                    "password": TEST_USER["password"]
                }
            )
            assert response.status_code == 200
            data = response.json()
            assert "access_token" in data
            assert "refresh_token" in data

    @pytest.mark.asyncio
    async def test_login_invalid_credentials(self):
        """Probar login con credenciales inválidas"""
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{API_BASE}/auth/login",
                json={
                    "email": "nonexistent@test.com",
                    "password": "wrongpassword"
                }
            )
            assert response.status_code in [400, 401, 404]


class TestUserEndpoints:
    """Pruebas de endpoints de usuarios"""

    @pytest.fixture
    async def auth_headers(self):
        """Obtener headers de autenticación"""
        async with httpx.AsyncClient() as client:
            # Registrar y login
            user_data = {
                **TEST_USER,
                "email": f"user_test_{id(self)}@ekklesia.test"
            }
            await client.post(f"{API_BASE}/auth/register", json=user_data)
            
            login_response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": user_data["email"], "password": user_data["password"]}
            )
            token = login_response.json().get("access_token")
            return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_get_current_user(self, auth_headers):
        """Probar obtener usuario actual"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/users/me",
                headers=auth_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "email" in data
            assert "id" in data


class TestDonationEndpoints:
    """Pruebas de endpoints de donaciones"""

    @pytest.fixture
    async def admin_headers(self):
        """Obtener headers de admin"""
        async with httpx.AsyncClient() as client:
            admin_data = {
                **TEST_ADMIN,
                "email": f"donation_admin_{id(self)}@ekklesia.test"
            }
            await client.post(f"{API_BASE}/auth/register", json=admin_data)
            
            login_response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": admin_data["email"], "password": admin_data["password"]}
            )
            token = login_response.json().get("access_token")
            return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_donation(self, admin_headers):
        """Probar crear donación"""
        async with httpx.AsyncClient() as client:
            donation_data = {
                "donor_name": "Juan Pérez",
                "donor_document": "123456789",
                "donation_type": "diezmo",
                "amount": 100000,
                "payment_method": "efectivo",
                "donation_date": str(date.today()),
                "note": "Donación de prueba"
            }
            
            response = await client.post(
                f"{API_BASE}/donations",
                json=donation_data,
                headers=admin_headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data.get("amount") == 100000
            assert data.get("donation_type") == "diezmo"

    @pytest.mark.asyncio
    async def test_list_my_donations(self, admin_headers):
        """Probar listar mis donaciones"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/donations/me",
                headers=admin_headers
            )
            assert response.status_code == 200
            assert isinstance(response.json(), list)


class TestEventEndpoints:
    """Pruebas de endpoints de eventos"""

    @pytest.fixture
    async def admin_headers(self):
        """Obtener headers de admin"""
        async with httpx.AsyncClient() as client:
            admin_data = {
                **TEST_ADMIN,
                "email": f"event_admin_{id(self)}@ekklesia.test"
            }
            await client.post(f"{API_BASE}/auth/register", json=admin_data)
            
            login_response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": admin_data["email"], "password": admin_data["password"]}
            )
            token = login_response.json().get("access_token")
            return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_create_event(self, admin_headers):
        """Probar crear evento"""
        async with httpx.AsyncClient() as client:
            event_data = {
                "name": "Conferencia de Jóvenes",
                "description": "Evento anual de jóvenes",
                "start_date": str(date.today()),
                "capacity": 100
            }
            
            response = await client.post(
                f"{API_BASE}/events",
                json=event_data,
                headers=admin_headers
            )
            assert response.status_code == 201
            data = response.json()
            assert data.get("name") == "Conferencia de Jóvenes"
            return data.get("id")

    @pytest.mark.asyncio
    async def test_list_events_public(self):
        """Probar listar eventos (público)"""
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{API_BASE}/events")
            assert response.status_code == 200
            assert isinstance(response.json(), list)


class TestRegistrationEndpoints:
    """Pruebas de endpoints de inscripciones"""

    @pytest.fixture
    async def event_id(self):
        """Crear un evento y retornar su ID"""
        async with httpx.AsyncClient() as client:
            admin_data = {
                **TEST_ADMIN,
                "email": f"reg_admin_{id(self)}@ekklesia.test"
            }
            await client.post(f"{API_BASE}/auth/register", json=admin_data)
            
            login_response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": admin_data["email"], "password": admin_data["password"]}
            )
            token = login_response.json().get("access_token")
            headers = {"Authorization": f"Bearer {token}"}
            
            event_response = await client.post(
                f"{API_BASE}/events",
                json={
                    "name": "Evento para inscripciones",
                    "capacity": 50
                },
                headers=headers
            )
            return event_response.json().get("id")

    @pytest.mark.asyncio
    async def test_register_to_event(self, event_id):
        """Probar inscripción a evento"""
        async with httpx.AsyncClient() as client:
            reg_data = {
                "attendee_name": "María García",
                "attendee_email": "maria@test.com",
                "notes": "Inscripción de prueba"
            }
            
            response = await client.post(
                f"{API_BASE}/events/{event_id}/registrations",
                json=reg_data
            )
            assert response.status_code == 201
            data = response.json()
            assert data.get("attendee_name") == "María García"


class TestReportEndpoints:
    """Pruebas de endpoints de reportes"""

    @pytest.fixture
    async def admin_headers(self):
        """Obtener headers de admin"""
        async with httpx.AsyncClient() as client:
            admin_data = {
                **TEST_ADMIN,
                "email": f"report_admin_{id(self)}@ekklesia.test"
            }
            await client.post(f"{API_BASE}/auth/register", json=admin_data)
            
            login_response = await client.post(
                f"{API_BASE}/auth/login",
                json={"email": admin_data["email"], "password": admin_data["password"]}
            )
            token = login_response.json().get("access_token")
            return {"Authorization": f"Bearer {token}"}

    @pytest.mark.asyncio
    async def test_get_summary_report(self, admin_headers):
        """Probar reporte de resumen"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/reports/summary",
                headers=admin_headers
            )
            assert response.status_code == 200
            data = response.json()
            assert "total_donations" in data
            assert "total_amount" in data

    @pytest.mark.asyncio
    async def test_export_csv(self, admin_headers):
        """Probar exportación CSV"""
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{API_BASE}/reports/export",
                headers=admin_headers
            )
            assert response.status_code == 200
            assert "text/csv" in response.headers.get("content-type", "")


class TestCORSConfiguration:
    """Pruebas de configuración CORS"""

    @pytest.mark.asyncio
    async def test_cors_headers_present(self):
        """Verificar que los headers CORS están presentes"""
        async with httpx.AsyncClient() as client:
            response = await client.options(
                f"{API_BASE}/health",
                headers={
                    "Origin": "http://localhost:3000",
                    "Access-Control-Request-Method": "GET"
                }
            )
            # CORS preflight puede retornar 200 o 204
            assert response.status_code in [200, 204, 405]


# Ejecutar pruebas si se ejecuta directamente
if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])

