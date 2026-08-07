#!/usr/bin/env python3
import argparse
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_REPO_URL = "https://github.com/OutSystems/docs-odc.git"
CANONICAL_SCP_REPO_URL = "git@github.com:OutSystems/docs-odc.git"
DEFAULT_BRANCH = "main"
REMOTE_LOOKUP_TIMEOUT_SECONDS = 15
CLONE_TIMEOUT_SECONDS = 30
MAX_GIT_DETAIL_CHARS = 500
MAX_SOURCE_DISPLAY_CHARS = 200
MAX_SOURCE_ERROR_CHARS = 1000
SOURCE_BASE_URL = "https://github.com/OutSystems/docs-odc/blob/main"
DEFAULT_SEARCH_ROOTS = [
    Path("src/eap/reference"),
    Path("src/eap/building-apps/ui"),
    Path("knowledge/outsystems/public/odc/reference"),
]
DEFAULT_O11_CATALOG_RELATIVE_PATH = Path("references/o11-designing-screens-widget-catalog.json")
DOCS_ODC_SEARCH_ROOTS = [
    Path("src/eap/reference"),
    Path("src/eap/building-apps/ui"),
]
DOCS_ODC_UI_ALLOWED_CANDIDATES = {
    "src/eap/building-apps/ui/screen-about.md",
    "src/eap/building-apps/ui/creating-screens/create-screen-scratch.md",
    "src/eap/building-apps/ui/icons/icon-widget-ref.md",
}
LOCAL_REFERENCE_ROOT = Path("knowledge/outsystems/public/odc/reference")
LOCAL_EXCLUDED_PATH_TERMS = {
    "agentic",
    "course",
    "intake",
    "mentor",
    "migration",
    "o11",
    "prompt",
    "workshop",
}
APPLICABILITY_PATTERNS = [
    ("reactive web apps", re.compile(r"\breactive\s+web\s+apps?\b", re.IGNORECASE)),
    ("web apps", re.compile(r"\bweb\s+apps?\b", re.IGNORECASE)),
    ("mobile apps", re.compile(r"\bmobile\s+apps?\b", re.IGNORECASE)),
]

TARGETS = [
    {"name": "Container", "kind": "widget", "category": "layout"},
    {"name": "Expression", "kind": "widget", "category": "display"},
    {"name": "If", "kind": "widget", "category": "control-flow"},
    {"name": "Text", "kind": "widget", "category": "display"},
    {"name": "Form", "kind": "widget", "category": "form"},
    {"name": "Input", "kind": "widget", "category": "form-input"},
    {"name": "Button", "kind": "widget", "category": "action"},
    {"name": "Button Group", "kind": "widget", "category": "action"},
    {"name": "Link", "kind": "widget", "category": "navigation"},
    {"name": "Popover Menu", "kind": "widget", "category": "navigation"},
    {"name": "List", "kind": "widget", "category": "data-display"},
    {"name": "List Item", "kind": "widget", "category": "data-display"},
    {"name": "Table", "kind": "widget", "category": "data-display"},
    {"name": "Checkbox", "kind": "widget", "category": "form-input"},
    {"name": "Radio Group", "kind": "widget", "category": "form-input", "legacy_names": ["Radio Button"]},
    {"name": "Dropdown", "kind": "widget", "category": "form-input"},
    {"name": "Label", "kind": "widget", "category": "form-input"},
    {"name": "Text Area", "kind": "widget", "category": "form-input"},
    {"name": "Switch", "kind": "widget", "category": "form-input"},
    {"name": "Image", "kind": "widget", "category": "media"},
    {"name": "Icon", "kind": "widget", "category": "media"},
    {"name": "Upload", "kind": "widget", "category": "file-input"},
    {"name": "Screen", "kind": "screen", "category": "ui-producer"},
    {"name": "Web Block", "kind": "block", "category": "ui-producer"},
]

TARGET_ALIASES = {
    "Screen": ["Screens", "Creating a Screen"],
    "Web Block": ["Block"],
    "Icon": ["Icon widget reference"],
}
O11_TARGET_ALIASES = {
    "Radio Group": ["Radio Group", "Radio Button"],
    "Web Block": ["Block Widget", "Block", "Web Block"],
}
O11_PAGE_FAMILY_PRIORITY = {
    "interface": 0,
    "traditional_web": 1,
    "unknown": 2,
}
LEGACY_SUPPORTING_SOURCE_COMPATIBILITY_STATUS = (
    "Legacy backward-compatible fallback; prefer generated o11_candidate_support when present."
)
OBSERVED_REAL_APP_EXAMPLES = {
    "Form": [
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "RecoverPasswordReset",
            "widget_name": "PasswordResetForm",
            "widget_type": "Form",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, LayoutBlank, and password reset context",
            "hierarchy": [
                "RecoverPasswordReset",
                "LayoutBlank",
                "Content",
                "Container",
                "Form named PasswordResetForm",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        }
    ],
    "Button": [
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3OrchestratorDemo",
            "widget_name": "Button",
            "widget_type": "Button",
            "text": "Start Upload",
            "section_title": "Start Upload",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, and S3 upload/staging context",
            "hierarchy": [
                "S3OrchestratorDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_UseCase",
                "Container named Ex1_1_UploadClientSideToS3",
                "Container named StartUploadCSide",
                "IfWidget named ShowStartUploadClientSide",
                "Container",
                "UIBlockInstanceWidget ButtonLoading",
                "Button",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        },
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3OrchestratorDemo",
            "widget_name": "DownloadGUID2",
            "widget_type": "Button",
            "text": "Download Binary from Staging Area to Temp",
            "section_title": "Download Binary from Staging Area to Temp",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, S3Binary, TempTable, and copy-to-temp context",
            "hierarchy": [
                "S3OrchestratorDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_UseCase",
                "Container named Ex1_3_DownloadCopyServerSide",
                "IfWidget",
                "Container named ShowDownloadButton",
                "UIBlockInstanceWidget ButtonLoading",
                "Button named DownloadGUID2",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        }
    ],
    "Table": [
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3OrchestratorDemo",
            "widget_name": "TblBinaries",
            "widget_type": "TableRecords",
            "section_title": "Staging Area Information stored in table S3Binary",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, and S3Binary staging context",
            "hierarchy": [
                "S3OrchestratorDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_UseCase",
                "Container named Ex1_2_DownloadFromS3ServerSide",
                "IfWidget",
                "Container named Spacer2",
                "TableRecords named TblBinaries",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        },
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3UtilitiesDemo",
            "widget_name": "TblGetObjectMetadata",
            "widget_type": "TableRecords",
            "section_title": "Metadata Actions (Get attributes, List with Filter)",
            "subsection_title": "GetObjectMetadata: Get metadata for an S3 object",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, and metadata/S3 object context",
            "hierarchy": [
                "S3UtilitiesDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_Utility",
                "Container named Cont_Metadata",
                "Container named Cont_GetObjectMetadata",
                "Container",
                "TableRecords named TblGetObjectMetadata",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        },
    ],
    "Upload": [
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3OrchestratorDemo",
            "widget_name": "Ex1_uplFile",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app and screen context",
            "hierarchy": [
                "S3OrchestratorDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_UseCase",
                "Container named Ex1_1_UploadClientSideToS3",
                "Container named Ex1_Phase1Name",
                "Container named ClientFileUpload",
                "Upload widget named Ex1_uplFile",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        }
    ],
    "Dropdown": [
        {
            "app": "S3Orchestrator_Sandbox",
            "screen": "S3UtilitiesDemo",
            "widget_name": "DropNormalizeMode",
            "evidence_level": "Studio-observed, user-confirmed; MCP confirms app, screen, and NormalizePdfMode context",
            "hierarchy": [
                "S3UtilitiesDemo",
                "LayoutTopMenu",
                "MainContent",
                "Form named Demo",
                "Tabs",
                "TabsContentItem named Tab_Utility",
                "Container named Cont_PDFinS3",
                "Container named Cont_NormalizePdfInS3WithQpdf",
                "Container named NormalizePdfBtn",
                "Container",
                "Dropdown DropNormalizeMode",
            ],
            "notes": "MCP context search did not expose this exact deep widget node; use as real-app naming and placement evidence, not official platform authority.",
        }
    ],
}
ODC_STUDIO_TOOLBOX_OBSERVATIONS = {
    "If": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "If",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Text": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Text",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "List Item": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "List Item",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Label": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Label",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Text Area": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Text Area",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Switch": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Switch",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Button Group": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Button Group",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Popover Menu": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Popover Menu",
            "evidence_level": "ODC Studio toolbox observation; not current public documentation authority",
            "notes": "Treat O11 support as support-only and require ODC Studio review before using this target as authoritative.",
        }
    ],
    "Radio Group": [
        {
            "source": "ODC Studio appshot",
            "observed_at": "2026-05-23",
            "studio_version": "ODC Studio 1.7.9",
            "label": "Radio Group",
            "evidence_level": "ODC Studio toolbox observed; public ODC docs search did not surface a matching widget reference",
            "notes": "Use Radio Group as the ODC Studio widget label; treat O11 Radio Group and Radio Button references as supporting compatibility sources only.",
        }
    ],
}


def official_o11_widget_source(title, slug, notes=None):
    default_notes = (
        f"Documents the {title} widget reference, including purpose, properties, "
        "events, and runtime Id where documented."
    )
    return {
        "source_family": "official_outsystems_public_docs_o11",
        "source_url": f"https://success.outsystems.com/documentation/11/reference/outsystems_language/interfaces/designing_screens/{slug}/",
        "title": f"{title} - OutSystems 11 Documentation",
        "evidence_level": "Official O11 reference; not current ODC authority",
        "notes": notes or f"{default_notes} Use as supporting source only unless a current ODC source is found.",
    }


OFFICIAL_SUPPORTING_SOURCES = {
    "Container": [
        official_o11_widget_source("Container", "container"),
    ],
    "Expression": [
        official_o11_widget_source("Expression", "expression"),
    ],
    "Form": [
        official_o11_widget_source("Form", "form"),
    ],
    "Input": [
        official_o11_widget_source("Input", "input"),
    ],
    "Button": [
        official_o11_widget_source("Button", "button"),
    ],
    "Link": [
        official_o11_widget_source("Link", "link"),
    ],
    "List": [
        official_o11_widget_source("List", "list"),
    ],
    "Table": [
        official_o11_widget_source("Table", "table"),
    ],
    "Checkbox": [
        official_o11_widget_source("Checkbox", "checkbox"),
    ],
    "Radio Group": [
        {
            "source_family": "official_outsystems_public_docs_o11",
            "source_url": "https://success.outsystems.com/documentation/11/reference/outsystems_language/interfaces/designing_screens/radio_group/",
            "title": "Radio group - OutSystems 11 Documentation",
            "evidence_level": "Official O11 reference; not current ODC authority",
            "notes": "Documents the Radio Group widget, grouped Radio Buttons, selected value binding through Variable, properties, events, and runtime Id.",
        },
        {
            "source_family": "official_outsystems_public_docs_o11_traditional_web",
            "source_url": "https://success.outsystems.com/documentation/11/reference/outsystems_language/traditional_web/web_interfaces/designing_screens/radio_button_widget/",
            "title": "Radio Button Widget - OutSystems 11 Documentation",
            "evidence_level": "Official O11 Traditional Web reference; not current ODC authority",
            "notes": "Documents individual Radio Button behavior for Traditional Web and should not be used alone to generate ODC Radio Group prompts.",
        },
    ],
    "Dropdown": [
        official_o11_widget_source("Dropdown", "dropdown"),
    ],
    "Image": [
        official_o11_widget_source("Image", "image"),
    ],
    "Upload": [
        official_o11_widget_source("Upload", "upload"),
    ],
    "Web Block": [
        official_o11_widget_source(
            "Block Widget",
            "block_widget",
            "Documents the O11 Block Widget reference; current ODC Web Block source remains the governing authority when available.",
        ),
    ],
}

CURRENT_CONTEXTUAL_SOURCES = {
    "Button": [
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/sending-emails/sending.md",
            "title": "Sending emails - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Button widget reference",
            "notes": "Documents a Button widget with an On Click event that calls a client action.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/self-registration/logic.md",
            "title": "Self-registration logic - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Button widget reference",
            "notes": "Documents selecting a Signup button and choosing New Client Action from the On Click event dropdown.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/navigation/pass-information-between-screens.md",
            "title": "Pass information between screens - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Button widget reference",
            "notes": "Documents that passing a value through an On Click Event works with a Link widget and also with a Button, including a destination Screen handler.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/seo/seo-best-practices.md",
            "title": "SEO best practices - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Button widget reference",
            "notes": "Documents caution around widgets that use OnClick client actions for navigation and recommends Button and Link components to link directly to URLs.",
        },
    ],
    "Dropdown": [
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/data/fetch-data/calculated-attribute-create.md",
            "title": "Create a Calculated Attribute in an Aggregate - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Dropdown widget reference",
            "notes": "Documents adding a Dropdown and setting its values to the returning list of an Aggregate, using the DropdownLabel attribute as the options text.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/data/fetch-data/aggregate.md",
            "title": "Query data using aggregates - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Dropdown widget reference",
            "notes": "Documents using Screen Aggregates to populate drop-down box lists and warns to set Max. Records higher than the expected maximum when fetching all records.",
        },
    ],
    "Input": [
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/data/client-variable.md",
            "title": "Client variables - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Input widget reference",
            "notes": "Documents: Select the Input widget and set a Client Variable through the Variable property.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/logic/local-variable.md",
            "title": "Local variables - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Input widget reference",
            "notes": "Documents: Select the Input widget and create a local variable through the Variable dropdown.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/self-registration/create-validation-form.md",
            "title": "Create validation form - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Input widget reference",
            "notes": "Documents configuring an Input-related Events > OnChange property to create a new Client Action.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/patterns/interaction/inputwithicon.md",
            "title": "Input with Icon - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Input widget reference",
            "notes": "Documents an OutSystems UI pattern containing Icon and Input widgets, using the Input Variable dropdown, and setting the Input Prompt property.",
        },
    ],
    "List": [
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/interaction/fetch-display.md",
            "title": "Fetch and display data from the database in OutSystems - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact List widget reference",
            "notes": "Documents that after fetching data with an Aggregate, the example uses a List widget but a Table or other widget can also display the data.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/interaction/fetch-display.md",
            "title": "Fetch and display data from the database in OutSystems - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact List widget reference",
            "notes": "Documents dragging a List widget to a Screen, setting the Source field to GetEmployees.List, and dragging an Entity Attribute into the List widget.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/data/fetch-data/aggregate.md",
            "title": "Query data using aggregates - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact List widget reference",
            "notes": "Documents creating an Aggregate in a Screen or Block through Fetch Data from Database before binding UI that consumes the resulting list.",
        },
    ],
    "Table": [
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/interaction/fetch-display.md",
            "title": "Fetch and display data from the database in OutSystems - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Table widget reference",
            "notes": "Documents that after fetching data with an Aggregate, the example uses a List widget but a Table or other widget can also display the data.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/ui/interaction/fetch-display.md",
            "title": "Fetch and display data from the database in OutSystems - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Table widget reference",
            "notes": "Documents setting a data-display widget source to GetEmployees.List after creating the GetEmployees Aggregate; use as Table data producer guidance only.",
        },
        {
            "source_family": "official_outsystems_public_docs_odc",
            "source_url": f"{SOURCE_BASE_URL}/src/eap/building-apps/data/fetch-data/aggregate.md",
            "title": "Query data using aggregates - OutSystems Developer Cloud documentation",
            "evidence_level": "Current ODC contextual documentation; not an exact Table widget reference",
            "notes": "Documents creating an Aggregate in a Screen or Block through Fetch Data from Database before binding UI that consumes the resulting list.",
        },
    ],
}

PROPERTY_SECTION_HEADINGS = {"properties", "attributes"}
EVENT_SECTION_HEADINGS = {"events"}
BINDING_SECTION_HEADINGS = {
    "binding",
    "bindings",
    "data binding",
    "data bindings",
    "data source",
    "data sources",
    "source",
    "variables",
    "parameters",
}


def read_markdown_files(source_root):
    source_root = Path(source_root)
    files = []
    seen = set()
    for search_root in DOCS_ODC_SEARCH_ROOTS:
        root = source_root / search_root
        if root.is_dir():
            for path in sorted(path for path in root.rglob("*.md") if path.is_file()):
                if path not in seen:
                    files.append(path)
                    seen.add(path)
    root = source_root / LOCAL_REFERENCE_ROOT
    if root.is_dir():
        for path in sorted(path for path in root.rglob("*.md") if path.is_file()):
            if path not in seen:
                files.append(path)
                seen.add(path)
    return files


def source_url_for(relative):
    if relative.as_posix().startswith("src/eap/"):
        return f"{SOURCE_BASE_URL}/{relative.as_posix()}"
    return ""


def is_local_reference_candidate(relative, text):
    relative_text = relative.as_posix().lower()
    if not relative_text.startswith(f"{LOCAL_REFERENCE_ROOT.as_posix()}/"):
        return False
    if relative.name != "source.md":
        return False
    if relative.parent.name == "normalized":
        pass
    elif "normalized" in relative.parts:
        return False
    if any(term in relative_text for term in LOCAL_EXCLUDED_PATH_TERMS):
        return False
    reference_text = text[:1000].lower()
    return "outsystems language and elements" in reference_text


def is_source_candidate(source_root, markdown_path, text):
    relative = markdown_path.relative_to(source_root)
    relative_text = relative.as_posix()
    if relative_text == "src/eap/reference/intro.md":
        return "outsystems language and elements" in text[:1000].lower()
    if relative_text.startswith("src/eap/building-apps/ui/"):
        return relative_text in DOCS_ODC_UI_ALLOWED_CANDIDATES
    return is_local_reference_candidate(relative, text)


def heading_pattern(name):
    escaped = re.escape(name)
    return re.compile(rf"^(?P<marks>#+)\s+{escaped}\s*$", re.IGNORECASE | re.MULTILINE)


def heading_names_for(target_name):
    return [target_name, *TARGET_ALIASES.get(target_name, [])]


def extract_heading_section(text, name):
    match = heading_pattern(name).search(text)
    if not match:
        return ""
    level = len(match.group("marks"))
    start = match.end()
    next_heading = re.search(rf"^#{{1,{level}}}\s+", text[start:], re.MULTILINE)
    end = start + next_heading.start() if next_heading else len(text)
    return text[start:end].strip()


def extract_named_subsections(section, allowed_names):
    subsections = []
    heading_matches = list(re.finditer(r"^(?P<marks>#+)\s+(?P<title>.+?)\s*$", section, re.MULTILINE))
    for index, match in enumerate(heading_matches):
        title = match.group("title").strip().lower()
        if title not in allowed_names:
            continue
        level = len(match.group("marks"))
        start = match.end()
        end = len(section)
        for next_match in heading_matches[index + 1 :]:
            if len(next_match.group("marks")) <= level:
                end = next_match.start()
                break
        subsections.append(section[start:end].strip())
    return "\n\n".join(subsections)


def is_weak_purpose_sentence(sentence):
    lowered = sentence.strip().lower().rstrip(".")
    return lowered in {
        "here are more details about blocks",
        "here are more details about block",
        "here are more details",
    }


def first_paragraph(section):
    lines = []
    for raw_line in section.splitlines():
        line = raw_line.strip()
        if not line:
            if lines:
                candidate = " ".join(lines)
                if not is_weak_purpose_sentence(candidate):
                    return candidate
                lines = []
            continue
        if line.startswith(("#", "|", "!", "<")):
            if lines:
                candidate = " ".join(lines)
                if not is_weak_purpose_sentence(candidate):
                    return candidate
                lines = []
            continue
        if line.startswith(("- ", "* ")):
            line = line[2:].strip()
            candidate = re.sub(r"\s+", " ", line)
            if candidate and not is_weak_purpose_sentence(candidate):
                return candidate
            continue
        lines.append(re.sub(r"\s+", " ", line))
    candidate = " ".join(lines)
    if candidate and not is_weak_purpose_sentence(candidate):
        return candidate
    return ""


def parse_table_properties(section):
    section = extract_named_subsections(section, PROPERTY_SECTION_HEADINGS)
    if not section:
        return []
    properties = []
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", section, re.MULTILINE):
        rows = [
            [cell.strip() for cell in line.strip().strip("|").split("|")]
            for line in table_match.group("table").splitlines()
        ]
        data_start = 1
        if len(rows) > 1 and all(set(cell) <= {"-", ":"} for cell in rows[1]):
            data_start = 2
        for cells in rows[data_start:]:
            if len(cells) < 2:
                continue
            name = cells[0].strip()
            if not name or set(name) <= {"-", ":"}:
                continue
            properties.append(name.split("(")[0].strip())
    return sorted(set(properties))


def extract_events(section):
    event_section = extract_named_subsections(section, EVENT_SECTION_HEADINGS)
    if not event_section:
        return []
    return sorted(set(re.findall(r"\bOn[A-Z][A-Za-z0-9]+", event_section)))


def extract_binding_shape(section):
    binding_shape = []
    binding_source = "\n\n".join(
        item
        for item in [
            extract_named_subsections(section, PROPERTY_SECTION_HEADINGS),
            extract_named_subsections(section, BINDING_SECTION_HEADINGS),
        ]
        if item
    )
    for table_match in re.finditer(r"(?P<table>(?:^\|.*\n?)+)", binding_source, re.MULTILINE):
        for line in table_match.group("table").splitlines():
            cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
            if len(cells) < 2 or cells[0].lower() == "property" or set(cells[0]) <= {"-", ":"}:
                continue
            clean = re.sub(r"\s+", " ", " ".join(cells))
            lowered = clean.lower()
            if any(keyword in lowered for keyword in ["bind", "variable", "aggregate", "data action", "form field", "list"]):
                binding_shape.append(clean)
    binding_sections = extract_named_subsections(section, BINDING_SECTION_HEADINGS)
    paragraphs = [re.sub(r"\s+", " ", item.strip()) for item in re.split(r"\n\s*\n", binding_sections)]
    for paragraph in paragraphs:
        lowered = paragraph.lower()
        if any(keyword in lowered for keyword in ["bind", "variable", "aggregate", "data action", "form field", "list"]):
            if paragraph and not paragraph.startswith(("#", "|", "!", "- ")):
                binding_shape.append(paragraph)
    return list(dict.fromkeys(binding_shape))[:4]


def extract_frontmatter(text):
    match = re.match(r"\A---\s*\n(?P<frontmatter>.*?)\n---\s*(?:\n|\Z)", text, re.DOTALL)
    return match.group("frontmatter") if match else ""


def extract_applicability(section, document_text=""):
    frontmatter = extract_frontmatter(document_text)
    source_text = ""
    for line in frontmatter.splitlines():
        if line.strip().lower().startswith("app_type:"):
            source_text = line.split(":", 1)[1]
            break
    if not source_text:
        source_text = section
    applies_to = []
    for label, pattern in APPLICABILITY_PATTERNS:
        if pattern.search(source_text):
            applies_to.append(label)
    if "reactive web apps" in applies_to and "web apps" in applies_to:
        applies_to.remove("web apps")
    return applies_to


def find_source_section_match(text, target_name):
    for priority, heading_name in enumerate(heading_names_for(target_name)):
        section = extract_heading_section(text, heading_name)
        if section and is_valid_target_section(target_name, section):
            return priority, section
    return None, ""


def find_source_section_in_text(text, target_name):
    _, section = find_source_section_match(text, target_name)
    return section


def relevant_markdown_files(source_root):
    source_root = Path(source_root)
    relevant = []
    for markdown_path in read_markdown_files(source_root):
        text = markdown_path.read_text(encoding="utf-8")
        if not is_source_candidate(source_root, markdown_path, text):
            continue
        if any(find_source_section_in_text(text, target["name"]) for target in TARGETS):
            relevant.append(markdown_path)
    return relevant


def is_valid_target_section(target_name, section):
    if target_name not in {"If", "Text"}:
        return True
    return bool(re.search(rf"\b{re.escape(target_name)}\s+widget\b", section, flags=re.IGNORECASE))


def has_relevant_source_files(source_root):
    return bool(relevant_markdown_files(Path(source_root)))


def find_source_section(source_root, target_name):
    candidates = []
    for file_priority, markdown_path in enumerate(relevant_markdown_files(source_root)):
        text = markdown_path.read_text(encoding="utf-8")
        heading_priority, section = find_source_section_match(text, target_name)
        if section:
            candidates.append((heading_priority, file_priority, markdown_path, section))
    if candidates:
        _, _, markdown_path, section = sorted(candidates, key=lambda item: (item[0], item[1]))[0]
        return markdown_path, section
    return None, ""


def prompt_guidance(name, binding_shape):
    if binding_shape:
        return f"Use the {name} element only after the producer values it consumes already exist."
    return f"Use the {name} element only for documented ODC Studio behavior; keep missing facts explicit."


def observed_examples_for(name):
    return OBSERVED_REAL_APP_EXAMPLES.get(name, [])


def studio_toolbox_observations_for(name):
    return ODC_STUDIO_TOOLBOX_OBSERVATIONS.get(name, [])


def official_supporting_sources_for(name, has_generated_o11_candidate=False):
    sources = OFFICIAL_SUPPORTING_SOURCES.get(name, [])
    if not has_generated_o11_candidate:
        return sources
    return [
        {
            **source,
            "compatibility_status": LEGACY_SUPPORTING_SOURCE_COMPATIBILITY_STATUS,
        }
        for source in sources
    ]


def current_contextual_sources_for(name):
    return CURRENT_CONTEXTUAL_SOURCES.get(name, [])


def o11_catalog_candidates(source_root):
    source_root = Path(source_root)
    return [
        source_root / DEFAULT_O11_CATALOG_RELATIVE_PATH,
        source_root / "skills" / "outsystems-mentor-implementation" / DEFAULT_O11_CATALOG_RELATIVE_PATH,
        source_root / ".agents" / "skills" / "outsystems-mentor-implementation" / DEFAULT_O11_CATALOG_RELATIVE_PATH,
    ]


def load_o11_catalog_entries(source_root=None, catalog_path=None):
    if catalog_path is not None:
        catalog_path = Path(catalog_path)
        if not catalog_path.is_file():
            return []
    else:
        for candidate in o11_catalog_candidates(source_root):
            if candidate.is_file():
                catalog_path = candidate
                break
        else:
            return []
    if not catalog_path.is_file():
        return []
    data = json.loads(catalog_path.read_text(encoding="utf-8"))
    return data.get("entries", [])


def o11_candidate_names_for_target(target):
    names = [target["name"]]
    names.extend(target.get("legacy_names", []))
    names.extend(O11_TARGET_ALIASES.get(target["name"], []))
    return list(dict.fromkeys(names))


def select_o11_candidate_support(target, o11_entries):
    candidate_names = set(o11_candidate_names_for_target(target))
    alias_names = candidate_names - {target["name"]}
    candidates = [
        entry
        for entry in o11_entries
        if entry.get("normalized_name") in candidate_names
        and (
            entry.get("support_status") == "O11-supported ODC candidate"
            or (
                entry.get("support_status") == "O11-only support"
                and entry.get("normalized_name") in alias_names
            )
        )
    ]
    if not candidates:
        return None
    selected = sorted(
        candidates,
        key=lambda entry: (
            O11_PAGE_FAMILY_PRIORITY.get(entry.get("page_family", "unknown"), 2),
            0 if entry.get("normalized_name") == target["name"] else 1,
            entry.get("normalized_name", ""),
            entry.get("doc_path", ""),
        ),
    )[0]
    return {
        "support_status": "O11-supported ODC candidate",
        "source_family": selected.get("source_family", ""),
        "source_url": selected.get("source_url", ""),
        "title": selected.get("title", ""),
        "normalized_name": selected.get("normalized_name", ""),
        "page_family": selected.get("page_family", ""),
        "purpose": selected.get("purpose", ""),
        "properties": selected.get("properties", []),
        "events": selected.get("events", []),
        "runtime_properties": selected.get("runtime_properties", []),
        "accessibility_notes": selected.get("accessibility_notes", []),
        "missing_facts": selected.get("missing_facts", []),
        "evidence_level": "Official O11 reference; not current ODC authority",
        "notes": "Use as support-only guidance for confirmed ODC Studio targets and verify in ODC Studio.",
    }


def entry_for_target(source_root, target, o11_entries=None):
    o11_entries = o11_entries or []
    o11_candidate_support = select_o11_candidate_support(target, o11_entries)
    official_supporting_sources = official_supporting_sources_for(
        target["name"], has_generated_o11_candidate=bool(o11_candidate_support)
    )
    markdown_path, section = find_source_section(source_root, target["name"])
    if not markdown_path:
        return {
            "name": target["name"],
            "legacy_names": target.get("legacy_names", []),
            "kind": target["kind"],
            "category": target["category"],
            "source_url": "",
            "doc_path": "",
            "applies_to": [],
            "purpose": "",
            "key_properties": [],
            "events": [],
            "binding_shape": [],
            "mentor_prompt_guidance": "",
            "evidence_status": "Unverified gap",
            "missing_facts": [f"Official source section not found for {target['name']}"],
            "observed_examples": observed_examples_for(target["name"]),
            "studio_toolbox_observations": studio_toolbox_observations_for(target["name"]),
            "current_contextual_sources": current_contextual_sources_for(target["name"]),
            "official_supporting_sources": official_supporting_sources,
            "o11_candidate_support": o11_candidate_support,
        }

    relative = markdown_path.relative_to(source_root)
    purpose = first_paragraph(section)
    properties = parse_table_properties(section)
    events = extract_events(section)
    binding_shape = extract_binding_shape(section)
    applies_to = extract_applicability(section, markdown_path.read_text(encoding="utf-8"))
    missing = []
    if not properties:
        missing.append("Documented properties not found in source section")
    if not events:
        missing.append("Documented events not found in source section")
    if not binding_shape:
        missing.append("Documented binding shape not found in source section")
    if not applies_to:
        missing.append("Documented applicability not found in source section")
    return {
        "name": target["name"],
        "legacy_names": target.get("legacy_names", []),
        "kind": target["kind"],
        "category": target["category"],
        "source_url": source_url_for(relative),
        "doc_path": relative.as_posix(),
        "applies_to": applies_to,
        "purpose": purpose,
        "key_properties": properties,
        "events": events,
        "binding_shape": binding_shape,
        "mentor_prompt_guidance": prompt_guidance(target["name"], binding_shape),
        "evidence_status": "Current official",
        "missing_facts": missing,
        "observed_examples": observed_examples_for(target["name"]),
        "studio_toolbox_observations": studio_toolbox_observations_for(target["name"]),
        "current_contextual_sources": current_contextual_sources_for(target["name"]),
        "official_supporting_sources": official_supporting_sources,
        "o11_candidate_support": o11_candidate_support,
    }


def build_catalog(source_root, o11_source_root=None, o11_catalog=None):
    source_root = Path(source_root)
    if o11_catalog is None and o11_source_root is None:
        o11_source_root = source_root
    o11_source_root = Path(o11_source_root) if o11_source_root is not None else None
    if not read_markdown_files(source_root):
        raise ValueError(f"No Markdown source files found under {source_root}")
    if not has_relevant_source_files(source_root):
        raise ValueError(f"No relevant ODC Studio widget source files found under {source_root}")
    o11_entries = load_o11_catalog_entries(o11_source_root, catalog_path=o11_catalog)
    widgets = [entry_for_target(source_root, target, o11_entries) for target in TARGETS]
    summary = {
        "target_count": len(widgets),
        "current_official_count": sum(1 for item in widgets if item["evidence_status"] == "Current official"),
        "unverified_gap_count": sum(1 for item in widgets if item["evidence_status"] == "Unverified gap"),
        "o11_candidate_support_count": sum(1 for item in widgets if item.get("o11_candidate_support")),
    }
    return {
        "source_family": "official_outsystems_docs_odc",
        "source_search_roots": [path.as_posix() for path in DEFAULT_SEARCH_ROOTS],
        "summary": summary,
        "widgets": widgets,
    }, []


def write_catalog(catalog, warnings, output_path, generated_at_utc=None):
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    generated_at_utc = generated_at_utc or datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    payload = {
        "generated_at_utc": generated_at_utc,
        "warnings": sorted(warnings),
        **catalog,
    }
    output_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def bounded_git_detail(value):
    detail = re.sub(r"\s+", " ", str(value or "")).strip()
    if len(detail) > MAX_GIT_DETAIL_CHARS:
        return detail[:MAX_GIT_DETAIL_CHARS] + "..."
    return detail


def bounded_text(value, limit):
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text if len(text) <= limit else text[:limit] + "..."


def resolve_explicit_source(raw_source):
    try:
        return Path(raw_source).expanduser().resolve()
    except (OSError, RuntimeError, ValueError) as exc:
        message = (
            f"Unable to resolve explicit --source '{bounded_text(raw_source, MAX_SOURCE_DISPLAY_CHARS)}': "
            f"{bounded_git_detail(exc)}. No clone fallback is used for explicit --source."
        )
        raise SystemExit(bounded_text(message, MAX_SOURCE_ERROR_CHARS)) from exc


def normalized_repo_identity(repo_url):
    if repo_url in {DEFAULT_REPO_URL, CANONICAL_SCP_REPO_URL}:
        return DEFAULT_REPO_URL
    return None


def valid_git_object_id(value):
    return bool(re.fullmatch(r"(?:[0-9a-fA-F]{40}|[0-9a-fA-F]{64})", value))


def isolated_git_environment():
    env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
    env.update(
        {
            "GIT_TERMINAL_PROMPT": "0",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_CONFIG_SYSTEM": os.devnull,
        }
    )
    return env


class ClonedRepo:
    def __init__(self, temporary_directory, checkout_root):
        self._temporary_directory = temporary_directory
        self.name = str(checkout_root)

    def cleanup(self):
        self._temporary_directory.cleanup()


def required_git_value(source_root, args, requirement, allow_empty=False):
    command = ["git", "-C", str(source_root), *args]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"{requirement} could not run Git: {bounded_git_detail(exc)}") from exc
    value = result.stdout.strip()
    if result.returncode != 0 or (not value and not allow_empty):
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"{requirement} failed: {detail}")
    return value


def required_origin_url(source_root):
    command = ["git", "-C", str(source_root), "config", "--local", "--null", "--get-all", "remote.origin.url"]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"Git origin check could not run Git: {bounded_git_detail(exc)}") from exc
    raw = result.stdout
    values = raw[:-1].split("\0") if raw.endswith("\0") else []
    if result.returncode != 0 or len(values) != 1 or not values[0]:
        detail = bounded_git_detail(result.stderr or raw or f"Git exited with status {result.returncode}")
        raise ValueError(f"Git origin check requires exactly one nonempty remote.origin.url: {detail}")
    origin = values[0]
    if normalized_repo_identity(origin) is None:
        raise ValueError(f"Git origin mismatch; URL is not an exact allowlisted value: {bounded_git_detail(origin)}")
    return origin


def reject_hidden_index_flags(source_root):
    command = ["git", "-C", str(source_root), "ls-files", "-v", "-z"]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"tracked index flags check could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"tracked index flags check failed: {detail}")
    suspicious = []
    for record in result.stdout.split("\0"):
        if not record:
            continue
        if len(record) < 3 or record[1] != " ":
            raise ValueError(f"tracked index flags check returned malformed output: {bounded_git_detail(record)}")
        status, path = record[0], record[2:]
        if status.islower() or status in {"S", "s"}:
            suspicious.append(f"{status} {path}")
    if suspicious:
        raise ValueError(f"tracked index flags detected: {bounded_git_detail(chr(10).join(suspicious))}")


def require_clean_checkout(source_root):
    reject_hidden_index_flags(source_root)
    command = [
        "git",
        "-c", "core.fileMode=false",
        "-c", "core.ignoreStat=false",
        "-c", "core.trustctime=true",
        "-c", "core.fsmonitor=false",
        "-C", str(source_root),
        "diff", "--quiet", "--no-ext-diff", "HEAD", "--",
    ]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except OSError as exc:
        raise ValueError(f"tracked changes check could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode == 1:
        raise ValueError("tracked changes detected by git diff --quiet HEAD --")
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"tracked changes check failed: {detail}")
    untracked = required_git_value(
        source_root,
        ["ls-files", "--others", "--exclude-standard"],
        "untracked files check",
        allow_empty=True,
    )
    if untracked:
        raise ValueError(f"untracked files detected: {bounded_git_detail(untracked)}")
    ignored = required_git_value(
        source_root,
        ["ls-files", "--others", "--ignored", "--exclude-standard"],
        "ignored untracked files check",
        allow_empty=True,
    )
    if ignored:
        raise ValueError(f"ignored untracked files detected: {bounded_git_detail(ignored)}")


def authoritative_remote_head():
    remote_ref = f"refs/heads/{DEFAULT_BRANCH}"
    command = ["git", "ls-remote", "--exit-code", DEFAULT_REPO_URL, remote_ref]
    env = isolated_git_environment()
    try:
        with tempfile.TemporaryDirectory() as lookup_root:
            result = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
                stdin=subprocess.DEVNULL,
                timeout=REMOTE_LOOKUP_TIMEOUT_SECONDS,
                env=env,
                cwd=lookup_root,
            )
    except subprocess.TimeoutExpired as exc:
        raise ValueError(f"authoritative remote lookup timed out after {REMOTE_LOOKUP_TIMEOUT_SECONDS}s") from exc
    except OSError as exc:
        raise ValueError(f"authoritative remote lookup could not run Git: {bounded_git_detail(exc)}") from exc
    if result.returncode != 0:
        detail = bounded_git_detail(result.stderr or result.stdout or f"Git exited with status {result.returncode}")
        raise ValueError(f"authoritative remote lookup failed: {detail}")
    fields = result.stdout.strip().split()
    if len(fields) != 2 or fields[1] != remote_ref or not valid_git_object_id(fields[0]):
        raise ValueError(f"authoritative remote lookup returned an invalid response: {bounded_git_detail(result.stdout)}")
    return fields[0]


def validate_explicit_source(source_root):
    source_root = resolve_explicit_source(source_root)
    try:
        top_level = required_git_value(source_root, ["rev-parse", "--show-toplevel"], "Git top-level checkout check")
        if Path(top_level).resolve() != source_root:
            raise ValueError(f"Git top-level checkout mismatch: expected {source_root}, got {Path(top_level).resolve()}")
        origin = required_origin_url(source_root)
        if normalized_repo_identity(origin) != normalized_repo_identity(DEFAULT_REPO_URL):
            raise ValueError(f"Git origin mismatch: expected {DEFAULT_REPO_URL}, got {bounded_git_detail(origin)}")
        branch = required_git_value(source_root, ["branch", "--show-current"], "Git branch check")
        if branch != DEFAULT_BRANCH:
            raise ValueError(f"Git branch mismatch: expected {DEFAULT_BRANCH}, got {bounded_git_detail(branch)}")
        head = required_git_value(source_root, ["rev-parse", "--verify", "HEAD^{commit}"], "valid HEAD commit check")
        if not valid_git_object_id(head):
            raise ValueError(f"valid HEAD commit check returned an invalid object id: {bounded_git_detail(head)}")
        remote_ref = f"refs/remotes/origin/{DEFAULT_BRANCH}"
        remote_head = required_git_value(
            source_root,
            ["rev-parse", "--verify", f"{remote_ref}^{{commit}}"],
            f"origin/{DEFAULT_BRANCH} remote-tracking ref check",
        )
        if not valid_git_object_id(remote_head):
            raise ValueError(f"origin/{DEFAULT_BRANCH} remote-tracking ref returned an invalid object id")
        if head != remote_head:
            raise ValueError(
                f"HEAD mismatch: local HEAD {head} must equal origin/{DEFAULT_BRANCH} {remote_head}"
            )
        require_clean_checkout(source_root)
        authoritative_head = authoritative_remote_head()
        if head != authoritative_head:
            raise ValueError(
                f"authoritative remote HEAD mismatch: local HEAD {head} must equal "
                f"{DEFAULT_REPO_URL} {DEFAULT_BRANCH} {authoritative_head}"
            )
    except ValueError as exc:
        message = (
            f"Invalid explicit --source '{bounded_text(source_root, MAX_SOURCE_DISPLAY_CHARS)}': "
            f"{bounded_git_detail(exc)}. Use the top-level {DEFAULT_REPO_URL} checkout on branch "
            f"{DEFAULT_BRANCH} at origin/{DEFAULT_BRANCH} with a clean working tree. "
            "No clone fallback is used for explicit --source."
        )
        raise SystemExit(bounded_text(message, MAX_SOURCE_ERROR_CHARS)) from exc
    return {
        "top_level": source_root,
        "origin": origin,
        "branch": branch,
        "head": head,
        "remote_head": remote_head,
        "authoritative_head": authoritative_head,
    }


def clone_repo(repo_url):
    parent = tempfile.TemporaryDirectory()
    clone = ClonedRepo(parent, Path(parent.name) / "checkout")
    command = ["git", "clone", "--depth", "1", "--branch", DEFAULT_BRANCH, repo_url, clone.name]
    env = isolated_git_environment()
    try:
        subprocess.run(
            command,
            check=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=CLONE_TIMEOUT_SECONDS,
            env=env,
            cwd=parent.name,
        )
        head_result = subprocess.run(
            ["git", "-C", clone.name, "rev-parse", "--verify", "HEAD^{commit}"],
            check=False,
            capture_output=True,
            text=True,
            stdin=subprocess.DEVNULL,
            timeout=CLONE_TIMEOUT_SECONDS,
            env=env,
            cwd=parent.name,
        )
        head = head_result.stdout.strip()
        if head_result.returncode != 0:
            detail = bounded_git_detail(
                head_result.stderr or head_result.stdout or f"Git exited with status {head_result.returncode}"
            )
            raise ValueError(f"cloned HEAD verification failed: {detail}")
        if not valid_git_object_id(head):
            raise ValueError(f"cloned HEAD verification returned an invalid object id: {bounded_git_detail(head)}")
        authoritative_head = authoritative_remote_head()
        if head != authoritative_head:
            raise ValueError(
                f"cloned HEAD {head} does not match authoritative remote {DEFAULT_REPO_URL} "
                f"branch {DEFAULT_BRANCH} at {authoritative_head}"
            )
    except (OSError, subprocess.CalledProcessError, subprocess.TimeoutExpired, ValueError) as exc:
        detail = bounded_git_detail(getattr(exc, "stderr", "") or getattr(exc, "stdout", "") or exc)
        clone.cleanup()
        raise SystemExit(
            f"Unable to clone approved public source {repo_url} on branch {DEFAULT_BRANCH}: {detail}. "
            "Confirm Git is installed and the repository is reachable, then retry."
        ) from exc
    return clone


def build_arg_parser():
    parser = argparse.ArgumentParser(description="Refresh the ODC Studio widget catalog for outsystems-mentor-implementation.")
    parser.add_argument("--source", help="Path to a local OutSystems/docs-odc checkout.")
    parser.add_argument(
        "--o11-source-root",
        help="Root containing outsystems-mentor-implementation/references/o11-designing-screens-widget-catalog.json.",
    )
    parser.add_argument("--o11-catalog", help="Explicit path to the generated O11 Designing Screens catalog JSON.")
    parser.add_argument("--output", required=True, help="Output JSON catalog path.")
    return parser


def resolve_o11_catalog_path(args, cwd=None):
    cwd = Path(cwd) if cwd is not None else Path.cwd()
    if args.o11_catalog:
        return Path(args.o11_catalog)
    if args.o11_source_root:
        return Path(args.o11_source_root) / DEFAULT_O11_CATALOG_RELATIVE_PATH

    repo_local = SKILL_ROOT / DEFAULT_O11_CATALOG_RELATIVE_PATH
    if repo_local.is_file():
        return repo_local
    return cwd / DEFAULT_O11_CATALOG_RELATIVE_PATH


def run_generation(args, cwd=None):
    cwd = Path(cwd) if cwd is not None else Path.cwd()

    cloned = None
    if args.source:
        source_root = validate_explicit_source(args.source)["top_level"]
    else:
        cloned = clone_repo(DEFAULT_REPO_URL)
        source_root = Path(cloned.name)
    o11_catalog = resolve_o11_catalog_path(args, cwd=cwd)

    try:
        try:
            catalog, warnings = build_catalog(source_root, o11_catalog=o11_catalog)
        except ValueError as exc:
            if args.source:
                raise SystemExit(
                    f"{bounded_git_detail(exc)}. Explicit --source must point to a valid OutSystems/docs-odc checkout; "
                    "no clone fallback is used for explicit --source."
                ) from exc
            raise SystemExit(bounded_git_detail(exc)) from exc
        write_catalog(catalog, warnings, args.output)
        print(f"targets={catalog['summary']['target_count']}")
        print(f"current_official={catalog['summary']['current_official_count']}")
        print(f"unverified_gap={catalog['summary']['unverified_gap_count']}")
        print(f"warnings={len(warnings)}")
        return catalog, warnings
    finally:
        if cloned:
            cloned.cleanup()


def main():
    parser = build_arg_parser()
    run_generation(parser.parse_args())


if __name__ == "__main__":
    main()
