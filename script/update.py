import os
from playwright.sync_api import sync_playwright
import requests
import json

EMAIL = os.environ["NATIXIS_EMAIL"]
PASSWORD = os.environ["NATIXIS_PASSWORD"]

with sync_playwright() as p:
    browser = p.chromium.launch(
        headless=True
    )

    page = browser.new_page()

    page.goto(
        "https://www.egepargne.com",
        wait_until="networkidle"
    )

    print("Current URL:", page.url)

    # A compléter après inspection réelle du HTML
    # page.locator(...).fill(EMAIL)
    page.wait_for_selector("#login-form-input", timeout=20000)
    page.click("#login-form-input")
    page.type("#login-form-input", EMAIL, delay=50)
    page.locator("#login-form-input").press("Tab")

    page.wait_for_timeout(3000)

    page.screenshot(path="before_confirm.png")

    submit_button = page.locator('button[type="submit"]')

    print(
        "Disabled avant attente :",
        submit_button.is_disabled()
    )

    page.wait_for_timeout(5000)

    print(
        "Disabled après attente :",
        submit_button.is_disabled()
    )

    submit_button.wait_for(state="visible", timeout=20000)

    page.wait_for_timeout(3000)
    
    def log_response(response):
        if response.status >= 400:
            print(f"ERROR {response.status} {response.url}")

    page.on("response", log_response)
    def log_request(req):
        if "authenticationModes/search" in req.url:
            print("=== POST DATA ===")
            print(req.post_data)

    page.on("request", log_request)
    submit_button.click()
    def log_response(resp):
        if "authenticationModes/search" in resp.url:
            print("=== RESPONSE STATUS ===")
            print(resp.status)

            try:
                print("=== RESPONSE BODY ===")
                print(resp.text())
            except Exception as e:
                print("ERROR:", e)

    page.on("response", log_response)
    page.wait_for_timeout(10000)
    page.screenshot(path="after_confirm.png")

    for digit in PASSWORD:
        page.locator("button").filter(
            has_text=digit
        ).first.click()
        
    submit = page.locator('button[type="submit"]')

    print("Nombre de boutons submit :", submit.count())

    submit.click()

    page.screenshot(
        path="before_next.png",
        full_page=True
        )

    page.wait_for_timeout(5000)

    print("URL after login:", page.url)

    page.screenshot(
        path="after_login.png",
        full_page=True
    )

    page.screenshot(path="debug_before_validate.png", full_page=True)

    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(page.content())
    print("récup token")
    access_token = page.evaluate("""
    () => {
        return sessionStorage.getItem('access_token')
    }
    """)

    print("TOKEN =", access_token[:30] + "...")
    employee_id = page.evaluate("""
    () => {
        return sessionStorage.getItem('EmployeeId')
    }
    """)
    
    print("EMPLOYEE =", employee_id)
    
    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }
    
    r = requests.get(
        f"https://nie.api.natixis.com/saving/v1/employees/{employee_id}/availableProducts",
        headers=headers,
    )
    
    print(r.status_code)
    
    data = r.json()
    funds = []

    for product in data["availableProducts"]:
        for fund in product["funds"]:
            funds.append({
                "product": product["displayableProductCode"],
                "id": fund["id"],
                "label": fund["label"]
            })

    print(f"{len(funds)} fonds trouvés")
    for f in funds:
        print(f)

    def get_history(fund_id, headers):
        history = []
        page = 0
    
        while True:
            r = requests.get(
                f"https://nie.api.natixis.com/fund/v1/funds/{fund_id}/unitValuesHistory?page={page}",
                headers=headers,
            )
    
            r.raise_for_status()
    
            data = r.json()
    
            content = data.get("content", [])
    
            if not content:
                break
    
            history.extend(content)
    
            print(
                f"Fund {fund_id} - page {page} - {len(content)} valeurs"
            )
    
            page += 1
    
        return history
    
    all_funds = []

    for fund in funds:
    
        history = get_history(
            fund["id"],
            headers
        )
    
        all_funds.append({
            "id": fund["id"],
            "label": fund["label"],
            "product": fund["product"],
            "history": history
        })

    os.makedirs("data", exist_ok=True)
    with open(
        "data/funds.json",
        "w",
        encoding="utf-8"
    ) as f:
        json.dump(
            all_funds,
            f,
            indent=2,
            ensure_ascii=False
        )
   
    browser.close()
    print("update de data terminé")
