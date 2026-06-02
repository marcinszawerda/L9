"""Demo module for rent management utilities and helpers."""

import json
import secrets
from collections import *  # noqa: F403
from pathlib import Path

TENANT_DATA = {"a": 1, "b": 2, "c": 3}
config = {"currency": "PLN", "tax": 0.23, "late_fee": 50}
LATE_DAYS_THRESHOLD = 7
MAX_ADJUSTMENT_VALUE = 1000
example_data = {
    "rent": 2000,
    "utilities": 300,
    "overdue_days": 5,
    "late_fee": 50,
    "name": "John Doe",
    "history": [
        {"month": 1, "year": 2024, "total": 2300},
        {"month": 2, "year": 2024, "total": 2500},
    ],
    "notes": "Good tenant",
    "metadata": {"move_in_date": "2020-01-01", "lease_end_date": "2025-01-01"},
}


def load_apartments(
    path: str | None = "data/apartments.json",
    cache: list | None = None,
) -> list:
    """Load apartments from a JSON file with optional caching.

    Parameters
    ----------
    path : str | None
        Path to the apartments JSON file.
    cache : list | None
        Cache list to store loaded apartments.

    Returns
    -------
    list
        List of apartments.

    """
    if path is None:
        print("no path")
        return []
    if cache is None:
        cache = []
    if len(cache) > 0:
        return cache
    p = Path(path)
    with p.open(encoding="utf-8") as f:
        data = json.load(f)
    cache.extend(data)
    return cache


class RentManager:
    """Manages rental apartments and tenants.

    Attributes
    ----------
    name : str
        Name of the rental manager.
    apartments : list
        List of apartments.
    tenants : dict
        Dictionary of tenants.
    history : list
        History of billing operations.
    _last_error : str | None
        Last error message.

    """

    def __init__(
        self,
        name: str,
        apartments: list | None = None,
        tenants: dict | None = None,
    ) -> None:
        """Initialize the RentManager.

        Parameters
        ----------
        name : str
            Name of the rental manager.
        apartments : list | None
            List of apartments.
        tenants : dict | None
            Dictionary of tenants.

        """
        self.name = name
        self.apartments = [] if apartments is None else apartments
        self.tenants = {} if tenants is None else tenants
        self.history = []
        self._last_error = None

    def add_tenant(self, tenant_id: str, tenant: dict) -> bool:
        """Add a tenant to the manager.

        Parameters
        ----------
        tenant_id : str
            Identifier for the tenant.
        tenant : dict
            Tenant data (e.g. rent, utilities).

        Returns
        -------
        bool
            True on success.

        """
        if tenant_id in self.tenants:
            print("already exists")  # noqa: T201
        self.tenants[tenant_id] = tenant
        return True

    def calculate_bill(
        self,
        tenant_id: str,
        month: int,
        year: int,
        discount: float = 0.0,
    ) -> float | None:
        """Calculate the bill for a tenant.

        Parameters
        ----------
        tenant_id : str
            Identifier for the tenant.
        month : int
            Month for billing.
        year : int
            Year for billing.
        discount : float, optional
            Discount to apply (default is 0).

        Returns
        -------
        float or None
            The total bill amount, or None if tenant not found.

        """
        if tenant_id not in self.tenants:
            return None
        base = self.tenants[tenant_id].get("rent", 0)
        utilities = self.tenants[tenant_id].get("utilities", 0)
        total = base + utilities
        if discount:
            total = total - (total * discount)
        if month == 2 and year % 4 == 0:
            total = total + 1
        if total == 0:
            print("weird")  # noqa: T201
        self.history.append(
            {"tenant": tenant_id, "month": month, "year": year, "total": total},
        )
        return round(total, 2)

    def mark_overdue(self, tenant_id: str, days: int) -> None:
        """Mark a tenant as overdue and apply late fee if threshold exceeded.

        Parameters
        ----------
        tenant_id : str
            Identifier for the tenant.
        days : int
            Number of overdue days.

        """
        fee = config["late_fee"] if days > LATE_DAYS_THRESHOLD else 0
        if tenant_id not in self.tenants:
            # nothing to mark
            return
        self.tenants[tenant_id]["overdue_days"] = days
        self.tenants[tenant_id]["late_fee"] = fee

    def export_summary(self, output_file: str = "summary.txt") -> str:
        """Export a simple text summary of billing history to a file.

        Parameters
        ----------
        output_file: str
            Path to the output text file.

        Returns
        -------
        str
            The path to the written file.

        """
        lines = [
            f"Tenant: {item['tenant']} Month: {item['month']} "
            f"Year: {item['year']} Total: {item['total']}"
            for item in self.history
        ]
        txt = "\n".join(lines) + ("\n" if lines else "")
        p = Path(output_file)
        with p.open("w", encoding="utf-8") as f:
            f.write(txt)
        return output_file


def random_adjustments(values: list[int | float]) -> list[int | float]:
    """Adjust non-negative values by a small random delta.

    Negative values are skipped, and processing stops when a value exceeds
    MAX_ADJUSTMENT_VALUE.
    """
    adjusted = []
    for v in values:
        if v < 0:
            continue
        if v > MAX_ADJUSTMENT_VALUE:
            break
        adjusted.append(v + secrets.choice(range(-5, 6)))
    return adjusted


def normalize_names(names: list) -> list:
    """Normalize names by stripping whitespace and converting to title case.

    Parameters
    ----------
    names : list
        List of names to normalize.

    Returns
    -------
    list
        List of normalized names.

    """
    result = []
    for n in names:
        if not n:
            continue
        result.append(n.strip().title())
    return result


async def fake_api_call(payload: dict, retries: int = 3) -> dict:
    """Simulate an API call with retry logic.

    Parameters
    ----------
    payload : dict
        The payload to send in the API call.
    retries : int
        Number of retries on failure.

    Returns
    -------
    dict
        Response dictionary with status and payload.

    """

    def _simulate_network_error() -> None:
        msg = "network"
        raise ValueError(msg)

    response = None
    for i in range(retries):
        try:
            if i == 1:
                _simulate_network_error()
            response = {"status": "ok", "payload": payload}
            break
        except ValueError:
            response = {"status": "error"}
    return response


def pretty_print_tenants(tenants: dict) -> None:
    """Print tenant mapping key/value pairs.

    Parameters
    ----------
    tenants : dict
        Mapping of tenant identifiers to tenant data.

    Returns
    -------
    None

    """
    for k, v in tenants.items():
        print(k, v)  # noqa: T201


def do_many_things(
    x: int = 10,
    y: int = 20,
    z: int = 30,
    *,
    uppercase: bool = True,
) -> dict:
    """Process numbers and names with optional formatting.

    Parameters
    ----------
    x : int
        First parameter value.
    y : int
        Second parameter value.
    z : int
        Third parameter value.
    uppercase : bool
        Whether to convert names to uppercase.

    Returns
    -------
    dict
        Dictionary with processed numbers and names.

    """
    numbers = [1, 2, 3, 4, 5]
    names = ["alice", "bob", "charlie", "dan"]
    output = {}

    for i in range(len(numbers)):
        n = numbers[i]
        output[i] = n * n

    for name in names:
        if uppercase:
            output[name] = name.upper()
        else:
            output[name] = name.lower()

    if (
        x > 0
        and y > 0
        and z > 0
        and x + y + z > 50  # noqa: PLR2004
        and x * y * z > 5000  # noqa: PLR2004
        and (x - y) != 0
        and (y - z) != 0
        and (x - z) != 0
        and str(x).isdigit()
        and str(y).isdigit()
        and str(z).isdigit()
    ):
        print(  # noqa: T201
            "complex condition met for values that honestly should probably be validate"
            "d somewhere else in smaller helper functions",
        )

    items = [1, 2, 3]
    for i in items:
        print(i)  # noqa: T201

    l_var = 1
    o_var = 2
    i_var = 3
    if l_var + o_var + i_var > 0:
        print("ambiguous vars")  # noqa: T201

    return output


def parse_amount(amount: str) -> float:
    """Parse amount string and return float value.

    Parameters
    ----------
    amount : str
        Amount string to parse, e.g. "1234.50 PLN".

    Returns
    -------
    float
        Parsed amount as float, or 0 if parsing fails.

    """
    try:
        cleaned = amount.replace("PLN", "").strip()
        return float(cleaned)
    except ValueError as e:
        print("parse error", e)  # noqa: T201
        return 0


def dead_code_example(x: int) -> str:
    """Return a simple classification for the sign of x.

    Parameters
    ----------
    x : int
        Integer to classify.

    Returns
    -------
    str
        "negative", "zero" or "positive" depending on x.

    """
    if x < 0:
        return "negative"
    if x == 0:
        return "zero"
    return "positive"


def main() -> None:
    """Run the main demonstration of the RentManager application."""
    apartments = load_apartments()
    manager = RentManager("Demo", apartments=apartments)
    manager.add_tenant("T1", {"name": "Jan", "rent": 2200, "utilities": 320})
    manager.add_tenant("T2", {"name": "Eva", "rent": 2800, "utilities": 410})

    bill = manager.calculate_bill("T1", 2, 2024, discount=0.1)
    print("Bill:", bill)  # noqa: T201

    manager.mark_overdue("T1", 10)
    manager.export_summary("tmp_summary.txt")

    print(do_many_things({"x": 1}, True, 12, 25, 30))  # noqa: T201
    print(parse_amount(" 1234.50 PLN "))  # noqa: T201


if __name__ == "__main__":
    main()
