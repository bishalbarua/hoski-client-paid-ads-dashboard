"""Central client registry for Google Ads reporting and exports."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
CLIENTS_ROOT = PROJECT_ROOT / "clients"


@dataclass(frozen=True)
class ClientConfig:
    display_name: str
    google_ads_customer_id: str
    folder_name: str
    google_sheet_id: str | None = None
    google_sheet_tab: str | None = None
    alert_email: str | None = None
    analysis_subdir: str = "analysis"

    @property
    def analysis_dir(self) -> Path:
        return CLIENTS_ROOT / self.folder_name / self.analysis_subdir

    @property
    def google_sheet_tab_name(self) -> str:
        return self.google_sheet_tab or f"Google - {self.display_name}"


def _client(
    display_name: str,
    google_ads_customer_id: str,
    *,
    folder_name: str | None = None,
    google_sheet_id: str | None = None,
    google_sheet_tab: str | None = None,
    alert_email: str | None = None,
) -> ClientConfig:
    return ClientConfig(
        display_name=display_name,
        google_ads_customer_id=google_ads_customer_id,
        folder_name=folder_name or f"{display_name} ({google_ads_customer_id})",
        google_sheet_id=google_sheet_id,
        google_sheet_tab=google_sheet_tab,
        alert_email=alert_email,
    )


GOOGLE_ADS_CLIENTS: dict[str, ClientConfig] = {
    "Anand Desai Law Firm": _client("Anand Desai Law Firm", "5865660247"),
    "Dentiste": _client("Dentiste", "3857223862"),
    "Estate Jewelry Priced Right": _client("Estate Jewelry Priced Right", "7709532223"),
    "FaBesthetics": _client("FaBesthetics", "9304117954"),
    "GDM Google Ads": _client("GDM Google Ads", "7087867966"),
    "Hoski.ca": _client("Hoski.ca", "5544702166"),
    "New Norseman": _client("New Norseman", "3720173680"),
    "Park Road Custom Furniture and Decor": _client("Park Road Custom Furniture and Decor", "7228467515"),
    "Serenity Familycare": _client("Serenity Familycare", "8134824884"),
    "Synergy Spine & Nerve Center": _client("Synergy Spine & Nerve Center", "7628667762"),
    "Texas FHC": _client("Texas FHC", "8159668041"),
    "Voit Dental 1": _client(
        "Voit Dental 1",
        "5216656756",
        folder_name="Voit Dental 1 (5216656756)",
    ),
    "Voit Dental 2": _client(
        "Voit Dental 2",
        "5907367258",
        folder_name="Voit Dental 2 (5907367258)",
    ),
}

_CLIENT_BY_CUSTOMER_ID = {
    cfg.google_ads_customer_id: cfg for cfg in GOOGLE_ADS_CLIENTS.values()
}
_CLIENT_BY_FOLDER_NAME = {
    cfg.folder_name: cfg for cfg in GOOGLE_ADS_CLIENTS.values()
}


def get_google_ads_targets() -> dict[str, str]:
    return {name: cfg.google_ads_customer_id for name, cfg in GOOGLE_ADS_CLIENTS.items()}


def get_client_config(identifier: str) -> ClientConfig:
    if identifier in GOOGLE_ADS_CLIENTS:
        return GOOGLE_ADS_CLIENTS[identifier]
    if identifier in _CLIENT_BY_CUSTOMER_ID:
        return _CLIENT_BY_CUSTOMER_ID[identifier]
    if identifier in _CLIENT_BY_FOLDER_NAME:
        return _CLIENT_BY_FOLDER_NAME[identifier]
    raise KeyError(f"Unknown client identifier: {identifier}")


def get_client_analysis_dir(identifier: str) -> Path:
    return get_client_config(identifier).analysis_dir


def resolve_google_sheet_target(
    identifier: str,
    *,
    fallback_sheet_id: str | None = None,
    fallback_tab: str | None = None,
) -> tuple[str | None, str]:
    cfg = get_client_config(identifier)
    return (
        cfg.google_sheet_id or fallback_sheet_id,
        cfg.google_sheet_tab_name or fallback_tab or f"Google - {cfg.display_name}",
    )
