import pytest
import json
import copy
from unittest.mock import patch, MagicMock, mock_open
from pathlib import Path
import subprocess
import os
import tempfile
import hashlib


# ---------------------------------------------------------------------------
# Fixtures & helpers
# ---------------------------------------------------------------------------

MOCK_AUDIT_WORKSPACE_A = {
    "auditReportVersion": 2,
    "vulnerabilities": {
        "lodash": {
            "name": "lodash",
            "severity": "critical",
            "isDirect": True,
            "via": [
                {
                    "source": 1179,
                    "name": "lodash",
                    "dependency": "lodash",
                    "title": "Prototype Pollution in lodash",
                    "url": "https://npmjs.com/advisories/1179",
                    "severity": "critical",
                    "cwe": ["CWE-1321"],
                    "cvss": {"score": 9.8, "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"},
                    "range": "<4.17.21",
                }
            ],
            "effects": [],
            "range": "<4.17.21",
            "nodes": ["node_modules/lodash"],
            "fixAvailable": {"name": "lodash", "version": "4.17.21", "isSemVerMajor": False},
        },
        "minimist": {
            "name": "minimist",
            "severity": "high",
            "isDirect": False,
            "via": [
                {
                    "source": 1179,
                    "name": "minimist",
                    "dependency": "minimist",
                    "title": "Prototype Pollution in minimist",
                    "url": "https://npmjs.com/advisories/1179",
                    "severity": "high",
                    "cwe": ["CWE-1321"],
                    "cvss": {"score": 7.3, "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:L/I:L/A:L"},
                    "range": "<1.2.6",
                }
            ],
            "effects": [],
            "range": "<1.2.6",
            "nodes": ["node_modules/minimist"],
            "fixAvailable": {"name": "minimist", "version": "1.2.6", "isSemVerMajor": False},
        },
    },
    "metadata": {
        "vulnerabilities": {"info": 0, "low": 0, "moderate": 0, "high": 1, "critical": 1, "total": 2},
        "dependencies": {"prod": 10, "dev": 5, "optional": 0, "peer": 0, "peerOptional": 0, "total": 15},
    },
}

MOCK_AUDIT_WORKSPACE_B = {
    "auditReportVersion": 2,
    "vulnerabilities": {
        "lodash": {
            "name": "lodash",
            "severity": "critical",
            "isDirect": True,
            "via": [
                {
                    "source": 1179,
                    "name": "lodash",
                    "dependency": "lodash",
                    "title": "Prototype Pollution in lodash",
                    "url": "https://npmjs.com/advisories/1179",
                    "severity": "critical",
                    "cwe": ["CWE-1321"],
                    "cvss": {"score": 9.8, "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"},
                    "range": "<4.17.21",
                }
            ],
            "effects": [],
            "range": "<4.17.21",
            "nodes": ["node_modules/lodash"],
            "fixAvailable": {"name": "lodash", "version": "4.17.21", "isSemVerMajor": False},
        },
        "axios": {
            "name": "axios",
            "severity": "moderate",
            "isDirect": True,
            "via": [
                {
                    "source": 1234,
                    "name": "axios",
                    "dependency": "axios",
                    "title": "Server-Side Request Forgery in axios",
                    "url": "https://npmjs.com/advisories/1234",
                    "severity": "moderate",
                    "cwe": ["CWE-918"],
                    "cvss": {"score": 5.9, "vectorString": "CVSS:3.1/AV:N/AC:H/PR:N/UI:N/S:U/C:H/I:N/A:N"},
                    "range": "<1.6.0",
                }
            ],
            "effects": [],
            "range": "<1.6.0",
            "nodes": ["node_modules/axios"],
            "fixAvailable": {"name": "axios", "version": "1.6.0", "isSemVerMajor": True},
        },
    },
    "metadata": {
        "vulnerabilities": {"info": 0, "low": 0, "moderate": 1, "high": 0, "critical": 1, "total": 2},
        "dependencies": {"prod": 8, "dev": 3, "optional": 0, "peer": 0, "peerOptional": 0, "total": 11},
    },
}

MOCK_AUDIT_WORKSPACE_C = {
    "auditReportVersion": 2,
    "vulnerabilities": {
        "node-fetch": {
            "name": "node-fetch",
            "severity": "low",
            "isDirect": False,
            "via": [
                {
                    "source": 5678,
                    "name": "node-fetch",
                    "dependency": "node-fetch",
                    "title": "Exposure of Sensitive Information in node-fetch",
                    "url": "https://npmjs.com/advisories/5678",
                    "severity": "low",
                    "cwe": ["CWE-200"],
                    "cvss": {"score": 2.6, "vectorString": "CVSS:3.1/AV:N/AC:H/PR:L/UI:R/S:U/C:L/I:N/A:N"},
                    "range": "<2.6.7",
                }
            ],
            "effects": [],
            "range": "<2.6.7",
            "nodes": ["node_modules/node-fetch"],
            "fixAvailable": {"name": "node-fetch", "version": "2.6.7", "isSemVerMajor": False},
        },
        "semver": {
            "name": "semver",
            "severity": "moderate",
            "isDirect": True,
            "via": [
                {
                    "source": 9012,
                    "name": "semver",
                    "dependency": "semver",
                    "title": "Regular Expression Denial of Service in semver",
                    "url": "https://npmjs.com/advisories/9012",
                    "severity": "moderate",
                    "cwe": ["CWE-1333"],
                    "cvss": {"score": 5.3, "vectorString": "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:N/I:N/A:L"},
                    "range": "<7.5.2",
                }
            ],
            "effects": [],
            "range": "<7.5.2",
            "nodes": ["node_modules/semver"],
            "fix