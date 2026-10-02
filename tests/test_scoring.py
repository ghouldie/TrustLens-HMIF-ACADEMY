from backend.scoring import assess


def test_high_risk_case():
    r = assess({"account": "1234567890", "price": 1500000, "category": "laptop bekas",
                "account_age_days": 10, "chat_text": "Transfer dulu ya kak, tanpa rekber, buruan stok terakhir"})
    assert r["level"] == "Tinggi" and r["confidence"] >= 0.8


def test_low_risk_case():
    r = assess({"account": "1111222233", "price": 5300000, "category": "laptop bekas",
                "account_age_days": 700, "chat_text": "Boleh COD di kampus kak"})
    assert r["level"] == "Rendah"


def test_no_input():
    assert assess({})["confidence"] == 0.0
