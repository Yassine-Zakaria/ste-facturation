from datetime import date


def calculate_usage_amount(consumption: int) -> int:
    """Calcul le montant HT selon les tranches de consommation."""
    if consumption <= 0:
        return 0

    total = 0
    remaining = consumption

    tranches = [
        (12, 200),
        (17, 300),
        (10, 405),
    ]

    for tranche_limit, unit_price in tranches:
        if remaining <= 0:
            break
        chunk = min(remaining, tranche_limit)
        total += chunk * unit_price
        remaining -= chunk

    if remaining > 0:
        total += remaining * 620

    return total


def calculate_total_with_fees(sub_total: int, compteur_fee: int = 230, branchement_fee: int = 345) -> int:
    """Retourne le montant total TTC/à payer avec les frais fixes."""
    return sub_total + compteur_fee + branchement_fee


def generate_invoice_number(year: int | None = None, sequence: int = 1) -> str:
    """Génère un numéro de facture standardisé."""
    current_year = year or date.today().year
    return f"F-{current_year}-{sequence:05d}"


def generate_client_matricule(year: int | None = None, next_id: int = 1) -> str:
    """Génère le matricule client."""
    current_year = year or date.today().year
    return f"FACT-{current_year}-{next_id}"
