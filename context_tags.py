"""
Context tagging configuration for test case conversion.
Add new keywords and tags as needed for different modules.
"""

CONTEXT_TAGS = {
    # Authentication & Access
    "Authentication": [
        "login",
        "logout",
        "sign in",
        "sign out",
        "password",
        "username",
        "credentials",
    ],
    "Authorization": [
        "permission",
        "access",
        "role",
        "user group",
        "admin",
        "unauthorized",
    ],
    # Dashboard & Reporting
    "Dashboard": ["dashboard", "landing page", "home page", "main page"],
    "KPI Reporting": ["kpi", "metrics", "report", "analytics", "statistics"],
    "Data Filtering": ["filter", "search", "sort", "criteria", "selection"],
    "Charts & Graphs": ["chart", "graph", "visualization", "heatmap", "bar graph"],
    # Acquisition Management
    "Acquisition Management": ["acquisition", "contract", "procurement", "vendor"],
    "Budget Management": ["budget", "financial", "cost", "expense", "funding"],
    "Workflow": ["approval", "workflow", "process", "submit", "review"],
    # Data Management
    "Data Entry": ["form", "input", "create", "add", "enter data"],
    "Data Validation": ["validate", "verify", "check", "validation", "error"],
    "Data Export": ["export", "download", "extract", "generate"],
    # User Interface
    "Navigation": ["navigate", "click", "button", "link", "menu"],
    "Forms": ["form", "field", "dropdown", "checkbox", "radio button"],
    "Tables": ["table", "grid", "list", "row", "column"],
    # System Functions
    "Notifications": ["notification", "alert", "message", "popup"],
    "File Management": ["upload", "download", "file", "document", "attachment"],
    "Integration": ["api", "sync", "integration", "external system"],
    # Status & States
    "Status Management": ["status", "state", "active", "inactive", "pending"],
    "Error Handling": ["error", "exception", "failure", "invalid"],
    "Acquisitions": ["acquisitions"],
    "Filters": ["filters"],
    "Weekly": ["weekly"],
    "Leadership": ["leadership"],
    "Management": ["management"],
    "Target": ["target"],
    "Filtered": ["filtered"],
    "Trigger": ["trigger"],
    "Reports": ["reports"],
    "Triggers": ["triggers"],
    "Dashboard": ["dashboard"],
    "KPI": ["kpi"],
    "Reporting": ["reporting"],
    "Acquisition": ["acquisition"],
    "Management": ["management"],
    "Budget": ["budget"],
    "Management": ["management"],
    "Workflow": ["workflow"],
    "Data": ["data"],
    "Management": ["management"],
    "User": ["user"],
    "Interface": ["interface"],
    "System": ["system"],
    "Functions": ["functions"],
    "Status": ["status"],
    "States": ["states"],
    "Error": ["error"],
    "Handling": ["handling"],
    "Acquisitions": ["acquisitions"],
    "Filters": ["filters"],
    "Weekly": ["weekly"],
    "Leadership": ["leadership"],
    "Management": ["management"],
    "Target": ["target"],
    "Filtered": ["filtered"],
    "Trigger": ["trigger"],
    "Reports": ["reports"],
    "Triggers": ["triggers"],
    "Dashboard": ["dashboard"],
    "KPI": ["kpi"],
    "Reporting": ["reporting"],
    "Acquisition": ["acquisition"],
    "Management": ["management"],
    "Budget": ["budget"],
    "Management": ["management"],
    "Workflow": ["workflow"],
    "Data": ["data"],
    "Management": ["management"],
    "User": ["user"],
    "Interface": ["interface"],
    "System": ["system"],
    "Functions": ["functions"],
    "Status": ["status"],
    "States": ["states"],
    "Error": ["error"],
    "Management": ["management"],
    "Filtered": ["filtered"],
    "Mergeagreementreport": ["mergeagreementreport"],
    "Filters": ["filters"],
    "Mergeagreementreportcostcenters": ["mergeagreementreportcostcenters"],
    "Unbudgeted": ["unbudgeted"],
    "Pipeline": ["pipeline"],
    "Filtering": ["filtering"],
    "Budgetary": ["budgetary"],
    "Triggered": ["triggered"],
}


def get_context_tags(content_text: str) -> list:
    """Extract context tags from content text."""
    content_lower = content_text.lower()
    found_tags = []

    for tag, keywords in CONTEXT_TAGS.items():
        if any(keyword in content_lower for keyword in keywords):
            found_tags.append(tag)

    return found_tags


def add_context_tag(tag_name: str, keywords: list):
    """Programmatically add a new context tag."""
    CONTEXT_TAGS[tag_name] = keywords
    print(f"Added tag '{tag_name}' with keywords: {keywords}")
