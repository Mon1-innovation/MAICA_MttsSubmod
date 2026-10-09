import ast
from pathlib import Path
import re
import ssl


ROOT = Path(__file__).resolve().parents[1]
SUBMOD = ROOT / "game" / "Submods" / "MAICA_MttsSubmod"
WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"


def test_mtts_requires_certifi_fixer_for_standalone_installation():
    header = (SUBMOD / "header.rpy").read_text(encoding="utf-8")
    dependencies = ast.literal_eval(
        re.search(r"dependencies=(\{[^\n]+\})", header).group(1)
    )

    assert dependencies["CertifiFixer"] == (None, None)
    assert dependencies["Ignore Translation Conflicts"] == (None, None)
    assert "MAICA Blessland" not in dependencies
    assert not (ROOT / "game" / "Submods" / "CertifiFixer").exists()


def test_network_initialization_follows_certifi_repair_and_precedes_ui():
    main = (SUBMOD / "main.rpy").read_text(encoding="utf-8")
    before_import = main[:main.index("    import mtts_package,")]
    init_priority = int(
        re.findall(r"(?m)^init (-?\d+) python in mtts:", before_import)[-1]
    )

    # CertifiFixer repairs files at -100; MTTS UI stores start at -1.
    assert -100 < init_priority < -1


def test_bundled_certificates_load_as_a_trust_store():
    bundle = ROOT / "game" / "python-packages" / "certifi" / "cacert.pem"
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    context.load_verify_locations(cafile=str(bundle))

    assert context.cert_store_stats()["x509_ca"] > 0


def test_release_stages_complete_certifi_fixer_before_packaging():
    workflow = WORKFLOW.read_text(encoding="utf-8")
    download_step = workflow.index("- name: Download CertifiFixer dependency")
    next_step = workflow.index("- name: Create release version file")
    package_step = workflow.index("- name: Create zip package")
    dependency_block = workflow[download_step:next_step]

    assert download_step < next_step < package_step
    assert "if: steps.get_version.outputs.is_development == 'false' && steps.check_release.outputs.create_release == 'true'" in dependency_block
    assert "GH_TOKEN: ${{ github.token }}" in dependency_block
    assert "gh release download --repo MAS-Submod-MoyuTeam/mas_certifi_fixer" in dependency_block
    assert '--pattern "CertifiFixer-*.zip"' in dependency_block
    assert "game/Submods/CertifiFixer" in dependency_block
    for filename in ("certifi_fixer.rpy", "certifi/core.py", "certifi/__init__.py", "certifi/cacert.pem"):
        assert filename in dependency_block
    assert 'cp -R "$dependency_source" game/Submods/' in dependency_block
    assert "exit 1" in dependency_block
