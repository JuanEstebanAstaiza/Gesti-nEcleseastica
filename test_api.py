#!/usr/bin/env python3
"""Script de pruebas para verificar que todos los endpoints funcionan"""

import httpx
import json
import sys

API_BASE = "http://localhost:6076/api"

results = {
    "passed": [],
    "failed": []
}

def test(name: str, method: str, endpoint: str, expected_status: int = 200, 
         json_data: dict = None, headers: dict = None, check_response: bool = True):
    """Ejecuta un test y registra el resultado"""
    url = f"{API_BASE}{endpoint}"
    try:
        if method == "GET":
            r = httpx.get(url, headers=headers, timeout=10)
        elif method == "POST":
            r = httpx.post(url, json=json_data, headers=headers, timeout=10)
        elif method == "PATCH":
            r = httpx.patch(url, json=json_data, headers=headers, timeout=10)
        elif method == "DELETE":
            r = httpx.delete(url, headers=headers, timeout=10)
        else:
            raise ValueError(f"Método no soportado: {method}")
        
        if r.status_code == expected_status:
            results["passed"].append(f"✅ {name}: {method} {endpoint} -> {r.status_code}")
            if check_response and r.status_code == 200:
                try:
                    data = r.json()
                    if isinstance(data, dict):
                        return data
                    return {"data": data}
                except:
                    pass
            return {"status": r.status_code}
        else:
            error_msg = r.text[:200] if len(r.text) > 200 else r.text
            results["failed"].append(f"❌ {name}: {method} {endpoint} -> {r.status_code} (esperaba {expected_status})\n   {error_msg}")
            return None
    except Exception as e:
        results["failed"].append(f"❌ {name}: {method} {endpoint} -> ERROR: {str(e)}")
        return None


def run_tests():
    print("=" * 60)
    print("🧪 PRUEBAS DE API - Sistema de Gestión Eclesiástica")
    print("=" * 60)
    
    # ========== ENDPOINTS PÚBLICOS ==========
    print("\n📌 ENDPOINTS PÚBLICOS (sin autenticación)")
    print("-" * 40)
    
    test("Configuración de iglesia", "GET", "/public/config")
    test("Eventos públicos", "GET", "/public/events?limit=5")
    test("Anuncios públicos", "GET", "/public/announcements?limit=5")
    test("Info de donaciones", "GET", "/public/donation-info")
    test("Transmisiones en vivo", "GET", "/public/streams")
    
    # ========== AUTENTICACIÓN ==========
    print("\n📌 AUTENTICACIÓN")
    print("-" * 40)
    
    # Login Admin
    admin_login = test("Login Admin", "POST", "/auth/login", 
                       json_data={"email": "admin@comunidadfe.org", "password": "admin123"})
    admin_token = admin_login.get("access_token") if admin_login else None
    admin_headers = {"Authorization": f"Bearer {admin_token}"} if admin_token else None
    
    # Login Member
    member_login = test("Login Miembro", "POST", "/auth/login",
                        json_data={"email": "juan.perez@email.com", "password": "member123"})
    member_token = member_login.get("access_token") if member_login else None
    member_headers = {"Authorization": f"Bearer {member_token}"} if member_token else None
    
    # Login Superadmin
    super_login = test("Login Superadmin", "POST", "/superadmin/auth/login",
                       json_data={"email": "super@ekklesia.com", "password": "superadmin123"})
    super_token = super_login.get("access_token") if super_login else None
    super_headers = {"Authorization": f"Bearer {super_token}"} if super_token else None
    
    # ========== PERFIL DE USUARIO ==========
    print("\n📌 PERFIL DE USUARIO")
    print("-" * 40)
    
    if admin_headers:
        test("Perfil Admin", "GET", "/auth/me", headers=admin_headers)
    
    if member_headers:
        test("Perfil Miembro", "GET", "/auth/me", headers=member_headers)
    
    # ========== EVENTOS (Admin) ==========
    print("\n📌 EVENTOS (Admin)")
    print("-" * 40)
    
    if admin_headers:
        test("Listar eventos", "GET", "/events", headers=admin_headers)
    
    # ========== DONACIONES (Admin) ==========
    print("\n📌 DONACIONES (Admin)")
    print("-" * 40)
    
    if admin_headers:
        test("Listar donaciones", "GET", "/donations", headers=admin_headers)
    
    # ========== MIS DONACIONES (Member) ==========
    print("\n📌 DONACIONES DEL MIEMBRO")
    print("-" * 40)
    
    if member_headers:
        test("Mis donaciones", "GET", "/donations/me", headers=member_headers)
    
    # ========== SUPERADMIN ==========
    print("\n📌 SUPERADMIN")
    print("-" * 40)
    
    if super_headers:
        test("Listar tenants", "GET", "/superadmin/tenants", headers=super_headers)
        test("Listar planes", "GET", "/superadmin/plans", headers=super_headers)
        test("Estadísticas", "GET", "/superadmin/stats", headers=super_headers)
        test("Listar backups", "GET", "/superadmin/backups", headers=super_headers)
        test("Métricas de ingresos", "GET", "/superadmin/revenue", headers=super_headers)
    
    # ========== RESUMEN ==========
    print("\n" + "=" * 60)
    print("📊 RESUMEN DE PRUEBAS")
    print("=" * 60)
    
    print(f"\n✅ PASARON: {len(results['passed'])}")
    for p in results["passed"]:
        print(f"   {p}")
    
    if results["failed"]:
        print(f"\n❌ FALLARON: {len(results['failed'])}")
        for f in results["failed"]:
            print(f"   {f}")
    
    total = len(results["passed"]) + len(results["failed"])
    success_rate = (len(results["passed"]) / total * 100) if total > 0 else 0
    print(f"\n📈 Tasa de éxito: {success_rate:.1f}%")
    
    return len(results["failed"]) == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)

