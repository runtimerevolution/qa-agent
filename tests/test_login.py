import pytest
from playwright.sync_api import Page

def test_login_valid_credentials(page: Page):
    """TC-001 — Login with valid credentials"""
    page.goto("https://your-app.com/login")
    page.fill("#email", "user@example.com")
    page.fill("#password", "password123")
    page.click("button[type=submit]")
    assert page.url == "https://your-app.com/dashboard"

def test_login_invalid_credentials(page: Page):
    """TC-002 — Login with invalid credentials"""
    page.goto("https://your-app.com/login")
    page.fill("#email", "invalid@example.com")
    page.fill("#password", "wrongpassword")
    page.click("button[type=submit]")
    assert page.locator(".error-message").is_visible()